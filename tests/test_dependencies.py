"""Smoke tests for declared runtime dependencies (integration-style boundary checks)."""


def test_opentelemetry_api_available():
    """The package depends on opentelemetry-api; ensure trace API imports."""
    from opentelemetry import trace

    assert trace is not None
