"""Contracts for portable Core Runtime control-flow signals."""

from prototype.runtime.backends.control_flow import (
    BreakSignal,
    ContinueSignal,
    ControlFlow,
    ReturnSignal,
    YieldSignal,
)
from prototype.runtime.backends.values import IntValue


def test_return_signal_is_explicit_control_flow():
    signal = ReturnSignal(IntValue(42))

    assert isinstance(signal, ControlFlow)
    assert signal.value == IntValue(42)


def test_loop_control_signals_are_explicit_control_flow():
    assert isinstance(BreakSignal(), ControlFlow)
    assert isinstance(ContinueSignal(), ControlFlow)


def test_yield_signal_carries_value():
    signal = YieldSignal(IntValue(7))

    assert isinstance(signal, ControlFlow)
    assert signal.value == IntValue(7)
