"""Central rules for which span attribute keys must never appear in log payloads.

OpenTelemetry attribute keys are matched case-insensitively for common secret-like
substrings. This module is the single source for that policy; see
**docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md** §5.
"""

from __future__ import annotations

from typing import Any

# Substrings (lowercase) — illustrative list extended only via spec maintenance.
_SENSITIVE_KEY_SUBSTRINGS: tuple[str, ...] = (
    "authorization",
    "password",
    "secret",
    "token",
    "api_key",
    "apikey",
    "bearer",
    "cookie",
    "credential",
)


def attribute_key_is_sensitive(key: str) -> bool:
    """Return True if *key* should be treated as sensitive for logging purposes.

    Matching is case-insensitive substring search against a fixed table
    (``_SENSITIVE_KEY_SUBSTRINGS``).
    """
    lower = key.lower()
    return any(fragment in lower for fragment in _SENSITIVE_KEY_SUBSTRINGS)


REDACTED_ATTRIBUTE_PLACEHOLDER = "[REDACTED]"


def redact_sensitive_attribute_values(attributes: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of *attributes* with sensitive keys replaced per triage IR spec.

    Values for keys where :func:`attribute_key_is_sensitive` is true become the
    literal string :data:`REDACTED_ATTRIBUTE_PLACEHOLDER`; other entries are
    unchanged. See **docs/SPEC_EXPORT_TRIAGE_METADATA.md** §3.
    """
    return {
        k: (REDACTED_ATTRIBUTE_PLACEHOLDER if attribute_key_is_sensitive(str(k)) else v)
        for k, v in attributes.items()
    }
