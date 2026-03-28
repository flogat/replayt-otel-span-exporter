"""Tests for ``ReplaytSpanExporter`` and ``PreparedSpanRecord`` (real SDK pipeline)."""

import logging
from unittest.mock import MagicMock

from opentelemetry import trace
from opentelemetry.sdk.trace import ReadableSpan, SpanProcessor, TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExportResult
from opentelemetry.trace import format_span_id, format_trace_id

from replayt_otel_span_exporter import PreparedSpanRecord, ReplaytSpanExporter


class _ReadableSpanCollector(SpanProcessor):
    """Collects finished spans so a test can call ``export`` with a multi-span batch."""

    def __init__(self) -> None:
        self.spans: list[ReadableSpan] = []

    def on_start(self, span, parent_context) -> None:
        return None

    def on_end(self, span: ReadableSpan) -> None:
        self.spans.append(span)

    def shutdown(self) -> None:
        return None

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True


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
    assert rec.workflow_id is None
    assert rec.step_id is None


def test_exporter_triage_metadata_populated_from_canonical_attributes():
    exporter = ReplaytSpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer(__name__)

    with tracer.start_as_current_span("triage-span") as span:
        span.set_attribute("replayt.workflow_id", "wf-alpha")
        span.set_attribute("replayt.step_id", "step-7")

    rec = exporter.records[0]
    assert rec.workflow_id == "wf-alpha"
    assert rec.step_id == "step-7"
    assert rec.attributes["replayt.workflow_id"] == "wf-alpha"
    assert rec.attributes["replayt.step_id"] == "step-7"


def test_exporter_triage_workflow_id_coerces_int():
    exporter = ReplaytSpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer(__name__)

    with tracer.start_as_current_span("coerce-span") as span:
        span.set_attribute("replayt.workflow_id", 99)

    rec = exporter.records[0]
    assert rec.workflow_id == "99"
    assert rec.attributes["replayt.workflow_id"] == "99"


def test_exporter_sensitive_attribute_redacted_triage_fields_unchanged():
    exporter = ReplaytSpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer(__name__)
    secret = "super-secret-value"
    with tracer.start_as_current_span("redact-span") as span:
        span.set_attribute("replayt.workflow_id", "wf-safe")
        span.set_attribute("replayt.step_id", "s1")
        span.set_attribute("user.password", secret)

    rec = exporter.records[0]
    assert rec.workflow_id == "wf-safe"
    assert rec.step_id == "s1"
    assert rec.attributes["user.password"] == "[REDACTED]"
    assert secret not in rec.attributes.values()
    assert rec.attributes["replayt.workflow_id"] == "wf-safe"


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


def test_exporter_export_returns_failure_when_transformation_raises(
    caplog, monkeypatch
):
    """Internal mapper errors surface as FAILURE without raising (spec 2.3)."""
    caplog.set_level(logging.ERROR, logger="replayt_otel_span_exporter.exporter")
    from replayt_otel_span_exporter import exporter as exporter_mod

    def _fail(_span):
        raise RuntimeError("simulated transformation failure")

    monkeypatch.setattr(exporter_mod, "prepared_span_record_from_readable", _fail)

    exporter = ReplaytSpanExporter()
    result = exporter.export([MagicMock()])
    assert result is SpanExportResult.FAILURE
    assert exporter.records == []

    errors = [r for r in caplog.records if r.levelno == logging.ERROR]
    assert errors
    assert errors[0].exc_info is not None
    assert getattr(errors[0], "span_count") == 1
    assert getattr(errors[0], "failed_span_index") == 0


def test_exporter_batch_failure_is_atomic_and_logs_failing_index(caplog, monkeypatch):
    caplog.set_level(logging.ERROR, logger="replayt_otel_span_exporter.exporter")
    from replayt_otel_span_exporter import exporter as exporter_mod
    from replayt_otel_span_exporter.records import prepared_span_record_from_readable

    real = prepared_span_record_from_readable
    calls = {"n": 0}

    def flaky(span):
        calls["n"] += 1
        if calls["n"] == 2:
            raise RuntimeError("simulated second-span failure")
        return real(span)

    monkeypatch.setattr(exporter_mod, "prepared_span_record_from_readable", flaky)

    collector = _ReadableSpanCollector()
    provider = TracerProvider()
    provider.add_span_processor(collector)
    tracer = provider.get_tracer(__name__)
    with tracer.start_as_current_span("s1"):
        pass
    with tracer.start_as_current_span("s2"):
        pass
    assert len(collector.spans) == 2

    exporter = ReplaytSpanExporter()
    assert exporter.export(collector.spans) is SpanExportResult.FAILURE
    assert exporter.records == []

    errors = [r for r in caplog.records if r.levelno == logging.ERROR]
    assert getattr(errors[0], "span_count") == 2
    assert getattr(errors[0], "failed_span_index") == 1


def test_exporter_failure_logs_do_not_include_sensitive_attribute_values(
    caplog, monkeypatch
):
    caplog.set_level(logging.ERROR, logger="replayt_otel_span_exporter.exporter")
    from replayt_otel_span_exporter import exporter as exporter_mod

    def _fail(_span):
        raise RuntimeError("mapper failed")

    monkeypatch.setattr(exporter_mod, "prepared_span_record_from_readable", _fail)

    collector = _ReadableSpanCollector()
    provider = TracerProvider()
    provider.add_span_processor(collector)
    tracer = provider.get_tracer(__name__)
    secret = "NOT_IN_LOGS_77231"
    with tracer.start_as_current_span("leaky") as span:
        span.set_attribute("user.password", secret)

    exporter = ReplaytSpanExporter()
    assert exporter.export(collector.spans) is SpanExportResult.FAILURE
    assert secret not in caplog.text

    errors = [r for r in caplog.records if r.levelno == logging.ERROR]
    assert getattr(errors[0], "sensitive_attribute_keys_present") is True
