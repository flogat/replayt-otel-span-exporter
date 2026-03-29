"""Integration tests at the replayt boundary (see docs/SPEC_REPLAYT_INTEGRATION_TESTS.md)."""

from __future__ import annotations

import tempfile
import tomllib
from importlib.metadata import version as distribution_version
from pathlib import Path
from typing import Any

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.trace import format_span_id, format_trace_id
from packaging.requirements import Requirement
from packaging.version import Version
from replayt.persistence.sqlite import SQLiteStore
from replayt.runner import RunContext, Runner
from replayt.testing import DryRunLLMClient
from replayt.types import LogMode
from replayt.workflow import Workflow

from replayt_otel_span_exporter import PreparedSpanRecord, ReplaytSpanExporter

# §4.4 — Runner, RunContext, Workflow, SQLiteStore, DryRunLLMClient, LogMode (see spec §7).

_BOUNDARY_PAYLOAD_KEYS = frozenset(
    {
        "trace_id",
        "span_id",
        "name",
        "kind",
        "start_time_unix_nano",
        "end_time_unix_nano",
        "attributes",
        "workflow_id",
        "step_id",
    }
)


def _pyproject_replayt_requirement() -> Requirement:
    root = Path(__file__).resolve().parents[2]
    with (root / "pyproject.toml").open("rb") as f:
        data = tomllib.load(f)
    dev = data["project"]["optional-dependencies"]["dev"]
    line = next(d for d in dev if d.strip().lower().startswith("replayt"))
    return Requirement(line)


def _assert_boundary_payload_matches_record(
    rec: PreparedSpanRecord, payload: dict[str, Any]
) -> None:
    """§4.5 — keys, types, and shallow-copy semantics for attributes (IR drift guard)."""
    assert set(payload.keys()) == _BOUNDARY_PAYLOAD_KEYS
    assert isinstance(payload["trace_id"], str) and len(payload["trace_id"]) == 32
    assert isinstance(payload["span_id"], str) and len(payload["span_id"]) == 16
    assert isinstance(payload["name"], str)
    assert isinstance(payload["kind"], str)
    assert isinstance(payload["start_time_unix_nano"], int)
    assert isinstance(payload["end_time_unix_nano"], int)
    assert isinstance(payload["attributes"], dict)
    wf = payload["workflow_id"]
    st = payload["step_id"]
    assert wf is None or isinstance(wf, str)
    assert st is None or isinstance(st, str)

    assert payload["trace_id"] == rec.trace_id
    assert payload["span_id"] == rec.span_id
    assert payload["name"] == rec.name
    assert payload["kind"] == rec.kind
    assert payload["start_time_unix_nano"] == rec.start_time_unix_nano
    assert payload["end_time_unix_nano"] == rec.end_time_unix_nano
    assert payload["workflow_id"] == rec.workflow_id
    assert payload["step_id"] == rec.step_id
    assert payload["attributes"] == dict(rec.attributes)

    attrs = payload["attributes"]
    assert attrs is not rec.attributes
    attrs["__replayt_boundary_mutation_probe__"] = 1
    assert "__replayt_boundary_mutation_probe__" not in rec.attributes
    del attrs["__replayt_boundary_mutation_probe__"]


def test_installed_replayt_satisfies_pyproject_lower_bound():
    """§4.6 — installed replayt must match the dev extra specifier (pin / env drift guard)."""
    req = _pyproject_replayt_requirement()
    assert req.name == "replayt"
    installed = Version(distribution_version("replayt"))
    assert req.specifier.contains(installed, prereleases=True)


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
    _assert_boundary_payload_matches_record(rec, payload)

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
