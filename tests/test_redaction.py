"""Tests for ``replayt_otel_span_exporter.redaction``."""

from replayt_otel_span_exporter.redaction import (
    attribute_key_is_sensitive,
    redact_sensitive_attribute_values,
)


def test_attribute_key_is_sensitive_matches_password_substring():
    assert attribute_key_is_sensitive("user.password") is True


def test_attribute_key_is_sensitive_case_insensitive():
    assert attribute_key_is_sensitive("X-Authorization-Token") is True


def test_attribute_key_is_sensitive_non_match():
    assert attribute_key_is_sensitive("http.route") is False


def test_redact_sensitive_attribute_values_replaces_sensitive_keys_only():
    out = redact_sensitive_attribute_values(
        {"safe": "ok", "user.password": "secret", "replayt.workflow_id": "wf-1"}
    )
    assert out["safe"] == "ok"
    assert out["user.password"] == "[REDACTED]"
    assert out["replayt.workflow_id"] == "wf-1"
