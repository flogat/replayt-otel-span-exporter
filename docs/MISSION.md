# Mission: OpenTelemetry Span Exporter for Replayt Workflows

This document is the **north star** for maintainers and integrators: problem, scope, how **replayt** relates to this repo, what “done” means in tests and CI, and who should read what next.

## Backlog traceability — “Define project mission and scope”

| Acceptance criterion | Where this doc satisfies it |
| -------------------- | --------------------------- |
| **User problem** stated clearly | [Users and problem](#users-and-problem) |
| **Replayt’s role** (this repo vs core) | [Replayt’s role](#replayts-role), [Primary positioning](#primary-positioning) |
| **Scope** (in / out) | [Scope](#scope) |
| **Success outcomes** | [Success criteria](#success-criteria) |
| **Concrete test / CI expectations** | [Test and CI expectations](#test-and-ci-expectations) (details in **[CI_SPEC.md](CI_SPEC.md)**) |

For implementation contracts, use the spec files linked from the [Scope](#scope) and [Test and CI expectations](#test-and-ci-expectations) sections.

## Users and problem

**Integrators** running Python services with OpenTelemetry tracing want a **narrow, well-tested bridge** from the OTel SDK to **replayt-oriented** workflow data. Today that path is underspecified; this package provides an explicit **exporter skeleton** and **documented intermediate representation** so replayt consumers can adopt it without forking replayt core.

**User-facing outcome:** Integrators can depend on a **small, versioned** Python package that turns live **`ReadableSpan`** batches into **documented prepared records**, with **predictable failure logging** and **attribute redaction** for sensitive keys. **`replayt`** stays out of **`[project].dependencies`**; contributors and default CI use the **`dev`** install path so **`tests/integration/test_replayt_boundary.py`** proves the hand-off against a pinned **`replayt`** per **[SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** (see scope exception below).

## Replayt’s role

- **This repo** owns the OTel → replayt-prep adapter surface, **version pins**, and **CI** that prove the contract against declared OpenTelemetry versions.
- **Replayt core** stays upstream: compatibility and feature requests flow through normal channels (**[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** — “Not a lever on core”).

## Primary positioning

- **Primary pattern:** **Framework bridge** (see **[REPLAYT_ECOSYSTEM_IDEA.md](REPLAYT_ECOSYSTEM_IDEA.md)**): OpenTelemetry Python SDK → documented prepared records for replayt workflows.

## Scope

| In scope | Out of scope (unless a later item says otherwise) |
| -------- | --------------------------------------------------- |
| **`SpanExporter`** implementation and **prepared span records** per **[SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)** | Runtime dependency on **`replayt`** for the skeleton milestone |
| **`opentelemetry-api`** + **`opentelemetry-sdk`** as declared dependencies | Full replayt workflow execution, storage backends, or network export |
| Unit/integration tests described in the specs below | Performance SLAs and advanced batching semantics |

**Exception — replayt integration tests:** **[SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** allows declaring **`replayt`** under **`[project.optional-dependencies]`** (for example bundled into **`dev`**) so CI can prove the boundary. That does **not** by itself add **`replayt`** to **`[project].dependencies`** for library users.

## Test and CI expectations

These bullets are the **mission-level summary**; **[CI_SPEC.md](CI_SPEC.md)** is authoritative if anything diverges.

- **Install path (contributors + default CI):** `pip install -e ".[dev]"` after upgrading **`pip`**, so **`replayt`** and other dev pins match **`pyproject.toml`** (see **[CI_SPEC.md](CI_SPEC.md)** §4–§5).
- **Tests command (default CI):** from the repository root,  
  `pytest --cov=replayt_otel_span_exporter --cov-report=xml`  
  so **all** collected tests under **`tests/`** run on every matrix cell unless **[CI_SPEC.md](CI_SPEC.md)** is explicitly revised (see §5–§6 there).
- **Python matrix:** versions must satisfy **`[project].requires-python`** (currently **≥ 3.11**); CI currently exercises **3.11** and **3.12** (see **[CI_SPEC.md](CI_SPEC.md)** §3 and the reference fingerprint §).
- **Workflow success:** a **green** change is a successful run of **every** job in **`.github/workflows/ci.yml`** (today at least **`test`** and **`supply-chain`**); see **[CI_SPEC.md](CI_SPEC.md)** §7.
- **Spec-to-suite mapping (what CI is expected to prove):**
  - **[SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)** — exporter IR, **`ReplaytSpanExporter`** behavior, and skeleton test contract (e.g. **`tests/test_exporter.py`**, **`tests/test_records.py`**).
  - **[SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)** — export failure logging, batch semantics, redaction on failure paths (plus associated tests; see that spec §6–§7).
  - **[SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)** — **`workflow_id`** / **`step_id`** and **`[REDACTED]`** attribute handling (see that spec §5).
  - **[SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** — replayt import boundary; **`tests/integration/test_replayt_boundary.py`** MUST be collected by default **`pytest`** when **`replayt`** is on the path (see that spec §3–§5 and §7).
  - **`tests/integration/test_opentelemetry_api_usage.py`** — OpenTelemetry trace API smoke only (no **`replayt`**), per **[CI_SPEC.md](CI_SPEC.md)** §5.
- **Supply chain:** **`supply-chain`** job expectations and **`pip-audit`** ignore rules live in **[DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)** and **[CI_SPEC.md](CI_SPEC.md)** (optional jobs §).

## Success criteria

- **Automated tests** (see **[CI_SPEC.md](CI_SPEC.md)** and [Test and CI expectations](#test-and-ci-expectations) above) cover span ingestion and transformation as specified in **[SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)**, export failure logging and redaction per **[SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)**, triage metadata and IR attribute redaction per **[SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)**, and the replayt boundary per **[SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** (**`tests/integration/test_replayt_boundary.py`**).
- **Public API** remains small and listed explicitly (**`__all__`**); extension points are documented in the spec and design principles.
- **Changelog** records user-visible API and dependency changes under **Unreleased** until release (**[CHANGELOG.md](../CHANGELOG.md)** at repo root).
- **CI** on the default integration branch remains **green** per **[CI_SPEC.md](CI_SPEC.md)** §7 for the documented install path and **`pytest`** command.

## Compatibility matrix (initial)

| Component | Policy |
| --------- | ------ |
| **Python** | **`requires-python`** in **`pyproject.toml`** (currently **≥ 3.11**); CI matrix is the source of truth. |
| **OpenTelemetry** | **`opentelemetry-api`** and **`opentelemetry-sdk`** pinned with compatible lower bounds; audit trail in **`DEPENDENCY_AUDIT.md`**. |
| **replayt** | **Not** a runtime dependency of the library unless a backlog promotes it. For integration tests, optional / **`dev`** pin and policy in **`DEPENDENCY_AUDIT.md`** per **[SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)**. |

Update this table when pins or CI versions change.

## Audience

| Audience | Needs |
| -------- | ----- |
| **Maintainers** | This file, **[CI_SPEC.md](CI_SPEC.md)**, **`DEPENDENCY_AUDIT.md`**, release notes in **[CHANGELOG.md](../CHANGELOG.md)** |
| **Integrators** | Stable adapter surface, compatibility matrix above, **[SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)**, README overview |
| **Contributors** | README quick start, specs under **`docs/`**, tests under **`tests/`** |

Extend audience rows in **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** when new stakeholder types appear.

## LLM and demos

This package is **not** an LLM runtime. Any demos or agent tooling that mention models, secrets, cost, or redaction MUST follow **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** § LLM / demos and stay consistent with **[SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)** and **[SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)** for logging and attribute handling.
