"""OpenTelemetry ``SpanExporter`` that materializes ``PreparedSpanRecord`` instances."""

from __future__ import annotations

import logging
import threading
from collections.abc import Sequence
from typing import Literal, NotRequired, Protocol, TypedDict

from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from opentelemetry.trace import format_span_id, format_trace_id

from replayt_otel_span_exporter.records import (
    PreparedSpanRecord,
    prepared_span_record_from_readable,
)
from replayt_otel_span_exporter.redaction import attribute_key_is_sensitive

# Log-pipeline bounds for untrusted strings (Unicode code points); see
# docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md §5.4.
_MAX_LOG_EXCEPTION_MESSAGE_CHARS = 1024
_MAX_LOG_SPAN_NAME_CHARS = 256

_LOGGER = logging.getLogger(__name__)
_AUDIT_LOGGER = logging.getLogger(f"{__name__}.audit")


class ExportCommitHook(Protocol):
    """Integrator policy gate: allow or deny committing a prepared batch (see SPEC_SPAN_EXPORT_APPROVAL_UX)."""

    def __call__(
        self,
        prepared: Sequence[PreparedSpanRecord],
        *,
        span_count: int,
    ) -> Literal["allow", "deny"]:
        ...


class ExportAuditEvent(TypedDict):
    """Allow-listed audit fields for export commit decisions (no full attribute maps)."""

    decision: Literal["allow", "deny"]
    prepared_count: int
    span_count: int
    trace_id: NotRequired[str]
    span_id: NotRequired[str]
    workflow_id: NotRequired[str]
    step_id: NotRequired[str]


class ExportAuditCallback(Protocol):
    def __call__(self, event: ExportAuditEvent) -> None:
        ...


def _sanitize_log_string(value: str | None, max_chars: int) -> str:
    """Strip C0/C1 controls (replace with space), then truncate by code points.

    Used for exception text, span names, and other integrator-supplied strings
    placed in export-failure log lines or string ``extra=`` fields. Stack traces
    from ``exc_info`` are not passed through this helper. See
    **docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md** §5.4.
    """
    if not value:
        return ""
    out_chars: list[str] = []
    for ch in value:
        o = ord(ch)
        if o <= 0x1F or 0x7F <= o <= 0x9F:
            out_chars.append(" ")
        else:
            out_chars.append(ch)
    s = "".join(out_chars)
    if len(s) > max_chars:
        s = s[:max_chars]
    return s


def _build_audit_event(
    decision: Literal["allow", "deny"],
    prepared: Sequence[PreparedSpanRecord],
    *,
    span_count: int,
) -> ExportAuditEvent:
    event: ExportAuditEvent = {
        "decision": decision,
        "prepared_count": len(prepared),
        "span_count": span_count,
    }
    if prepared:
        first = prepared[0]
        event["trace_id"] = first.trace_id
        event["span_id"] = first.span_id
        if first.workflow_id is not None:
            event["workflow_id"] = first.workflow_id
        if first.step_id is not None:
            event["step_id"] = first.step_id
    return event


def _log_approval_hook_failure(
    exc: BaseException,
    *,
    span_count: int,
    prepared_count: int,
) -> None:
    exc_message = _sanitize_log_string(str(exc), _MAX_LOG_EXCEPTION_MESSAGE_CHARS)
    extra: dict[str, object] = {
        "span_count": span_count,
        "prepared_count": prepared_count,
        "exc_type": type(exc).__name__,
        "exc_message": exc_message,
    }
    _LOGGER.error(
        "Span export failed in approval hook: %s",
        exc_message,
        extra=extra,
        exc_info=exc,
    )


def _log_export_failure(
    exc: BaseException,
    *,
    span_count: int,
    failed_span_index: int | None,
    span: object | None,
) -> None:
    """Emit ERROR with exception info and safe structured fields (no attribute maps)."""
    exc_message = _sanitize_log_string(str(exc), _MAX_LOG_EXCEPTION_MESSAGE_CHARS)
    extra: dict[str, object] = {
        "span_count": span_count,
        "exc_type": type(exc).__name__,
        "exc_message": exc_message,
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
        extra["span_name"] = _sanitize_log_string(
            span.name or "", _MAX_LOG_SPAN_NAME_CHARS
        )
        extra["span_kind"] = span.kind.name
        attrs = span.attributes
        if attrs:
            extra["sensitive_attribute_keys_present"] = any(
                attribute_key_is_sensitive(str(k)) for k in attrs
            )
    _LOGGER.error(
        "Span export failed while preparing records: %s",
        exc_message,
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

    Optional **on_export_commit** runs after mapping to :class:`PreparedSpanRecord`
    and before appending to **records**. If it returns ``"deny"``, no records
    from that call are appended and :meth:`export` still returns
    :attr:`SpanExportResult.SUCCESS` (policy outcome, not transport failure). See
    **docs/SPEC_SPAN_EXPORT_APPROVAL_UX.md**.

    :meth:`export` catches unexpected exceptions and returns
    :attr:`SpanExportResult.FAILURE` so the SDK tracing pipeline is not torn
    down by exporter bugs. Failures are logged at ERROR under
    ``replayt_otel_span_exporter.exporter`` with ``exc_info`` set; see
    **docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md** and README **Export failures**.
    """

    def __init__(
        self,
        records: list[PreparedSpanRecord] | None = None,
        *,
        on_export_commit: ExportCommitHook | None = None,
        on_export_audit: ExportAuditCallback | None = None,
    ) -> None:
        self._records = records if records is not None else []
        self._lock = threading.Lock()
        self._shutdown = False
        self._on_export_commit = on_export_commit
        self._on_export_audit = on_export_audit

    @property
    def records(self) -> list[PreparedSpanRecord]:
        """Copy of prepared records exported so far (thread-safe snapshot)."""
        with self._lock:
            return list(self._records)

    def _emit_export_audit(
        self,
        decision: Literal["allow", "deny"],
        prepared: Sequence[PreparedSpanRecord],
        *,
        span_count: int,
    ) -> None:
        event = _build_audit_event(decision, prepared, span_count=span_count)
        if decision == "deny":
            msg = (
                "Span export batch denied by integrator policy (not an OpenTelemetry "
                "export failure); prepared records were not committed to the buffer"
            )
        else:
            msg = "Span export batch allowed; prepared records committed to the buffer"
        _AUDIT_LOGGER.info(msg, extra=dict(event))
        if self._on_export_audit is not None:
            self._on_export_audit(event)

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

                if self._on_export_commit is not None:
                    try:
                        decision = self._on_export_commit(
                            new_records,
                            span_count=span_count,
                        )
                    except Exception as exc:
                        _log_approval_hook_failure(
                            exc,
                            span_count=span_count,
                            prepared_count=len(new_records),
                        )
                        return SpanExportResult.FAILURE
                    if decision not in ("allow", "deny"):
                        bad = ValueError(
                            "approval hook must return 'allow' or 'deny', "
                            f"got {decision!r}",
                        )
                        _log_approval_hook_failure(
                            bad,
                            span_count=span_count,
                            prepared_count=len(new_records),
                        )
                        return SpanExportResult.FAILURE
                    try:
                        self._emit_export_audit(
                            decision,
                            new_records,
                            span_count=span_count,
                        )
                    except Exception as exc:
                        _log_export_failure(
                            exc,
                            span_count=span_count,
                            failed_span_index=None,
                            span=None,
                        )
                        return SpanExportResult.FAILURE
                    if decision == "deny":
                        return SpanExportResult.SUCCESS

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
