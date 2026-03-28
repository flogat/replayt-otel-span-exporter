# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Documentation

- Backlog **“Define project mission and scope”** (phase **2** spec): **[docs/MISSION.md](docs/MISSION.md)** adds backlog traceability, expanded user outcome wording, a **Test and CI expectations** section (install line, **`pytest --cov`** command, Python matrix, green-run definition, spec-to-suite mapping), **Success criteria** that name changelog and CI expectations, an **Audience** table, and **LLM and demos** boundaries linked to design principles and specs.

### Added

- **`PreparedSpanRecord`** **`workflow_id`** and **`step_id`** (from span attributes **`replayt.workflow_id`** / **`replayt.step_id`**) and **`[REDACTED]`** placeholders on sensitive keys in **`attributes`** per **[docs/SPEC_EXPORT_TRIAGE_METADATA.md](docs/SPEC_EXPORT_TRIAGE_METADATA.md)**; **`redact_sensitive_attribute_values`** in **`replayt_otel_span_exporter.redaction`**.
- **Export failure logging (backlog: error handling and logging for span export failures):** **`ReplaytSpanExporter`** logs internal **`export`** mapping/buffer errors at **ERROR** under **`replayt_otel_span_exporter.exporter`** with **`exc_info`**, structured fields (**`span_count`**, **`failed_span_index`** when known, trace and span hex ids and span name/kind for real **`ReadableSpan`** batches), and a boolean **`sensitive_attribute_keys_present`** derived from **`replayt_otel_span_exporter.redaction.attribute_key_is_sensitive`**. A single batch either appends all prepared records or none. README **Export failures** and **[docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)** describe integrator-visible behavior.
- **`replayt>=0.4.25`** on the **`dev`** optional extra for CI and local runs; integration tests **`tests/integration/test_replayt_boundary.py`** exercise **`PreparedSpanRecord`** → **`replayt`** **`RunContext`** via **`Runner.before_step`** (see **`docs/SPEC_REPLAYT_INTEGRATION_TESTS.md`** §7).
- **`ReplaytSpanExporter`**: OpenTelemetry SDK **`SpanExporter`** that appends **`PreparedSpanRecord`** snapshots to a test-observable buffer; **`shutdown`** stops further appends; **`force_flush`** is a synchronous no-op returning **`True`**.
- **`PreparedSpanRecord`** IR and attribute serialization helpers in `replayt_otel_span_exporter.records`.
- Runtime dependency **`opentelemetry-sdk>=1.0.0`** (alongside existing **`opentelemetry-api`**).
- Tests: `tests/test_exporter.py` (real **`TracerProvider`** + **`SimpleSpanProcessor`**), `tests/test_records.py` (attribute serialization).
- Integration test under `tests/integration/` exercising the OpenTelemetry trace API.
- CI pipeline specification and testable acceptance criteria in `docs/CI_SPEC.md`.
- `pytest-cov` in dev extras so CI coverage matches local installs.
- Dependency smoke tests for OpenTelemetry API imports and SDK export types (`tests/test_dependencies.py`).

### Changed

- **`ReplaytSpanExporter.export`:** a batch that hits an internal error no longer leaves earlier spans from that call in the buffer (all-or-nothing append per **[docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)** §1).
- **`dev`** pins **`requests>=2.33.0`** for a clean **`pip-audit`** graph with **`replayt`**; **`supply-chain`** ignores **CVE-2025-69872** (**diskcache** / pickle) with rationale in **`docs/DEPENDENCY_AUDIT.md`** (same pattern as **pygments**).
- GitHub Actions: default workflow **`permissions: contents: read`** for least-privilege **`GITHUB_TOKEN`** use.
- Codecov upload step uses `fail_ci_if_error: false` so token or fork limitations do not fail CI.
- GitHub Actions test job Python matrix aligned with `requires-python` (3.11 and 3.12).
- README CI section names the workflow file, branch triggers, and Python versions used in CI.

### Documentation

- Backlog **“Add metadata for triage without leaking secrets”** (phase **2** spec): **[docs/SPEC_EXPORT_TRIAGE_METADATA.md](docs/SPEC_EXPORT_TRIAGE_METADATA.md)** defines canonical span attributes **`replayt.workflow_id`** / **`replayt.step_id`**, **`PreparedSpanRecord`** **`workflow_id`** / **`step_id`** fields, **`[REDACTED]`** values for sensitive keys via **`attribute_key_is_sensitive`**, test contract §5, and checklist §7. Cross-links in **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](docs/SPEC_OTEL_EXPORTER_SKELETON.md)** (§3 IR table, §4.5, §6 item 8), **[docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)** §5.1, **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](docs/SPEC_REPLAYT_INTEGRATION_TESTS.md)** §7, **[docs/CI_SPEC.md](docs/CI_SPEC.md)** §5, **[docs/MISSION.md](docs/MISSION.md)**, and **[README.md](README.md)**.
- Architecture review (phase **5**, same backlog): **[docs/MISSION.md](docs/MISSION.md)**, **[docs/CI_SPEC.md](docs/CI_SPEC.md)** §5, and **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](docs/SPEC_OTEL_EXPORTER_SKELETON.md)** §3 / §4.5 / §6 item **8** state triage metadata as current behavior (removed “when implemented” / “when in scope” wording left over from the spec-only phase).
- Backlog **“Add error handling and logging for span export failures”**: phase **2** added **[docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)** (logging contract, redaction rules, batch semantics, test contract, acceptance checklist). Cross-links in **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](docs/SPEC_OTEL_EXPORTER_SKELETON.md)** §2.3, **[README.md](README.md)**, **[docs/MISSION.md](docs/MISSION.md)**, and **[docs/CI_SPEC.md](docs/CI_SPEC.md)**. Phase **3** added README **Export failures**, implementation, and tests per that spec.
- Architecture review (phase 5): `docs/CI_SPEC.md`, `docs/MISSION.md`, and `docs/SPEC_OTEL_EXPORTER_SKELETON.md` §2.3 describe **[docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)** as active CI and exporter requirements (no “when implemented” wording). `README.md`, `docs/CI_SPEC.md`, `docs/MISSION.md`, and `docs/SPEC_REPLAYT_INTEGRATION_TESTS.md` describe replayt integration tests against the **`dev`** extra in present tense (no “when the backlog lands” placeholders for that path).
- Backlog **“Add replayt integration tests”**: spec phase 2 added `docs/SPEC_REPLAYT_INTEGRATION_TESTS.md` (boundary definition, scenarios, optional-deps policy, §6 checklist); phase 3 filled §7 and wired **`tests/integration/test_replayt_boundary.py`**. Cross-links and CI expectations in `docs/CI_SPEC.md`, `docs/MISSION.md`, `docs/SPEC_OTEL_EXPORTER_SKELETON.md`, `docs/DEPENDENCY_AUDIT.md`, and `README.md`.
- Refined exporter skeleton spec (phase 2): canonical names (`ReplaytSpanExporter`, `PreparedSpanRecord`, `__all__`), aligned dependency wording with `pyproject.toml`, exporter threading/shutdown/`SpanExportResult` semantics, IR edge cases, expanded test contract, and §6 verifiable acceptance checklist in `docs/SPEC_OTEL_EXPORTER_SKELETON.md`; `docs/CI_SPEC.md` references the checklist.
- Mission and positioning filled in `docs/MISSION.md` and `docs/REPLAYT_ECOSYSTEM_IDEA.md` (framework-bridge pattern).
- Builder contract for the OpenTelemetry span exporter skeleton: `docs/SPEC_OTEL_EXPORTER_SKELETON.md` (public API, prepared-span IR, test expectations, `opentelemetry-sdk` dependency note).
- README links the exporter spec alongside mission and ecosystem docs.
- `docs/DEPENDENCY_AUDIT.md`: OpenTelemetry API/SDK pin notes for the exporter skeleton.

## [0.1.0] - 2026-03-25

### Added

- Initial scaffold and package layout.
