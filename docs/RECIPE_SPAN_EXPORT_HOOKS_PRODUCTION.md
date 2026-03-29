# Recipe: Approval and audit hooks in production

This document is an **integrator-facing cookbook** for optional **`ReplaytSpanExporter`** hooks described in **[SPEC_SPAN_EXPORT_APPROVAL_UX.md](SPEC_SPAN_EXPORT_APPROVAL_UX.md)**. It is **informative**; the normative contract is **§4** (hooks) and **§5** (audit allow list) in that spec.

**Goal:** Use **`on_export_commit`** / **`on_export_audit`** safely under real concurrency, emit audit events to **your** sink (logs, SIEM, queue) using **only** documented safe fields, and **never** persist or forward full prepared attribute maps.

## 1. Contract reminder (read the spec)

- Hooks run **after** IR mapping and **before** buffer append, under the exporter’s **buffer lock** (spec **§4.4**).
- **`on_export_commit`** must return **`"allow"`** or **`"deny"`** **synchronously** (spec **§4.1**).
- **`on_export_audit`** (if present) is invoked **synchronously** with a small event carrying **§5.2** fields only.
- Audit payloads **MUST NOT** include **`PreparedSpanRecord.attributes`** or other arbitrary attribute-derived strings (spec **§5.2**).

## 2. Async-safe patterns

The OpenTelemetry Python SDK invokes **`export`** from a worker thread. Your hooks therefore run on that thread while holding the exporter mutex. Treat them like a **critical section**:

1. **Do not block** on network I/O, disk, or locks held by code that waits on tracing.
2. **Do not** call **`await`** inside the hook; hooks are not async functions in this contract.
3. **Read policy from an already-resolved snapshot** (for example an atomic flag, a versioned config struct updated elsewhere, or a precomputed decision table) instead of performing remote policy checks inside the hook.
4. **Defer heavy or async work** by enqueueing a **minimal** payload for a background worker:
   - From **`on_export_audit`**, push a **`dict`** (or your ORM row) that contains **only** keys you copied from the allow list (**§3** below).
   - Use **`queue.SimpleQueue`** or **`asyncio.get_running_loop().call_soon_threadsafe`** from a dedicated worker context you control; avoid unbounded growth (drop or sample under overload if your org policy allows, and document that behavior).

**Anti-pattern:** Calling **`requests.post`**, opening a database transaction that waits on locks, or **`await remote_allow()`** inside **`on_export_commit`** — these stall tracing and can deadlock.

**Pattern — snapshot gate:**

```python
# Application updates this from async tasks / HTTP handlers (outside the hook).
class ExportGate:
    def __init__(self) -> None:
        self._allow = True

    def set_allow(self, value: bool) -> None:
        self._allow = value

    def snapshot_allow(self) -> bool:
        return self._allow


gate = ExportGate()


def on_export_commit(prepared, *, span_count: int):
    # Synchronous read only; no I/O.
    return "allow" if gate.snapshot_allow() else "deny"
```

## 3. Allow-listed audit fields only

When forwarding to your sink, **copy** fields explicitly. Do **not** pass through the **`prepared`** sequence, **`PreparedSpanRecord`**, or **`attributes`** to persistent storage or external systems.

**Normative allow list** (spec **§5.2**): **`decision`**, **`prepared_count`**, **`span_count`**, and when applicable **`trace_id`**, **`span_id`**, **`workflow_id`**, **`step_id`** (from the **first** prepared record in batch order). Optional **`reason_code`** applies only if the Builder exposes that shape (spec **§5.2**).

```python
ALLOWED_AUDIT_KEYS = frozenset({
    "decision",
    "prepared_count",
    "span_count",
    "trace_id",
    "span_id",
    "workflow_id",
    "step_id",
    # "reason_code",  # only if your installed exporter API documents it
})


def on_export_audit(event: dict) -> None:
    safe = {k: event[k] for k in ALLOWED_AUDIT_KEYS if k in event}
    audit_queue.put_nowait(safe)  # drained by your async / threaded sink
```

**Forbidden:** Serializing **`prepared`**, logging **`repr(prepared)`**, or storing **`PreparedSpanRecord.attributes`** “for debugging.” Use OpenTelemetry’s own sampling and separate secure tooling if you need deeper span inspection.

## 4. Idempotency and duplicate signals

The SDK may call **`export`** multiple times for overlapping or retried work. Your **`on_export_audit`** callback may therefore run **more than once** for semantically related batches.

- **Do not** assume one audit event per logical span for all time; correlate using allow-listed identifiers (**`trace_id`**, **`span_id`**) plus your own **monotonic receive counter** or **ULID** assigned **at enqueue time** (not from span attributes).
- If your sink requires idempotent writes, define a key from **allow-listed fields plus** an integrator-generated id, for example  
  **`f"{trace_id}:{span_id}:{decision}:{received_ulid}"`**  
  rather than hashing attribute payloads.
- If the same batch is retried and your hook returns the same decision, duplicate audit rows may still occur; dedupe in the sink or accept at-least-once semantics and document retention.

## 5. End-to-end sketch (queue → async writer)

```python
import asyncio
import queue
import uuid
from typing import Any

audit_queue: queue.SimpleQueue[dict[str, Any]] = queue.SimpleQueue()


def on_export_audit(event: dict) -> None:
    safe = {k: event[k] for k in ALLOWED_AUDIT_KEYS if k in event}
    safe["_audit_ingest_id"] = str(uuid.uuid4())  # integrator-only; not from OTel IR
    audit_queue.put_nowait(safe)


async def audit_drain_loop() -> None:
    while True:
        if audit_queue.empty():
            await asyncio.sleep(0.05)
            continue
        row = audit_queue.get_nowait()
        # await send_to_siems(row)  # your async I/O here
        await asyncio.sleep(0)  # placeholder
```

The ingest id is **not** part of the exporter contract; it exists so your downstream pipeline can dedupe or trace internal delivery without touching span attributes.

## 6. Cross-links

- Normative hook and audit rules: **[SPEC_SPAN_EXPORT_APPROVAL_UX.md](SPEC_SPAN_EXPORT_APPROVAL_UX.md)** (**§4**, **§5**, **§8**, **§9**).
- Summary pointer from mission scope: **[MISSION.md](MISSION.md)** (scope table).
- Redaction and triage context for **`workflow_id`** / **`step_id`**: **[SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)**.
- Failure logging (separate from policy denial): **[SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)**.
