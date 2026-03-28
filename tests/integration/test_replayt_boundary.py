"""Integration tests at the replayt boundary (see docs/SPEC_REPLAYT_INTEGRATION_TESTS.md)."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.trace import format_span_id, format_trace_id
from replayt.persistence.sqlite import SQLiteStore
from replayt.runner import RunContext, Runner
from replayt.testing import DryRunLLMClient
from replayt.types import LogMode
from replayt.workflow import Workflow

from replayt_otel_span_exporter import PreparedSpanRecord, ReplaytSpanExporter


def test_tracer_pipeline_produces_prepared_record_matching_span():
    """§4.1 — TracerProvider → ReplaytSpanExporter → PreparedSpanRecord fields match the live span."""
    exporter = ReplaytSpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer(__name__)

    with tracer.start_as_current_span("replayt-boundary-span") as span:
        span.set_attribute("integration.marker", "replayt-boundary")
        ctx = span.get_span_context()
        want_trace = format_trace_id(ctx.trace_id)
        want_span = format_span_id(ctx.span_id)

    records = exporter.records
    assert len(records) >= 1
    rec = records[0]
    assert isinstance(rec, PreparedSpanRecord)
    assert rec.name == "replayt-boundary-span"
    assert rec.trace_id == want_trace
    assert rec.span_id == want_span
    assert rec.kind == trace.SpanKind.INTERNAL.name
    assert rec.start_time_unix_nano > 0
    assert rec.end_time_unix_nano > 0
    assert rec.start_time_unix_nano <= rec.end_time_unix_nano
    assert rec.attributes["integration.marker"] == "replayt-boundary"


def test_prepared_record_crosses_replayt_run_context_boundary():
    """§4.2 — PreparedSpanRecord-derived payload is accepted by replayt RunContext (integrator hook path)."""
    exporter = ReplaytSpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer(__name__)

    with tracer.start_as_current_span("ctx-bridge-span") as span:
        span.set_attribute("bridge", True)
        span.set_attribute("replayt.workflow_id", "wf-bridge")
        span.set_attribute("replayt.step_id", "bridge-step")
    rec = exporter.records[0]
    payload = {
        "trace_id": rec.trace_id,
        "span_id": rec.span_id,
        "name": rec.name,
        "kind": rec.kind,
        "start_time_unix_nano": rec.start_time_unix_nano,
        "end_time_unix_nano": rec.end_time_unix_nano,
        "attributes": dict(rec.attributes),
        "workflow_id": rec.workflow_id,
        "step_id": rec.step_id,
    }

    def before_step(ctx: RunContext, state: str) -> None:
        assert state == "start"
        ctx.set("otel_span", payload)

    wf = Workflow(name="otel-replayt-bridge-smoke", version="1")
    verified: dict[str, Any] = {}

    @wf.step("start")
    def start(ctx: RunContext) -> None:
        got = ctx.get("otel_span")
        assert got == payload
        verified["ok"] = True
        return None

    wf.set_initial("start")

    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "replayt_events.db"
        store = SQLiteStore(db_path)
        runner = Runner(
            wf,
            store,
            llm_client=DryRunLLMClient(),
            log_mode=LogMode.redacted,
            before_step=before_step,
        )
        try:
            result = runner.run()
        finally:
            runner.close()

    assert result.status == "completed"
    assert verified.get("ok") is True
