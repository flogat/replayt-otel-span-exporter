"""Unit tests for ``PreparedSpanRecord`` helpers."""

from replayt_otel_span_exporter.records import serialize_attribute_value


def test_serialize_attribute_value_scalars_and_sequences():
    assert serialize_attribute_value("x") == "x"
    assert serialize_attribute_value(True) is True
    assert serialize_attribute_value(42) == 42
    assert serialize_attribute_value(3.5) == 3.5
    assert serialize_attribute_value([1, 2, 3]) == [1, 2, 3]
    assert serialize_attribute_value(("a", "b")) == ["a", "b"]


def test_serialize_attribute_value_bytes_utf8():
    assert serialize_attribute_value(b"hello") == "hello"


def test_serialize_attribute_value_unknown_type_stringifies():
    class Odd:
        def __str__(self) -> str:
            return "odd"

    assert serialize_attribute_value(Odd()) == "odd"  # type: ignore[arg-type]
