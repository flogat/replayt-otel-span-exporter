"""Tests for ``replayt_otel_span_exporter.redaction``."""

from replayt_otel_span_exporter.redaction import attribute_key_is_sensitive


def test_attribute_key_is_sensitive_matches_password_substring():
    assert attribute_key_is_sensitive("user.password") is True


def test_attribute_key_is_sensitive_case_insensitive():
    assert attribute_key_is_sensitive("X-Authorization-Token") is True


def test_attribute_key_is_sensitive_non_match():
    assert attribute_key_is_sensitive("http.route") is False
