def test_import():
    """Test that the package can be imported."""
    import replayt_otel_span_exporter

    assert replayt_otel_span_exporter is not None


def test_version():
    """Test that the package has a version."""
    import replayt_otel_span_exporter

    # The package should have a __version__ attribute
    assert hasattr(replayt_otel_span_exporter, "__version__")
    assert replayt_otel_span_exporter.__version__ == "0.1.0"


def test_package_all_matches_public_contract():
    import replayt_otel_span_exporter as pkg

    assert set(pkg.__all__) == {
        "PreparedSpanRecord",
        "ReplaytSpanExporter",
        "__version__",
    }
