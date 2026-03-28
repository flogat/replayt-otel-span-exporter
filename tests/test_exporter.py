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


def test_exporter_approval_allow_appends_and_audits(caplog):
    """SPEC_SPAN_EXPORT_APPROVAL_UX §8 — allow commits batch and emits audit."""
    caplog.set_level(logging.INFO, logger="replayt_otel_span_exporter.exporter.audit")
    audit_events: list[dict] = []

    def commit(prepared, *, span_count: int):
        assert span_count == 1
        assert len(prepared) == 1
        return "allow"

    def audit(event):
        audit_events.append(dict(event))

    exporter = ReplaytSpanExporter(
        on_export_commit=commit,
        on_export_audit=audit,
    )
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer(__name__)

    with tracer.start_as_current_span("approval-allow") as span:
        span.set_attribute("replayt.workflow_id", "wf-audit")
        span.set_attribute("replayt.step_id", "s1")

    assert len(exporter.records) == 1
    assert len(audit_events) == 1
    ev = audit_events[0]
    assert ev["decision"] == "allow"
    assert ev["prepared_count"] == 1
    assert ev["span_count"] == 1
    assert "trace_id" in ev and "span_id" in ev
    assert ev.get("workflow_id") == "wf-audit"
    assert ev.get("step_id") == "s1"

    infos = [r for r in caplog.records if r.levelno == logging.INFO]
    assert infos
    assert getattr(infos[0], "decision") == "allow"


def test_exporter_approval_deny_success_no_append_and_audits(caplog):
    """SPEC_SPAN_EXPORT_APPROVAL_UX §8 — deny returns SUCCESS and skips buffer append."""
    caplog.set_level(logging.INFO, logger="replayt_otel_span_exporter.exporter.audit")

    def commit(_prepared, *, span_count: int):
        assert span_count == 1
        return "deny"

    exporter = ReplaytSpanExporter(on_export_commit=commit)
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer(__name__)

    with tracer.start_as_current_span("approval-deny"):
        pass

    assert len(exporter.records) == 0
    infos = [r for r in caplog.records if r.levelno == logging.INFO]
    assert infos
    assert getattr(infos[0], "decision") == "deny"
    assert "policy" in infos[0].getMessage().lower() or "denied" in infos[0].getMessage().lower()


def test_exporter_approval_hook_failure_returns_failure_no_partial_append(caplog):
    """SPEC_SPAN_EXPORT_APPROVAL_UX §8 — hook exception is FAILURE without partial append."""
    caplog.set_level(logging.ERROR, logger="replayt_otel_span_exporter.exporter")

    def commit(_p, *, span_count: int):
        raise RuntimeError("hook exploded")

    exporter = ReplaytSpanExporter(on_export_commit=commit)
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer(__name__)

    with tracer.start_as_current_span("approval-boom"):
        pass

    assert len(exporter.records) == 0
    errors = [r for r in caplog.records if r.levelno == logging.ERROR]
    assert errors
    assert "approval hook" in errors[0].getMessage().lower()
    assert errors[0].exc_info is not None


def test_exporter_approval_shutdown_does_not_invoke_hook():
    """SPEC_SPAN_EXPORT_APPROVAL_UX §8 — post-shutdown export is a no-op; hook does not run."""
    calls = {"n": 0}

    def commit(_p, *, span_count: int):
        calls["n"] += 1
        return "allow"

    exporter = ReplaytSpanExporter(on_export_commit=commit)
    exporter.shutdown()
    assert exporter.export([]) is SpanExportResult.SUCCESS
    assert calls["n"] == 0
