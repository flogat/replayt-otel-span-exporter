# Scripts

## OpenTelemetry → prepared record demo

**`otel_to_prepared_demo.py`** runs the SDK → **`ReplaytSpanExporter`** → **`PreparedSpanRecord`** pipeline and prints IR fields to stdout. It does **not** import **`replayt`**.

**Tracing setup:** the script uses **`trace.get_tracer(..., tracer_provider=provider)`** instead of **`trace.set_tracer_provider`**, so a normal subprocess run avoids OpenTelemetry’s stderr warning about overriding the global provider. The root README quick start still uses set/restore for in-process pytest isolation (**`tests/readme_usage_example_snippet.py`**).

**Prerequisite:** from the repository root, install the package in editable mode with dev extras (pulls **OpenTelemetry** per **`pyproject.toml`**):

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

**Run** (repository root):

```bash
python scripts/otel_to_prepared_demo.py
```

Contract: **[docs/SPEC_SCRIPTS_OTEL_PREPARED_DEMO.md](../docs/SPEC_SCRIPTS_OTEL_PREPARED_DEMO.md)**.
