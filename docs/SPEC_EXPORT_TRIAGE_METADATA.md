# Specification: Triage metadata on prepared spans without leaking secrets

This document refines the backlog item **“Add metadata for triage without leaking secrets”** into testable requirements. **Production code and tests** belong in **`src/replayt_otel_span_exporter/`** and **`tests/`**; this file is the contract for what “done” means for that item.

It **extends** **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)** (prepared-span IR, §3) and **reuses** **[docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)** **§5** (sensitive key detection via **`replayt_otel_span_exporter.redaction.attribute_key_is_sensitive`**). Where the two overlap, **failure-handling** rules remain authoritative for **log** payloads; **this document** is authoritative for **values stored on `PreparedSpanRecord`** (the exported in-memory IR) until a follow-on spec reconciles them.

## Backlog traceability

| Original acceptance criterion | Satisfied by (this doc) |
| ----------------------------- | ------------------------ |
| Metadata fields defined and populated | [§2 Canonical span attributes and IR fields](#2-canonical-span-attributes-and-ir-fields), [§7 Verifiable acceptance checklist](#7-verifiable-acceptance-checklist) |
| Redaction applied to sensitive data | [§3 Redaction rules for prepared attributes](#3-redaction-rules-for-prepared-attributes), [§7 Checklist](#7-verifiable-acceptance-checklist) |
| Tests verify redaction | [§5 Test contract (Builder)](#5-test-contract-builder), [§7 Checklist](#7-verifiable-acceptance-checklist) |

## Goals

- **Operators and integrators** can correlate prepared span snapshots with **replayt-oriented** workflow context using **stable, first-class** **`workflow_id`** and **`step_id`** fields derived from documented OpenTelemetry span attributes.
- **`PreparedSpanRecord.attributes`** remains useful for arbitrary integrator keys but **MUST NOT** carry raw values for keys classified as sensitive by the **existing** redaction helper (**`attribute_key_is_sensitive`**).
- Behavior stays compatible with the **small public surface**: only **`PreparedSpanRecord`** (and internal helpers) change unless a follow-on backlog explicitly exports new symbols.

## Non-goals (this backlog)

- Redacting **values** based on heuristics (regex for JWTs, credit cards, etc.)—only **key**-based redaction via **`attribute_key_is_sensitive`** is required.
- New **logging** requirements beyond what **[docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)** already defines (this backlog may **interact** with logging via redacted IR, but does not expand log fields).
- Defining replayt **runtime** APIs or changing **`[project].dependencies`** to require **`replayt`**.

## 1. Definitions

- **Triage metadata** — The pair **`workflow_id`** / **`step_id`** on **`PreparedSpanRecord`**, each either a **non-empty string** or **`None`** (see §2.3).
- **Prepared attributes** — The **`attributes`** mapping on **`PreparedSpanRecord`** after serialization (per skeleton §3) and **after** §3 redaction is applied.

## 2. Canonical span attributes and IR fields

### 2.1 Canonical OpenTelemetry attribute keys

Integrators **SHOULD** set the following **string keys** on spans (OpenTelemetry attribute keys are strings; matching is **case-sensitive** and **exact** for this contract):

| Key | Purpose |
| --- | ------- |
| **`replayt.workflow_id`** | Stable identifier of the logical workflow or run grouping (string form chosen by the integrator). |
| **`replayt.step_id`** | Stable identifier of the step or stage within that workflow (string form chosen by the integrator). |

These keys are **namespaced** under the **`replayt.`** prefix so they are unlikely to collide with generic application attributes. If an integrator omits a key, the corresponding IR field is **`None`**.

### 2.2 Serialization before extraction

Values taken from the span for both **triage fields** and **`attributes`** **MUST** pass through the same **attribute value** serialization rules as the rest of the IR (**`serialize_attribute_value`** / equivalent documented in **`replayt_otel_span_exporter.records`**). That implies:

- Scalar types, homogeneous sequences, **`bytes`**, and unknown-type fallbacks behave per skeleton §3 / **`records`** module docs.
- If the stored attribute value serializes to a type that is **not** a **single string** (for example a **number**, **bool**, or **sequence**), the implementation **MUST** coerce to a **string** for **`workflow_id`** / **`step_id`** using **`str(...)`** after serialization, so the IR fields remain **`str | None`**.

### 2.3 `PreparedSpanRecord` fields (normative)

The **`PreparedSpanRecord`** dataclass **MUST** expose two additional **fields** (exact names):

| Field | Type | Semantics |
| ----- | ---- | --------- |
| **`workflow_id`** | **`str | None`** | **`None`** if span has no **`replayt.workflow_id`** attribute; otherwise non-empty string per §2.2. If the attribute exists but serializes to an **empty string** after coercion, store **`None`**. |
| **`step_id`** | **`str | None`** | Same rules using **`replayt.step_id`**. |

**Stability:** **`PreparedSpanRecord`** remains **frozen**; add these fields in the **same** maintenance pass as the mapper update. Tests and the replayt boundary spec **MAY** assume these names once this backlog lands.

### 2.4 Duplication vs `attributes`

The **`attributes`** mapping lists **all** span keys after §3 redaction. The dedicated **`workflow_id`** / **`step_id`** fields **MUST** be copied from the **serialized** values of **`replayt.workflow_id`** / **`replayt.step_id`** **before** §3 redaction runs on the full mapping (or from an equivalent single pass that preserves the same semantics).

For the **canonical keys in §2.1**, **`attribute_key_is_sensitive`** is **False**, so their entries in **`attributes`** remain the ordinary serialized strings after §3 and **MUST** match the dedicated fields (same string values as **`workflow_id`** / **`step_id`** when those are not **`None`**).

## 3. Redaction rules for prepared attributes

### 3.1 Single policy module

**Sensitive key detection** **MUST** continue to use **`replayt_otel_span_exporter.redaction.attribute_key_is_sensitive`** (same table as **[docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)** §5.1). The Builder **MAY** add a small helper in **`redaction.py`** (for example **`redact_sensitive_attribute_values`**) or implement redaction inline in **`records.py`**, but **MUST NOT** fork the substring table into a second source of truth.

### 3.2 Replacement value

For every key **K** in the prepared attributes mapping where **`attribute_key_is_sensitive(K)`** is **True**, the value stored in **`PreparedSpanRecord.attributes[K]`** **MUST** be replaced with the **literal string** **`"[REDACTED]"`** (ASCII, square brackets as shown). Keys **without** sensitive substrings keep serialized values unchanged.

### 3.3 Ordering

The mapper **SHOULD** build the serialized attribute dict first, then apply §3.2, then set **`workflow_id`** / **`step_id`** from the **unredacted** serialized values for **`replayt.workflow_id`** / **`replayt.step_id`** (if present). That guarantees triage strings remain usable for correlation while arbitrary secret-like keys do not leak through **`attributes`**.

### 3.4 DEBUG / logging

**`SPEC_SPAN_EXPORT_FAILURE_HANDLING`** already forbids dumping full attribute maps on failure logs and (§5.4) **requires** truncation and control stripping for untrusted strings on failure paths. This spec **does not** authorize logging raw pre-redaction attributes at **INFO** or higher. **`DEBUG`** traces, if added later, **MUST** still respect §3.2 unless a future spec explicitly relaxes that.

## 4. Relationship to other specs

- **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)** §3 — field list and encoding; this spec **adds** triage fields and **tightens** attribute handling.
- **[docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)** §5 — shared **key** sensitivity; **this spec** adds **value** replacement on the IR.
- **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** §7 — when this backlog is satisfied, the **replayt** boundary payload **SHOULD** include **`workflow_id`** and **`step_id`** (see that section’s maintenance note).

## 5. Test contract (Builder)

Tests **MUST** prove:

1. **Triage population:** With a real **`TracerProvider`** path (same class of test as skeleton §4.1), set attributes **`replayt.workflow_id`** and **`replayt.step_id`** on a span; after export, a **`PreparedSpanRecord`** has **`workflow_id`** and **`step_id`** equal to the serialized string values.
2. **Absence:** Spans **without** those attributes yield **`None`** for both fields.
3. **Coercion:** If **`replayt.workflow_id`** is set to a non-string scalar (for example an **int**), the IR **`workflow_id`** string matches the specified coercion rule (§2.2).
4. **Redaction:** A span carrying both a triage key and a sensitive key (for example **`user.password`**) **MUST** result in **`attributes["user.password"] == "[REDACTED]"`** (or the key present with that value), while **`workflow_id`** / **`step_id`** remain correct for the triage keys.
5. **Regression guard:** Extend **`tests/test_records.py`** and/or **`tests/test_exporter.py`** (or a focused new module) so default **`pytest`** discovery covers §5.1–§5.4 without conflicting with existing **`tests/test_redaction.py`** responsibilities (**`attribute_key_is_sensitive`** unit tests remain the home for key-table behavior).

## 6. Documentation deliverables (Builder)

The Builder **MUST**:

- Summarize canonical attribute keys and redacted **`attributes`** behavior in **`README.md`** (short subsection or bullet list; link to **this spec**).
- Update **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** §7 **Data passed across the boundary** to list **`workflow_id`** and **`step_id`** when this backlog’s implementation merges.

## 7. Verifiable acceptance checklist

Use this checklist in **Spec gate**, **Build gate**, and PR review for this backlog.

1. **`PreparedSpanRecord`** includes **`workflow_id`** and **`step_id`** per §2.3 and they are populated per §2.1–§2.2 from span attributes.
2. **`PreparedSpanRecord.attributes`** applies §3 redaction using **`attribute_key_is_sensitive`** only—no second sensitivity table.
3. Sensitive values never appear in **`attributes`** after export (§3.2); triage fields do not leak secret-like keys from other attributes.
4. Automated tests satisfy [§5](#5-test-contract-builder).
5. **README** and **§6** cross-links are updated.

## Implementation notes for Builder / Maintainer

- Prefer one function (for example **`prepared_span_record_from_readable`**) that performs serialization → redaction → triage extraction so call sites cannot skip redaction.
- If **`CHANGELOG.md`** ships user-visible IR changes in the same PR, record them under **Unreleased** per project convention.
- When pins or OpenTelemetry attribute typing changes, update **[docs/DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)** if behavior or supported types shift materially.
