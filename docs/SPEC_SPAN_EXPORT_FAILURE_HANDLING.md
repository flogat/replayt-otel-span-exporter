# Specification: Error handling and logging for span export failures

This document refines the backlog item **“Add error handling and logging for span export failures”** into testable requirements. **Production code and tests** belong in **`src/replayt_otel_span_exporter/`** and **`tests/`**; this file is the contract for what “done” means for that item.

A follow-on backlog, **“Audit exporter logging for injection and oversized fields on failure paths”**, **tightens** §5–§7 with **normative** caps on untrusted strings, **C0 / C1 control-character** handling for log fields, and **explicit** tests ([§6](#6-test-contract-builder) items 4–6) so centralized log pipelines stay safe. **§5.4** and those tests are **blocking** for that backlog’s **Build gate** once this revision is merged.

It **extends** **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)** (especially §2.2–§2.3). Where the two conflict after this backlog lands, **this document wins** for logging, redaction, and integrator-visible failure documentation until a follow-on spec reconciles them.

## Backlog traceability

| Original acceptance criterion | Satisfied by (this doc) |
| --------------------------- | ------------------------ |
| Errors are logged with context | [§3 Logging contract](#3-logging-contract), [§7 Verifiable acceptance checklist](#7-verifiable-acceptance-checklist) |
| Failure surfaces are documented | [§4 Integrator-visible failure surfaces](#4-integrator-visible-failure-surfaces), [§8 Documentation deliverables](#8-documentation-deliverables) |
| No secrets leaked in logs | [§5 Secrets, attributes, and redaction](#5-secrets-attributes-and-redaction), [§7 Checklist](#7-verifiable-acceptance-checklist) |
| **Audit: cap / sanitize third-party exception text; length limits; redaction alignment; tests** (backlog **“Audit exporter logging for injection and oversized fields on failure paths”**) | [§5.2](#52-third-party-exception-messages-and-untrusted-strings)–[§5.4](#54-bounded-string-fields-and-log-injection-hardening), [§6](#6-test-contract-builder), [§7](#7-verifiable-acceptance-checklist) |

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
- Values of keys that are **commonly sensitive**, classified by the **same** case-insensitive substring policy as **`replayt_otel_span_exporter.redaction.attribute_key_is_sensitive`** (see **[docs/SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)** §3.1). The Builder **MUST NOT** fork that table into a second implementation for logging-only checks; use **`attribute_key_is_sensitive`** (or a thin wrapper that delegates to it) anywhere export-failure logging needs key sensitivity.
- Raw **W3C trace context** header strings if ever handled as strings in this package (not expected today—if added later, treat as sensitive).

**Allowed** at **ERROR** with failure context: **trace** and **span** identifiers per §3.3, **span name** (string, after §5.4), **span kind** (enum name or string), **batch size**, **exception type** name (fully qualified is fine if short), and **exception message** text **only** after §5.2–§5.4 sanitization and truncation.

### 5.2 Third-party exception messages and untrusted strings

**Untrusted** for this section means any string not constructed entirely from values defined inside **`replayt_otel_span_exporter`** (for example **`str(exception)`** from a third-party library, OpenTelemetry internals, or integrator-supplied span names). Integrators are trusted for intent but **not** for size or character content in log sinks.

- The implementation **MUST** pass **exception messages** (and any other untrusted strings placed in the **log message line** or string-valued **`extra=`** fields on export-failure paths) through the **same** sanitization pipeline as §5.4 before emission.
- **`exc_info=True`** remains **required** for unexpected failures (§3.2); stack traces from **`logging`** are **out of band** for §5.4’s character limits on the **primary** message and **`extra`** strings, but **message** / **`extra`** text the implementation **builds** from **`str(exception)`** **MUST** still be capped and control-stripped so formatters cannot be driven to multi-megabyte single fields.
- **Document** in §8 (and **README**) that integrators should treat **exception text** as **untrusted** for security policy even after sanitization.

### 5.3 DEBUG and finer detail

**DEBUG**-level logs **MAY** include more detail for maintainers, but **MUST** still apply the same redaction rules as **INFO** and above unless the spec is explicitly amended. Tests **MUST** prove that sensitive attribute values do not appear at **ERROR** (see [§6](#6-test-contract-builder)).

### 5.4 Bounded string fields and log-injection hardening

For **every** untrusted string copied into the **user-visible** parts of a failure log record—the **`msg`** format string’s **interpolated** segments, **`%`-style** substitutions, **f-string** payloads, and **string** values in **`extra=`** that are not fixed literals—the implementation **MUST**:

1. **Truncate** by **Unicode code points** (Python **`len` on `str`**) to at most:
   - **`1024`** for **exception message** text (derived from **`str(exception)`** or **`args`**, after any coercion to string).
   - **`256`** for **span name** (and, if logged on failure paths, any other single integrator-chosen free-text label documented in §3.3 or Builder maintenance notes).
2. **Strip control risk:** Remove or replace **Unicode** code points in the ranges **U+0000–U+001F** (C0 controls) and **U+007F–U+009F** (DEL and C1 controls) **before** truncation (order **MAY** be replace-then-truncate or truncate-then-replace, but the final emitted string **MUST** satisfy both rules). **Recommended** replacement: **`U+0020 SPACE`** for all such code points so line-oriented aggregators do not treat embedded **LF** / **CR** / **NEL** as record boundaries.
3. **Document** the numeric limits and the control ranges in **`CHANGELOG.md`** when behavior ships and in code (**module-level constants** or the sanitization helper’s docstring) so operators can tune downstream parsers.

**Normative constants (informative names):** The Builder **SHOULD** expose **`_MAX_LOG_EXCEPTION_MESSAGE_CHARS`** and **`_MAX_LOG_SPAN_NAME_CHARS`** (or equivalent private constants) next to the sanitizer to avoid magic numbers in tests.

**Rationale:** Prevents oversized fields from blowing up log storage and reduces **log injection** (fake severity lines, CRLF splits) when third-party or integrator data is echoed into **`stdout`** / JSON encoders / SIEM parsers.

## 6. Test contract (Builder)

Tests **MUST** prove:

1. **Failure return + log:** When transformation is forced to fail (stub span, monkeypatched mapper, or similar), **`export`** returns **`SpanExportResult.FAILURE`**, does **not** raise, and emits **≥1** log record on the **`replayt_otel_span_exporter`** logger subtree at **`ERROR`** (or the documented level) with **`exc_info`** set (assert via **`caplog`** / **`pytest`’s** **`caplog`** or equivalent).
2. **Context:** The failure log **SHOULD** include **`span_count`** (or an equivalent clearly documented field). If **`failed_span_index`** is implemented, cover it in at least one test.
3. **Redaction:** A span whose attributes contain a **synthetic secret-like** key (for example **`user.password`**) and value **MUST NOT** cause that **value** to appear in the **captured log output** for the export-failure record (string search on **`caplog.text`** or structured capture).
4. **Exception message bound:** Force a failure with an exception whose **`str()`** exceeds **`1024`** code points; assert the **sanitized** exception substring present in the **message** or documented **`extra`** fields is **at most** **`1024`** characters (or that content beyond the limit does not appear verbatim—e.g. suffix probe).
5. **Control / injection hardening:** Force a failure with an exception message containing **LF** (**U+000A**), **CR** (**U+000D**), and at least one **C1** control (for example **`U+0085` NEL**). Assert **U+000A**, **U+000D**, and **U+0085** from that synthetic payload do **not** appear in the **sanitized** **message** / documented **`extra`** string fields (they **MAY** appear inside **`logging`**’s traceback attachment from **`exc_info`**—the test **SHOULD** target the structured fields or **record.msg** / **record.getMessage()** rather than the full **`caplog.text`** if tracebacks would confuse the assertion).
6. **Span name bound:** When the failure path logs **span name**, use a name longer than **`256`** code points; assert the **logged** name segment is **at most** **`256`** code points (or that the excess does not appear).

Existing skeleton tests for **`shutdown`** / **`force_flush`** remain; add focused tests in **`tests/test_exporter.py`** (or a dedicated module if the suite is split) without bypassing default **`pytest`** discovery.

## 7. Verifiable acceptance checklist

Use this checklist in **Spec gate**, **Build gate**, and PR review for this backlog.

1. On internal **`export`** failure, **`SpanExportResult.FAILURE`** is returned and **no** exception propagates to the SDK caller (skeleton §2.3).
2. A **documented** **`logging`** logger under **`replayt_otel_span_exporter.*`** emits **ERROR** (or documented **WARNING**) with **`exc_info`** for that failure path.
3. Log context includes **batch size** and, when feasible, **failing span index** and **trace_id** / **span_id** in hex—without dumping full attribute maps (§3, §5).
4. **Redaction** rules from §5 are implemented centrally (**`attribute_key_is_sensitive`** for key policy) and covered by tests ([§6](#6-test-contract-builder) item 3).
5. **Untrusted strings** on failure paths satisfy §5.4 (truncation + control stripping) and are covered by tests ([§6](#6-test-contract-builder) items 4–6).
6. **[§8 Documentation deliverables](#8-documentation-deliverables)** are present and linked from **[README.md](../README.md)** or the package overview.

## 8. Documentation deliverables

The Builder **MUST**:

- Add a short **“Export failures”** (or equivalent) subsection to **`README.md`** stating: failures surface as **`SpanExportResult.FAILURE`**, **logs** use the **`replayt_otel_span_exporter`** logger hierarchy, **sensitive span attributes are not logged** on failure, and **exception text / span names are bounded and control-stripped** for log-pipeline safety—pointing to **this spec** for field names, redaction rules, and numeric limits (§5.4).
- Cross-link this spec from **`docs/SPEC_OTEL_EXPORTER_SKELETON.md`** §2.3 (already required by skeleton maintenance when this backlog completes).

## Implementation notes for Builder / Maintainer

- Prefer **one** helper (for example **`_sanitize_log_string(value, max_chars)`** plus **`_log_export_failure(...)`**) over scattered **`logger.exception`** calls so redaction, caps, and field names stay consistent.
- If OpenTelemetry or Python **`logging`** conventions change, update this spec and **`CHANGELOG.md`** in the same maintenance pass.
