"""Core Runtime support for portable operation nodes."""

import pytest

from prototype.runtime import create_session
from prototype.runtime.backends.core_runtime import CoreRuntimeEvaluator
from prototype.syntax.core import (
    BinaryOp,
    Bind,
    BooleanOp,
    CompareOp,
    Literal,
    Module,
    UnaryOp,
)


def test_core_runtime_evaluates_binary_operations():
    backend = CoreRuntimeEvaluator()
    core = Module(
        body=(
            Bind(
                name="x",
                value=BinaryOp(
                    left=Literal(value=1),
                    op="+",
                    right=Literal(value=2),
                ),
            ),
        )
    )

    result = backend.evaluate(core)

    assert result.bindings["x"] == 3


def test_core_runtime_evaluates_unary_compare_and_boolean_operations():
    backend = CoreRuntimeEvaluator()
    core = Module(
        body=(
            Bind(name="neg", value=UnaryOp(op="-", operand=Literal(value=5))),
            Bind(
                name="cmp",
                value=CompareOp(
                    left=Literal(value=1),
                    ops=("<", "<="),
                    comparators=(Literal(value=2), Literal(value=2)),
                ),
            ),
            Bind(
                name="choice",
                value=BooleanOp(
                    op="or",
                    values=(Literal(value=0), Literal(value="fallback")),
                ),
            ),
        )
    )

    result = backend.evaluate(core)

    assert result.bindings["neg"] == -5
    assert result.bindings["cmp"] is True
    assert result.bindings["choice"] == "fallback"


def test_core_runtime_session_can_run_simple_expression_program():
    session = create_session(mode="nomi", eval_backend="core-runtime")

    result = session.run(source="x = 1 + 2\ny = x < 5\n")

    assert result.ok
    assert result.bindings["x"] == 3
    assert result.bindings["y"] is True


@pytest.mark.parametrize(
    ("source", "expected"),
    (
        ("x = not False\n", True),
        ("x = 0 or 4\n", 4),
        ("x = 1 and 4\n", 4),
        ("x = 1 < 2 < 3\n", True),
    ),
)
def test_core_runtime_session_runs_operation_sources(source, expected):
    session = create_session(mode="nomi", eval_backend="core-runtime")

    result = session.run(source=source)

    assert result.ok
    assert result.bindings["x"] == expected
