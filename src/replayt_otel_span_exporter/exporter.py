"""OpenTelemetry ``SpanExporter`` that materializes ``PreparedSpanRecord`` instances."""

from __future__ import annotations

import threading
from collections.abc import Sequence
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult

from replayt_otel_span_exporter.records import (
    PreparedSpanRecord,
    prepared_span_record_from_readable,
)


class ReplaytSpanExporter(SpanExporter):
    """Exports finished spans into an in-memory list of ``PreparedSpanRecord``.

    The **records** list is intended for tests and in-process inspection; it is
    append-only until :meth:`shutdown` is called.

    After **shutdown**, :meth:`export` returns :attr:`SpanExportResult.SUCCESS`
    without mutating **records** (no-op). :meth:`force_flush` always returns
    ``True``; there is no asynchronous export queue in this skeleton.

    :meth:`export` catches unexpected exceptions and returns
    :attr:`SpanExportResult.FAILURE` so the SDK tracing pipeline is not torn
    down by exporter bugs.
    """

    def __init__(self, records: list[PreparedSpanRecord] | None = None) -> None:
        self._records = records if records is not None else []
        self._lock = threading.Lock()
        self._shutdown = False

    @property
    def records(self) -> list[PreparedSpanRecord]:
        """Copy of prepared records exported so far (thread-safe snapshot)."""
        with self._lock:
            return list(self._records)

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        try:
            with self._lock:
                if self._shutdown:
                    return SpanExportResult.SUCCESS
                for span in spans:
                    self._records.append(prepared_span_record_from_readable(span))
            return SpanExportResult.SUCCESS
        except Exception:
            return SpanExportResult.FAILURE

    def shutdown(self) -> None:
        with self._lock:
            self._shutdown = True

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True
