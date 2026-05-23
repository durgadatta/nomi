"""Tests for small statement-control Core IR nodes."""

import ast as py_ast

from prototype.syntax.core import (
    Break,
    Continue,
    Loop,
    NoOp,
    Module,
    core_to_python_ast,
    dump_core,
    lower_python_ast_to_core,
    verify_core,
)


def test_lower_python_ast_to_core_pass_break_continue():
    no_op = lower_python_ast_to_core(py_ast.parse("pass")).body[0]
    loop = lower_python_ast_to_core(py_ast.parse("while True:\n break\n continue"))

    assert isinstance(no_op, NoOp)
    assert isinstance(loop.body[0], Loop)
    assert isinstance(loop.body[0].body.body[0], Break)
    assert isinstance(loop.body[0].body.body[1], Continue)


def test_statement_control_nodes_verify_dump_and_roundtrip():
    core = Module(
        body=(
            Loop(
                body=Module(
                    body=(
                        NoOp(),
                        Break(),
                    )
                )
            ),
        )
    )

    verify_core(core, strict=True)
    output = dump_core(core)
    tree = core_to_python_ast(core)
    dumped = py_ast.dump(tree, include_attributes=False, indent=2)

    assert "NoOp" in output
    assert "Break" in output
    assert "Pass" in dumped
    assert "Break" in dumped
