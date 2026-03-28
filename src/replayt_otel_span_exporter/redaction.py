"""Central rules for which span attribute keys must never appear in log payloads.

OpenTelemetry attribute keys are matched case-insensitively for common secret-like
substrings. This module is the single source for that policy; see
**docs/SPEC_SPAN_EXPORT_FAILURE_HANDLING.md** §5.
"""

from __future__ import annotations

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
