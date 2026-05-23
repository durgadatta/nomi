"""Portable runtime values for Core IR eval backends.

These dataclasses are the Python reference shape for future native backends.
The evaluator may be implemented in Python, but language values should cross
backend boundaries as tagged Nomi values rather than raw host primitives.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Mapping

if TYPE_CHECKING:
    from prototype.runtime.backends.environment import Frame
    from prototype.syntax.core import Module


@dataclass(frozen=True, slots=True)
class Value:
    """Base class for all Core Runtime values."""


@dataclass(frozen=True, slots=True)
class IntValue(Value):
    value: int


@dataclass(frozen=True, slots=True)
class FloatValue(Value):
    value: float


@dataclass(frozen=True, slots=True)
class BoolValue(Value):
    value: bool


@dataclass(frozen=True, slots=True)
class StrValue(Value):
    value: str


@dataclass(frozen=True, slots=True)
class NilValue(Value):
    """Unit/absence value at the portable runtime boundary."""


NIL = NilValue()


@dataclass(frozen=True, slots=True)
class SequenceValue(Value):
    elements: tuple[Value, ...] = ()


@dataclass(frozen=True, slots=True)
class MappingValue(Value):
    entries: Mapping[Any, Value]


@dataclass(frozen=True, slots=True)
class DataValue(Value):
    name: str
    fields: Mapping[str, Value]


@dataclass(frozen=True, slots=True)
class FunctionValue(Value):
    params: tuple[str, ...]
    body: Module | None
    closure: Frame


@dataclass(frozen=True, slots=True)
class NativeValue(Value):
    name: str
    callable: Callable[..., Any]


@dataclass(frozen=True, slots=True)
class ErrorValue(Value):
    message: str
    payload: Value | None = None


def box_value(value: Any) -> Value:
    """Wrap a host value in the reference runtime value system."""
    if isinstance(value, Value):
        return value
    if value is None:
        return NIL
    if isinstance(value, bool):
        return BoolValue(value)
    if isinstance(value, int):
        return IntValue(value)
    if isinstance(value, float):
        return FloatValue(value)
    if isinstance(value, str):
        return StrValue(value)
    if isinstance(value, (list, tuple)):
        return SequenceValue(tuple(box_value(item) for item in value))
    if isinstance(value, dict):
        return MappingValue(
            {
                key: box_value(item_value)
                for key, item_value in value.items()
            }
        )
    if callable(value):
        name = getattr(value, "__name__", type(value).__name__)
        return NativeValue(name=str(name), callable=value)
    raise TypeError(f"Cannot box {type(value).__name__} as a Core Runtime value")


def unbox_value(value: Value) -> Any:
    """Convert a runtime value back to a host value at the API boundary."""
    if isinstance(value, BoolValue):
        return value.value
    if isinstance(value, IntValue):
        return value.value
    if isinstance(value, FloatValue):
        return value.value
    if isinstance(value, StrValue):
        return value.value
    if isinstance(value, NilValue):
        return None
    if isinstance(value, SequenceValue):
        return [unbox_value(item) for item in value.elements]
    if isinstance(value, MappingValue):
        return {
            key: unbox_value(item_value)
            for key, item_value in value.entries.items()
        }
    if isinstance(value, DataValue):
        return {
            value.name: {
                name: unbox_value(field_value)
                for name, field_value in value.fields.items()
            }
        }
    if isinstance(value, FunctionValue):
        return f"<function ({', '.join(value.params)})>"
    if isinstance(value, NativeValue):
        return value.callable
    if isinstance(value, ErrorValue):
        raise RuntimeError(value.message)
    raise TypeError(f"Cannot unbox {type(value).__name__}")


def is_truthy(value: Value) -> bool:
    """Truthiness used by the portable evaluator."""
    if isinstance(value, BoolValue):
        return value.value
    if isinstance(value, NilValue):
        return False
    if isinstance(value, IntValue):
        return value.value != 0
    if isinstance(value, FloatValue):
        return value.value != 0.0
    if isinstance(value, StrValue):
        return value.value != ""
    if isinstance(value, SequenceValue):
        return bool(value.elements)
    if isinstance(value, MappingValue):
        return bool(value.entries)
    return True
