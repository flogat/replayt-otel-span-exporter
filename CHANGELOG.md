# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- **`tests/integration/test_replayt_boundary.py`:** §4.6 reads the **`replayt`** line from **`[project.optional-dependencies].dev`** by **normalized** dependency name (**`replayt`**), requires **exactly one** such line, and still compares **`importlib.metadata.version("replayt")`** with **`Requirement.specifier.contains(..., prereleases=True)`** (no second hard-coded minimum). Backlog **“Integration test: replayt pin drift and boundary failure modes”** (`da6412b4-2b98-44cf-82a1-70fbc12c777c`), phase **3**.

### Documentation

- **Replayt integration tests (spec):** **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](docs/SPEC_REPLAYT_INTEGRATION_TESTS.md)** — backlog **“Integration test: replayt pin drift and boundary failure modes”** (`da6412b4-2b98-44cf-82a1-70fbc12c777c`), phase **2**: traceability table and normative **Builder acceptance summary**; **§4.6** promoted to **MUST** (installed **`replayt`** vs **`pyproject.toml`** **`dev`** specifier, single source of truth); **§8** failure-mode / **`pytest`** diagnostics (collection exit **2** vs per-test signals); checklist **§6** aligned. **[docs/COMPATIBILITY.md](docs/COMPATIBILITY.md)** §6 — **Pin bump proof** cross-links **§8**.

- **Python 3.13 CI matrix (spec):** **[docs/CI_SPEC.md](docs/CI_SPEC.md)** §3.1 — Mission Control backlog **`4a00b7f7-af4e-4200-9d28-38e3827fa2e5`** (**Expand CI matrix to Python 3.13 with documented policy**), phase **2**: traceability id in backlog tables; **structural vs green CI** clarification (workflow + **`tests/test_compatibility_contract.py`** vs **`test`** / **`supply-chain`** success including **`tests/integration/test_replayt_boundary.py`**); tightened **Blocked** paragraph (single change set for **`ci.yml`**, fingerprint, contract test, **COMPATIBILITY**). **[docs/COMPATIBILITY.md](docs/COMPATIBILITY.md)** §4.1.1 (**pip-audit** 3.13-only ignores) and **§4.1.2** (deferring / removing a matrix Python). **[docs/DEPENDENCY_AUDIT.md](docs/DEPENDENCY_AUDIT.md)** — matrix-wide **`pip-audit`** context. **[docs/MISSION.md](docs/MISSION.md)** — **Python matrix maintenance** bullet → §3.1 / §4.1.2.

- **Reference documentation (spec):** **[docs/SPEC_REFERENCE_DOCUMENTATION.md](docs/SPEC_REFERENCE_DOCUMENTATION.md)** — backlog **“Seed `docs/reference-documentation/` with replayt + OTel snapshot markdown”**, phase **2**: backlog traceability for Mission Control item **dda05c31-9820-45d0-9e56-e58625f1686f**; **§4.3** stub-only index files vs optional verbatim snapshots and coupling to **`tests/test_reference_documentation.py`**; **§9.0** testable acceptance checklist; directory presence rule aligned with two index files (**§2**). **[docs/CI_SPEC.md](docs/CI_SPEC.md)** §5 — pointer to **§9.0** / **§4.3**.

- **Reference documentation (spec / CI text):** **[docs/SPEC_REFERENCE_DOCUMENTATION.md](docs/SPEC_REFERENCE_DOCUMENTATION.md)** §8 and **[docs/CI_SPEC.md](docs/CI_SPEC.md)** §5 — root **README** §7 included in **`tests/test_reference_documentation.py`** contract. Backlog **dda05c31-9820-45d0-9e56-e58625f1686f**, phase **3**.

- **Reference documentation (spec, §7):** **[docs/SPEC_REFERENCE_DOCUMENTATION.md](docs/SPEC_REFERENCE_DOCUMENTATION.md)** §7 and **§9.0** — project layout rows now name **`docs/reference-documentation/`** and **`docs/SPEC_REFERENCE_DOCUMENTATION.md`**, matching **`tests/test_reference_documentation.py`** and the root **README**. Backlog **“Seed `docs/reference-documentation/` with replayt + OTel snapshot markdown”** (**dda05c31-9820-45d0-9e56-e58625f1686f**), phase **5** (architecture review).

- **Optional PyPI trusted publishing (spec):** **[docs/CI_SPEC.md](docs/CI_SPEC.md)** §8 — backlog **“Add optional GitHub Actions trusted publishing for PyPI”**, phase **2**: backlog traceability table, normative **[§8.0](docs/CI_SPEC.md#80-testable-acceptance-criteria-normative-backlog)** acceptance checklist (guarded **`workflow_dispatch`** / **`v*`** tags, **`python -m build`**, **`twine check`**, OIDC **`id-token`**, GitHub Environment **`pypi`**, no long-lived PyPI tokens or embedded passwords in-repo for the default path). Cross-links from **[docs/SPEC_FIRST_ALPHA_RELEASE.md](docs/SPEC_FIRST_ALPHA_RELEASE.md)** (related backlog) and **[docs/ROADMAP.md](docs/ROADMAP.md)** (backlog traceability). **§8.3** clarifies credential posture.

- **Optional PyPI trusted publishing (spec, §8.0 item 2):** §8.0 item **2** requires the **`publish`** job id in **`release.yml`**, matching **`tests/test_release_workflow_contract.py`** (phase **5** architecture review).

- **Beta / 1.0 promotion and API stability (spec):** **[docs/SPEC_BETA_AND_STABLE_PROMOTION.md](docs/SPEC_BETA_AND_STABLE_PROMOTION.md)** — backlog **“Define beta/1.0 promotion criteria and public API stability promises”**, phase **2**: normative **beta** and **1.0** promotion checklists (after **[docs/SPEC_FIRST_ALPHA_RELEASE.md](docs/SPEC_FIRST_ALPHA_RELEASE.md)** §5 index verification), **SemVer** tables for **`PreparedSpanRecord`** and **`ReplaytSpanExporter`**, **CHANGELOG** discipline for majors / deprecations, optional **hook** evolution (**§5**). **[docs/ROADMAP.md](docs/ROADMAP.md)** — release phase summary for maintainers and Mission Control. Cross-links from **[docs/MISSION.md](docs/MISSION.md)** (scope, success criteria, audience), **[docs/SPEC_FIRST_ALPHA_RELEASE.md](docs/SPEC_FIRST_ALPHA_RELEASE.md)** §8, **[docs/DESIGN_PRINCIPLES.md](docs/DESIGN_PRINCIPLES.md)** Releases, **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](docs/SPEC_OTEL_EXPORTER_SKELETON.md)** reference naming, **[docs/SPEC_SPAN_EXPORT_APPROVAL_UX.md](docs/SPEC_SPAN_EXPORT_APPROVAL_UX.md)**; **[README.md](README.md)** overview. Phase **3** intro clarifies **`tests/test_beta_stable_promotion_docs.py`** (heading/link smoke) vs optional automated §2 gates.

- **Runnable `scripts/` demo (spec):** **[docs/SPEC_SCRIPTS_OTEL_PREPARED_DEMO.md](docs/SPEC_SCRIPTS_OTEL_PREPARED_DEMO.md)** — backlog **“Ship a runnable scripts/ demo beyond the README snippet test harness”**, phase **2**: normative contract for **`scripts/otel_to_prepared_demo.py`** (TracerProvider + **`replayt.workflow_id`** / **`replayt.step_id`**, printed **`PreparedSpanRecord`** fields, no **`replayt`** import), documentation surfaces (README and/or **`scripts/README.md`**), subprocess-friendly CI test bar (**`tests/test_scripts_otel_prepared_demo.py`**). Cross-links from **[docs/MISSION.md](docs/MISSION.md)** (scope table, spec-to-suite mapping, success criteria), **[docs/CI_SPEC.md](docs/CI_SPEC.md)** §5, **[docs/SPEC_README_QUICK_START.md](docs/SPEC_README_QUICK_START.md)** related contracts, **[docs/DESIGN_PRINCIPLES.md](docs/DESIGN_PRINCIPLES.md)** observable automation.

### Added

- **`tests/test_reference_documentation.py`:** root **README.md** §7 checks (**Reference documentation** section + project layout rows for **`docs/reference-documentation/`** and **`docs/SPEC_REFERENCE_DOCUMENTATION.md`**). Backlog **“Seed docs/reference-documentation/ with replayt + OTel snapshot markdown”** (**dda05c31-9820-45d0-9e56-e58625f1686f**), phase **3**.

- **`tests/test_release_workflow_contract.py`:** extended assertions for **`docs/CI_SPEC.md`** §8.0 / **`release.yml`** — **`publish`** job id, **`rm -rf dist`**, **`python -m pip install --upgrade pip`**, **concurrency** group string, and OIDC path **without** repository PyPI token / **`password: ${{ secrets.`** wiring. **[docs/CI_SPEC.md](docs/CI_SPEC.md)** §8.0 item **10** lists the contract. Backlog **“Add optional GitHub Actions trusted publishing for PyPI”**, phase **3**.

- **`tests/test_beta_stable_promotion_docs.py`:** default **`pytest`** smoke for **`docs/SPEC_BETA_AND_STABLE_PROMOTION.md`** (§2–§5 headings, semver tables) and **`docs/ROADMAP.md`** (links to **MISSION** and **first alpha** spec). Recorded in **[docs/CI_SPEC.md](docs/CI_SPEC.md)** §5. Backlog **“Define beta/1.0 promotion criteria and public API stability promises”**, phase **3**.

- **`scripts/otel_to_prepared_demo.py`** and **`scripts/README.md`:** runnable OpenTelemetry → **`PreparedSpanRecord`** demo (**`replayt.workflow_id`** / **`replayt.step_id`**, labeled stdout); no **`replayt`** import. **`tests/test_scripts_otel_prepared_demo.py`** runs the script in a subprocess (exit **0** + field checks). Spec: **[docs/SPEC_SCRIPTS_OTEL_PREPARED_DEMO.md](docs/SPEC_SCRIPTS_OTEL_PREPARED_DEMO.md)**; backlog **“Ship a runnable scripts/ demo beyond the README snippet test harness”**, phase **3**.
- **`tests/test_compatibility_contract.py`:** asserts runtime **`opentelemetry-api`** / **`opentelemetry-sdk`** specifiers contain **no** **`<`** upper bound and that **[docs/COMPATIBILITY.md](docs/COMPATIBILITY.md)** and **[docs/DEPENDENCY_AUDIT.md](docs/DEPENDENCY_AUDIT.md)** link **[docs/SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md](docs/SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md)** (backlog **“Document OpenTelemetry upper-bound or float policy in pyproject and COMPATIBILITY”**, phase **3**). **Expand CI matrix to Python 3.13 with documented policy** (**`4a00b7f7-af4e-4200-9d28-38e3827fa2e5`**), phase **3**: asserts **[docs/CI_SPEC.md](docs/CI_SPEC.md)** **Reference fingerprint** documents the same **`python-version`** set as **`_EXPECTED_CI_PYTHON_VERSIONS`** / **`.github/workflows/ci.yml`**.

### Documentation

- **OpenTelemetry dependency policy:** **[docs/SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md](docs/SPEC_OPENTELEMETRY_DEPENDENCY_POLICY.md)** — backlog **“Document OpenTelemetry upper-bound or float policy in pyproject and COMPATIBILITY”**, phase **2**: lower bounds only (no runtime upper cap), how default **CI** observes new **1.x** releases via floating **`pip`** resolution, integrator pinning (**API** + **SDK** together). Updates **[docs/COMPATIBILITY.md](docs/COMPATIBILITY.md)** §2–§3 (**§3.1** float policy), **[docs/DEPENDENCY_AUDIT.md](docs/DEPENDENCY_AUDIT.md)** § Runtime, **[docs/CI_SPEC.md](docs/CI_SPEC.md)** §4 + backlog traceability, **[docs/MISSION.md](docs/MISSION.md)** compatibility summary; **`pyproject.toml`** comments on runtime OTel deps.

### Changed

- **Export failure logging:** Exception messages and span names in **`ReplaytSpanExporter`** failure logs are **C0 / C1 control-stripped** (replaced with spaces) and **truncated** to **1024** and **256** Unicode code points respectively, with matching **`exc_message`** / **`span_name`** string fields in log **`extra`**; see **[docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)** §5.4. Backlog **“Audit exporter logging for injection and oversized fields on failure paths”**, phase **3** build.

### Documentation

- **Export failure logging (spec audit):** **[docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)** — backlog **“Audit exporter logging for injection and oversized fields on failure paths”**, phase **2** spec: normative **`attribute_key_is_sensitive`** alignment for key checks (**§5.1**), untrusted exception / span-name handling (**§5.2**), **§5.4** truncation (**1024** / **256** code points) and **C0 / C1** control stripping, expanded **§6** test contract (items **4–6**) and **§7** checklist; cross-links from **[docs/SPEC_EXPORT_TRIAGE_METADATA.md](docs/SPEC_EXPORT_TRIAGE_METADATA.md)** **§3.4**, **[docs/CI_SPEC.md](docs/CI_SPEC.md)** §5, and **[docs/MISSION.md](docs/MISSION.md)** spec-to-suite mapping.

- **Integrator cookbook (approval / audit hooks):** **[docs/RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md](docs/RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md)** — async-safe hook usage, idempotency for audit emission, allow-list-only forwarding to integrator sinks (no full **`PreparedSpanRecord`** / attribute maps). **[docs/SPEC_SPAN_EXPORT_APPROVAL_UX.md](docs/SPEC_SPAN_EXPORT_APPROVAL_UX.md)** **§7**, **§9**, **§10** and **[docs/MISSION.md](docs/MISSION.md)** scope table / audience rows cross-link the recipe (backlog **“Integrator cookbook: on_export_commit and on_export_audit in production”**, phase **2** spec). **[README.md](README.md)** links the recipe from the overview, optional hook subsection, and project layout (phase **3** build).

- **Integrator cookbook (follow-up):** **[docs/RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md](docs/RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md)** — **`on_export_audit`** only runs when **`on_export_commit`** is set; scheduling note for hooks on the SDK worker thread vs **`loop.call_soon_threadsafe`**; points integrators at **`ExportAuditEvent`**. **[docs/DESIGN_PRINCIPLES.md](docs/DESIGN_PRINCIPLES.md)** audience table and **[docs/CI_SPEC.md](docs/CI_SPEC.md)** §5 reference the recipe (same backlog, phase **5** architect).

- **Replayt boundary hardening (spec):** **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](docs/SPEC_REPLAYT_INTEGRATION_TESTS.md)** — backlog **“Strengthen replayt boundary tests for pin bumps and contract drift”**, phase **2**: CI pin-bump validation (**§5.1**), import-surface and **`PreparedSpanRecord`** → replayt payload contracts (**§4.4–§4.6**), collection reliability under **`pip install -e ".[dev]"`** (**§3**), expanded §6 checklist; cross-links from **[docs/CI_SPEC.md](docs/CI_SPEC.md)** §5, **[docs/COMPATIBILITY.md](docs/COMPATIBILITY.md)** §6, and **[docs/MISSION.md](docs/MISSION.md)** spec-to-suite mapping.

### Changed

- **Replayt boundary tests:** **`tests/integration/test_replayt_boundary.py`** asserts the §4.5 payload (keys, types, and isolated **`attributes`** mapping), uses **`LogMode.redacted`** on **`Runner`**, and adds **`test_installed_replayt_satisfies_pyproject_lower_bound`** (§4.6). **`pyproject.toml`** **`[project.optional-dependencies].dev`** includes **`packaging>=23.2`** for specifier parsing (**[docs/DEPENDENCY_AUDIT.md](docs/DEPENDENCY_AUDIT.md)**). Same backlog as the spec bullet above (build + phase **5** architecture review).
- **CI:** **`test`** and **`supply-chain`** jobs in **`.github/workflows/ci.yml`** run on **Python 3.13** as well as **3.11** and **3.12** (backlog **“Expand CI matrix to Python 3.13 with documented policy”**, phase **3** build). **`tests/test_compatibility_contract.py`**, **[README.md](README.md)** (CI summary), **[docs/COMPATIBILITY.md](docs/COMPATIBILITY.md)** §2 / §4 / §4.1.1, **[docs/CI_SPEC.md](docs/CI_SPEC.md)** reference fingerprint, **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](docs/SPEC_REPLAYT_INTEGRATION_TESTS.md)** §6, and **[docs/MISSION.md](docs/MISSION.md)** matrix summary match the expanded matrix.

### Documentation

- **`docs/reference-documentation/`**: folder **README** (licensing, scope, refresh policy) plus stub indexes **[opentelemetry-python.md](docs/reference-documentation/opentelemetry-python.md)** and **[replayt.md](docs/reference-documentation/replayt.md)** with canonical **`https://`** links and maintainer summaries (backlog **“Populate `docs/reference-documentation/` for offline replayt and OTel context”**, phase **3** build).
- **[README.md](README.md)**: **Reference documentation** section states the tree is present; project layout table row updated for **`docs/reference-documentation/`**.
- **[docs/SPEC_REFERENCE_DOCUMENTATION.md](docs/SPEC_REFERENCE_DOCUMENTATION.md)**: backlog **“Populate `docs/reference-documentation/` for offline replayt and OTel context”** — normative contract for optional stub indexes, bounded snapshots, folder **README** (licensing, scope, refresh policy), size bounds, and acceptance checklists (phase **2** spec).

### Added

- **`tests/test_reference_documentation.py`**: contract checks for the reference-documentation folder **README**, stub pages, **`https://`** links, and total tree size vs **[docs/SPEC_REFERENCE_DOCUMENTATION.md](docs/SPEC_REFERENCE_DOCUMENTATION.md)** guidance.
- **`.github/workflows/release.yml`**: optional **PyPI** publish via **OIDC** (trusted publishing): guarded **`workflow_dispatch`** and **`v*`** tag pushes, GitHub Environment **`pypi`**, **`python -m build`** + **`twine check`**, build-tooling-only install (no **`[dev]`**), **`pypa/gh-action-pypi-publish`** pinned to commit **`ed0c539`**. Documented in **[docs/CI_SPEC.md](docs/CI_SPEC.md)** §8 Reference fingerprint.
- **`tests/test_release_workflow_contract.py`**: asserts **`release.yml`** matches **§8** (triggers, permissions, environment name, build/twine steps, no dev install) and **`docs/CI_SPEC.md`** contains normative **§8** subsections (OIDC, environment **`pypi`**, rollback).
- **`tests/test_readme_integrator_install.py`**: README **`pip install replayt-otel-span-exporter==<version>`** matches **`[project].version`**, documents **`--pre`** for alphas, and **`[project].readme`** is set (**[docs/SPEC_README_QUICK_START.md](docs/SPEC_README_QUICK_START.md)** §2.1).
- **`tests/test_release_packaging.py`**: after **`python -m build`** and **`twine check`**, installs the built wheel into a **fresh venv** and asserts **`importlib.metadata`**, **`__version__`**, and **no `replayt`** on the minimal install path (per that spec §4–§5).
- **`scripts/verify_published_release.sh`**: maintainer helper for post-upload **§5** verification against PyPI or **`INDEX_URL`**.

### Changed

- **[docs/MISSION.md](docs/MISSION.md)** spec-to-suite bullet and **[docs/SPEC_REFERENCE_DOCUMENTATION.md](docs/SPEC_REFERENCE_DOCUMENTATION.md)** section 8 now match **[docs/CI_SPEC.md](docs/CI_SPEC.md)** §5: default **`pytest`** runs **`tests/test_reference_documentation.py`** (local checks only; phase **5** architecture review).
- **[docs/CI_SPEC.md](docs/CI_SPEC.md)** §5 documents **`tests/test_reference_documentation.py`** and the **`docs/reference-documentation/`** tree alongside default **`pytest`** discovery.
- **`[project].readme`** in **`pyproject.toml`** points at **`README.md`** so sdist/wheel metadata includes the long description (cleaner **`twine check`**).
- **`tests/test_release_metadata.py`**: asserts **CHANGELOG** has a dated **`## [<version>] - YYYY-MM-DD`** heading matching **`[project].version`** and a **`[Unreleased]`** section (per that spec §3).

### Documentation

- **[README.md](README.md)** quick start for integrators: PyPI project link, pinned **`==0.2.0a1`** install matching **[docs/SPEC_FIRST_ALPHA_RELEASE.md](docs/SPEC_FIRST_ALPHA_RELEASE.md)** §5, **`--pre`** note for prereleases, and honest wording when the index does not list the build yet.
- **[docs/COMPATIBILITY.md](docs/COMPATIBILITY.md)** §2 ties published-metadata expectations to the **`0.2.0a1`** changelog line and pre-index source of truth.
- **[docs/CI_SPEC.md](docs/CI_SPEC.md)** §5 lists **`tests/test_readme_integrator_install.py`** next to README release-adjacent tests.
- **[docs/CI_SPEC.md](docs/CI_SPEC.md)** §8 (optional **`release.yml`** / OIDC): operator-facing subsections for triggers, build + **`twine check`**, GitHub Environment **`pypi`**, PyPI trusted publisher alignment, OIDC vs private-index secrets, **`replayt`** / publish-runner install policy, optional **TestPyPI** note, rollback table, and maintainer expectations.
- **[README.md](README.md)** **Continuous integration** and **[docs/MISSION.md](docs/MISSION.md)** spec-to-suite row point maintainers to **[docs/CI_SPEC.md](docs/CI_SPEC.md)** §8 and **`release.yml`** for optional OIDC publishing.
- Refined **[docs/SPEC_FIRST_ALPHA_RELEASE.md](docs/SPEC_FIRST_ALPHA_RELEASE.md)** for the **Publish first alpha release** backlog: expanded testable acceptance criteria ([§0](docs/SPEC_FIRST_ALPHA_RELEASE.md#0-testable-acceptance-criteria-expanded-backlog-wording)), **`__version__`** / **`importlib.metadata`** alignment with **`[project].version`**, recommended **`twine check`**, private-index install example, **`--pre`** note for integrators, [§5.1](docs/SPEC_FIRST_ALPHA_RELEASE.md#51-ci-and-suite-health-informative) CI vs **§5** verification scope, and checklist updates.
- Phase **2** spec pass (**Close first alpha**): **[docs/SPEC_FIRST_ALPHA_RELEASE.md](docs/SPEC_FIRST_ALPHA_RELEASE.md)** — follow-on backlog traceability, §0.1 testable mapping, normative **`python -m build`** / **`twine check`** before upload ([§4](docs/SPEC_FIRST_ALPHA_RELEASE.md#4-publishing-target-normative)), [§5.2](docs/SPEC_FIRST_ALPHA_RELEASE.md#52-release-handoff-record-normative) release handoff fields, §6 README pin guidance; **[docs/SPEC_README_QUICK_START.md](docs/SPEC_README_QUICK_START.md)** §2.1 version-pin rule; **[docs/COMPATIBILITY.md](docs/COMPATIBILITY.md)** §6 checklist item for published distribution; **[docs/MISSION.md](docs/MISSION.md)** success criterion cross-link.

## [0.2.0a1] - 2026-03-28

First **PEP 440 alpha** prerelease of the OpenTelemetry → replayt-prep bridge. **`replayt`** stays on the **`dev`** extra only; runtime deps remain **`opentelemetry-api`** and **`opentelemetry-sdk`**. Publish with **`python -m build`** and **`twine upload`**, then run **[docs/SPEC_FIRST_ALPHA_RELEASE.md](docs/SPEC_FIRST_ALPHA_RELEASE.md)** §5 verification. Backlog **“Publish first alpha release”** (phase **3** build): **`[project].version`** / **`__version__`** set to **`0.2.0a1`**; **`tests/test_release_metadata.py`** guards the alpha version shape; **`tests/test_init.py`** ties **`__version__`** to **`pyproject.toml`** and **`importlib.metadata`**.

### Added

- **`ReplaytSpanExporter`** and **`PreparedSpanRecord`** IR with optional **`on_export_commit`** / **`on_export_audit`** hooks per **[docs/SPEC_SPAN_EXPORT_APPROVAL_UX.md](docs/SPEC_SPAN_EXPORT_APPROVAL_UX.md)**.
- Triage fields **`workflow_id`** / **`step_id`** and sensitive-attribute **`[REDACTED]`** handling per **[docs/SPEC_EXPORT_TRIAGE_METADATA.md](docs/SPEC_EXPORT_TRIAGE_METADATA.md)**.
- Export failure logging and all-or-nothing batch append semantics per **[docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)**.
- Integration tests: **`tests/integration/test_replayt_boundary.py`** (**`replayt`** boundary), **`tests/integration/test_opentelemetry_api_usage.py`**; **`tests/test_compatibility_contract.py`** for docs/CI alignment with pins; README usage pipeline (**`tests/test_readme_usage_example.py`**, **`tests/readme_usage_example_snippet.py`** per **[docs/SPEC_README_QUICK_START.md](docs/SPEC_README_QUICK_START.md)**).
- Specs and cross-links under **`docs/`** (mission, CI, compatibility, exporter skeleton, integration tests, first-alpha release, dependency audit).

### Changed

- **`ReplaytSpanExporter.export`:** failed batches do not leave partial appends in the buffer.
- **`dev`** optional extra includes **`replayt>=0.4.25`**, **`requests>=2.33.0`** (supply-chain graph); GitHub Actions **`permissions: contents: read`**, Python **3.11** / **3.12** matrix, Codecov **`fail_ci_if_error: false`**.

### Documentation

- **[docs/MISSION.md](docs/MISSION.md)**, **[docs/COMPATIBILITY.md](docs/COMPATIBILITY.md)**, **[docs/CI_SPEC.md](docs/CI_SPEC.md)**, **[docs/SPEC_FIRST_ALPHA_RELEASE.md](docs/SPEC_FIRST_ALPHA_RELEASE.md)**, **[README.md](README.md)**, and related specs as linked from the mission scope table.

## [0.1.0] - 2026-03-25

### Added

- Initial scaffold and package layout.
