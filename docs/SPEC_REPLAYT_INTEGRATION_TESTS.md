# Specification: Replayt integration tests

This document refines the backlog items **“Add replayt integration tests”**, **“Strengthen replayt boundary tests for pin bumps and contract drift”**, and **“Integration test: replayt pin drift and boundary failure modes”** (Mission Control `da6412b4-2b98-44cf-82a1-70fbc12c777c`) into testable requirements. **Production code and tests** belong in **`src/replayt_otel_span_exporter/`** and **`tests/`**; this file is the contract for what “done” means for those items.

It complements **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)** (OTel → **`PreparedSpanRecord`**) by defining how the suite proves compatibility at the **replayt** import boundary. It does **not** require replayt as a **runtime** dependency for library users unless a later backlog promotes that.

## Backlog traceability

| Original acceptance criterion | Satisfied by (this doc) |
| ----------------------------- | ------------------------ |
| Integration tests added to the test suite | [§3 Placement and discovery](#3-placement-and-discovery), [§4 Scenarios](#4-minimum-test-scenarios), [§6 Checklist](#6-verifiable-acceptance-checklist) |
| Tests run successfully with **`pytest`** | [§5 Local and CI invocation](#5-local-and-ci-invocation) |
| CI configuration includes these tests | [§5 Local and CI invocation](#5-local-and-ci-invocation), **[docs/CI_SPEC.md](CI_SPEC.md)** §5 |

**Strengthen replayt boundary tests for pin bumps and contract drift:**

| Theme | Satisfied by (this doc) |
| ----- | ------------------------ |
| How **`replayt`** version bumps are validated in CI | [§5.1](#51-how-replayt-pin-bumps-are-validated-in-ci-normative), **[docs/CI_SPEC.md](CI_SPEC.md)** §5, **[docs/COMPATIBILITY.md](COMPATIBILITY.md)** §3–§4 |
| Import and IR / payload contract regressions | [§4.4](#44-import-surface-contract), [§4.5](#45-prepared-span-record--replayt-payload-contract), [§7](#7-implemented-boundary-concrete-api-under-test) |
| Reliable **`pytest`** collection after **`pip install -e ".[dev]"`** | [§3](#3-placement-and-discovery), [§4.4](#44-import-surface-contract), [§6](#6-verifiable-acceptance-checklist) |

**Integration test: replayt pin drift and boundary failure modes** (`da6412b4-2b98-44cf-82a1-70fbc12c777c`):

| Acceptance theme | Satisfied by (this doc) |
| ---------------- | ------------------------ |
| **Pin bumps validated** — raising or lowering the **`replayt`** lower bound is safe only when default CI stays green | [§5.1](#51-how-replayt-pin-bumps-are-validated-in-ci-normative), [§4.6](#46-installed-replayt-version-sanity-normative), **[docs/COMPATIBILITY.md](COMPATIBILITY.md)** §4 (**Pin bump proof**) |
| **Import / contract regressions** when replayt or this adapter changes | [§4.4](#44-import-surface-contract), [§4.5](#45-prepared-span-record--replayt-payload-contract), [§7](#7-implemented-boundary-concrete-api-under-test), [§8](#8-boundary-failure-modes-and-pytest-diagnostics-normative) |
| **pytest collection** reliable after **`pip install -e ".[dev]"`** (no silent skip of the boundary module on the default path) | [§3](#3-placement-and-discovery), [§5.1](#51-how-replayt-pin-bumps-are-validated-in-ci-normative), [§6](#6-verifiable-acceptance-checklist), [§8.1](#81-collection-time-failures-pytest-exit-code-2) |

**Testable acceptance criteria for the Builder (normative summary):**

1. **`replayt`** pin changes: full **`pytest`** after **`pip install -e ".[dev]"`** collects and passes **`tests/integration/test_replayt_boundary.py`** on **every** CI matrix Python (**[docs/CI_SPEC.md](CI_SPEC.md)** §5; **§5.1** here).
2. **§4.6** MUST run in default CI and fail if the installed **`replayt`** distribution does not satisfy the **`dev`** extra specifier for **`replayt`** (pin / env drift guard).
3. **§4.4** / **§4.5** MUST hold: module-level imports for §7 entry points; payload key set, types, and attribute copy semantics as specified.
4. **§3** MUST hold: no **`importorskip`** or equivalent that allows exit **0** while skipping the boundary module when **`replayt`** is expected from **`[dev]`**.

## 1. Goals

- Exercise **at least one documented replayt public API** using data that originates from a real OpenTelemetry SDK span flowing through **`ReplaytSpanExporter`** (see skeleton spec §4).
- Keep failures **actionable**: if replayt changes its consumer contract, CI should point to the boundary test and the pinned version policy.
- Make **pin bumps** safe: when maintainers raise the **`replayt`** lower bound on the **`dev`** extra, default CI MUST prove that imports, **`PreparedSpanRecord`** shape, and the chosen replayt API still align (see §5.1).
- Keep **default collection** honest: with the documented **`dev`** install, **`pytest`** MUST collect **`tests/integration/test_replayt_boundary.py`** without import-time surprises that only appear mid-run (see §3 and §4.4).

## 2. Definitions

- **Replayt boundary** — The narrow surface where **this package** hands off **replayt-oriented** data to **replayt** itself: typically **`PreparedSpanRecord`** fields (or a structure replayt documents as input) passed into replayt’s **public** types or functions. It is **not** the full workflow engine, storage, or network export stack.
- **Integration test (replayt)** — A test that **`import`s `replayt`** (submodules allowed) and asserts behavior at that boundary. This is **distinct** from **`tests/integration/test_opentelemetry_api_usage.py`**, which only checks the OpenTelemetry trace API.

## 3. Placement and discovery

- New tests MUST live under **`tests/integration/`** with filenames that make the intent obvious (for example **`test_replayt_boundary.py`**).
- Tests MUST be collected by the **default** **`pytest`** invocation from the repository root (no extra path arguments required for CI). If the project later introduces markers, **`pytest.mark.replayt`** MAY be added for **optional** local filtering; **CI MUST still run the full suite** (including replayt tests) on every matrix cell unless **[docs/CI_SPEC.md](CI_SPEC.md)** is explicitly revised with a justified subset.
- **Collection reliability (`pip install -e ".[dev]"`):** After the documented dev install, importing **`tests.integration.test_replayt_boundary`** MUST succeed whenever **`replayt`** resolves for that environment. The Builder MUST NOT wrap **`import replayt`** (or required submodules) in **`pytest.importorskip`**, broad **`try` / `except ImportError`** that turns missing replayt into **skipped** tests, or other patterns that let the default CI job **skip** the boundary module while still exiting **0**. Missing **`replayt`** on a machine **without** the **`dev`** extra is expected to fail at **install** or **collection** with a clear error — not a silent pass.
- **Import layout:** Required **`replayt`** symbols used by the suite SHOULD be imported at **module level** in **`test_replayt_boundary.py`** (or a thin companion module collected with it) so **renamed modules, removed exports, or incompatible transitive pins** surface as **collection errors** (`pytest` exit code **2**) or **import errors** with stack traces that name **`replayt`**, not as unrelated assertion failures deep inside a test body.

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

### 4.4 Import surface contract

- The integration module MUST **import every replayt entry point** listed in §7 **Public entry point(s)** (modules / types / callables the test relies on) at import or collection time, consistent with §3.
- If upstream **moves or renames** a required symbol, CI MUST fail until maintainers update §7, **`docs/DEPENDENCY_AUDIT.md`**, and the test imports in the **same** change set (see §5.1 maintenance pass).

### 4.5 PreparedSpanRecord → replayt payload contract

- The **`dict`** (or equivalent structure) passed into replayt MUST include at least the keys documented in §7 **Data passed across the boundary**, with values consistent with **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)** for **`PreparedSpanRecord`** (**`trace_id`**, **`span_id`**, **`name`**, **`kind`**, timestamps, **`attributes`**, **`workflow_id`**, **`step_id`**) and **[docs/SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)** for triage fields.
- The Builder MUST add or tighten assertions so that **wrong types, missing keys, or accidental mutation** of the payload fails the test (regression signal for IR or exporter drift, not only replayt-side changes).
- Where **`attributes`** is passed, the test MUST reflect **mapping** semantics the exporter actually produces (for example **`dict(rec.attributes)`** or the type **`ReplaytSpanExporter`** exposes) so shallow-copy / mutation bugs are caught.

### 4.6 Installed `replayt` version sanity (normative)

- The suite MUST assert that the **installed** **`replayt`** distribution version satisfies the **`replayt`** requirement declared on **`[project.optional-dependencies].dev`** in **`pyproject.toml`** (for example: read the **`dev`** list, select the line whose **normalized** dependency name is **`replayt`**, parse it with **`packaging.requirements.Requirement`**, compare **`importlib.metadata.version("replayt")`** as **`packaging.version.Version`** using **`Requirement.specifier.contains(..., prereleases=True)`**). This catches **pin drift** and **stale venvs** that still import **`replayt`** but run below policy. The assertion MUST **not** duplicate the minimum as a hard-coded second source of truth beyond **`pyproject.toml`** (single policy string).

## 5. Local and CI invocation

- **`[project].dependencies`** MUST remain free of **`replayt`** for this backlog unless a separate item promotes it to runtime (see **[docs/MISSION.md](MISSION.md)** scope table).
- **`replayt`** MUST be declared under **`[project.optional-dependencies]`** — either the existing **`dev`** extra or a dedicated extra (for example **`integration`**) that CI merges into its install line.
- The documented install path for contributors and CI MUST install **`replayt`** without a second manual step. Today that means extending the **`pip install -e ".[dev]"`** line (or the equivalent documented in **[docs/CI_SPEC.md](CI_SPEC.md)**) so the integration tests always run in **`pytest`** on PRs and pushes.
- When pins change, update **`docs/DEPENDENCY_AUDIT.md`** and **[docs/COMPATIBILITY.md](COMPATIBILITY.md)** in the same maintenance pass (see §6 checklist).

### 5.1 How `replayt` pin bumps are validated in CI (normative)

Default CI does **not** use a separate “replayt only” job: the boundary is proven by the same bar as the rest of the suite.

1. **Install:** On every **Python** matrix cell in **`.github/workflows/ci.yml`**, the **`test`** job runs **`pip install -e ".[dev]"`** per **[docs/CI_SPEC.md](CI_SPEC.md)** §4 so **`replayt`** resolves according to **`pyproject.toml`** **`[project.optional-dependencies].dev`** (lower bound + resolver).
2. **Collection + run:** The job then runs **`pytest --cov=replayt_otel_span_exporter --cov-report=xml`** from the repository root per **[docs/CI_SPEC.md](CI_SPEC.md)** §5. That command MUST **collect** **`tests/integration/test_replayt_boundary.py`** and execute its tests successfully. A **collection error** (exit code **2**) or **failed** boundary test blocks merge like any other test failure.
3. **What a bump proves:** Raising or lowering the **`replayt`** lower bound in **`pyproject.toml`** is valid only if the above steps stay green on **all** matrix Pythons. That is the project’s primary signal that §7 APIs, §4 payload shape, and **replayt**’s types still agree.
4. **Maintenance pass when the pin or boundary changes:** In one coherent change set (or linked PRs per team policy), update **`pyproject.toml`** **`dev`** **`replayt`** specifier, §7 (**minimum version**, **public entry point(s)**, **data passed across the boundary** if needed), **`docs/DEPENDENCY_AUDIT.md`** (Test / integration: **replayt** row), **[docs/COMPATIBILITY.md](COMPATIBILITY.md)** §2 / §3 as applicable, and **[docs/CI_SPEC.md](CI_SPEC.md)** **Reference fingerprint** if install commands or matrix wording change. Do not merge a pin-only edit that leaves §7 or **COMPATIBILITY** describing a different minimum.

## 6. Verifiable acceptance checklist

Use this checklist in **Spec gate**, **Build gate**, and PR review for **replayt** integration and **boundary hardening** backlogs.

1. At least one file under **`tests/integration/`** imports **`replayt`** and is named so reviewers can find it quickly.
2. §4.1 and §4.2 scenarios are covered by automated tests; failures clearly indicate OTel/IR vs replayt-boundary issues where practical.
3. §4.4–§4.6: import surface, **`PreparedSpanRecord`** → replayt payload contract, and **§4.6 installed-version** assertion are covered as specified (§4.6 is **normative**; no skip via **`DEPENDENCY_AUDIT.md`**).
4. §3 **Collection reliability:** no **`importorskip`** / silent skip for **`replayt`** on the default **`dev`** / CI path; module-level imports fail fast when §7 entry points break.
5. **`replayt`** appears only in **optional** dependencies (or **`dev`**) in **`pyproject.toml`**, not in **`[project].dependencies`**, unless mission scope is explicitly updated elsewhere.
6. **`docs/DEPENDENCY_AUDIT.md`** includes a **Test / integration: replayt** row with the version policy and rationale.
7. §7 **Implemented boundary** is filled in with concrete modules, symbols, and minimum version — no placeholders left at merge.
8. Default CI (**[docs/CI_SPEC.md](CI_SPEC.md)**) runs **`pytest`** in a way that collects **`tests/integration/test_replayt_boundary.py`** on every **Python** version in the **`ci.yml`** matrix (see **Reference fingerprint** there) without extra flags; see §5.1 for pin-bump interpretation.

## 7. Implemented boundary (concrete API under test)

The bullets below record the API exercised by **`tests/integration/test_replayt_boundary.py`**. Update them when replayt or this adapter changes.

- **Minimum `replayt` version (PEP 440 specifiers):** **`>=0.4.25`** (declared on the **`dev`** extra in **`pyproject.toml`**).
- **Public entry point(s) (modules / callables / types):**
  - **`replayt.runner.Runner`** — constructed with a **`Workflow`**, an **`EventStore`**, and optional lifecycle hooks; **`run()`** drives execution.
  - **`replayt.runner.RunContext`** — **`set(key, value)`** / **`get(key, default=None)`** for per-run context data (documented on **`Runner`** as the hook surface for trace IDs and similar side data via **`before_step`**).
  - **`replayt.workflow.Workflow`** — minimal one-step workflow for the smoke run.
  - **`replayt.persistence.sqlite.SQLiteStore`** — durable store implementation used only so **`Runner`** can complete a real run (file-backed temp DB in tests).
  - **`replayt.testing.DryRunLLMClient`** — no-network LLM client so the workflow run does not need API keys.
  - **`replayt.types.LogMode`** — passed to **`Runner`** as **`log_mode`** (for example **`LogMode.redacted`**) so CI logs stay bounded.
- **Data passed across the boundary:** A plain **`dict`** built from **`PreparedSpanRecord`** (**`trace_id`**, **`span_id`**, **`name`**, **`kind`**, **`start_time_unix_nano`**, **`end_time_unix_nano`**, **`attributes`**, **`workflow_id`**, **`step_id`**) is written with **`RunContext.set("otel_span", ...)`** inside **`Runner`**’s **`before_step`** callback; the step handler reads it with **`get`** and asserts equality. **`workflow_id`** / **`step_id`** mirror the record fields (each may be **`None`**). **`tests/integration/test_replayt_boundary.py`** covers this shape per **[docs/SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)**.
- **What “success” means at the boundary:** No **`ContextSchemaError`** or type errors from replayt; the step sees the same mapping; **`Runner.run()`** returns **`RunResult`** with **`status == "completed"`**.

## 8. Boundary failure modes and pytest diagnostics (normative)

This section is for **operators and reviewers** interpreting failures from **`tests/integration/test_replayt_boundary.py`**. It does not add new scenarios beyond §4; it ties symptoms to the right fix.

### 8.1 Collection-time failures (pytest exit code 2)

- **Symptom:** `Interrupted: … error(s) during collection` with a traceback pointing at **`tests/integration/test_replayt_boundary.py`** or a **`replayt`** submodule import.
- **Likely causes and responses:**
  - **`replayt`** missing from the environment — use **`pip install -e ".[dev]"`** from the repository root (**[docs/CI_SPEC.md](CI_SPEC.md)** §4). A plain editable install **without** **`[dev]`** is **not** the documented contributor path and may fail collection by design (see §3).
  - **§7 entry points moved or renamed** upstream — expected **hard** failure until maintainers update §7, **`tests/integration/test_replayt_boundary.py`** imports, **`docs/DEPENDENCY_AUDIT.md`**, **`docs/COMPATIBILITY.md`**, and **`pyproject.toml`** in one maintenance pass (**§5.1** step 4).
  - **Syntax or import errors in this repo’s test module** — fix the test file; distinguish from upstream **`replayt`** issues via the traceback’s top frames.

### 8.2 Test-time failures (after collection succeeds)

Use the failing **test name** to narrow whether to fix **this package’s IR**, **replayt**, or **environment pins**:

| Signal | Likely layer | First checks |
| ------ | ------------ | ------------- |
| **`test_installed_replayt_satisfies_pyproject_lower_bound`** (§4.6) | Installed dist **older** than **`dev`** specifier, wrong package name, or **`pyproject.toml`** / test parser drift | Reinstall **`".[dev]"`** with upgrade; ensure CI uses the documented install line; keep §4.6 parsing aligned with the **`dev`** list shape. |
| **`test_tracer_pipeline_produces_prepared_record_matching_span`** (§4.1) | **OTel → `PreparedSpanRecord`** (exporter / skeleton IR) | **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)**; not primarily replayt core. |
| **`test_prepared_record_crosses_replayt_run_context_boundary`** (§4.2, §4.5) | **Payload shape**, **types**, **`RunContext`** contract, or replayt rejecting the mapping | Assertions in **`_assert_boundary_payload_matches_record`** (keys, types, **`attributes`** copy semantics) vs replayt errors (**`ContextSchemaError`**, type errors) per §7 **What “success” means**. |

### 8.3 Green CI after a `replayt` pin change

Merging a change to the **`replayt`** line on **`[project.optional-dependencies].dev`** is valid only if **§5.1** steps 1–2 stay green on **all** matrix Pythons. That is the primary proof that §7 symbols, §4.5 payload rules, and §4.6 installed-version policy still align for the new bound.

## Non-goals (this backlog)

- Running full replayt workflows against live backends or credentials.
- Performance or load testing of replayt.
- Changing the **runtime** dependency set of **`replayt-otel-span-exporter`** to require **`replayt`** for end users (optional/test-only unless promoted by another item).

## Implementation notes for Builder / Maintainer

- Prefer **stable, documented** replayt APIs over private attributes; if only unstable hooks exist, document the risk in **`docs/DEPENDENCY_AUDIT.md`** and keep the boundary test narrow.
- If replayt’s packaging or API diverges between Python versions, **match** the CI matrix in **`docs/CI_SPEC.md`** or extend the matrix in the same change.
- When this spec and **`docs/MISSION.md`** diverge from **`pyproject.toml`** or CI, update **code and docs** in the same maintenance pass.
