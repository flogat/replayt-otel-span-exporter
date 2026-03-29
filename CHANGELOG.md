# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Documentation

- **Export failure logging (spec audit):** **[docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)** — backlog **“Audit exporter logging for injection and oversized fields on failure paths”**, phase **2** spec: normative **`attribute_key_is_sensitive`** alignment for key checks (**§5.1**), untrusted exception / span-name handling (**§5.2**), **§5.4** truncation (**1024** / **256** code points) and **C0 / C1** control stripping, expanded **§6** test contract (items **4–6**) and **§7** checklist; cross-links from **[docs/SPEC_EXPORT_TRIAGE_METADATA.md](docs/SPEC_EXPORT_TRIAGE_METADATA.md)** **§3.4**, **[docs/CI_SPEC.md](docs/CI_SPEC.md)** §5, and **[docs/MISSION.md](docs/MISSION.md)** spec-to-suite mapping.

- **Integrator cookbook (approval / audit hooks):** **[docs/RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md](docs/RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md)** — async-safe hook usage, idempotency for audit emission, allow-list-only forwarding to integrator sinks (no full **`PreparedSpanRecord`** / attribute maps). **[docs/SPEC_SPAN_EXPORT_APPROVAL_UX.md](docs/SPEC_SPAN_EXPORT_APPROVAL_UX.md)** **§7**, **§9**, **§10** and **[docs/MISSION.md](docs/MISSION.md)** scope table / audience rows cross-link the recipe (backlog **“Integrator cookbook: on_export_commit and on_export_audit in production”**, phase **2** spec). **[README.md](README.md)** links the recipe from the overview, optional hook subsection, and project layout (phase **3** build).

- **Integrator cookbook (follow-up):** **[docs/RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md](docs/RECIPE_SPAN_EXPORT_HOOKS_PRODUCTION.md)** — **`on_export_audit`** only runs when **`on_export_commit`** is set; scheduling note for hooks on the SDK worker thread vs **`loop.call_soon_threadsafe`**; points integrators at **`ExportAuditEvent`**. **[docs/DESIGN_PRINCIPLES.md](docs/DESIGN_PRINCIPLES.md)** audience table and **[docs/CI_SPEC.md](docs/CI_SPEC.md)** §5 reference the recipe (same backlog, phase **5** architect).

- **Replayt boundary hardening (spec):** **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](docs/SPEC_REPLAYT_INTEGRATION_TESTS.md)** — backlog **“Strengthen replayt boundary tests for pin bumps and contract drift”**, phase **2**: CI pin-bump validation (**§5.1**), import-surface and **`PreparedSpanRecord`** → replayt payload contracts (**§4.4–§4.6**), collection reliability under **`pip install -e ".[dev]"`** (**§3**), expanded §6 checklist; cross-links from **[docs/CI_SPEC.md](docs/CI_SPEC.md)** §5, **[docs/COMPATIBILITY.md](docs/COMPATIBILITY.md)** §6, and **[docs/MISSION.md](docs/MISSION.md)** spec-to-suite mapping.

### Changed

- **Replayt boundary tests:** **`tests/integration/test_replayt_boundary.py`** asserts the §4.5 payload (keys, types, and isolated **`attributes`** mapping), uses **`LogMode.redacted`** on **`Runner`**, and adds **`test_installed_replayt_satisfies_pyproject_lower_bound`** (§4.6). **`pyproject.toml`** **`[project.optional-dependencies].dev`** includes **`packaging>=23.2`** for specifier parsing (**[docs/DEPENDENCY_AUDIT.md](docs/DEPENDENCY_AUDIT.md)**). Same backlog as the spec bullet above (build + phase **5** architecture review).
- **CI:** **`test`** and **`supply-chain`** jobs in **`.github/workflows/ci.yml`** run on **Python 3.13** as well as **3.11** and **3.12** (backlog **“Expand CI matrix to Python 3.13 with documented compatibility fingerprint”**, phase **3** build). **`tests/test_compatibility_contract.py`**, **[README.md](README.md)** (CI summary), **[docs/COMPATIBILITY.md](docs/COMPATIBILITY.md)** §2 / §4 / §4.1.1, **[docs/CI_SPEC.md](docs/CI_SPEC.md)** reference fingerprint, **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](docs/SPEC_REPLAYT_INTEGRATION_TESTS.md)** §6, and **[docs/MISSION.md](docs/MISSION.md)** matrix summary match the expanded matrix.

### Documentation

- **Python 3.13 CI matrix (spec):** **[docs/CI_SPEC.md](docs/CI_SPEC.md)** §3.1 — normative acceptance criteria for adding **3.13** to **`test`** / **`supply-chain`**, **`pip-audit`** / **DEPENDENCY_AUDIT** alignment, **COMPATIBILITY** fingerprint, and **`tests/test_compatibility_contract.py`**; **[docs/COMPATIBILITY.md](docs/COMPATIBILITY.md)** §4.1 — **3.13** notes; cross-links from **[docs/MISSION.md](docs/MISSION.md)** and **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](docs/SPEC_REPLAYT_INTEGRATION_TESTS.md)** §6 (backlog **“Expand CI matrix to Python 3.13 with documented compatibility fingerprint”**, phase **2** spec).

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
