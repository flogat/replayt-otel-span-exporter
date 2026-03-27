# OpenTelemetry Span Exporter for Replayt Workflows

## Overview

This project builds on **[replayt](https://pypi.org/project/replayt/)**. Read
**[docs/REPLAYT_ECOSYSTEM_IDEA.md](docs/REPLAYT_ECOSYSTEM_IDEA.md)** for positioning options, then
**[docs/MISSION.md](docs/MISSION.md)** for scope and goals. Backlog-driven contracts live in specs such as
**[docs/SPEC_OTEL_EXPORTER_SKELETON.md](docs/SPEC_OTEL_EXPORTER_SKELETON.md)**.

## Design principles

**[docs/DESIGN_PRINCIPLES.md](docs/DESIGN_PRINCIPLES.md)** covers **replayt** compatibility, versioning, and (for showcases)
**LLM** boundaries.


## Reference documentation (optional)

This checkout does not yet include [`docs/reference-documentation/`](docs/reference-documentation/). You can add markdown
copies of upstream replayt documentation there for offline review or agent context.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
pip install -e ".[dev]"
```

## Continuous integration

**`.github/workflows/ci.yml`** runs on **push** and **pull_request** to **`master`** and **`mc/**`**. The **`test`** job installs with **`pip install -e ".[dev]"`**, runs **`pytest`** with coverage on Python **3.11** and **3.12**, and uploads coverage; the **`supply-chain`** job runs **`pip-audit`** on the same matrix. See **[docs/CI_SPEC.md](docs/CI_SPEC.md)** for full acceptance criteria, the definition of a “green” run, and maintainer notes.

## Optional agent workflows

This repo may include a [`.cursor/skills/`](.cursor/skills/) directory for Cursor-style agent skills. **`.gitignore`**
lists **`path/`** (so documentation-style placeholder paths are never committed), **`.cursor/skills/`**, and related
local tooling entries. Adapt or remove optional directories to match your team’s workflow.

## Project layout

| Path | Purpose |
| ---- | ------- |
| `docs/REPLAYT_ECOSYSTEM_IDEA.md` | Positioning (core-gap / showcase / bridge / combinator prompts) |
| `docs/MISSION.md` | Mission and scope |
| `docs/SPEC_OTEL_EXPORTER_SKELETON.md` | Exporter skeleton backlog — API, IR, tests (Builder contract) |
| `docs/DESIGN_PRINCIPLES.md` | Design and integration principles |
| `docs/CI_SPEC.md` | CI triggers, Python matrix, install path, and test expectations |
| `docs/reference-documentation/` | Optional markdown snapshot for contributors (when present) |
| `src/replayt_otel_span_exporter/` | Python package (import `replayt_otel_span_exporter`) |
| `pyproject.toml` | Package metadata |
| `.gitignore` | Ignores `path/` (doc placeholders), `.orchestrator/`, `.cursor/skills/`, and `AGENTS.md` (local tooling) |
