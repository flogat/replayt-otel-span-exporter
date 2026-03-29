# OpenTelemetry Python (trace and export)

No third-party verbatim excerpts in this file.

## Why this matters here

**replayt-otel-span-exporter** implements a **`SpanExporter`** that turns **`ReadableSpan`** batches into **prepared records** for replayt-oriented workflows. The OpenTelemetry Python **SDK** owns span lifecycle, processors, and the call into exporters; this package sits at that export boundary. Read **[docs/SPEC_OTEL_EXPORTER_SKELETON.md](../SPEC_OTEL_EXPORTER_SKELETON.md)** for the IR and exporter rules.

## Span data at the boundary

Spans carry **attributes** and identifiers the SDK passes through to exporters. For triage fields used by this repo, integrators set **`replayt.workflow_id`** and **`replayt.step_id`** (exact keys) on spans; see **[docs/SPEC_EXPORT_TRIAGE_METADATA.md](../SPEC_EXPORT_TRIAGE_METADATA.md)**. Broader attribute and trace semantics live in the OpenTelemetry trace specification and semantic conventions linked below.

## Canonical links

- **Python language docs (opentelemetry.io):** [https://opentelemetry.io/docs/languages/python/](https://opentelemetry.io/docs/languages/python/)
- **Trace API specification:** [https://opentelemetry.io/docs/specs/otel/trace/api/](https://opentelemetry.io/docs/specs/otel/trace/api/)
- **OpenTelemetry Python SDK — trace export (`SpanExporter`, processors):** [https://opentelemetry-python.readthedocs.io/en/latest/sdk/trace.export.html](https://opentelemetry-python.readthedocs.io/en/latest/sdk/trace.export.html)
- **Distribution this repo depends on — `opentelemetry-sdk` on PyPI:** [https://pypi.org/project/opentelemetry-sdk/](https://pypi.org/project/opentelemetry-sdk/)
- **Distribution this repo depends on — `opentelemetry-api` on PyPI:** [https://pypi.org/project/opentelemetry-api/](https://pypi.org/project/opentelemetry-api/)
