# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- CI pipeline specification and testable acceptance criteria in `docs/CI_SPEC.md`.
- `pytest-cov` in dev extras so CI coverage matches local installs.
- Dependency smoke test for OpenTelemetry API imports.

### Changed

- GitHub Actions test job Python matrix aligned with `requires-python` (3.11 and 3.12).

## [0.1.0] - 2026-03-25

### Added

- Initial scaffold and package layout.
