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

## Release phases and API stability (beta / 1.0)

After a **first alpha** is verified on an index (**[SPEC_FIRST_ALPHA_RELEASE.md](SPEC_FIRST_ALPHA_RELEASE.md)** §5), promotion to **beta** or **1.0**, **semver** expectations for **`PreparedSpanRecord`** and **`ReplaytSpanExporter`**, **changelog** discipline, **optional hook** evolution, and **deprecation** policy are defined in **[SPEC_BETA_AND_STABLE_PROMOTION.md](SPEC_BETA_AND_STABLE_PROMOTION.md)** (§2–§6). A short phase-oriented index for maintainers and Mission Control lives in **[ROADMAP.md](ROADMAP.md)**.

## Backlog traceability — “Define beta/1.0 promotion criteria and public API stability promises”

| Acceptance theme | Where satisfied |
| ---------------- | ---------------- |
| Beta / 1.0 **promotion checklists** | **[SPEC_BETA_AND_STABLE_PROMOTION.md](SPEC_BETA_AND_STABLE_PROMOTION.md)** §2 |
| **Semver** for **`PreparedSpanRecord`** / **`ReplaytSpanExporter`** | Same doc §3 |
| **Changelog** discipline | Same doc §4 |
| **Optional hooks** evolution | Same doc §5 |
| **Deprecation** before removal of **`__all__`**, IR, exporter, or hook contracts | Same doc §6 |
| Integrator / MC **roadmap** alignment | **[ROADMAP.md](ROADMAP.md)** |

## Backlog traceability — “Post-alpha roadmap: beta or 1.0 criteria and deprecation policy”

Mission Control **`e9115fe4-6d8f-44b7-97e1-008a1a8cf478`** (phase **2** spec lead): after first **alpha** index verification, explicit **beta** / **1.0** promotion rules, **semver** and **changelog** expectations, **optional hook** evolution, and **deprecation** policy so integrators and Mission Control share the same phase language.

| Acceptance theme | Where satisfied |
| ---------------- | ---------------- |
| **Beta** / **1.0** promotion checklists | **[SPEC_BETA_AND_STABLE_PROMOTION.md](SPEC_BETA_AND_STABLE_PROMOTION.md)** §2 |
| **SemVer** for **`PreparedSpanRecord`** / **`ReplaytSpanExporter`** | Same doc §3 |
| **Changelog** discipline (incl. deprecations) | Same doc §4 |
| **Optional hooks** evolution | Same doc §5 |
| **Deprecation** policy (warnings, **CHANGELOG**, timeline) | Same doc §6 |
| **Roadmap** / MC alignment | **[ROADMAP.md](ROADMAP.md)** + **MISSION** links |
| **Testable doc closure** for this backlog | Same spec **§7.1** |

## Backlog traceability — “Document integrator cookbook: approval hook + audit in production services”

Mission Control **`29efde6c-c106-43ca-a17a-1623d53145f5`** (phase **2** spec lead): integrator-facing guidance for **`on_export_commit`** / **`on_export_audit`** in production.

| Acceptance theme | Where satisfied |
| ---------------- | ---------------- |
| **Minimal async-safe pattern** and hook constraints | **[RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md](RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md)** §1.5–§2 |
| **Idempotency** and duplicate **`export`** / audit semantics | Same recipe **§4** |
| **Audit sink examples** without persisting full prepared **attributes** | Same recipe **§3**, **§5** (stdlib **`logging`** and queue deferral) |
| **Normative hook + allow list** (contracts) | **[SPEC_SPAN_EXPORT_APPROVAL_UX.md](SPEC_SPAN_EXPORT_APPROVAL_UX.md)** **§4–§5**, **§10** |
| **Discoverability** from mission scope | [Scope](#scope) table row (approval / audit hooks + recipe); root **[README.md](../README.md)** — **Optional approval hook** |

## Backlog traceability — “Harden failure-path logging against log injection and oversized messages”

Mission Control **`dad27282-2904-4839-ba1c-070e8e3ba7c8`** (phase **2** spec lead): **ERROR**-path logging safety (untrusted exception text, length limits, redaction alignment, tests).

| Acceptance theme | Where satisfied |
| ---------------- | ---------------- |
| **Inventory** of stdlib **`logging`** call sites and **approval-hook ERROR parity** | **[SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)** **§5.5** |
| **Untrusted strings**, **C0/C1** stripping, **1024** / **256** code-point caps | Same spec **§5.2**–**§5.4** |
| **Redaction table** — no fork of **`attribute_key_is_sensitive`** on failure paths | Same spec **§5.1**; **[SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)** §3.1 (IR context) |
| **`pytest`** contract (bounds, injection hardening, optional hook-path mirror) | Same spec **§6**–**§7**; explicit MC checklist **§9** |
| **CI / suite mapping** | **[CI_SPEC.md](CI_SPEC.md)** §5 (failure-handling bullet) |

## Backlog traceability — “Clarify OpenTelemetry upper-bound strategy in pyproject and COMPATIBILITY”

Mission Control **`9b94e677-914a-471a-8499-071c1cb92455`** (phase **2** spec lead): **runtime** **`opentelemetry-api`** / **`opentelemetry-sdk`** upper-bound strategy (**none** on **1.x**), how **CI** proves compatibility on floating resolution, and what **integrators** should pin.

| Acceptance theme | Where satisfied |
| ---------------- | ---------------- |
| **Policy** — lower bounds only, **no** **`<`** runtime cap | **[SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md](SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md)** **§1**, **§1.2**, **§7** row **A**; **[COMPATIBILITY.md](COMPATIBILITY.md)** §2–§3.1 |
| **CI proof** — **`test`** after **`pip install -e ".[dev]"`**; **`supply-chain`** is not the OTel API bar | Same spec **§4**; **[DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)** (runtime section + MC table); **[CI_SPEC.md](CI_SPEC.md)** §4–§5 |
| **Integrator pins** — **API** + **SDK** together; floors vs app lockfiles | **[SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md](SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md)** **§1.1**, **§7** row **C** |
| **Compatibility matrix** (summary row) | [Compatibility matrix](#compatibility-matrix) — **OpenTelemetry** row |

## Backlog traceability — “Ship a minimal runnable example package or scripts/ recipe”

Mission Control **`21487c24-8d58-4085-896c-4a6bad8d0af4`** (phase **2** spec lead): **copy-paste runnable** OpenTelemetry → **`PreparedSpanRecord`** demo under **`scripts/`**, **without** **`replayt`** as a runtime dependency, **beyond** the README snippet harness.

| Acceptance theme | Where satisfied |
| ---------------- | --------------- |
| **`scripts/`** primary module, canonical **`python scripts/otel_to_prepared_demo.py`**, contributor install | **[SPEC_SCRIPTS_OTEL_PREPARED_DEMO.md](SPEC_SCRIPTS_OTEL_PREPARED_DEMO.md)** §2, §5 |
| **`TracerProvider`**, **`ReplaytSpanExporter`**, triage attributes, printed IR fields, exit codes | Same spec §3–§4 |
| **Design principles** / **LLM–demos** hygiene; **no** **`replayt`** import or **`[project].dependencies`** change | Same spec §4–§5 |
| **CI proof** via **`tests/test_scripts_otel_prepared_demo.py`** | Same spec §6; **[CI_SPEC.md](CI_SPEC.md)** §5 |
| **“Example package”** disambiguation (in-repo recipe vs PyPI subpackage) | Same spec opening + traceability |

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
| Optional **approval / audit hooks** for **`ReplaytSpanExporter`** per **[SPEC_SPAN_EXPORT_APPROVAL_UX.md](SPEC_SPAN_EXPORT_APPROVAL_UX.md)** (integrator policy gate; not an in-repo UI). Production-oriented patterns (async-safe use, audit sink examples, idempotency) live in **[RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md](RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md)**, summarized in that spec **§10**. | Interactive approval products, persistent audit stores, or **replayt** runtime dependency for gating |
| **First alpha (and later) PyPI / private-index publishing** — versioning, changelog, artifact upload, and install verification per **[SPEC_FIRST_ALPHA_RELEASE.md](SPEC_FIRST_ALPHA_RELEASE.md)** | Organization-wide release platforms, signing policy beyond normal **`twine`** usage, or changing **replayt** runtime dependency policy without a separate backlog |
| **Beta / stable promotion, semver, public API stability, and deprecation** — criteria after alpha verification, **`__all__`** / IR / exporter semver tables, changelog rules, optional hook evolution, and deprecation policy per **[SPEC_BETA_AND_STABLE_PROMOTION.md](SPEC_BETA_AND_STABLE_PROMOTION.md)** §2–§6; phase summary **[ROADMAP.md](ROADMAP.md)** | Calendar-based or download-count gates; automated promotion jobs unless a backlog adds them to **[CI_SPEC.md](CI_SPEC.md)** |
| Optional **`docs/reference-documentation/`** — bounded upstream context and index pages per **[SPEC_REFERENCE_DOCUMENTATION.md](SPEC_REFERENCE_DOCUMENTATION.md)** | Full mirrors of upstream documentation sites; substituting this folder for **[COMPATIBILITY.md](COMPATIBILITY.md)** or **[MISSION.md](MISSION.md)** policy |
| Runnable **`scripts/`** OpenTelemetry → **`PreparedSpanRecord`** demo per **[SPEC_SCRIPTS_OTEL_PREPARED_DEMO.md](SPEC_SCRIPTS_OTEL_PREPARED_DEMO.md)** | **`console_scripts`** / PyPI-packaged CLIs for the demo, **`replayt`** imports in the script, or substituting this script for the README snippet CI contract (**[SPEC_README_QUICK_START.md](SPEC_README_QUICK_START.md)** §4) |
| Unit/integration tests described in the specs below | Performance SLAs and advanced batching semantics |

**Exception — replayt integration tests:** **[SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** allows declaring **`replayt`** under **`[project.optional-dependencies]`** (for example bundled into **`dev`**) so CI can prove the boundary. That does **not** by itself add **`replayt`** to **`[project].dependencies`** for library users.

## Test and CI expectations

These bullets are the **mission-level summary**; **[CI_SPEC.md](CI_SPEC.md)** is authoritative if anything diverges.

- **Install path (contributors + default CI):** `python -m pip install --upgrade pip` then `pip install -e ".[dev]"` so **`replayt`** and other dev pins match **`pyproject.toml`** (see **[CI_SPEC.md](CI_SPEC.md)** §4–§5).
- **Tests command (default CI):** from the repository root,  
  `pytest --cov=replayt_otel_span_exporter --cov-report=xml`  
  so **all** collected tests under **`tests/`** run on every matrix cell unless **[CI_SPEC.md](CI_SPEC.md)** is explicitly revised (see §5–§6 there).
- **Python matrix:** versions must satisfy **`[project].requires-python`** (currently **≥ 3.11**); CI exercises **3.11**, **3.12**, and **3.13** on every matrix cell (see **Reference fingerprint** in **[CI_SPEC.md](CI_SPEC.md)**). If a future interpreter cannot be added without policy changes, **[COMPATIBILITY.md](COMPATIBILITY.md)** §4.1 records the deferral until unblocked.
- **Python matrix maintenance:** Testable criteria for the **3.13** row (and deferring or removing a matrix Python without doc drift) are normative in **[CI_SPEC.md](CI_SPEC.md)** §3.1 (Mission Control backlog **`4a00b7f7-af4e-4200-9d28-38e3827fa2e5`**); operator deferral steps live in **[COMPATIBILITY.md](COMPATIBILITY.md)** §4.1.2.
- **Workflow success:** a **green** change is a successful run of **every** job in **`.github/workflows/ci.yml`** (today at least **`test`** and **`supply-chain`**); see **[CI_SPEC.md](CI_SPEC.md)** §7.
- **Spec-to-suite mapping (what CI is expected to prove):**
  - **[SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)** — exporter IR, **`ReplaytSpanExporter`** behavior, and skeleton test contract (e.g. **`tests/test_exporter.py`**, **`tests/test_records.py`**).
  - **[SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)** — export failure logging, batch semantics, redaction on failure paths, bounded untrusted strings and log-injection hardening (**§5.4**–**§5.5**; tests **§6**–**§7** and MC **`dad27282`** checklist **§9**; **§6** items **4–6** required, item **7** recommended for approval-hook **ERROR** templates).
  - **[SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)** — **`workflow_id`** / **`step_id`** and **`[REDACTED]`** attribute handling (see that spec §5).
  - **[SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** — replayt import boundary, **`PreparedSpanRecord`** → replayt payload contract, and reliable collection after **`pip install -e ".[dev]"`**; **`tests/integration/test_replayt_boundary.py`** MUST be collected by default **`pytest`** when **`replayt`** is on the path (see that spec §3–§5, §5.1, and §7).
  - **`tests/integration/test_opentelemetry_api_usage.py`** — OpenTelemetry trace API smoke only (no **`replayt`**), per **[CI_SPEC.md](CI_SPEC.md)** §5.
  - **[SPEC_README_QUICK_START.md](SPEC_README_QUICK_START.md)** — README quick start, usage example, and CI proof via **`tests/test_readme_usage_example.py`** and **`tests/readme_usage_example_snippet.py`** (names recorded in **[CI_SPEC.md](CI_SPEC.md)** §5).
  - **[SPEC_SCRIPTS_OTEL_PREPARED_DEMO.md](SPEC_SCRIPTS_OTEL_PREPARED_DEMO.md)** — runnable **`scripts/otel_to_prepared_demo.py`**, documented invocation, and CI proof via **`tests/test_scripts_otel_prepared_demo.py`** (name recorded in **[CI_SPEC.md](CI_SPEC.md)** §5).
  - **[SPEC_SPAN_EXPORT_APPROVAL_UX.md](SPEC_SPAN_EXPORT_APPROVAL_UX.md)** — optional **`ReplaytSpanExporter`** **`on_export_commit`** / **`on_export_audit`**, **`SpanExportResult.SUCCESS`** on policy denial, audit allow-list, tests in **`tests/test_exporter.py`** per that spec §8, and **`tests/test_recipe_span_export_hooks_production_docs.py`** for **§10.1** integrator cookbook doc acceptance (**[RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md](RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md)**, **MISSION.md**, **README.md**).
  - **[SPEC_FIRST_ALPHA_RELEASE.md](SPEC_FIRST_ALPHA_RELEASE.md)** — first **alpha** prerelease to PyPI or a private index: PEP 440 **alpha** **`[project].version`**, **[CHANGELOG.md](../CHANGELOG.md)** release section, upload, and §5 install verification (optional **GitHub Actions** / OIDC: **[CI_SPEC.md](CI_SPEC.md) [§8](CI_SPEC.md#8-optional-release-workflow-oidc-trusted-publishing)** and **`release.yml`**).
  - **[SPEC_BETA_AND_STABLE_PROMOTION.md](SPEC_BETA_AND_STABLE_PROMOTION.md)** — post-alpha **beta** / **1.0** promotion, **SemVer**, **CHANGELOG** / **deprecation** policy, and optional **hook** evolution; default **`pytest`** includes **`tests/test_beta_stable_promotion_docs.py`** per **[CI_SPEC.md](CI_SPEC.md)** §5 (structural smoke for §2–§6 and **ROADMAP** links; **§7–§8** are reviewer-checked).
  - **[SPEC_REFERENCE_DOCUMENTATION.md](SPEC_REFERENCE_DOCUMENTATION.md)** — optional **`docs/reference-documentation/`** tree for contributor / agent context; default **`pytest`** includes **`tests/test_reference_documentation.py`** per **[CI_SPEC.md](CI_SPEC.md)** §5 (folder **README**, stub pages, size bound; **no** outbound HTTP).
- **Supply chain:** **`supply-chain`** job expectations and **`pip-audit`** ignore rules live in **[DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)** and **[CI_SPEC.md](CI_SPEC.md)** (optional jobs §).

## Success criteria

- **Automated tests** (see **[CI_SPEC.md](CI_SPEC.md)** and [Test and CI expectations](#test-and-ci-expectations) above) cover span ingestion and transformation as specified in **[SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)**, export failure logging, redaction, and bounded / sanitized log fields per **[SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)**, triage metadata and IR attribute redaction per **[SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)**, the replayt boundary per **[SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** (**`tests/integration/test_replayt_boundary.py`**), the README usage pipeline per **[SPEC_README_QUICK_START.md](SPEC_README_QUICK_START.md)** (**`tests/test_readme_usage_example.py`**), the **`scripts/`** prepared-record demo per **[SPEC_SCRIPTS_OTEL_PREPARED_DEMO.md](SPEC_SCRIPTS_OTEL_PREPARED_DEMO.md)** (**`tests/test_scripts_otel_prepared_demo.py`**), and approval / audit behavior per **[SPEC_SPAN_EXPORT_APPROVAL_UX.md](SPEC_SPAN_EXPORT_APPROVAL_UX.md)** §8 (**`tests/test_exporter.py`**) plus **§10.1** cookbook doc structure (**`tests/test_recipe_span_export_hooks_production_docs.py`**).
- **Public API** remains small and listed explicitly (**`__all__`**); extension points are documented in the spec and design principles.
- **Changelog** records user-visible API and dependency changes under **Unreleased** until release (**[CHANGELOG.md](../CHANGELOG.md)** at repo root).
- **First alpha release** (backlogs **“Publish first alpha release”** and **“Close first alpha: upload, verify SPEC_FIRST_ALPHA section 5, align README install prose”**): **`[project].version`** is a PEP 440 **alpha** prerelease, **CHANGELOG** contains a dated section for that version, **`python -m build`** + **`twine check`** precede upload per **[SPEC_FIRST_ALPHA_RELEASE.md](SPEC_FIRST_ALPHA_RELEASE.md)** §4, artifacts are on the chosen index, **§5 verification** and **[§5.2](SPEC_FIRST_ALPHA_RELEASE.md#52-release-handoff-record-normative)** handoff fields pass, and README / compatibility prose updated per that spec §6 when the index is live.
- **Beta / 1.0, API stability, and deprecation** (backlogs **“Define beta/1.0 promotion criteria and public API stability promises”** and Mission Control **`e9115fe4-6d8f-44b7-97e1-008a1a8cf478`** — **Post-alpha roadmap: beta or 1.0 criteria and deprecation policy**): promotion checklists, semver rules, changelog discipline, optional hook evolution, and deprecation policy per **[SPEC_BETA_AND_STABLE_PROMOTION.md](SPEC_BETA_AND_STABLE_PROMOTION.md)** §2–§6; maintainers and Mission Control use **[ROADMAP.md](ROADMAP.md)** for phase alignment; doc closure criteria in that spec **§7.1**.
- **CI** on the default integration branch remains **green** per **[CI_SPEC.md](CI_SPEC.md)** §7 for the documented install path and **`pytest`** command.

## Compatibility matrix

**Canonical documentation:** **[docs/COMPATIBILITY.md](COMPATIBILITY.md)** — full matrix, pin strategy, how CI proves the contract, and links to **replayt** releases on PyPI.

| Component | Policy (summary) |
| --------- | ---------------- |
| **Python** | **`requires-python`** in **`pyproject.toml`** (currently **≥ 3.11**); CI matrix (**3.11** / **3.12** / **3.13**) is described in **[CI_SPEC.md](CI_SPEC.md)** and **[COMPATIBILITY.md](COMPATIBILITY.md)** §4–§4.1. |
| **OpenTelemetry** | **`opentelemetry-api`** and **`opentelemetry-sdk`** — **lower bounds only** in **`pyproject.toml`** (no runtime **`<`** cap); **CI** floats to newest compatible **1.x** on each **`pip install -e ".[dev]"`**. Policy and integrator pinning: **[docs/SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md](SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md)**; audit context: **[docs/DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md)**. |
| **replayt** | **Not** a runtime dependency unless a backlog promotes it. **Dev / CI** lower bound on the **`dev`** extra; boundary and minimum version in **[SPEC_REPLAYT_INTEGRATION_TESTS.md](SPEC_REPLAYT_INTEGRATION_TESTS.md)** §7. |

When pins or CI versions change, update **`COMPATIBILITY.md`** in the same maintenance pass as **`pyproject.toml`** and **`CI_SPEC.md`** (reference fingerprint).

## Audience

| Audience | Needs |
| -------- | ----- |
| **Maintainers** | This file, **[CI_SPEC.md](CI_SPEC.md)**, **`DEPENDENCY_AUDIT.md`**, **[SPEC_FIRST_ALPHA_RELEASE.md](SPEC_FIRST_ALPHA_RELEASE.md)** (alpha / publish checklist), **[ROADMAP.md](ROADMAP.md)** / **[SPEC_BETA_AND_STABLE_PROMOTION.md](SPEC_BETA_AND_STABLE_PROMOTION.md)** (beta / stable / semver), release notes in **[CHANGELOG.md](../CHANGELOG.md)** |
| **Integrators** | Stable adapter surface, **[COMPATIBILITY.md](COMPATIBILITY.md)**, **[SPEC_OTEL_EXPORTER_SKELETON.md](SPEC_OTEL_EXPORTER_SKELETON.md)**, README overview; when using approval / audit hooks, **[RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md](RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md)** |
| **Governance / compliance** (when applicable) | **[SPEC_SPAN_EXPORT_APPROVAL_UX.md](SPEC_SPAN_EXPORT_APPROVAL_UX.md)** audit allow-list, **[RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md](RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md)** (sink-friendly patterns), **[SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)** redaction, **[SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)** triage fields |
| **Contributors** | README quick start, specs under **`docs/`**, optional **`docs/reference-documentation/`** per **[SPEC_REFERENCE_DOCUMENTATION.md](SPEC_REFERENCE_DOCUMENTATION.md)**, tests under **`tests/`** |

Extend audience rows in **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** when new stakeholder types appear.

## LLM and demos

This package is **not** an LLM runtime. Any demos or agent tooling that mention models, secrets, cost, or redaction MUST follow **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** § LLM / demos and stay consistent with **[SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)** and **[SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)** for logging and attribute handling.
