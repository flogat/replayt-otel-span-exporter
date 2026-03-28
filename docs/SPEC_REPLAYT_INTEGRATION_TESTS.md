# Specification: Replayt integration tests

This document refines the backlog item **“Add replayt integration tests”** into testable requirements. **Production code and tests** belong in **`src/replayt_otel_span_exporter/`** and **`tests/`**; this file is the contract for what “done” means for that item.

It complements **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)** (OTel → **`PreparedSpanRecord`**) by defining how the suite proves compatibility at the **replayt** import boundary. It does **not** require replayt as a **runtime** dependency for library users unless a later backlog promotes that.

## Backlog traceability

| Original acceptance criterion | Satisfied by (this doc) |
| ----------------------------- | ------------------------ |
| Integration tests added to the test suite | [§3 Placement and discovery](#3-placement-and-discovery), [§4 Scenarios](#4-minimum-test-scenarios), [§6 Checklist](#6-verifiable-acceptance-checklist) |
| Tests run successfully with **`pytest`** | [§5 Local and CI invocation](#5-local-and-ci-invocation) |
| CI configuration includes these tests | [§5 Local and CI invocation](#5-local-and-ci-invocation), **[docs/CI_SPEC.md](CI_SPEC.md)** §5 |

## 1. Goals

- Exercise **at least one documented replayt public API** using data that originates from a real OpenTelemetry SDK span flowing through **`ReplaytSpanExporter`** (see skeleton spec §4).
- Keep failures **actionable**: if replayt changes its consumer contract, CI should point to the boundary test and the pinned version policy.

## 2. Definitions

- **Replayt boundary** — The narrow surface where **this package** hands off **replayt-oriented** data to **replayt** itself: typically **`PreparedSpanRecord`** fields (or a structure replayt documents as input) passed into replayt’s **public** types or functions. It is **not** the full workflow engine, storage, or network export stack.
- **Integration test (replayt)** — A test that **`import`s `replayt`** (submodules allowed) and asserts behavior at that boundary. This is **distinct** from **`tests/integration/test_opentelemetry_api_usage.py`**, which only checks the OpenTelemetry trace API.

## 3. Placement and discovery

- New tests MUST live under **`tests/integration/`** with filenames that make the intent obvious (for example **`test_replayt_boundary.py`**).
- Tests MUST be collected by the **default** **`pytest`** invocation from the repository root (no extra path arguments required for CI). If the project later introduces markers, **`pytest.mark.replayt`** MAY be added for **optional** local filtering; **CI MUST still run the full suite** (including replayt tests) on every matrix cell unless **[docs/CI_SPEC.md](CI_SPEC.md)** is explicitly revised with a justified subset.

## 4. Minimum test scenarios

The Builder MUST implement **all** of the following. Exact assertion shapes follow replayt’s documented API once the entry point is chosen (see §5 dependency notes).

### 4.1 Tracer pipeline → prepared records

- Configure a **`TracerProvider`** with a span processor wired to **`ReplaytSpanExporter`** (same class of setup as skeleton spec §4.1).
- Start and end at least **one** non-trivial span (name + at least one attribute recommended).
- Assert the exporter’s buffer contains **≥ 1** **`PreparedSpanRecord`** and that core fields match the live span (**`name`**, **`trace_id`** / **`span_id`** encoding per skeleton §3, ordered **start/end** times).

### 4.2 Replayt boundary invocation

- Using the prepared record(s) from §4.1 (or a conversion explicitly documented in replayt’s API), call **at least one** replayt public API that represents how integrators connect external trace or workflow data to replayt.
- The test MUST fail if replayt raises **due to incompatible shape or types** for that API (as opposed to optional features not used in this package). Document the chosen API in §7 **Implemented boundary** in the same change set as the tests.

### 4.3 Dependency presence

- Missing **`replayt`** on the install path MUST surface as a **failed** install or **import error** during test collection or execution — **not** a silent skip — unless the repository adopts a **documented** optional CI job (not the default today). Default policy: **`replayt`** is required for the standard **`dev`** / CI install.

## 5. Local and CI invocation

- **`[project].dependencies`** MUST remain free of **`replayt`** for this backlog unless a separate item promotes it to runtime (see **[docs/MISSION.md](MISSION.md)** scope table).
- **`replayt`** MUST be declared under **`[project.optional-dependencies]`** — either the existing **`dev`** extra or a dedicated extra (for example **`integration`**) that CI merges into its install line.
- The documented install path for contributors and CI MUST install **`replayt`** without a second manual step. Today that means extending the **`pip install -e ".[dev]"`** line (or the equivalent documented in **[docs/CI_SPEC.md](CI_SPEC.md)**) so the integration tests always run in **`pytest`** on PRs and pushes.
- When pins change, update **`docs/DEPENDENCY_AUDIT.md`** in the same maintenance pass (see §6 checklist).

## 6. Verifiable acceptance checklist

Use this checklist in **Spec gate**, **Build gate**, and PR review for the **“Add replayt integration tests”** backlog.

1. At least one file under **`tests/integration/`** imports **`replayt`** and is named so reviewers can find it quickly.
2. §4.1 and §4.2 scenarios are covered by automated tests; failures clearly indicate OTel/IR vs replayt-boundary issues where practical.
3. **`replayt`** appears only in **optional** dependencies (or **`dev`**) in **`pyproject.toml`**, not in **`[project].dependencies`**, unless mission scope is explicitly updated elsewhere.
4. **`docs/DEPENDENCY_AUDIT.md`** includes a **Test / integration: replayt** row with the version policy and rationale.
5. §7 **Implemented boundary** is filled in with concrete modules, symbols, and minimum version — no placeholders left at merge.
6. Default CI (**[docs/CI_SPEC.md](CI_SPEC.md)**) runs **`pytest`** in a way that collects the new tests on **Python 3.11** and **3.12** without extra flags.

## 7. Implemented boundary (concrete API under test)

The bullets below record the API exercised by **`tests/integration/test_replayt_boundary.py`**. Update them when replayt or this adapter changes.

- **Minimum `replayt` version (PEP 440 specifiers):** **`>=0.4.25`** (declared on the **`dev`** extra in **`pyproject.toml`**).
- **Public entry point(s) (modules / callables / types):**
  - **`replayt.runner.Runner`** — constructed with a **`Workflow`**, an **`EventStore`**, and optional lifecycle hooks; **`run()`** drives execution.
  - **`replayt.runner.RunContext`** — **`set(key, value)`** / **`get(key, default=None)`** for per-run context data (documented on **`Runner`** as the hook surface for trace IDs and similar side data via **`before_step`**).
  - **`replayt.workflow.Workflow`** — minimal one-step workflow for the smoke run.
  - **`replayt.persistence.sqlite.SQLiteStore`** — durable store implementation used only so **`Runner`** can complete a real run (file-backed temp DB in tests).
  - **`replayt.testing.DryRunLLMClient`** — no-network LLM client so the workflow run does not need API keys.
- **Data passed across the boundary:** A plain **`dict`** built from **`PreparedSpanRecord`** (**`trace_id`**, **`span_id`**, **`name`**, **`kind`**, **`start_time_unix_nano`**, **`end_time_unix_nano`**, **`attributes`**) is written with **`RunContext.set("otel_span", ...)`** inside **`Runner`**’s **`before_step`** callback; the step handler reads it with **`get`** and asserts equality.
- **What “success” means at the boundary:** No **`ContextSchemaError`** or type errors from replayt; the step sees the same mapping; **`Runner.run()`** returns **`RunResult`** with **`status == "completed"`**.

## Non-goals (this backlog)

- Running full replayt workflows against live backends or credentials.
- Performance or load testing of replayt.
- Changing the **runtime** dependency set of **`replayt-otel-span-exporter`** to require **`replayt`** for end users (optional/test-only unless promoted by another item).

## Implementation notes for Builder / Maintainer

- Prefer **stable, documented** replayt APIs over private attributes; if only unstable hooks exist, document the risk in **`docs/DEPENDENCY_AUDIT.md`** and keep the boundary test narrow.
- If replayt’s packaging or API diverges between Python versions, align with the CI matrix in **`docs/CI_SPEC.md`** or extend the matrix in the same change.
- When this spec and **`docs/MISSION.md`** diverge from **`pyproject.toml`** or CI, update **code and docs** in the same maintenance pass.
