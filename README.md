# OpenTelemetry Span Exporter for Replayt Workflows

## Overview

This project builds on **[replayt](https://pypi.org/project/replayt/)**. Read
**[docs/REPLAYT_ECOSYSTEM_IDEA.md](docs/REPLAYT_ECOSYSTEM_IDEA.md)** for positioning prompts, then
**[docs/MISSION.md](docs/MISSION.md)** for scope and goals (stubs until you flesh them out).

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

The **test** job in **`.github/workflows/ci.yml`** runs **`pytest`** with coverage on **push** and **pull_request** to **`master`** and **`mc/**`**, on Python **3.11** and **3.12**, after **`pip install -e ".[dev]"`** (same as quick start). See **[docs/CI_SPEC.md](docs/CI_SPEC.md)** for acceptance criteria and maintainer notes.

## Optional agent workflows

This repo may include a [`.cursor/skills/`](.cursor/skills/) directory for Cursor-style agent skills. **`.gitignore`**
lists **`path/`** (so documentation-style placeholder paths are never committed), **`.cursor/skills/`**, and related
local tooling entries. Adapt or remove optional directories to match your team’s workflow.

## Project layout

| Path | Purpose |
| ---- | ------- |
| `docs/REPLAYT_ECOSYSTEM_IDEA.md` | Positioning (core-gap / showcase / bridge / combinator prompts) |
| `docs/MISSION.md` | Mission and scope |
| `docs/DESIGN_PRINCIPLES.md` | Design and integration principles |
| `docs/CI_SPEC.md` | CI triggers, Python matrix, install path, and test expectations |
| `docs/reference-documentation/` | Optional markdown snapshot for contributors (when present) |
| `src/replayt_otel_span_exporter/` | Python package (import `replayt_otel_span_exporter`) |
| `pyproject.toml` | Package metadata |
| `.gitignore` | Ignores `path/` (doc placeholders), `.orchestrator/`, `.cursor/skills/`, and `AGENTS.md` (local tooling) |
