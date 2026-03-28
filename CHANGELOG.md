# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **`tests/test_release_packaging.py`**: after **`python -m build`** and **`twine check`**, installs the built wheel into a **fresh venv** and asserts **`importlib.metadata`**, **`__version__`**, and **no `replayt`** on the minimal install path (per that spec §4–§5).
- **`scripts/verify_published_release.sh`**: maintainer helper for post-upload **§5** verification against PyPI or **`INDEX_URL`**.

### Changed

- **`tests/test_release_metadata.py`**: asserts **CHANGELOG** has a dated **`## [<version>] - YYYY-MM-DD`** heading matching **`[project].version`** and a **`[Unreleased]`** section (per that spec §3).

### Documentation

- **[docs/CI_SPEC.md](docs/CI_SPEC.md)** §5 lists **`tests/test_release_packaging.py`** next to release metadata tests.
- Refined **[docs/SPEC_FIRST_ALPHA_RELEASE.md](docs/SPEC_FIRST_ALPHA_RELEASE.md)** for the **Publish first alpha release** backlog: expanded testable acceptance criteria ([§0](docs/SPEC_FIRST_ALPHA_RELEASE.md#0-testable-acceptance-criteria-expanded-backlog-wording)), **`__version__`** / **`importlib.metadata`** alignment with **`[project].version`**, recommended **`twine check`**, private-index install example, **`--pre`** note for integrators, [§5.1](docs/SPEC_FIRST_ALPHA_RELEASE.md#51-ci-and-suite-health-informative) CI vs **§5** verification scope, and checklist updates.

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
