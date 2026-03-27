# Specification: OpenTelemetry span exporter skeleton

This document refines the backlog item **“Implement basic OpenTelemetry span exporter skeleton”** into testable requirements. **Production code and tests** belong in **`src/replayt_otel_span_exporter/`** and **`tests/`**; this file is the contract for what “done” means for that item.

## Backlog traceability

| Original acceptance criterion | Satisfied by (this doc) |
| ----------------------------- | ------------------------ |
| Exporter class exists with basic interface | [§2 Public surface](#2-public-surface-and-opentelemetry-contract) |
| Unit tests verify span ingestion and basic transformation | [§4 Test contract](#4-test-contract) |
| Code follows project layout and style | [§5 Layout and style](#5-layout-and-style) |

## Goals

- Provide a **small, explicit** Python API that plugs into the **OpenTelemetry Python SDK** tracing pipeline as a **`SpanExporter`**, so spans can be collected and **normalized into a replayt-oriented representation** without yet depending on the **`replayt`** distribution.
- Keep **consumer-side** evolution safe: document what is stable vs experimental, and what additional dependencies the Builder is expected to add.

## Non-goals (this backlog)

- Shipping a full replayt workflow integration, RPC, or file format—only **in-process preparation** of span data.
- Adding **`replayt`** as a runtime dependency unless a later backlog item requires it.
- Performance tuning, batching policies beyond what the SDK already provides, or custom `SpanProcessor` types unless needed to satisfy §2–§4.

## 1. Dependencies and versions

- **`opentelemetry-api`** remains a baseline dependency (already declared in **`pyproject.toml`**).
- Implementing a **`SpanExporter`** requires the **OpenTelemetry Python SDK** trace export types. The Builder **must** add **`opentelemetry-sdk`** to **`[project].dependencies`** (with a lower bound consistent with **`opentelemetry-api`**, e.g. the same major/minor policy the project uses elsewhere—document the chosen pins in **`docs/DEPENDENCY_AUDIT.md`** when they change).
- **Supported OpenTelemetry versions** for this skeleton: document in **`docs/MISSION.md`** (compatibility matrix or prose). CI must stay green on the versions exercised there.

## 2. Public surface and OpenTelemetry contract

### 2.1 Type and module placement

- The primary exporter class lives in **`src/replayt_otel_span_exporter/`** in a dedicated module (for example **`exporter.py`**). Avoid dumping implementation-only helpers into **`__init__.py`** beyond thin re-exports if the package chooses to expose the class at package root.
- **`__all__`** (package and/or module) should list **only** symbols intended for integrators. Internal helpers use a leading underscore or live in a clearly private submodule (for example **`_records.py`**).

### 2.2 Exporter behavior

- The class **subclasses** **`opentelemetry.sdk.trace.export.SpanExporter`** (or otherwise satisfies the same contract if the SDK’s typing evolves—prefer subclassing for clarity).
- **Required methods** (names and semantics aligned with the SDK):
  - **`export(spans)`** — Accept an iterable/sequence of **finished readable spans** from the SDK, perform **basic transformation** into the **prepared record** shape defined in §3, and store or append those records in a **test-observable** buffer unless the spec’s testing strategy uses another explicit hook documented in §4.
  - **`shutdown()`** — Release resources; after shutdown, further exports should be safe (no-op or documented behavior) and covered by tests.
  - **`force_flush(timeout_millis=...)`** — Return a boolean per SDK expectations; for the skeleton, flushing may be a no-op if there is no async work, but behavior must be **documented and tested** (even if the test asserts the trivial case).

### 2.3 Error handling

- **`export`** must not raise for **normal** SDK callback usage: follow SDK patterns (**`SpanExportResult`** success/failure) so a buggy exporter does not crash the application’s tracing thread. Document any case where exceptions are intentionally propagated.

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
| **attributes** | Span attributes | Mapping (string keys to scalar or homogeneous list values) **suitable for JSON-style serialization** where possible; document any types that are intentionally dropped or stringified. |

**Optional for this skeleton** (document if present or explicitly deferred): parent span id, status code/message, links, events, resource attributes.

The IR type must be **importable for tests** (public or test-only module per project convention—prefer **`replayt_otel_span_exporter`** namespace with a clear name like **`PreparedSpanRecord`**).

## 4. Test contract

Tests are implemented in phase **3** (Builder) and later; this section defines **what** they must prove.

### 4.1 Span ingestion

- At least one test **drives the real SDK** far enough to produce **finished** spans that flow into the exporter (for example: configure a **`TracerProvider`** with a **`SimpleSpanProcessor`** or **`BatchSpanProcessor`** wired to the new exporter, start a span, end it, then force flush/shutdown as needed).
- Assertions: after export, the exporter’s observable buffer (or equivalent) contains **the expected number** of prepared records (≥ 1 for the minimal case).

### 4.2 Basic transformation

- Assertions on **at least one** prepared record:
  - **name** matches the span started in the test.
  - **trace_id** and **span_id** are **non-empty** and **consistent** with the span context (exact format as documented in §3).
  - **start/end** times are **ordered** (`start <= end`) and **non-zero** for a normal span.
  - **attributes**: setting a simple attribute on the span appears on the prepared record’s **attributes** mapping with the expected key and value.

### 4.3 Lifecycle

- Tests cover **`shutdown()`** (and **`force_flush()`** if non-trivial) with expectations spelled in §2.2–§2.3.

### 4.4 Placement

- Prefer **`tests/unit/`** for fast, focused tests if the repo introduces that layout; otherwise follow **[docs/CI_SPEC.md](CI_SPEC.md)** §6 and place files under **`tests/`** with clear naming (for example **`test_exporter.py`**). New tests must run under the **default `pytest` invocation** documented in CI.

## 5. Layout and style

- Match **`ruff`**-clean style and existing package patterns (**`src/`** layout, **`pyproject.toml`** metadata).
- No new top-level packages; keep code under **`src/replayt_otel_span_exporter/`**.
- Update **`docs/DEPENDENCY_AUDIT.md`** when **`opentelemetry-sdk`** (or related pins) are added.

## Implementation notes for Builder / Maintainer

- When this spec and **`docs/MISSION.md`** diverge from **`pyproject.toml`** or CI, update **both** the code and the docs in the same maintenance pass.
- If OpenTelemetry Python changes **`SpanExporter`** or **`ReadableSpan`** in a way that breaks subclassing, add a compatibility note under **[docs/DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** (“Consumer-side maintenance”) and adjust this spec in the same change.
