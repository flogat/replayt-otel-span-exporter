"""Tests for ``ReplaytSpanExporter`` and ``PreparedSpanRecord`` (real SDK pipeline)."""

from unittest.mock import MagicMock

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExportResult
from opentelemetry.trace import format_span_id, format_trace_id

from replayt_otel_span_exporter import PreparedSpanRecord, ReplaytSpanExporter


def test_exporter_ingests_finished_span_via_simple_processor():
    exporter = ReplaytSpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer(__name__)

    with tracer.start_as_current_span("builder-ingest-span") as span:
        span.set_attribute("test.attr", "expected-value")
        ctx = span.get_span_context()
        want_trace = format_trace_id(ctx.trace_id)
        want_span = format_span_id(ctx.span_id)

    records = exporter.records
    assert len(records) == 1
    rec = records[0]
    assert isinstance(rec, PreparedSpanRecord)
    assert rec.name == "builder-ingest-span"
    assert rec.trace_id == want_trace
    assert rec.span_id == want_span
    assert rec.kind == trace.SpanKind.INTERNAL.name
    assert rec.start_time_unix_nano > 0
    assert rec.end_time_unix_nano > 0
    assert rec.start_time_unix_nano <= rec.end_time_unix_nano
    assert rec.attributes["test.attr"] == "expected-value"


def test_exporter_shutdown_prevents_further_appends():
    exporter = ReplaytSpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer(__name__)

    with tracer.start_as_current_span("before-shutdown"):
        pass
    assert len(exporter.records) == 1

    exporter.shutdown()

    with tracer.start_as_current_span("after-shutdown"):
        pass
    assert len(exporter.records) == 1


def test_exporter_force_flush_returns_true():
    exporter = ReplaytSpanExporter()
    assert exporter.force_flush() is True
    assert exporter.force_flush(timeout_millis=1) is True


def test_exporter_export_returns_failure_when_transformation_raises(monkeypatch):
    """Internal mapper errors surface as FAILURE without raising (spec 2.3)."""
    from replayt_otel_span_exporter import exporter as exporter_mod

    def _fail(_span):
        raise RuntimeError("simulated transformation failure")

    monkeypatch.setattr(exporter_mod, "prepared_span_record_from_readable", _fail)

    exporter = ReplaytSpanExporter()
    result = exporter.export([MagicMock()])
    assert result is SpanExportResult.FAILURE
    assert exporter.records == []
