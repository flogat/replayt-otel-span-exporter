# Scripts

## OpenTelemetry → prepared record demo

**`otel_to_prepared_demo.py`** runs the SDK → **`ReplaytSpanExporter`** → **`PreparedSpanRecord`** pipeline and prints IR fields to stdout. It does **not** import **`replayt`**.

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
