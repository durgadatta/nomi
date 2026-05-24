"""Tests for the portable Core Runtime backend."""

import pytest

from prototype.interpreter.python.interpreter import Interpreter as PyInterpreter
from prototype.runtime.backends import get_eval_backend, render_eval_backend_table
from prototype.runtime.backends.core_runtime import (
    CORE_RUNTIME_SPEC,
    CoreRuntimeEvaluator,
)
from prototype.runtime.backends.python_ast import PythonAstBackend
from prototype.syntax.core import (
    Bind,
    Branch,
    Call,
    ConstructData,
    Diagnostic,
    Function,
    GetField,
    Literal,
    Load,
    Loop,
    Match,
    Module,
    PatternTest,
    Return,
    Sequence,
    Spread,
)


def test_core_runtime_is_registered_but_not_selectable():
    backend = get_eval_backend("core-runtime")

    assert backend.spec is CORE_RUNTIME_SPEC
    assert CORE_RUNTIME_SPEC.capabilities.evaluates_native_ir is True
    assert CORE_RUNTIME_SPEC.capabilities.selectable_for_execution is False
    assert "core-runtime" in render_eval_backend_table()


def test_core_runtime_evaluates_bindings():
    backend = CoreRuntimeEvaluator()
    core = Module(
        body=(
            Bind(name="x", value=Literal(value=42)),
            Bind(name="y", value=Load(name="x")),
        )
    )

    result = backend.evaluate(core)

    assert result.bindings == {"x": 42, "y": 42}


def test_core_runtime_evaluates_function_call():
    backend = CoreRuntimeEvaluator()
    core = Module(
        body=(
            Bind(
                name="identity",
                value=Function(
                    params=("x",),
                    body=Module(body=(Return(value=Load(name="x")),)),
                ),
            ),
            Bind(
                name="result",
                value=Call(func=Load(name="identity"), args=(Literal(value=42),)),
            ),
        )
    )

    result = backend.evaluate(core)

    assert result.bindings["result"] == 42
    assert result.bindings["identity"] == "<function (x)>"


def test_core_runtime_evaluates_branch():
    backend = CoreRuntimeEvaluator()
    core = Module(
        body=(
            Branch(
                test=Literal(value=False),
                then_body=Module(body=(Bind(name="x", value=Literal(value=1)),)),
                else_body=Module(body=(Bind(name="x", value=Literal(value=2)),)),
            ),
        )
    )

    result = backend.evaluate(core)

    assert result.bindings["x"] == 2


def test_core_runtime_can_display_last_expression():
    backend = CoreRuntimeEvaluator()
    core = Module(
        body=(
            Bind(name="x", value=Literal(value=7)),
            Load(name="x"),
        )
    )

    result = backend.evaluate(core, display_last_expr=True)

    assert result.has_value
    assert result.value == 7


def test_core_runtime_calls_explicit_host_functions():
    backend = CoreRuntimeEvaluator(host_calls={"add1": lambda x: x + 1})
    core = Module(
        body=(
            Bind(
                name="result",
                value=Call(func=Load(name="add1"), args=(Literal(value=4),)),
            ),
        )
    )

    result = backend.evaluate(core)

    assert result.bindings["result"] == 5
    assert "add1" in result.bindings


def test_core_runtime_rejects_missing_host_function():
    backend = CoreRuntimeEvaluator()
    core = Module(
        body=(Call(func=Load(name="missing"), args=(Literal(value=1),)),)
    )

    with pytest.raises(NameError, match="missing"):
        backend.evaluate(core)


@pytest.mark.parametrize(
    ("core", "message"),
    (
        (
            Module(body=(Diagnostic(message="bad"),)),
            "Diagnostic node: 'bad'",
        ),
        (
            Module(body=(Spread(value=Literal(value=1)),)),
            "Spread can only be evaluated inside Sequence",
        ),
        (
            Module(
                body=(
                    PatternTest(
                        pattern=Literal(value=1),
                        body=Module(body=(Literal(value="one"),)),
                    ),
                )
            ),
            "PatternTest can only be evaluated inside Match or Handle",
        ),
    ),
)
def test_core_runtime_rejects_misplaced_or_diagnostic_core(core, message):
    backend = CoreRuntimeEvaluator()

    with pytest.raises(Exception, match=message):
        backend.evaluate(core)


def test_core_runtime_evaluates_sequence_and_data_values():
    backend = CoreRuntimeEvaluator()
    core = Module(
        body=(
            Bind(
                name="items",
                value=Sequence(elements=(Literal(value=1), Literal(value=2))),
            ),
            Bind(
                name="point",
                value=ConstructData(
                    name="Point",
                    fields=(("x", Literal(value=3)), ("y", Literal(value=4))),
                ),
            ),
            Bind(
                name="x",
                value=GetField(object_=Load(name="point"), field="x"),
            ),
        )
    )

    result = backend.evaluate(core)

    assert result.bindings["items"] == [1, 2]
    assert result.bindings["point"] == {"Point": {"x": 3, "y": 4}}
    assert result.bindings["x"] == 3


def test_core_runtime_evaluates_loop_else_when_test_is_false():
    backend = CoreRuntimeEvaluator()
    core = Module(
        body=(
            Loop(
                test=Literal(value=False),
                body=Module(body=(Bind(name="x", value=Literal(value=1)),)),
                else_body=Module(body=(Bind(name="x", value=Literal(value=2)),)),
            ),
        )
    )

    result = backend.evaluate(core)

    assert result.bindings["x"] == 2


def test_core_runtime_match_literal_pattern():
    backend = CoreRuntimeEvaluator()
    core = Module(
        body=(
            Bind(
                name="result",
                value=Match(
                    subject=Literal(value=2),
                    cases=(
                        PatternTest(
                            pattern=Literal(value=1),
                            body=Module(body=(Literal(value="one"),)),
                        ),
                        PatternTest(
                            pattern=Literal(value=2),
                            body=Module(body=(Literal(value="two"),)),
                        ),
                    ),
                ),
            ),
        )
    )

    result = backend.evaluate(core)

    assert result.bindings["result"] == "two"


@pytest.mark.parametrize(
    "core",
    (
        Module(body=(Bind(name="x", value=Literal(value=1)),)),
        Module(
            body=(
                Bind(
                    name="identity",
                    value=Function(
                        params=("x",),
                        body=Module(body=(Return(value=Load(name="x")),)),
                    ),
                ),
                Bind(
                    name="result",
                    value=Call(
                        func=Load(name="identity"),
                        args=(Literal(value=42),),
                    ),
                ),
            )
        ),
        Module(
            body=(
                Branch(
                    test=Literal(value=True),
                    then_body=Module(body=(Bind(name="x", value=Literal(value=1)),)),
                    else_body=Module(body=(Bind(name="x", value=Literal(value=2)),)),
                ),
            )
        ),
        Module(
            body=(
                Bind(
                    name="items",
                    value=Sequence(elements=(Literal(value=1), Literal(value=2))),
                ),
            )
        ),
        Module(
            body=(
                Loop(
                    test=Literal(value=False),
                    body=Module(body=(Bind(name="x", value=Literal(value=1)),)),
                    else_body=Module(body=(Bind(name="x", value=Literal(value=2)),)),
                ),
            )
        ),
    ),
)
def test_core_runtime_matches_python_ast_backend_for_basic_subset(core):
    core_runtime = CoreRuntimeEvaluator()
    python_ast = PythonAstBackend(PyInterpreter)

    core_result = core_runtime.evaluate(core)
    python_result = python_ast.evaluate(core)

    comparable = {
        name: value
        for name, value in python_result.bindings.items()
        if not callable(value)
    }
    assert {
        name: core_result.bindings[name]
        for name in comparable
    } == comparable
