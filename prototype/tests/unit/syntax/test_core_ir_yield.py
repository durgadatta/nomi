"""Tests for Core IR yield projection."""

import ast as py_ast

from prototype.syntax.core import (
    Function,
    Literal,
    Module,
    Yield,
    core_to_python_ast,
    lower_python_ast_to_core,
    verify_core,
)


def test_lower_python_ast_to_core_yield_expression():
    core = lower_python_ast_to_core(py_ast.parse("def f():\n yield 1"))
    body_node = core.body[0].value.body.body[0]

    assert isinstance(body_node, Yield)
    assert isinstance(body_node.value, Literal)
    verify_core(core, strict=True)


def test_core_to_python_ast_lowers_yield_expression():
    core = Module(
        body=(
            Function(
                params=(),
                body=Module(body=(Yield(value=Literal(value=1)),)),
            ),
        )
    )

    tree = core_to_python_ast(core)
    dumped = py_ast.dump(tree, include_attributes=False, indent=2)

    assert "Yield" in dumped
