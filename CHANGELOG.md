# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Integration test under `tests/integration/` exercising the OpenTelemetry trace API.
- CI pipeline specification and testable acceptance criteria in `docs/CI_SPEC.md`.
- `pytest-cov` in dev extras so CI coverage matches local installs.
- Dependency smoke test for OpenTelemetry API imports.

### Changed

- Codecov upload step uses `fail_ci_if_error: false` so token or fork limitations do not fail CI.
- GitHub Actions test job Python matrix aligned with `requires-python` (3.11 and 3.12).
- README CI section names the workflow file, branch triggers, and Python versions used in CI.

## [0.1.0] - 2026-03-25

### Added

- Initial scaffold and package layout.
