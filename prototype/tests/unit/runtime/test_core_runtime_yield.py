"""Core Runtime yield signal support."""

import pytest

from prototype.runtime.backends.core_runtime import CoreRuntimeEvaluator
from prototype.syntax.core import Literal, Module, Yield


def test_core_runtime_rejects_module_level_yield_signal():
    backend = CoreRuntimeEvaluator()

    with pytest.raises(RuntimeError, match="YieldSignal"):
        backend.evaluate(Module(body=(Yield(value=Literal(value=1)),)))
