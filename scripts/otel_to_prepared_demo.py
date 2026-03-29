"""OpenTelemetry → PreparedSpanRecord demo (docs/SPEC_SCRIPTS_OTEL_PREPARED_DEMO.md)."""

from __future__ import annotations

import re
import sys

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

from replayt_otel_span_exporter import PreparedSpanRecord, ReplaytSpanExporter

# Fictional triage ids only (docs/DESIGN_PRINCIPLES.md — LLM / demos).
_DEMO_WORKFLOW_ID = "wf-demo-scripts"
_DEMO_STEP_ID = "step-demo-1"
_DEMO_SPAN_NAME = "demo-prepared-span"
_DEMO_ATTR_KEY = "app.demo"
_DEMO_ATTR_VALUE = "fiction"

_TRACE_ID_RE = re.compile(r"^[0-9a-f]{32}$")
_SPAN_ID_RE = re.compile(r"^[0-9a-f]{16}$")


def _validate(rec: PreparedSpanRecord) -> str | None:
    if rec.name != _DEMO_SPAN_NAME:
        return f"unexpected span name: {rec.name!r}"
    if not _TRACE_ID_RE.fullmatch(rec.trace_id):
        return f"invalid trace_id encoding: {rec.trace_id!r}"
    if not _SPAN_ID_RE.fullmatch(rec.span_id):
        return f"invalid span_id encoding: {rec.span_id!r}"
    if rec.kind != trace.SpanKind.INTERNAL.name:
        return f"unexpected kind: {rec.kind!r}"
    if rec.start_time_unix_nano <= 0 or rec.end_time_unix_nano <= 0:
        return "expected positive start/end nanoseconds"
    if rec.start_time_unix_nano > rec.end_time_unix_nano:
        return "start_time_unix_nano after end_time_unix_nano"
    if rec.workflow_id != _DEMO_WORKFLOW_ID or rec.step_id != _DEMO_STEP_ID:
        return "workflow_id or step_id missing or mismatched"
    if rec.attributes.get(_DEMO_ATTR_KEY) != _DEMO_ATTR_VALUE:
        return f"missing or wrong {_DEMO_ATTR_KEY!r} attribute"
    return None


def _print_record(rec: PreparedSpanRecord) -> None:
    print(f"name: {rec.name}")
    print(f"trace_id: {rec.trace_id}")
    print(f"span_id: {rec.span_id}")
    print(f"kind: {rec.kind}")
    print(f"start_time_unix_nano: {rec.start_time_unix_nano}")
    print(f"end_time_unix_nano: {rec.end_time_unix_nano}")
    print(f"workflow_id: {rec.workflow_id}")
    print(f"step_id: {rec.step_id}")
    print(f"attributes.{_DEMO_ATTR_KEY}: {rec.attributes[_DEMO_ATTR_KEY]}")


def main() -> int:
    records: list[PreparedSpanRecord] = []
    exporter = ReplaytSpanExporter(records=records)
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))

    previous = trace.get_tracer_provider()
    try:
        trace.set_tracer_provider(provider)
        tracer = trace.get_tracer("otel-to-prepared-demo")
        # Non-root span (spec §3.2): attributes live on the child.
        with tracer.start_as_current_span("demo-root"):
            with tracer.start_as_current_span(_DEMO_SPAN_NAME) as span:
                span.set_attribute(_DEMO_ATTR_KEY, _DEMO_ATTR_VALUE)
                span.set_attribute("replayt.workflow_id", _DEMO_WORKFLOW_ID)
                span.set_attribute("replayt.step_id", _DEMO_STEP_ID)
        provider.shutdown()
    finally:
        trace.set_tracer_provider(previous)

    if not records:
        print("no prepared records after shutdown", file=sys.stderr)
        return 1

    try:
        rec = next(r for r in records if r.name == _DEMO_SPAN_NAME)
    except StopIteration:
        print(f"no prepared record for span {_DEMO_SPAN_NAME!r}", file=sys.stderr)
        return 1
    err = _validate(rec)
    if err:
        print(err, file=sys.stderr)
        return 1

    _print_record(rec)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
