# OpenTelemetry Span Exporter for Replayt Workflows

## Overview

This project builds on **[replayt](https://pypi.org/project/replayt/)**. Read
**[docs/REPLAYT_ECOSYSTEM_IDEA.md](docs/REPLAYT_ECOSYSTEM_IDEA.md)** for positioning options, then
**[docs/MISSION.md](docs/MISSION.md)** for scope and goals. Backlog-driven contracts live in specs such as
**[docs/SPEC_OTEL_EXPORTER_SKELETON.md](docs/SPEC_OTEL_EXPORTER_SKELETON.md)**, **[docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)** (logging and redaction on export failure), **[docs/SPEC_EXPORT_TRIAGE_METADATA.md](docs/SPEC_EXPORT_TRIAGE_METADATA.md)** (**`workflow_id`** / **`step_id`** triage fields and **`[REDACTED]`** sensitive attribute values on prepared records), **[docs/SPEC_SPAN_EXPORT_APPROVAL_UX.md](docs/SPEC_SPAN_EXPORT_APPROVAL_UX.md)** (optional integrator approval hook and audit visibility for span export), and **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](docs/SPEC_REPLAYT_INTEGRATION_TESTS.md)** (replayt boundary contract; tests in **`tests/integration/test_replayt_boundary.py`**), and **[docs/SPEC_FIRST_ALPHA_RELEASE.md](docs/SPEC_FIRST_ALPHA_RELEASE.md)** (first **alpha** PyPI or private-index publish: versioning, changelog, verification).

## Design principles

**[docs/DESIGN_PRINCIPLES.md](docs/DESIGN_PRINCIPLES.md)** covers **replayt** compatibility, versioning, and **LLM** boundaries for demos and agent tooling.

## Reference documentation (optional)

This checkout does not yet include [`docs/reference-documentation/`](docs/reference-documentation/). You can add markdown
copies of upstream replayt documentation there for offline review or agent context.

## Quick start

### Library users (integrators)

This package targets **Python 3.11+** (`requires-python` in **`pyproject.toml`**). The PyPI project is **[replayt-otel-span-exporter](https://pypi.org/project/replayt-otel-span-exporter/)**; the first alpha in the changelog is **`0.2.0a1`**. If that version is not listed on the project page yet, use **Contributors and CI parity** below from a clone until upload finishes.

After the wheel and sdist for **`0.2.0a1`** appear on the index, install with an explicit pin (same pattern as **[docs/SPEC_FIRST_ALPHA_RELEASE.md](docs/SPEC_FIRST_ALPHA_RELEASE.md)** §5):

```bash
python -m pip install --upgrade pip
pip install replayt-otel-span-exporter==0.2.0a1
```

Prereleases are not chosen by unpinned **`pip install replayt-otel-span-exporter`**; to track the latest alpha without a pin, use **`pip install --pre replayt-otel-span-exporter`**.

Runtime install pulls **OpenTelemetry** only, not **`replayt`**; that matches the **Usage** example below. Pin policy and matrix: **[docs/COMPATIBILITY.md](docs/COMPATIBILITY.md)**.

### Contributors and CI parity

```bash
python -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Usage

The block below matches **`tests/readme_usage_example_snippet.py`**, which **`tests/test_readme_usage_example.py`** runs in CI. Standalone scripts can omit the global **`TracerProvider`** save/restore that the snippet uses for test isolation.

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

from replayt_otel_span_exporter import PreparedSpanRecord, ReplaytSpanExporter

records: list[PreparedSpanRecord] = []
exporter = ReplaytSpanExporter(records=records)
provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(exporter))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("readme-example")
with tracer.start_as_current_span("example-span") as span:
    span.set_attribute("app.operation", "demo")
    span.set_attribute("replayt.workflow_id", "wf-readme")
    span.set_attribute("replayt.step_id", "step-1")

provider.shutdown()

rec = records[0]
print(rec.name, rec.trace_id)
```

**PreparedSpanRecord** values are the hand-off for replayt-oriented workflows: this package prepares span-shaped data for downstream consumers without importing **`replayt`**. The concrete **`replayt`** import boundary in CI is **[docs/SPEC_REPLAYT_INTEGRATION_TESTS.md](docs/SPEC_REPLAYT_INTEGRATION_TESTS.md)** (section 7) and **`tests/integration/test_replayt_boundary.py`** when **`replayt`** is installed via the **`dev`** extra.

### Optional approval hook

**`ReplaytSpanExporter`** accepts optional keyword-only **`on_export_commit`**: a callable
``(prepared, *, span_count) -> "allow" | "deny"`` that runs after IR mapping and before
appending to the **`records`** buffer. **`"deny"`** returns **`SpanExportResult.SUCCESS`**
to the OpenTelemetry SDK (policy outcome, not a transport failure) and does not append that
batch. Optional **`on_export_audit`** receives a small typed event with allow-listed fields
(decision, counts, first-record ids, **`workflow_id`** / **`step_id`** when present); it runs
only together with **`on_export_commit`** (passing **`on_export_audit`** alone has no effect).
Without a hook, behavior matches the default path above. Full rules: **[docs/SPEC_SPAN_EXPORT_APPROVAL_UX.md](docs/SPEC_SPAN_EXPORT_APPROVAL_UX.md)**.

## Continuous integration

**`.github/workflows/ci.yml`** runs on **push** and **pull_request** to **`master`** and **`mc/**`**. The **`test`** job installs with **`pip install -e ".[dev]"`**, runs **`pytest`** with coverage on Python **3.11** and **3.12**, and uploads coverage; the **`supply-chain`** job runs **`pip-audit`** on the same matrix. See **[docs/CI_SPEC.md](docs/CI_SPEC.md)** for full acceptance criteria, the definition of a “green” run, and maintainer notes.

## Export failures

When mapping or buffering fails inside **`ReplaytSpanExporter.export`**, the exporter returns **`SpanExportResult.FAILURE`** and does not raise into the OpenTelemetry SDK. If the optional **`on_export_commit`** hook **raises**, **`export`** returns **`FAILURE`** with no partial append; a policy **`"deny"`** return is **`SUCCESS`** with no append (see **Optional approval hook** above). Operational detail is written with **`logging`**: loggers live under the **`replayt_otel_span_exporter`** hierarchy (for example **`replayt_otel_span_exporter.exporter`**). Failure records use **ERROR** and include exception info for stack traces. Full prepared attribute maps are not attached to those records; a shared redaction table defines sensitive attribute **key** patterns. Field names, batch semantics, and redaction rules are defined in **[docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md](docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md)**. Third-party exception messages should be treated as untrusted even when they appear inside traceback text.

## Prepared span metadata (triage)

Integrators **SHOULD** set OpenTelemetry span attributes **`replayt.workflow_id`** and **`replayt.step_id`** (exact, case-sensitive keys) so **`PreparedSpanRecord`** exposes first-class **`workflow_id`** and **`step_id`** for correlation. Triage strings are taken from serialized span values before key-based redaction; sensitive attribute keys (per **`replayt_otel_span_exporter.redaction.attribute_key_is_sensitive`**) are stored as **`[REDACTED]`** in **`PreparedSpanRecord.attributes`**. Details: **[docs/SPEC_EXPORT_TRIAGE_METADATA.md](docs/SPEC_EXPORT_TRIAGE_METADATA.md)**.

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
| `docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md` | Export failure logging, redaction, and integrator-visible surfaces (Builder contract) |
| `docs/SPEC_EXPORT_TRIAGE_METADATA.md` | Triage metadata on prepared spans — canonical OTel keys, IR fields, attribute redaction, tests |
| `docs/SPEC_REPLAYT_INTEGRATION_TESTS.md` | Replayt integration boundary — scenarios, pins, CI, `test_replayt_boundary.py` |
| `docs/SPEC_README_QUICK_START.md` | README quick start, usage example, and CI proof (`test_readme_usage_example.py`) — Builder contract |
| `docs/SPEC_SPAN_EXPORT_APPROVAL_UX.md` | Optional approval hook, audit signals, and tests for `ReplaytSpanExporter` — Builder contract |
| `docs/DESIGN_PRINCIPLES.md` | Design and integration principles |
| `docs/CI_SPEC.md` | CI triggers, Python matrix, install path, and test expectations |
| `docs/COMPATIBILITY.md` | Supported versions matrix, pin strategy, CI alignment, replayt release links |
| `docs/reference-documentation/` | Optional markdown snapshot for contributors (when present) |
| `src/replayt_otel_span_exporter/` | Python package (import `replayt_otel_span_exporter`) |
| `pyproject.toml` | Package metadata |
| `.gitignore` | Ignores `path/` (doc placeholders), `.orchestrator/`, `.cursor/skills/`, and `AGENTS.md` (local tooling) |
