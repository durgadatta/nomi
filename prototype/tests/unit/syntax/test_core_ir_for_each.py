"""Tests for preserving Python/Nomi for-loops as Core IR ForEach nodes."""

import ast as py_ast

from prototype.syntax.core import (
    ForEach,
    Literal,
    Module,
    NoOp,
    Sequence,
    core_to_python_ast,
    dump_core,
    lower_python_ast_to_core,
    verify_core,
)


def test_lower_python_ast_to_core_for_loop():
    core = lower_python_ast_to_core(py_ast.parse("for item in [1, 2]:\n pass"))
    stmt = core.body[0]

    assert isinstance(stmt, ForEach)
    assert stmt.target == "item"
    assert isinstance(stmt.iterable, Sequence)
    assert isinstance(stmt.body, Module)
    assert isinstance(stmt.body.body[0], NoOp)
    verify_core(core, strict=True)


def test_core_to_python_ast_roundtrips_for_each():
    core = Module(
        body=(
            ForEach(
                target="item",
                iterable=Sequence(elements=(Literal(value=1), Literal(value=2))),
                body=Module(body=(NoOp(),)),
            ),
        )
    )

    output = dump_core(core)
    tree = core_to_python_ast(core)
    dumped = py_ast.dump(tree, include_attributes=False, indent=2)

    assert "ForEach('item')" in output
    assert "For(" in dumped
    assert "Name(id='item'" in dumped
