# Design principles

Revise as the project matures. Defaults below are minimal—expand with rules for **your** codebase.

1. **Explicit contracts** — Document supported replayt (and third-party framework) versions; test integration boundaries.
2. **Small public surfaces** — Prefer narrow APIs and documented extension points.
3. **Observable automation** — Local scripts and CI produce clear logs and exit codes.
4. **Consumer-side maintenance** — Compatibility shims and pins live **here**; upstream changes are tracked with tests
   and changelog notes.
5. **Not a lever on core** — This repo does not exist to steer replayt core; propose upstream changes through normal
   channels.

## Compatibility

Supported **Python**, **OpenTelemetry**, and **replayt (dev/test)** versions, **pin strategy**, **CI matrix** alignment, and **links to replayt release tracking** on PyPI are documented in **[docs/COMPATIBILITY.md](COMPATIBILITY.md)**. Update that file whenever **`pyproject.toml`** pins or **`.github/workflows/ci.yml`** matrix entries change.

## LLM / demos (if applicable)

Document models, secrets handling, cost and redaction expectations here or in MISSION.

## Audience (extend)

| Audience | Needs |
| -------- | ----- |
| **Maintainers** | Mission, scripts, pinned versions, release notes |
| **Integrators** | Stable adapter surface, **[docs/COMPATIBILITY.md](COMPATIBILITY.md)** (matrix and replayt policy) |
| **Governance / compliance** (when applicable) | **[docs/SPEC_SPAN_EXPORT_APPROVAL_UX.md](SPEC_SPAN_EXPORT_APPROVAL_UX.md)** (audit visibility), **[docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)** and **[docs/SPEC_EXPORT_TRIAGE_METADATA.md](SPEC_EXPORT_TRIAGE_METADATA.md)** (redaction and triage) |
| **Contributors** | README, tests, coding expectations |
