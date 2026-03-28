"""Prepared span intermediate representation (IR) for replayt-oriented workflows.

``PreparedSpanRecord`` is the stable, documented shape produced from finished
OpenTelemetry SDK ``ReadableSpan`` instances. See module docstrings on each
field and on ``serialize_attribute_value`` for encoding rules.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.trace import format_span_id, format_trace_id
from opentelemetry.util import types

from replayt_otel_span_exporter.redaction import redact_sensitive_attribute_values

# Canonical OpenTelemetry attribute keys (case-sensitive); see SPEC_EXPORT_TRIAGE_METADATA §2.1.
WORKFLOW_ID_ATTRIBUTE_KEY = "replayt.workflow_id"
STEP_ID_ATTRIBUTE_KEY = "replayt.step_id"


def serialize_attribute_value(value: types.AttributeValue) -> Any:
    """Convert an OpenTelemetry attribute value to a JSON-friendly Python value.

    - ``str``, ``bool``, ``int``, and ``float`` are returned unchanged.
    - Homogeneous ``Sequence`` entries of those scalars are returned as
      ``list`` with each element serialized the same way.
    - ``bytes`` are decoded as UTF-8; invalid UTF-8 bytes are decoded with
      replacement characters (``errors="replace"``).
    - Any other type is converted with ``str()`` so the result is a string
      (nested mappings or mixed-type sequences are not part of the typed
      ``AttributeValue`` union but may appear from future SDK data).
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, float):
        return value
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, (list, tuple)):
        return [serialize_attribute_value(item) for item in value]
    return str(value)


def prepared_attributes_from_readable(
    attributes: Mapping[str, types.AttributeValue],
) -> dict[str, Any]:
    """Build a plain dict of JSON-style attribute keys to serialized values."""
    return {str(k): serialize_attribute_value(v) for k, v in attributes.items()}


def triage_id_from_serialized_value(serialized: Any) -> str | None:
    """Coerce a serialized attribute value to a triage id string, or ``None`` if empty.

    Per **docs/SPEC_EXPORT_TRIAGE_METADATA.md** §2.2–§2.3: values pass through
    :func:`serialize_attribute_value` first; non-strings are coerced with
    ``str(...)``. An empty string after coercion becomes ``None``. A missing
    attribute yields ``serialized is None`` from ``dict.get`` and maps to
    ``None``.
    """
    if serialized is None:
        return None
    if isinstance(serialized, str):
        coerced = serialized
    else:
        coerced = str(serialized)
    return coerced if coerced else None


@dataclass(frozen=True, slots=True)
class PreparedSpanRecord:
    """Normalized span snapshot for replayt-facing consumers (skeleton IR).

    **trace_id** / **span_id**: Lowercase hexadecimal strings, zero-padded to
    32 and 16 characters respectively, matching ``opentelemetry.trace``
    ``format_trace_id`` / ``format_span_id``. Invalid or missing span context
    uses all-zero IDs.

    **kind**: The name of the OpenTelemetry ``SpanKind`` enum member (e.g.
    ``\"INTERNAL\"``, ``\"SERVER\"``).

    **start_time_unix_nano** / **end_time_unix_nano**: Integer nanoseconds since
    Unix epoch, aligned with ``ReadableSpan`` time fields. Missing times are
    stored as ``0`` so the record always holds integers.

    **attributes**: String keys mapped to JSON-friendly values; see
    ``serialize_attribute_value``. Values for keys classified as sensitive by
    :func:`replayt_otel_span_exporter.redaction.attribute_key_is_sensitive`
    are replaced with the literal ``"[REDACTED]"`` (see **SPEC_EXPORT_TRIAGE_METADATA** §3).

    **workflow_id** / **step_id**: First-class triage fields from span attributes
    ``replayt.workflow_id`` and ``replayt.step_id`` (exact keys), each ``None``
    when absent or empty after coercion.
    """

    trace_id: str
    span_id: str
    name: str
    kind: str
    start_time_unix_nano: int
    end_time_unix_nano: int
    attributes: dict[str, Any]
    workflow_id: str | None
    step_id: str | None


def prepared_span_record_from_readable(span: ReadableSpan) -> PreparedSpanRecord:
    """Map a finished ``ReadableSpan`` to a ``PreparedSpanRecord``."""
    ctx = span.context
    if ctx is not None and ctx.is_valid:
        trace_id = format_trace_id(ctx.trace_id)
        span_id = format_span_id(ctx.span_id)
    else:
        trace_id = format_trace_id(0)
        span_id = format_span_id(0)

    start = span.start_time
    end = span.end_time
    if start is None:
        start = 0
    if end is None:
        end = 0

    serialized_attrs = prepared_attributes_from_readable(span.attributes)
    workflow_id = triage_id_from_serialized_value(
        serialized_attrs.get(WORKFLOW_ID_ATTRIBUTE_KEY)
    )
    step_id = triage_id_from_serialized_value(
        serialized_attrs.get(STEP_ID_ATTRIBUTE_KEY)
    )
    redacted_attrs = redact_sensitive_attribute_values(serialized_attrs)
    # Canonical keys must match triage string form (§2.4), not raw serialized scalars.
    if workflow_id is not None:
        redacted_attrs[WORKFLOW_ID_ATTRIBUTE_KEY] = workflow_id
    if step_id is not None:
        redacted_attrs[STEP_ID_ATTRIBUTE_KEY] = step_id

    return PreparedSpanRecord(
        trace_id=trace_id,
        span_id=span_id,
        name=span.name,
        kind=span.kind.name,
        start_time_unix_nano=start,
        end_time_unix_nano=end,
        attributes=redacted_attrs,
        workflow_id=workflow_id,
        step_id=step_id,
    )
