# Specification: Approval UX and audit hooks for span export

This document refines the backlog item **“Define and implement approval UX for span export”** into testable requirements. **Production code and tests** belong in **`src/replayt_otel_span_exporter/`** and **`tests/`**; this file is the contract for what “done” means for that item.

It **extends** **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)** (especially §2.2 exporter behavior and constructor). Where the two conflict after this backlog lands, **this document wins** for approval gating, audit visibility, and integrator hook contracts until a follow-on spec reconciles them.

**Hook evolution and semver** (stable releases): **[docs/SPEC_BETA_AND_STABLE_PROMOTION.md](SPEC_BETA_AND_STABLE_PROMOTION.md)** §5.

**Failure logging and redaction** on **internal errors** remain governed by **[docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)**. A **policy denial** (integrator chooses not to commit a batch) is **not** an export failure under that spec: the exporter **MUST NOT** return **`SpanExportResult.FAILURE`** solely because approval was denied (see §4.2).

## Backlog traceability

| Original acceptance criterion | Satisfied by (this doc) |
| ----------------------------- | ------------------------ |
| Approval flow documented | [§2 Concepts](#2-concepts-and-stakeholders), [§3 Integrator workflow](#3-integrator-workflow-normative), [§7 Documentation deliverables](#7-documentation-deliverables) |
| Implementation includes necessary hooks | [§4 Hook contract](#4-hook-contract-normative), [§6 Verifiable acceptance checklist](#6-verifiable-acceptance-checklist) |
| UX is clear for stakeholders | [§2 Concepts](#2-concepts-and-stakeholders), [§5 Audit visibility](#5-audit-visibility-and-redaction-normative), [§7 Documentation deliverables](#7-documentation-deliverables) |

**Document integrator cookbook: approval hook + audit in production services** (Mission Control **`29efde6c-c106-43ca-a17a-1623d53145f5`**):

| Backlog acceptance theme | Satisfied by (this doc + recipe) |
| ------------------------ | -------------------------------- |
| Cookbook content and examples | **[docs/RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md](RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md)** — see [§10](#10-integrator-cookbook-on_export_commit-and-on_export_audit-in-production-informative) and **§10.1** below |
| Mission / README discoverability | **[docs/MISSION.md](MISSION.md)** backlog traceability subsection for this id; root **`README.md`** **Optional approval hook** |

## 1. Goals

- Give **integrators** an optional, **in-process** way to **gate** whether a batch of **`PreparedSpanRecord`** values is **committed** to the exporter buffer (the hand-off surface described in the skeleton spec).
- Make **stakeholder visibility** possible through **documented audit signals** (stdlib **`logging`** and/or an optional integrator callback) that explain **allow vs deny** decisions **without** leaking sensitive span attribute payloads.
- Preserve **default behavior** when no hook is configured: today’s semantics (map batch, append on success path) remain unchanged so existing integrators are not broken.

## 2. Concepts and stakeholders

| Term | Meaning in this package |
| ---- | ----------------------- |
| **Span export action** | A single **`ReplaytSpanExporter.export(spans)`** call that has **passed** internal mapping to **`PreparedSpanRecord`** and is about to **append** those records to the configured buffer (or would append, if allowed). |
| **Approval (policy gate)** | Integrator-defined **allow / deny** for committing **the prepared batch** produced by that call. This is **not** a human-in-the-loop UI shipped inside **`replayt-otel-span-exporter`**; it is a **hook** where the host application may consult policy, feature flags, or asynchronous approvals already represented in application state. |
| **Stakeholders** | **Operators** (logs, dashboards), **security / compliance** (audit trail), and **application owners** (who embed the exporter). They consume **signals**, not a built-in web console. |

## 3. Integrator workflow (normative)

1. Integrator installs **`ReplaytSpanExporter`** in the OpenTelemetry pipeline per **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)**.
2. **Optional:** Integrator supplies an **approval hook** (§4) on construction.
3. On each **`export`**:
   - The exporter maps **`ReadableSpan`** → **`PreparedSpanRecord`** using existing IR and redaction rules (**[docs/SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)**).
   - If mapping fails with an internal exception, behavior stays per **[docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)** (**`SpanExportResult.FAILURE`**, error logging).
   - If mapping succeeds, the exporter evaluates the hook (if any):
     - **Allow** — append **all** prepared records for this call to the buffer; return **`SpanExportResult.SUCCESS`**.
     - **Deny** — append **none** of the prepared records for this call; return **`SpanExportResult.SUCCESS`** (see §4.2).
4. Integrator **MAY** forward allowed records from the buffer to downstream systems (including **replayt**-oriented consumers) per existing docs; denial means those records **never** enter the buffer for that call.

## 4. Hook contract (normative)

### 4.1 Placement and shape

- The hook **MUST** run **after** **`PreparedSpanRecord`** instances are constructed and **before** any append to the exporter’s **`records`** buffer for that **`export`** call, so decisions apply to **redacted IR** (not raw **`ReadableSpan`** attribute maps).
- The exporter **SHOULD** expose a single optional constructor parameter (name is a **Builder** choice; **`on_export_commit`** or **`approval`** are acceptable examples) whose value is either **`None`** (default — no gating) or a **callable** matching the protocol below.

**Callable protocol (normative minimum):**

```text
(prepared: Sequence[PreparedSpanRecord], *, span_count: int) -> Literal["allow", "deny"]
```

- **`prepared`** — The ordered sequence of records for this batch (same order as successful per-span mapping).
- **`span_count`** — **`len(spans)`** from the original **`export`** argument (SDK batch size), even if **`len(prepared)`** differs in edge cases; document if the implementation guarantees equality when all spans map successfully.
- Return value:
  - **`"allow"`** — Commit the batch to the buffer.
  - **`"deny"`** — Do not commit; §4.2 applies.

**Typing:** The Builder **SHOULD** expose a **`Protocol`** or **`TypeAlias`** for this callable in the package namespace if integrators need static typing; listing new symbols in **`replayt_otel_span_exporter.__all__`** is **optional** and subject to the **small public surface** rule in **[docs/MISSION.md](MISSION.md)** — if only the parameter type is needed, a **`Protocol`** in **`exporter`** may remain undocumented in **`__all__`** until a maintainer explicitly expands **`__all__`**.

### 4.2 OpenTelemetry return code on denial

- When the hook returns **`"deny"`**, **`export`** **MUST** return **`SpanExportResult.SUCCESS`** so the SDK tracing thread does not interpret policy as a **transport failure**. Denial is an **application policy outcome**, not an exporter bug.
- The exporter **MUST NOT** append **any** records from that batch to the buffer when denying.

### 4.3 Hook errors

- If the hook **raises** an **unexpected exception**, treat it as an **internal exporter error**: **`export`** **MUST** return **`SpanExportResult.FAILURE`** and **MUST NOT** partially append that batch. Logging **SHOULD** follow the same severity and safety rules as other internal failures (**[docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)**), with a clear message that the failure occurred **in the approval hook** (without blaming the SDK).

### 4.4 Threading

- The hook **MUST** be invoked under the **same mutual exclusion** used for buffer mutation today (see skeleton §2.2 **Thread safety**), so **`export`**, **`shutdown`**, and hook side effects remain serializable with respect to the buffer.

### 4.5 Shutdown

- After **`shutdown()`**, **`export`** remains a no-op per skeleton §2.2; the hook **MUST NOT** run on that path (no prepared batch exists to evaluate).

## 5. Audit visibility and redaction (normative)

Stakeholders need enough context to answer: **was a batch committed, and why or why not?** without reading application secrets from span attributes.

### 5.1 Required audit signals

When an approval hook is configured, the exporter **MUST** emit **at least one** of the following per **`export`** call that reaches the hook (mapping succeeded, not shut down):

1. **Library audit log** — A **`logging`** record on a **documented** logger (for example **`replayt_otel_span_exporter.exporter`** or a child such as **`replayt_otel_span_exporter.exporter.audit`**) at **`INFO`** (or a documented configurable level) containing structured **`extra`** fields per §5.2; **or**
2. **Integrator callback** — An optional second constructor parameter (for example **`on_export_audit`**) invoked synchronously with a **small, typed event object** or **`TypedDict`** containing the same **safe** fields as §5.2.

If both are provided, **both** MAY run; the spec does not require deduplication.

### 5.2 Safe fields (allow list)

Audit records **MUST NOT** include the full **`PreparedSpanRecord.attributes`** mapping or arbitrary string values from attributes (they may contain PII). **Allowed** structured fields:

| Field | Required when | Notes |
| ----- | ------------- | ----- |
| **`decision`** | Always | **`"allow"`** or **`"deny"`**. |
| **`prepared_count`** | Always | Number of **`PreparedSpanRecord`** instances in the batch being decided. |
| **`span_count`** | Always | SDK batch size (`len(spans)`). |
| **`trace_id`** / **`span_id`** | When **`prepared_count >= 1`** | Taken from the **first** prepared record in batch order, using skeleton §3 encoding (lowercase hex). If the batch is empty but the hook still runs, omit or document **`None`** / zero-id behavior explicitly. |
| **`workflow_id`** / **`step_id`** | When present on the first prepared record | Same first-record rule; values are already subject to triage / redaction rules per **[docs/SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)**. |

**Optional (integrator-provided, not logged by default):** A short **`reason_code`** string **supplied by the hook implementation** is allowed only if the API is designed so the **hook returns** both decision and reason (for example a small **`dataclass`** or **`NamedTuple`** instead of a bare **`Literal`**). If the Builder adopts that shape, document it as the **canonical** contract and keep **`reason_code`** length-bounded or document integrator responsibility for not placing secrets there.

### 5.3 Deny default

If the minimal callable protocol (§4.1) is kept without a reason field, audit entries **MUST** still state **`decision="deny"`** and counts; human-readable messages **SHOULD** clarify that denial was **policy** (integrator hook), not OTel **FAILURE**.

## 6. Non-goals (this backlog)

- Shipping an interactive **approval UI**, email workflows, or persistent **audit storage** inside this repository.
- Adding **`replayt`** as a runtime dependency for approvals.
- Changing **replayt** core; any org-wide approval product remains **upstream** or **integrator-owned** (**[docs/DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** — “Not a lever on core”).

## 7. Documentation deliverables

The Builder **MUST** update:

- **`README.md`** — Short subsection or bullet under exporter usage: optional approval hook, **SUCCESS on deny**, and pointer to this spec.
- **`docs/MISSION.md`** and **`docs/CI_SPEC.md`** — Spec-to-suite mapping when tests land (see §8).
- **`docs/RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md`** — Integrator cookbook (informative): async-safe patterns, idempotency guidance, and examples that forward audit data using only §5.2 allow-listed fields (see **§10** and testable checklist **§10.1**).

## 8. Test contract (Builder)

Tests **MUST** prove at least:

1. **Default (no hook)** — Behavior matches pre-backlog baseline for a normal batch (records appended; **`SUCCESS`**).
2. **Allow** — Hook returns **`"allow"`**; records appear in the buffer; audit signal (§5) records **`decision="allow"`** if the audit path is implemented.
3. **Deny** — Hook returns **`"deny"`**; **no** records appended for that call; **`export`** returns **`SUCCESS`** (not **`FAILURE`**); audit shows **`decision="deny"`**.
4. **Hook raises** — **`FAILURE`** return, no partial append, and error logging consistent with **[docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)** (message indicates hook failure).
5. **Shutdown** — No hook invocation on post-shutdown **`export`** (no-op path).

Prefer **`tests/test_exporter.py`** or a focused new module under **`tests/`**; follow default **`pytest`** discovery in **[docs/CI_SPEC.md](CI_SPEC.md)** §5.

## 9. Verifiable acceptance checklist

Use this checklist in **Spec gate**, **Build gate**, and PR review.

1. Optional hook is documented and wired **after** IR mapping, **before** buffer append.
2. **`"deny"`** does **not** return **`SpanExportResult.FAILURE`** and does **not** append records.
3. Hook exceptions yield **`FAILURE`** without partial batch append.
4. Audit signals use only §5.2 allow-listed fields (no full attribute maps).
5. Threading: hook runs under the exporter’s buffer lock.
6. README and mission / CI spec cross-links updated per §7.
7. Automated tests cover §8 scenarios.
8. **Integrator cookbook** — **[docs/RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md](RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md)** meets **§10.1** (file review); linked from **§10** and the **[docs/MISSION.md](MISSION.md)** scope table; **[docs/MISSION.md](MISSION.md)** includes the backlog traceability subsection for Mission Control **`29efde6c-c106-43ca-a17a-1623d53145f5`**.

## 10. Integrator cookbook: `on_export_commit` and `on_export_audit` in production (informative)

This section and **[docs/RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md](RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md)** are **informative** guidance for integrators. **§4–§5** remain the normative hook and audit contract.

**Read next:** **[RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md](RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md)** — async-safe patterns, idempotency when writing audit events to an integrator-owned sink, and copy-only examples that never store or ship **`PreparedSpanRecord.attributes`** or arbitrary attribute strings.

### 10.1 Testable documentation acceptance (Spec gate / Build gate — backlog `29efde6c`)

Verify by **documentation review** (no new **`pytest`** module is required for this backlog unless Mission Control adds a follow-on doc-contract item).

1. **`docs/RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md`** **MUST** include:
   - **§1.5** (or a clearly titled equivalent) — a **minimal** end-to-end pattern: synchronous **`on_export_commit`** with **no** I/O, plus **`on_export_audit`** that copies **only** §5.2 allow-listed keys before hand-off to a sink.
   - **§2** (async-safe patterns) — states hooks **MUST NOT** use **`await`** or blocking network / disk I/O under the exporter lock; names at least one deferral mechanism (**`queue.SimpleQueue`**, **`loop.call_soon_threadsafe`**, and/or stdlib **`logging`**).
   - **§4** (idempotency) — states **`export`** / audit may run **more than once** for related work; dedupe keys **MUST** use allow-listed fields **plus** integrator-generated correlation (**not** hashes of attribute payloads or full **`prepared`** dumps).
   - **§5.1** — an example that emits audit events via **stdlib `logging`** on an **integrator-owned** logger using **only** the copied allow-listed mapping (**no** **`repr(prepared)`**, **`PreparedSpanRecord.attributes`**, or arbitrary attribute strings).
   - **§3** and **§5** — reinforce that **`prepared`**, **`PreparedSpanRecord`**, and attribute maps **MUST NOT** be persisted or forwarded to external systems.
2. **`docs/MISSION.md`** **MUST** link the recipe from the **[Scope](MISSION.md#scope)** **approval / audit hooks** row (as today) **and** include the **Backlog traceability** subsection titled **“Document integrator cookbook: approval hook + audit in production services”** naming Mission Control id **`29efde6c-c106-43ca-a17a-1623d53145f5`**.
3. Root **`README.md`** **MUST** retain the **Optional approval hook** subsection with pointers to this spec and the recipe.

### Backlog acceptance criteria (summary — “Integrator cookbook”)

| Criterion | Evidence |
| --------- | -------- |
| Async-safe patterns documented | Recipe **§2**; minimal pattern **§1.5**. |
| Idempotency guidance | Recipe **§4**. |
| Audit sink examples use allow list only | Recipe **§3**, **§5**; stdlib **`logging`** example **§5.1**. |
| Discoverable from mission scope | **[docs/MISSION.md](MISSION.md)** scope table + traceability subsection; this **§10**. |
