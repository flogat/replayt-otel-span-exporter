"""OpenTelemetry span exporter skeleton for replayt-oriented workflows."""

from replayt_otel_span_exporter.exporter import ReplaytSpanExporter
from replayt_otel_span_exporter.records import PreparedSpanRecord

__all__ = [
    "PreparedSpanRecord",
    "ReplaytSpanExporter",
    "__version__",
]

__version__ = "0.2.0a1"
