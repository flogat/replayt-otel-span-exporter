def test_import():
    """Test that the package can be imported."""
    import replayt_otel_span_exporter

    assert replayt_otel_span_exporter is not None


def test_version():
    """Package version matches pyproject.toml and install metadata."""
    import importlib.metadata
    import pathlib
    import tomllib

    import replayt_otel_span_exporter as pkg

    assert hasattr(pkg, "__version__")
    root = pathlib.Path(__file__).resolve().parents[1]
    expected = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"][
        "version"
    ]
    assert pkg.__version__ == expected
    assert importlib.metadata.version("replayt-otel-span-exporter") == expected


def test_package_all_matches_public_contract():
    import replayt_otel_span_exporter as pkg

    assert set(pkg.__all__) == {
        "PreparedSpanRecord",
        "ReplaytSpanExporter",
        "__version__",
    }
