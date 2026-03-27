"""Smoke tests for declared runtime dependencies (integration-style boundary checks)."""


def test_opentelemetry_api_available():
    """The package depends on opentelemetry-api; ensure trace API imports."""
    from opentelemetry import trace

    assert trace is not None


def test_opentelemetry_sdk_export_surface():
    """The package depends on opentelemetry-sdk for SpanExporter wiring."""
    from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult

    assert SpanExporter is not None
    assert SpanExportResult.SUCCESS is not None
