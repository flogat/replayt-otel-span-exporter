# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **`.github/workflows/release.yml`**: optional **PyPI** publish via **OIDC** (trusted publishing): guarded **`workflow_dispatch`** and **`v*`** tag pushes, GitHub Environment **`pypi`**, **`python -m build`** + **`twine check`**, build-tooling-only install (no **`[dev]`**), **`pypa/gh-action-pypi-publish`**. Documented in **[docs/CI_SPEC.md](docs/CI_SPEC.md)** §8 Reference fingerprint.
- **`tests/test_release_workflow_contract.py`**: asserts **`release.yml`** matches **§8** (triggers, permissions, environment name, build/twine steps, no dev install).
- **`tests/test_readme_integrator_install.py`**: README **`pip install replayt-otel-span-exporter==<version>`** matches **`[project].version`**, documents **`--pre`** for alphas, and **`[project].readme`** is set (**[docs/SPEC_README_QUICK_START.md](docs/SPEC_README_QUICK_START.md)** §2.1).
- **`tests/test_release_packaging.py`**: after **`python -m build`** and **`twine check`**, installs the built wheel into a **fresh venv** and asserts **`importlib.metadata`**, **`__version__`**, and **no `replayt`** on the minimal install path (per that spec §4–§5).
- **`scripts/verify_published_release.sh`**: maintainer helper for post-upload **§5** verification against PyPI or **`INDEX_URL`**.

### Changed

- **`[project].readme`** in **`pyproject.toml`** points at **`README.md`** so sdist/wheel metadata includes the long description (cleaner **`twine check`**).
- **`tests/test_release_metadata.py`**: asserts **CHANGELOG** has a dated **`## [<version>] - YYYY-MM-DD`** heading matching **`[project].version`** and a **`[Unreleased]`** section (per that spec §3).

### Documentation

- **[README.md](README.md)** quick start for integrators: PyPI project link, pinned **`==0.2.0a1`** install matching **[docs/SPEC_FIRST_ALPHA_RELEASE.md](docs/SPEC_FIRST_ALPHA_RELEASE.md)** §5, **`--pre`** note for prereleases, and honest wording when the index does not list the build yet.
- **[docs/COMPATIBILITY.md](docs/COMPATIBILITY.md)** §2 ties published-metadata expectations to the **`0.2.0a1`** changelog line and pre-index source of truth.
- **[docs/CI_SPEC.md](docs/CI_SPEC.md)** §5 lists **`tests/test_readme_integrator_install.py`** next to README release-adjacent tests.
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
