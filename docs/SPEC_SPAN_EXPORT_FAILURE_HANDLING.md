# Specification: Error handling and logging for span export failures

This document refines the backlog item **“Add error handling and logging for span export failures”** into testable requirements. **Production code and tests** belong in **`src/replayt_otel_span_exporter/`** and **`tests/`**; this file is the contract for what “done” means for that item.

It **extends** **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)** (especially §2.2–§2.3). Where the two conflict after this backlog lands, **this document wins** for logging, redaction, and integrator-visible failure documentation until a follow-on spec reconciles them.

## Backlog traceability

| Original acceptance criterion | Satisfied by (this doc) |
| --------------------------- | ------------------------ |
| Errors are logged with context | [§3 Logging contract](#3-logging-contract), [§7 Verifiable acceptance checklist](#7-verifiable-acceptance-checklist) |
| Failure surfaces are documented | [§4 Integrator-visible failure surfaces](#4-integrator-visible-failure-surfaces), [§8 Documentation deliverables](#8-documentation-deliverables) |
| No secrets leaked in logs | [§5 Secrets, attributes, and redaction](#5-secrets-attributes-and-redaction), [§7 Checklist](#7-verifiable-acceptance-checklist) |

## Goals

- When **`ReplaytSpanExporter.export`** (or the documented mapping path from **`ReadableSpan`** to **`PreparedSpanRecord`**) hits an **internal** error, **integrators and operators** get **actionable signals**: structured logs with enough context to correlate failures with traces, without dumping unsafe data.
- **Stakeholder-visible reports** (log aggregation, support tickets) can rely on **stable logger names**, **severity levels**, and **documented fields** rather than reading library source.
- Behavior stays compatible with the OpenTelemetry Python SDK expectation that exporters **avoid raising** for normal pipeline use; **`SpanExportResult.FAILURE`** remains the primary programmatic signal (see skeleton §2.3).

## Non-goals (this backlog)

- Defining a new public exception type for integrators to catch from **`export`** (the SDK contract remains return-code oriented unless OpenTelemetry upstream patterns change).
- Remote log shipping, metrics backends, or **OpenTelemetry** logging exporter integration—only **stdlib** **`logging`** (or a thin wrapper that still uses the standard **`Logger`** API) is in scope.
- Changing **replayt** boundary tests beyond what is needed to keep CI honest when this spec adds tests (see **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** for boundary ownership).

## 1. Scope of “export failure”

For this backlog, an **export failure** means any case where **`ReplaytSpanExporter.export`** returns **`SpanExportResult.FAILURE`** due to an **unexpected exception** in this package while handling a batch (mapping spans, appending to the buffer, or lock-protected sections), **excluding**:

- **Post-`shutdown()` no-op exports** — still **`SUCCESS`** per skeleton §2.2; no failure logging required for that path.
- **Policy denial via an integrator approval hook** — per **[docs/SPEC_SPAN_EXPORT_APPROVAL_UX.md](SPEC_SPAN_EXPORT_APPROVAL_UX.md)**, a hook returning **`"deny"`** is **not** an export failure: **`export`** returns **`SUCCESS`** and does not append records. That path is **not** required to emit **ERROR**-level failure logs from this package; audit visibility is specified in the approval spec §5.

**Batch semantics (normative):** If any span in the batch raises during processing, the exporter **MUST** return **`FAILURE`** for the whole batch (consistent with today’s single **`try`** around the loop). It **MUST NOT** claim **`SUCCESS`** if any span in that call was not appended. The log entry **SHOULD** include the **batch size** (`len(spans)`). If the implementation can identify **which span** failed (index or stable id), **SHOULD** include that in structured fields.

## 2. Relationship to the skeleton spec

- Skeleton **[§2.3 Error handling](SPEC_OTEL_EXPORTER_SKELETON.md#23-error-handling)** remains: **do not raise** into the SDK for normal use; return **`FAILURE`** on internal errors.
- This spec **adds**: **logging**, **redaction rules**, and **documented integrator-facing failure behavior** (below).
- The skeleton’s **“Recommended test (non-blocking for spec gate)”** becomes **blocking** for this backlog: controlled failure tests **MUST** exist and **MUST** be extended per [§6 Test contract](#6-test-contract-builder).

## 3. Logging contract

### 3.1 Logger naming

- Use the **`logging`** hierarchy under **`replayt_otel_span_exporter`** (for example **`replayt_otel_span_exporter.exporter`** for code in **`exporter.py`**). **Do not** introduce ad hoc root loggers or unnamed loggers.

### 3.2 When to log

- On the code path that returns **`SpanExportResult.FAILURE`** because of an **unexpected exception**, emit **at least one** log record at **`logging.ERROR`** (or **`logging.WARNING`** only if the project explicitly documents a recoverable class of errors—default to **`ERROR`** for unexpected exceptions).
- Include **`exc_info=True`** on that record so operators see stack traces in standard log pipelines.

### 3.3 Context fields (minimum)

Log messages **SHOULD** be human-readable one-line summaries (for example that export failed while preparing spans). Structured attributes **SHOULD** be attached in a way typical for **`logging`** in this codebase (**`extra=`** dict or parameterized message fields), including where available:

| Field | Meaning |
| ----- | ------- |
| **`span_count`** | Number of spans in the **`export`** call (`len(spans)`). |
| **`failed_span_index`** | Zero-based index of the span being processed when the exception occurred, if known. |
| **`trace_id`** / **`span_id`** | For per-span failures, **lowercase hex** matching skeleton §3 encoding (same as **`format_trace_id`** / **`format_span_id`**), so logs correlate with traces **without** leaking arbitrary attribute payloads. |

Fields **MUST NOT** duplicate full span **attribute** maps in log **message** text or **`extra`** by default (see §5).

## 4. Integrator-visible failure surfaces

Integrators observe failures through:

1. **`SpanExportResult.FAILURE`** from **`export`** (programmatic).
2. **Log records** emitted per §3 (operational).
3. **Documentation** per [§8](#8-documentation-deliverables) (discoverable).

**Human-readable** means: the **primary** log line is understandable without reading Python tracebacks (tracebacks remain available via **`exc_info`**). Avoid opaque codes unless documented in §8.

## 5. Secrets, attributes, and redaction

### 5.1 Prohibited content in export-failure logs

**Prepared-span IR:** Key-based **value** redaction on **`PreparedSpanRecord.attributes`** (literal **`"[REDACTED]"`** for sensitive keys) is specified in **[docs/SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)** §3. That work **does not** change §5.1’s logging prohibitions; it **does** make exported buffers safer for in-process inspection.

On **export failure** log records (and on **INFO** or higher in exporter code paths), **MUST NOT** emit:

- Full **`PreparedSpanRecord.attributes`** mappings or raw **`ReadableSpan`** attribute dicts.
- Values of keys that are **commonly sensitive**, including case-insensitive substring matches for: **`authorization`**, **`password`**, **`secret`**, **`token`**, **`api_key`**, **`apikey`**, **`bearer`**, **`cookie`**, **`credential`**. (List is illustrative; Builder **MUST** implement a **single documented redaction helper** or rule set used by the exporter’s logging path.)
- Raw **W3C trace context** header strings if ever handled as strings in this package (not expected today—if added later, treat as sensitive).

**Allowed** at **ERROR** with failure context: **trace** and **span** identifiers per §3.3, **span name** (string), **span kind** (enum name or string), **batch size**, **exception type** name, and **exception message** text **unless** §5.2 (third-party messages) applies.

### 5.2 Third-party exception messages

If the raised exception originates outside this package (for example **`opentelemetry`** internals), still log with **`exc_info=True`**, but **document** in §8 that integrators should treat **exception messages** as **untrusted**. The implementation **SHOULD NOT** concatenate untrusted exception messages into a single user-facing string without bounds; prefer structured logging fields and standard **`logging`** exception formatting.

### 5.3 DEBUG and finer detail

**DEBUG**-level logs **MAY** include more detail for maintainers, but **MUST** still apply the same redaction rules as **INFO** and above unless the spec is explicitly amended. Tests **MUST** prove that sensitive attribute values do not appear at **ERROR** (see [§6](#6-test-contract-builder)).

## 6. Test contract (Builder)

Tests **MUST** prove:

1. **Failure return + log:** When transformation is forced to fail (stub span, monkeypatched mapper, or similar), **`export`** returns **`SpanExportResult.FAILURE`**, does **not** raise, and emits **≥1** log record on the **`replayt_otel_span_exporter`** logger subtree at **`ERROR`** (or the documented level) with **`exc_info`** set (assert via **`caplog`** / **`pytest`’s** **`caplog`** or equivalent).
2. **Context:** The failure log **SHOULD** include **`span_count`** (or an equivalent clearly documented field). If **`failed_span_index`** is implemented, cover it in at least one test.
3. **Redaction:** A span whose attributes contain a **synthetic secret-like** key (for example **`user.password`**) and value **MUST NOT** cause that **value** to appear in the **captured log output** for the export-failure record (string search on **`caplog.text`** or structured capture).

Existing skeleton tests for **`shutdown`** / **`force_flush`** remain; add focused tests in **`tests/test_exporter.py`** (or a dedicated module if the suite is split) without bypassing default **`pytest`** discovery.

## 7. Verifiable acceptance checklist

Use this checklist in **Spec gate**, **Build gate**, and PR review for this backlog.

1. On internal **`export`** failure, **`SpanExportResult.FAILURE`** is returned and **no** exception propagates to the SDK caller (skeleton §2.3).
2. A **documented** **`logging`** logger under **`replayt_otel_span_exporter.*`** emits **ERROR** (or documented **WARNING**) with **`exc_info`** for that failure path.
3. Log context includes **batch size** and, when feasible, **failing span index** and **trace_id** / **span_id** in hex—without dumping full attribute maps (§3, §5).
4. **Redaction** rules from §5 are implemented centrally and covered by tests ([§6](#6-test-contract-builder) item 3).
5. **[§8 Documentation deliverables](#8-documentation-deliverables)** are present and linked from **[README.md](../README.md)** or the package overview.

## 8. Documentation deliverables

The Builder **MUST**:

- Add a short **“Export failures”** (or equivalent) subsection to **`README.md`** stating: failures surface as **`SpanExportResult.FAILURE`**, **logs** use the **`replayt_otel_span_exporter`** logger hierarchy, and **sensitive span attributes are not logged** on failure—pointing to **this spec** for field names and redaction rules.
- Cross-link this spec from **`docs/SPEC_OTEL_EXPORTER_SKELETON.md`** §2.3 (already required by skeleton maintenance when this backlog completes).

## Implementation notes for Builder / Maintainer

- Prefer **one** helper (for example **`_log_export_failure(...)`**) over scattered **`logger.exception`** calls so redaction and field names stay consistent.
- If OpenTelemetry or Python **`logging`** conventions change, update this spec and **`CHANGELOG.md`** in the same maintenance pass.
