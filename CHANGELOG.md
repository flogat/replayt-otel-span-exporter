# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Documentation

- Backlog **“Add replayt integration tests”** (spec phase 2): new Builder contract `docs/SPEC_REPLAYT_INTEGRATION_TESTS.md` (replayt boundary definition, minimum scenarios, optional-deps policy, §6 checklist, §7 API anchor to fill on implementation). Cross-links and CI expectations in `docs/CI_SPEC.md`, `docs/MISSION.md` (compatibility matrix + scope exception), `docs/SPEC_OTEL_EXPORTER_SKELETON.md` (non-goals clarification), `docs/DEPENDENCY_AUDIT.md` (placeholder test/integration row), and `README.md` layout.
- Refined exporter skeleton spec (phase 2): canonical names (`ReplaytSpanExporter`, `PreparedSpanRecord`, `__all__`), aligned dependency wording with `pyproject.toml`, exporter threading/shutdown/`SpanExportResult` semantics, IR edge cases, expanded test contract, and §6 verifiable acceptance checklist in `docs/SPEC_OTEL_EXPORTER_SKELETON.md`; `docs/CI_SPEC.md` references the checklist.
- Mission and positioning filled in `docs/MISSION.md` and `docs/REPLAYT_ECOSYSTEM_IDEA.md` (framework-bridge pattern).
- Builder contract for the OpenTelemetry span exporter skeleton: `docs/SPEC_OTEL_EXPORTER_SKELETON.md` (public API, prepared-span IR, test expectations, `opentelemetry-sdk` dependency note).
- README links the exporter spec alongside mission and ecosystem docs.
- `docs/DEPENDENCY_AUDIT.md`: OpenTelemetry API/SDK pin notes for the exporter skeleton.

### Added

- **`ReplaytSpanExporter`**: OpenTelemetry SDK **`SpanExporter`** that appends **`PreparedSpanRecord`** snapshots to a test-observable buffer; **`shutdown`** stops further appends; **`force_flush`** is a synchronous no-op returning **`True`**.
- **`PreparedSpanRecord`** IR and attribute serialization helpers in `replayt_otel_span_exporter.records`.
- Runtime dependency **`opentelemetry-sdk>=1.0.0`** (alongside existing **`opentelemetry-api`**).
- Tests: `tests/test_exporter.py` (real **`TracerProvider`** + **`SimpleSpanProcessor`**), `tests/test_records.py` (attribute serialization).
- Integration test under `tests/integration/` exercising the OpenTelemetry trace API.
- CI pipeline specification and testable acceptance criteria in `docs/CI_SPEC.md`.
- `pytest-cov` in dev extras so CI coverage matches local installs.
- Dependency smoke tests for OpenTelemetry API imports and SDK export types (`tests/test_dependencies.py`).

### Changed

- GitHub Actions: default workflow **`permissions: contents: read`** for least-privilege **`GITHUB_TOKEN`** use.
- Codecov upload step uses `fail_ci_if_error: false` so token or fork limitations do not fail CI.
- GitHub Actions test job Python matrix aligned with `requires-python` (3.11 and 3.12).
- README CI section names the workflow file, branch triggers, and Python versions used in CI.

## [0.1.0] - 2026-03-25

### Added

- Initial scaffold and package layout.
