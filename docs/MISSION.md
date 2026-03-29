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
| Optional **approval / audit hooks** for **`ReplaytSpanExporter`** per **[SPEC_SPAN_EXPORT_APPROVAL_UX.md](SPEC_SPAN_EXPORT_APPROVAL_UX.md)** (integrator policy gate; not an in-repo UI) | Interactive approval products, persistent audit stores, or **replayt** runtime dependency for gating |
| **First alpha (and later) PyPI / private-index publishing** — versioning, changelog, artifact upload, and install verification per **[SPEC_FIRST_ALPHA_RELEASE.md](SPEC_FIRST_ALPHA_RELEASE.md)** | Organization-wide release platforms, signing policy beyond normal **`twine`** usage, or changing **replayt** runtime dependency policy without a separate backlog |
| Optional **`docs/reference-documentation/`** — bounded upstream context and index pages per **[SPEC_REFERENCE_DOCUMENTATION.md](SPEC_REFERENCE_DOCUMENTATION.md)** | Full mirrors of upstream documentation sites; substituting this folder for **[COMPATIBILITY.md](COMPATIBILITY.md)** or **[MISSION.md](MISSION.md)** policy |
| Unit/integration tests described in the specs below | Performance SLAs and advanced batching semantics |

**Exception — replayt integration tests:** **[SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** allows declaring **`replayt`** under **`[project.optional-dependencies]`** (for example bundled into **`dev`**) so CI can prove the boundary. That does **not** by itself add **`replayt`** to **`[project].dependencies`** for library users.

## Test and CI expectations

These bullets are the **mission-level summary**; **[CI_SPEC.md](CI_SPEC.md)** is authoritative if anything diverges.

- **Install path (contributors + default CI):** `python -m pip install --upgrade pip` then `pip install -e ".[dev]"` so **`replayt`** and other dev pins match **`pyproject.toml`** (see **[CI_SPEC.md](CI_SPEC.md)** §4–§5).
- **Tests command (default CI):** from the repository root,  
  `pytest --cov=replayt_otel_span_exporter --cov-report=xml`  
  so **all** collected tests under **`tests/`** run on every matrix cell unless **[CI_SPEC.md](CI_SPEC.md)** is explicitly revised (see §5–§6 there).
- **Python matrix:** versions must satisfy **`[project].requires-python`** (currently **≥ 3.11**); CI exercises **3.11** and **3.12** today and MUST add **3.13** on every matrix cell when **[CI_SPEC.md](CI_SPEC.md)** [§3.1](CI_SPEC.md#31-python-313-matrix-expansion-normative-backlog) is satisfied (see **Reference fingerprint** under **Implementation notes** there). If **3.13** is blocked, **[COMPATIBILITY.md](COMPATIBILITY.md)** §4.1.2 records the deferral until unblocked.
- **Workflow success:** a **green** change is a successful run of **every** job in **`.github/workflows/ci.yml`** (today at least **`test`** and **`supply-chain`**); see **[CI_SPEC.md](CI_SPEC.md)** §7.
- **Spec-to-suite mapping (what CI is expected to prove):**
  - **[SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)** — exporter IR, **`ReplaytSpanExporter`** behavior, and skeleton test contract (e.g. **`tests/test_exporter.py`**, **`tests/test_records.py`**).
  - **[SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)** — export failure logging, batch semantics, redaction on failure paths (plus associated tests; see that spec §6–§7).
  - **[SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)** — **`workflow_id`** / **`step_id`** and **`[REDACTED]`** attribute handling (see that spec §5).
  - **[SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** — replayt import boundary; **`tests/integration/test_replayt_boundary.py`** MUST be collected by default **`pytest`** when **`replayt`** is on the path (see that spec §3–§5 and §7).
  - **`tests/integration/test_opentelemetry_api_usage.py`** — OpenTelemetry trace API smoke only (no **`replayt`**), per **[CI_SPEC.md](CI_SPEC.md)** §5.
  - **[SPEC_README_QUICK_START.md](SPEC_README_QUICK_START.md)** — README quick start, usage example, and CI proof via **`tests/test_readme_usage_example.py`** and **`tests/readme_usage_example_snippet.py`** (names recorded in **[CI_SPEC.md](CI_SPEC.md)** §5).
  - **[SPEC_SPAN_EXPORT_APPROVAL_UX.md](SPEC_SPAN_EXPORT_APPROVAL_UX.md)** — optional **`ReplaytSpanExporter`** **`on_export_commit`** / **`on_export_audit`**, **`SpanExportResult.SUCCESS`** on policy denial, audit allow-list, and tests in **`tests/test_exporter.py`** per that spec §8.
  - **[SPEC_FIRST_ALPHA_RELEASE.md](SPEC_FIRST_ALPHA_RELEASE.md)** — first **alpha** prerelease to PyPI or a private index: PEP 440 **alpha** **`[project].version`**, **[CHANGELOG.md](../CHANGELOG.md)** release section, upload, and §5 install verification (optional **GitHub Actions** / OIDC: **[CI_SPEC.md](CI_SPEC.md) [§8](CI_SPEC.md#8-optional-release-workflow-oidc-trusted-publishing)** and **`release.yml`**).
  - **[SPEC_REFERENCE_DOCUMENTATION.md](SPEC_REFERENCE_DOCUMENTATION.md)** — optional **`docs/reference-documentation/`** tree for contributor / agent context; default **`pytest`** includes **`tests/test_reference_documentation.py`** per **[CI_SPEC.md](CI_SPEC.md)** §5 (folder **README**, stub pages, size bound; **no** outbound HTTP).
- **Supply chain:** **`supply-chain`** job expectations and **`pip-audit`** ignore rules live in **[DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)** and **[CI_SPEC.md](CI_SPEC.md)** (optional jobs §).

## Success criteria

- **Automated tests** (see **[CI_SPEC.md](CI_SPEC.md)** and [Test and CI expectations](#test-and-ci-expectations) above) cover span ingestion and transformation as specified in **[SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)**, export failure logging and redaction per **[SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)**, triage metadata and IR attribute redaction per **[SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)**, the replayt boundary per **[SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** (**`tests/integration/test_replayt_boundary.py`**), the README usage pipeline per **[SPEC_README_QUICK_START.md](SPEC_README_QUICK_START.md)** (**`tests/test_readme_usage_example.py`**), and approval / audit behavior per **[SPEC_SPAN_EXPORT_APPROVAL_UX.md](SPEC_SPAN_EXPORT_APPROVAL_UX.md)** §8 (**`tests/test_exporter.py`**).
- **Public API** remains small and listed explicitly (**`__all__`**); extension points are documented in the spec and design principles.
- **Changelog** records user-visible API and dependency changes under **Unreleased** until release (**[CHANGELOG.md](../CHANGELOG.md)** at repo root).
- **First alpha release** (backlogs **“Publish first alpha release”** and **“Close first alpha: upload, verify SPEC_FIRST_ALPHA section 5, align README install prose”**): **`[project].version`** is a PEP 440 **alpha** prerelease, **CHANGELOG** contains a dated section for that version, **`python -m build`** + **`twine check`** precede upload per **[SPEC_FIRST_ALPHA_RELEASE.md](SPEC_FIRST_ALPHA_RELEASE.md)** §4, artifacts are on the chosen index, **§5 verification** and **[§5.2](SPEC_FIRST_ALPHA_RELEASE.md#52-release-handoff-record-normative)** handoff fields pass, and README / compatibility prose updated per that spec §6 when the index is live.
- **CI** on the default integration branch remains **green** per **[CI_SPEC.md](CI_SPEC.md)** §7 for the documented install path and **`pytest`** command.

## Compatibility matrix

**Canonical documentation:** **[docs/COMPATIBILITY.md](COMPATIBILITY.md)** — full matrix, pin strategy, how CI proves the contract, and links to **replayt** releases on PyPI.

| Component | Policy (summary) |
| --------- | ---------------- |
| **Python** | **`requires-python`** in **`pyproject.toml`** (currently **≥ 3.11**); CI matrix (**3.11** / **3.12**; plus **3.13** per **[CI_SPEC.md](CI_SPEC.md)** §3.1 when green) is described in **[CI_SPEC.md](CI_SPEC.md)** and **[COMPATIBILITY.md](COMPATIBILITY.md)** §4–§4.1. |
| **OpenTelemetry** | **`opentelemetry-api`** and **`opentelemetry-sdk`** lower bounds in **`pyproject.toml`**; rationale in **`DEPENDENCY_AUDIT.md`**. |
| **replayt** | **Not** a runtime dependency unless a backlog promotes it. **Dev / CI** lower bound on the **`dev`** extra; boundary and minimum version in **[SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** §7. |

When pins or CI versions change, update **`COMPATIBILITY.md`** in the same maintenance pass as **`pyproject.toml`** and **`CI_SPEC.md`** (reference fingerprint).

## Audience

| Audience | Needs |
| -------- | ----- |
| **Maintainers** | This file, **[CI_SPEC.md](CI_SPEC.md)**, **`DEPENDENCY_AUDIT.md`**, **[SPEC_FIRST_ALPHA_RELEASE.md](SPEC_FIRST_ALPHA_RELEASE.md)** (alpha / publish checklist), release notes in **[CHANGELOG.md](../CHANGELOG.md)** |
| **Integrators** | Stable adapter surface, **[COMPATIBILITY.md](COMPATIBILITY.md)**, **[SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)**, README overview |
| **Governance / compliance** (when applicable) | **[SPEC_SPAN_EXPORT_APPROVAL_UX.md](SPEC_SPAN_EXPORT_APPROVAL_UX.md)** audit allow-list, **[SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)** redaction, **[SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)** triage fields |
| **Contributors** | README quick start, specs under **`docs/`**, optional **`docs/reference-documentation/`** per **[SPEC_REFERENCE_DOCUMENTATION.md](SPEC_REFERENCE_DOCUMENTATION.md)**, tests under **`tests/`** |

Extend audience rows in **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** when new stakeholder types appear.

## LLM and demos

This package is **not** an LLM runtime. Any demos or agent tooling that mention models, secrets, cost, or redaction MUST follow **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** § LLM / demos and stay consistent with **[SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)** and **[SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)** for logging and attribute handling.
