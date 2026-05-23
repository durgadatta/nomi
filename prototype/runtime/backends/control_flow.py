"""Explicit control-flow signals for portable Core Runtime backends."""

from __future__ import annotations

from dataclasses import dataclass

from prototype.runtime.backends.values import Value


@dataclass(frozen=True, slots=True)
class ControlFlow:
    """Base class for language-level control-flow signals."""


@dataclass(frozen=True, slots=True)
class ReturnSignal(ControlFlow):
    value: Value


@dataclass(frozen=True, slots=True)
class BreakSignal(ControlFlow):
    pass


@dataclass(frozen=True, slots=True)
class ContinueSignal(ControlFlow):
    pass


@dataclass(frozen=True, slots=True)
class YieldSignal(ControlFlow):
    value: Value
