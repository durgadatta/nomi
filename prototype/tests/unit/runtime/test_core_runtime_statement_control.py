"""Core Runtime support for small statement-control nodes."""

from prototype.runtime.backends.core_runtime import CoreRuntimeEvaluator
from prototype.syntax.core import (
    Bind,
    Break,
    Literal,
    Loop,
    Module,
    NoOp,
)


def test_core_runtime_evaluates_no_op_as_nil():
    backend = CoreRuntimeEvaluator()

    result = backend.evaluate(Module(body=(NoOp(),)))

    assert result.bindings == {}


def test_core_runtime_break_exits_loop():
    backend = CoreRuntimeEvaluator()
    core = Module(
        body=(
            Bind(name="x", value=Literal(value=1)),
            Loop(
                test=Literal(value=True),
                body=Module(
                    body=(
                        Bind(name="x", value=Literal(value=2)),
                        Break(),
                        Bind(name="x", value=Literal(value=3)),
                    )
                ),
            ),
        )
    )

    result = backend.evaluate(core)

    assert result.bindings["x"] == 2
