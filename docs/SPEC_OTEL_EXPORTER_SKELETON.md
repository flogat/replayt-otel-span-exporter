# Specification: OpenTelemetry span exporter skeleton

This document refines the backlog item **“Implement basic OpenTelemetry span exporter skeleton”** into testable requirements. **Production code and tests** belong in **`src/replayt_otel_span_exporter/`** and **`tests/`**; this file is the contract for what “done” means for that item.

## Backlog traceability

| Original acceptance criterion | Satisfied by (this doc) |
| ----------------------------- | ------------------------ |
| Exporter class exists with basic interface | [§2 Public surface](#2-public-surface-and-opentelemetry-contract), [§6 Checklist](#6-verifiable-acceptance-checklist) |
| Unit tests verify span ingestion and basic transformation | [§4 Test contract](#4-test-contract), [§6 Checklist](#6-verifiable-acceptance-checklist) |
| Code follows project layout and style | [§5 Layout and style](#5-layout-and-style), [§6 Checklist](#6-verifiable-acceptance-checklist) |

**Export failure UX:** **[docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)** extends §2.3 with logging, redaction, and integrator documentation requirements for **`ReplaytSpanExporter.export`** failures.

**Triage metadata and IR attribute redaction:** **[docs/SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)** extends §3 with **`workflow_id`** / **`step_id`** fields and key-based value redaction on **`PreparedSpanRecord.attributes`** using **`replayt_otel_span_exporter.redaction.attribute_key_is_sensitive`**.

## Reference naming (normative for this repository)

These names are the **canonical** integration surface for the backlog item; Builder and review phases should treat them as the stable contract unless a follow-on backlog explicitly renames or splits them.

| Symbol | Location | Notes |
| ------ | -------- | ----- |
| **`ReplaytSpanExporter`** | **`replayt_otel_span_exporter.exporter`** | **`SpanExporter`** implementation; primary hook for **`TracerProvider`** processors. |
| **`PreparedSpanRecord`** | **`replayt_otel_span_exporter.records`** | Frozen dataclass IR (see §3). |
| **`__version__`** | **`replayt_otel_span_exporter`** (package) | Package version string; listed in **`__all__`**. |

**`replayt_otel_span_exporter.__all__`** MUST list **only** integrator-facing symbols: **`ReplaytSpanExporter`**, **`PreparedSpanRecord`**, and **`__version__`**. Helpers such as **`prepared_span_record_from_readable`** and **`serialize_attribute_value`** live in **`records`** and MAY remain **omitted** from **`__all__`** as long as their behavior is covered by tests (exporter pipeline tests and/or focused unit tests).

## Goals

- Provide a **small, explicit** Python API that plugs into the **OpenTelemetry Python SDK** tracing pipeline as a **`SpanExporter`**, so spans can be collected and **normalized into a replayt-oriented representation** without yet depending on the **`replayt`** distribution.
- Keep **consumer-side** evolution safe: document what is stable vs experimental, and what additional dependencies the Builder is expected to add.

## Non-goals (this backlog)

- Shipping a full replayt workflow integration, RPC, or file format—only **in-process preparation** of span data.
- Adding **`replayt`** as a runtime dependency unless a later backlog item requires it. (Test-time / optional **`replayt`** for integration tests is specified separately in **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)**.)
- Performance tuning, batching policies beyond what the SDK already provides, or custom `SpanProcessor` types unless needed to satisfy §2–§4.

## 1. Dependencies and versions

- **`opentelemetry-api`** and **`opentelemetry-sdk`** are **runtime** dependencies declared in **`[project].dependencies`** in **`pyproject.toml`** (lower bounds must stay aligned—typically the same minimum major/minor policy for both packages).
- When pins change, update **`docs/DEPENDENCY_AUDIT.md`** in the same maintenance pass and keep CI green on the Python matrix defined in **`docs/CI_SPEC.md`**.
- **Supported OpenTelemetry versions** for this skeleton: minimum versions follow **`pyproject.toml`**; resolved versions in CI/dev installs should remain compatible with the APIs this spec relies on (**`SpanExporter`**, **`ReadableSpan`**, **`TracerProvider`**, **`SimpleSpanProcessor`** or **`BatchSpanProcessor`**). Document material compatibility shifts in **`docs/MISSION.md`** when the matrix or pins change.

## 2. Public surface and OpenTelemetry contract

### 2.1 Type and module placement

- The primary exporter class lives in **`src/replayt_otel_span_exporter/`** in a dedicated module (for example **`exporter.py`**). Avoid dumping implementation-only helpers into **`__init__.py`** beyond thin re-exports if the package chooses to expose the class at package root.
- **`__all__`** (package and/or module) should list **only** symbols intended for integrators. Internal helpers use a leading underscore or live in a clearly private submodule (for example **`_records.py`**).

### 2.2 Exporter behavior

- The class **subclasses** **`opentelemetry.sdk.trace.export.SpanExporter`** (or otherwise satisfies the same contract if the SDK’s typing evolves—prefer subclassing for clarity).
- **Constructor** — MUST accept an optional **shared buffer** argument (for example **`records: list[PreparedSpanRecord] | None = None`**) so tests can inject a list and observe appends without reflection. When omitted, the exporter uses an internal empty list.
- **Required methods** (names and semantics aligned with the SDK):
  - **`export(spans)`** — Accept a **`Sequence`** (or equivalent) of **finished** **`ReadableSpan`** instances, map each to **`PreparedSpanRecord`** (§3), and **append** to the buffer. Return **`SpanExportResult.SUCCESS`** when all spans in the batch are handled without internal error.
  - **`shutdown()`** — Idempotent flag so that **subsequent** **`export`** calls do **not** append new records; those calls still return **`SpanExportResult.SUCCESS`** (no-op export) for this skeleton so the SDK pipeline is not left in a failure state after shutdown.
  - **`force_flush(timeout_millis=...)`** — Return a **`bool`**. For this skeleton there is **no** asynchronous queue: **`force_flush`** MAY be a synchronous no-op that always returns **`True`**; document the chosen behavior and cover it with a unit test (including that a provided **`timeout_millis`** is accepted without error).

**Thread safety:** If the exporter uses a mutable buffer and may be called from SDK worker threads, concurrent **`export`** / **`shutdown`** / reads of the buffer MUST be safe (for example a **`threading.Lock`** around buffer mutation and snapshots).

### 2.3 Error handling

- **`export`** MUST NOT raise into the SDK for **normal** callback usage: unexpected errors during transformation SHOULD be caught and surfaced as **`SpanExportResult.FAILURE`** so a buggy exporter does not tear down the application’s tracing thread. Document any intentional propagation of exceptions.
- **Logging, redaction, and documented failure surfaces** for export failures are specified in **[docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)**. Treat that spec’s **§7** checklist as part of exporter “done” for failure UX.
- **Required tests:** a controlled test that forces transformation to fail (for example a stub span or monkeypatched mapper) **MUST** assert **`export`** returns **`SpanExportResult.FAILURE`** without raising. The suite **MUST** also satisfy **`SPEC_SPAN_EXPORT_FAILURE_HANDLING.md`** §6 (logging and redaction assertions).

## 3. Prepared span records (“replayt-oriented”)

The backlog asks to **prepare** spans for replayt workflows **before** this repo takes a hard dependency on replayt. The Builder must define a **stable, documented intermediate representation** (IR) used across implementation and tests.

**Minimum fields** each prepared record should expose (names may be attribute names on a **`dataclass`**, **`TypedDict`**, or read-only properties—pick one style and use it consistently):

| Field | Source (conceptual) | Notes |
| ----- | ------------------- | ----- |
| **trace_id** | Span context | Hex string or raw 16-byte representation—**document the encoding**. |
| **span_id** | Span context | Same as above for span id (8 bytes). |
| **name** | Span name | Non-empty string for typical spans. |
| **kind** | Span kind | String or enum name stable for tests. |
| **start_time_unix_nano** / **end_time_unix_nano** | Span start/end | Integer nanoseconds since Unix epoch, matching SDK `ReadableSpan` time fields. |
| **attributes** | Span attributes | Plain **`dict`** with string keys and JSON-friendly values; serialization rules MUST match the **`records`** module contract (scalars, homogeneous sequences, **`bytes`** → UTF-8 text with replacement on decode errors, unknown types stringified). Values for keys classified as sensitive by **`replayt_otel_span_exporter.redaction.attribute_key_is_sensitive`** MUST be replaced per **[docs/SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)** §3 when that backlog is in scope. |
| **workflow_id** | Span attribute **`replayt.workflow_id`** | **`str | None`** — first-class triage field; see **[docs/SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)** §2. |
| **step_id** | Span attribute **`replayt.step_id`** | **`str | None`** — first-class triage field; same spec. |

**Edge cases (normative):**

- **Invalid or missing span context** — **`trace_id`** and **`span_id`** use the same **zero-padded lowercase hex** encoding as **`opentelemetry.trace.format_trace_id`** / **`format_span_id`** for the all-zero ID (32 and 16 hex characters respectively).
- **Missing start or end times** — Store **`0`** for the missing side so fields remain **`int`**; tests using real finished spans from the SDK should still see positive, ordered timestamps.

**Optional for this skeleton** (document if present or explicitly deferred): parent span id, status code/message, links, events, resource attributes.

The IR type must be **importable for tests** under the package namespace (**`PreparedSpanRecord`** in **`replayt_otel_span_exporter.records`**, re-exported from **`replayt_otel_span_exporter`** per the reference naming section).

## 4. Test contract

Tests are implemented in phase **3** (Builder) and later; this section defines **what** they must prove.

### 4.1 Span ingestion

- At least one test **drives the real SDK** far enough to produce **finished** spans that flow into the exporter (for example: configure a **`TracerProvider`** with a **`SimpleSpanProcessor`** or **`BatchSpanProcessor`** wired to the new exporter, start a span, end it, then force flush/shutdown as needed).
- Assertions: after export, the exporter’s observable buffer (or equivalent) contains **the expected number** of prepared records (≥ 1 for the minimal case).

### 4.2 Basic transformation

- Assertions on **at least one** prepared record:
  - **name** matches the span started in the test.
  - **trace_id** and **span_id** are **non-empty** (for valid SDK spans) and **exactly equal** to **`format_trace_id`** / **`format_span_id`** applied to the live span context (§3 encoding).
  - **kind** matches the **`SpanKind`** enum **member name** used for that span (for example **`INTERNAL`** for default internal spans).
  - **start/end** times are **ordered** (`start <= end`) and **strictly positive** for a normal finished span created through the SDK in the test.
  - **attributes**: setting a string attribute on the span appears on the prepared record’s **attributes** mapping with the expected key and value.

**Attribute serialization (unit tests):** At least one test module MUST exercise **`serialize_attribute_value`** (or equivalent documented helper) for representative **`AttributeValue`** shapes—scalars, short homogeneous sequences, **`bytes`**, and the “unknown type → string” fallback—so IR attribute rules do not regress without going through a full tracer pipeline.

### 4.3 Lifecycle

- Tests cover **`shutdown()`** preventing further appends while leaving the buffer content stable, and **`force_flush()`** per the documented §2.2 semantics (including acceptance of **`timeout_millis`** when the signature includes it).

### 4.4 Placement

- Prefer **`tests/unit/`** for fast, focused tests if the repo introduces that layout; otherwise follow **[docs/CI_SPEC.md](CI_SPEC.md)** §6 and place files under **`tests/`** with clear naming (for example **`test_exporter.py`**). New tests must run under the **default `pytest` invocation** documented in CI.

### 4.5 Triage metadata and redacted attributes (when in scope)

- When the **“Add metadata for triage without leaking secrets”** backlog is active, extend coverage per **[docs/SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)** §5 (triage field population, absence, coercion, and **`[REDACTED]`** values for sensitive attribute keys).

## 5. Layout and style

- Match **`ruff`**-clean style and existing package patterns (**`src/`** layout, **`pyproject.toml`** metadata).
- No new top-level packages; keep code under **`src/replayt_otel_span_exporter/`**.
- Update **`docs/DEPENDENCY_AUDIT.md`** when **`opentelemetry-api`**, **`opentelemetry-sdk`**, or related pins change.

## 6. Verifiable acceptance checklist

Use this checklist in **Spec gate**, **Build gate**, and PR review. Every item MUST pass before treating the backlog item as satisfied.

1. **`ReplaytSpanExporter`** is importable from **`replayt_otel_span_exporter`** and subclasses **`opentelemetry.sdk.trace.export.SpanExporter`**.
2. **`PreparedSpanRecord`** is importable from the package root and matches §3 field names and encodings (including edge cases).
3. **`export`**, **`shutdown`**, and **`force_flush`** behave per §2.2–§2.3 and are covered by automated tests.
4. At least one test drives a real **`TracerProvider`** + span processor so a finished span reaches **`export`**; assertions cover §4.1–§4.2.
5. Attribute serialization rules have focused coverage per §4.2 (not only through end-to-end tracer tests).
6. **`__all__`** contains only **`ReplaytSpanExporter`**, **`PreparedSpanRecord`**, and **`__version__`** (no accidental public leakage of helpers).
7. Layout and **`ruff`**-clean style per §5; dependency audit row for OpenTelemetry matches **`pyproject.toml`**.
8. When the **“Add metadata for triage without leaking secrets”** backlog is in scope: **`PreparedSpanRecord`** triage fields, redacted **`attributes`**, tests, and docs per **[docs/SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)** §7.

## Implementation notes for Builder / Maintainer

- When this spec and **`docs/MISSION.md`** diverge from **`pyproject.toml`** or CI, update **both** the code and the docs in the same maintenance pass.
- If OpenTelemetry Python changes **`SpanExporter`** or **`ReadableSpan`** in a way that breaks subclassing, add a compatibility note under **[docs/DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** (“Consumer-side maintenance”) and adjust this spec in the same change.
