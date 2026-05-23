"""Tests for the Core IR direct evaluator backend."""

import pytest

from prototype.runtime.backends.core_direct import CoreDirectEvaluator, CORE_DIRECT_SPEC
from prototype.syntax.core import (
    Bind,
    Branch,
    Call,
    Function,
    Literal,
    Load,
    Module,
    Return,
)


def test_spec_not_selectable_for_execution():
    assert CORE_DIRECT_SPEC.capabilities.selectable_for_execution is False
    assert CORE_DIRECT_SPEC.capabilities.evaluates_native_ir is True
    assert CORE_DIRECT_SPEC.name == "core-direct"
    assert CORE_DIRECT_SPEC.status == "prototype"


def test_evaluates_literal_module():
    backend = CoreDirectEvaluator()
    core = Module(body=(Literal(value=42),))
    result = backend.evaluate(core)
    assert result.bindings == {}


def test_evaluates_bind():
    backend = CoreDirectEvaluator()
    core = Module(body=(Bind(name="x", value=Literal(value=42)),))
    result = backend.evaluate(core)
    assert result.bindings == {"x": 42}


def test_evaluates_load():
    backend = CoreDirectEvaluator()
    core = Module(body=(
        Bind(name="x", value=Literal(value=7)),
        Bind(name="y", value=Load(name="x")),
    ))
    result = backend.evaluate(core)
    assert result.bindings == {"x": 7, "y": 7}


def test_evaluates_call_python_function():
    backend = CoreDirectEvaluator()
    core = Module(body=(
        Call(
            func=Load(name="print"),
            args=(Literal(value="hello"),),
        ),
    ))
    result = backend.evaluate(core)
    assert isinstance(result.bindings, dict)


def test_evaluates_function_def_and_call():
    backend = CoreDirectEvaluator()
    core = Module(body=(
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
    ))
    result = backend.evaluate(core)
    assert result.bindings.get("result") == 42


def test_evaluates_branch_true():
    backend = CoreDirectEvaluator()
    core = Module(body=(
        Branch(
            test=Literal(value=True),
            then_body=Module(body=(Bind(name="x", value=Literal(value=1)),)),
            else_body=Module(body=(Bind(name="x", value=Literal(value=0)),)),
        ),
    ))
    result = backend.evaluate(core)
    assert result.bindings.get("x") == 1


def test_evaluates_branch_false():
    backend = CoreDirectEvaluator()
    core = Module(body=(
        Branch(
            test=Literal(value=False),
            then_body=Module(body=(Bind(name="x", value=Literal(value=1)),)),
            else_body=Module(body=(Bind(name="x", value=Literal(value=0)),)),
        ),
    ))
    result = backend.evaluate(core)
    assert result.bindings.get("x") == 0


def test_rejects_invalid_core():
    from prototype.syntax.core import Diagnostic

    backend = CoreDirectEvaluator()
    core = Module(body=(Diagnostic(message="bad"),))
    with pytest.raises(Exception):
        backend.evaluate(core)


def test_function_closure_preserves_outer_env():
    """Function should not mutate the outer environment through its params."""
    backend = CoreDirectEvaluator()
    core = Module(body=(
        Bind(name="outer", value=Literal(value=10)),
        Bind(
            name="f",
            value=Function(
                params=("x",),
                body=Module(body=(
                    Bind(name="x", value=Literal(value=99)),
                )),
            ),
        ),
        Call(func=Load(name="f"), args=(Literal(value=0),)),
    ))
    result = backend.evaluate(core)
    assert result.bindings.get("outer") == 10
    assert result.bindings.get("x") not in result.bindings
