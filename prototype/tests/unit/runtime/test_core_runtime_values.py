"""Contracts for portable Core Runtime values."""

import pytest

from prototype.runtime.backends.environment import Frame
from prototype.runtime.backends.values import (
    BoolValue,
    DataValue,
    ErrorValue,
    FloatValue,
    FunctionValue,
    IntValue,
    NIL,
    NativeValue,
    SequenceValue,
    StrValue,
    box_value,
    is_truthy,
    unbox_value,
)
from prototype.syntax.core import Module


def test_box_value_wraps_host_primitives():
    assert box_value(True) == BoolValue(True)
    assert box_value(7) == IntValue(7)
    assert box_value(1.5) == FloatValue(1.5)
    assert box_value("hi") == StrValue("hi")
    assert box_value(None) is NIL


def test_bool_boxes_before_int():
    value = box_value(False)

    assert isinstance(value, BoolValue)
    assert not isinstance(value, IntValue)


def test_box_value_wraps_sequences_recursively():
    value = box_value([1, "two", None])

    assert value == SequenceValue((IntValue(1), StrValue("two"), NIL))
    assert unbox_value(value) == [1, "two", None]


def test_box_value_wraps_callable_as_native_value():
    def sample():
        return 1

    value = box_value(sample)

    assert isinstance(value, NativeValue)
    assert value.name == "sample"
    assert unbox_value(value) is sample


def test_unbox_data_value_uses_named_record_shape():
    value = DataValue(
        name="Point",
        fields={"x": IntValue(1), "y": IntValue(2)},
    )

    assert unbox_value(value) == {"Point": {"x": 1, "y": 2}}


def test_unbox_function_value_is_stable_debug_string():
    value = FunctionValue(
        params=("x",),
        body=Module(body=()),
        closure=Frame(),
    )

    assert unbox_value(value) == "<function (x)>"


def test_unbox_error_value_raises_runtime_error():
    with pytest.raises(RuntimeError, match="boom"):
        unbox_value(ErrorValue("boom"))


@pytest.mark.parametrize(
    ("value", "expected"),
    (
        (BoolValue(False), False),
        (BoolValue(True), True),
        (NIL, False),
        (IntValue(0), False),
        (IntValue(1), True),
        (FloatValue(0.0), False),
        (StrValue(""), False),
        (StrValue("x"), True),
        (SequenceValue(()), False),
        (SequenceValue((IntValue(1),)), True),
    ),
)
def test_is_truthy(value, expected):
    assert is_truthy(value) is expected
