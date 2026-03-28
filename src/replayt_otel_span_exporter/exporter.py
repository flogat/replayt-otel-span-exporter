"""OpenTelemetry ``SpanExporter`` that materializes ``PreparedSpanRecord`` instances."""

from __future__ import annotations

import logging
import threading
from collections.abc import Sequence

from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from opentelemetry.trace import format_span_id, format_trace_id

from replayt_otel_span_exporter.records import (
    PreparedSpanRecord,
    prepared_span_record_from_readable,
)
from replayt_otel_span_exporter.redaction import attribute_key_is_sensitive

_LOGGER = logging.getLogger(__name__)


def _log_export_failure(
    exc: BaseException,
    *,
    span_count: int,
    failed_span_index: int | None,
    span: object | None,
) -> None:
    """Emit ERROR with exception info and safe structured fields (no attribute maps)."""
    extra: dict[str, object] = {
        "span_count": span_count,
        "exc_type": type(exc).__name__,
    }
    if failed_span_index is not None:
        extra["failed_span_index"] = failed_span_index
    if isinstance(span, ReadableSpan):
        ctx = span.context
        if ctx is not None and ctx.is_valid:
            extra["trace_id"] = format_trace_id(ctx.trace_id)
            extra["span_id"] = format_span_id(ctx.span_id)
        else:
            extra["trace_id"] = format_trace_id(0)
            extra["span_id"] = format_span_id(0)
        extra["span_name"] = span.name
        extra["span_kind"] = span.kind.name
        attrs = span.attributes
        if attrs:
            extra["sensitive_attribute_keys_present"] = any(
                attribute_key_is_sensitive(str(k)) for k in attrs
            )
    _LOGGER.error(
        "Span export failed while preparing records",
        extra=extra,
        exc_info=exc,
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
    down by exporter bugs. Failures are logged at ERROR under
    ``replayt_otel_span_exporter.exporter`` with ``exc_info`` set; see
    **docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md** and README **Export failures**.
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
        span_count = len(spans)
        try:
            with self._lock:
                if self._shutdown:
                    return SpanExportResult.SUCCESS
                new_records: list[PreparedSpanRecord] = []
                for index, span in enumerate(spans):
                    try:
                        new_records.append(prepared_span_record_from_readable(span))
                    except Exception as exc:
                        _log_export_failure(
                            exc,
                            span_count=span_count,
                            failed_span_index=index,
                            span=span,
                        )
                        return SpanExportResult.FAILURE
                self._records.extend(new_records)
            return SpanExportResult.SUCCESS
        except Exception as exc:
            _log_export_failure(
                exc,
                span_count=span_count,
                failed_span_index=None,
                span=None,
            )
            return SpanExportResult.FAILURE

    def shutdown(self) -> None:
        with self._lock:
            self._shutdown = True

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True
