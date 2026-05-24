"""Tests for the Python AST eval backend."""

import ast as py_ast

import pytest

from prototype.interpreter.python.interpreter import Interpreter as PyInterpreter
from prototype.runtime.backends import EvalBackendCapabilities
from prototype.runtime.backends.python_ast import (
    PythonAstBackend,
    PYTHON_AST_BACKEND_SPEC,
    make_python_ast_backend_for_mode,
)
from prototype.syntax.core import (
    Bind,
    Call,
    Literal,
    Load,
    Module,
    core_to_python_ast,
    lower_python_ast_to_core,
)


def test_spec_has_correct_capabilities():
    caps = PYTHON_AST_BACKEND_SPEC.capabilities
    assert caps.lowers_to_python_ast is True
    assert caps.supports_full_language is True
    assert caps.supports_blocks is True
    assert caps.selectable_for_session_execution is True
    assert caps.default_for_cli is True
    assert caps.selectable_for_execution is True


def test_spec_name_is_python_ast():
    assert PYTHON_AST_BACKEND_SPEC.name == "python-ast"
    assert PYTHON_AST_BACKEND_SPEC.status == "implemented"


def test_backend_evaluates_simple_bind():
    backend = PythonAstBackend(PyInterpreter)
    core = Module(body=(Bind(name="x", value=Literal(value=42)),))
    result = backend.evaluate(core)
    assert result.bindings.get("x") == 42


def test_backend_evaluates_call():
    backend = PythonAstBackend(PyInterpreter)
    core = Module(
        body=(
            Call(
                func=Load(name="print"),
                args=(Literal(value="hello"),),
            ),
        )
    )
    result = backend.evaluate(core)
    assert isinstance(result.bindings, dict)


def test_backend_last_expr_display_no_value():
    """display_last_expr=True but interpreter returns None — no last-value support yet."""
    backend = PythonAstBackend(PyInterpreter)
    core = Module(body=(Literal(value=99),))
    result = backend.evaluate(core, display_last_expr=True)
    assert result.has_value is False
    assert result.value is None


def test_backend_render_lowered():
    backend = PythonAstBackend(PyInterpreter)
    core = Module(body=(Bind(name="x", value=Literal(value=1)),))
    output = backend.render_lowered(core)
    assert "Assign" in output
    assert "Constant(value=1)" in output


def test_backend_rejects_invalid_core():
    from prototype.syntax.core import Diagnostic

    backend = PythonAstBackend(PyInterpreter)
    core = Module(body=(Diagnostic(message="bad"),))
    with pytest.raises(Exception):
        backend.evaluate(core)


def test_roundtrip_through_backend():
    """Parse to Python AST, lower to Core, evaluate through backend."""
    src = "x = 42\ny = x\n"
    core = lower_python_ast_to_core(py_ast.parse(src))
    backend = PythonAstBackend(PyInterpreter)
    result = backend.evaluate(core)
    assert result.bindings.get("x") == 42
    assert result.bindings.get("y") == 42


def test_backend_evaluates_function_def():
    src = (
        "def identity(x):\n"
        "    return x\n"
        "x = identity(42)\n"
    )
    core = lower_python_ast_to_core(py_ast.parse(src))
    backend = PythonAstBackend(PyInterpreter)
    result = backend.evaluate(core)
    assert result.bindings.get("x") == 42


def test_make_backend_for_mode_constructs():
    from prototype.runtime.modes import get_mode_spec

    for mode_name in ("python", "nomi", "reduced"):
        mode_spec = get_mode_spec(mode_name)
        backend = make_python_ast_backend_for_mode(mode_spec)
        assert isinstance(backend, PythonAstBackend)
        # Quick smoke: evaluate a trivial module
        core = Module(body=(Bind(name="_ok", value=Literal(value=True)),))
        result = backend.evaluate(core)
        assert result.bindings.get("_ok") is True
