"""Executable README usage example; keep README.md Usage fenced block aligned with this module."""

from __future__ import annotations

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.trace import format_span_id, format_trace_id

from replayt_otel_span_exporter import PreparedSpanRecord, ReplaytSpanExporter


def run_readme_usage_example() -> list[PreparedSpanRecord]:
    """Run the README OpenTelemetry + ReplaytSpanExporter pipeline.

    Restores the previous global tracer provider so pytest order stays isolated.
    """
    records: list[PreparedSpanRecord] = []
    exporter = ReplaytSpanExporter(records=records)
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))

    previous = trace.get_tracer_provider()
    want_trace: str | None = None
    want_span: str | None = None
    try:
        trace.set_tracer_provider(provider)
        tracer = trace.get_tracer("readme-example")
        with tracer.start_as_current_span("example-span") as span:
            span.set_attribute("app.operation", "demo")
            span.set_attribute("replayt.workflow_id", "wf-readme")
            span.set_attribute("replayt.step_id", "step-1")
            ctx = span.get_span_context()
            want_trace = format_trace_id(ctx.trace_id)
            want_span = format_span_id(ctx.span_id)
        provider.shutdown()
    finally:
        trace.set_tracer_provider(previous)

    assert records, "expected at least one PreparedSpanRecord after shutdown"
    assert want_trace is not None and want_span is not None
    rec = records[0]
    assert rec.name == "example-span"
    assert rec.trace_id == want_trace
    assert rec.span_id == want_span
    assert rec.kind == trace.SpanKind.INTERNAL.name
    assert rec.start_time_unix_nano > 0
    assert rec.end_time_unix_nano > 0
    assert rec.start_time_unix_nano <= rec.end_time_unix_nano
    assert rec.attributes["app.operation"] == "demo"
    assert rec.workflow_id == "wf-readme"
    assert rec.step_id == "step-1"
    assert rec.attributes["replayt.workflow_id"] == "wf-readme"
    assert rec.attributes["replayt.step_id"] == "step-1"
    return records
