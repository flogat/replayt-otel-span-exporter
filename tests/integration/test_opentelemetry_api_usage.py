"""Integration-style checks against the OpenTelemetry trace API (runtime dependency)."""


def test_tracer_and_span_context():
    from opentelemetry import trace

    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("ci-integration-span") as span:
        assert span is not None
        assert span.get_span_context() is not None
