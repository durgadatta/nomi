"""Tests for annotated binding projection into Core IR."""

import ast as py_ast

from prototype.syntax.core import Bind, Literal, lower_python_ast_to_core, verify_core


def test_lower_python_ast_to_core_annotated_assign_with_value():
    core = lower_python_ast_to_core(py_ast.parse("age: int = 35"))
    stmt = core.body[0]

    assert isinstance(stmt, Bind)
    assert stmt.name == "age"
    assert isinstance(stmt.value, Literal)
    assert stmt.value.value == 35
    verify_core(core, strict=True)


def test_lower_python_ast_to_core_annotated_assign_without_value():
    core = lower_python_ast_to_core(py_ast.parse("name: str"))
    stmt = core.body[0]

    assert isinstance(stmt, Bind)
    assert stmt.name == "name"
    assert isinstance(stmt.value, Literal)
    assert stmt.value.value is None
    verify_core(core, strict=True)
