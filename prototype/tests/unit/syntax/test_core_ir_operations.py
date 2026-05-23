"""Tests for portable Core IR operation nodes."""

import ast as py_ast

from prototype.syntax.core import (
    BinaryOp,
    BooleanOp,
    CompareOp,
    Literal,
    Module,
    UnaryOp,
    core_to_python_ast,
    dump_core,
    lower_python_ast_to_core,
    verify_core,
)


def test_lower_python_ast_to_core_binary_operation():
    core = lower_python_ast_to_core(py_ast.parse("x = 1 + 2"))
    value = core.body[0].value

    assert isinstance(value, BinaryOp)
    assert value.op == "+"


def test_lower_python_ast_to_core_unary_boolean_and_compare_operations():
    unary = lower_python_ast_to_core(py_ast.parse("x = not False")).body[0].value
    boolean = lower_python_ast_to_core(py_ast.parse("x = True and False")).body[0].value
    compare = lower_python_ast_to_core(py_ast.parse("x = 1 < 2 <= 3")).body[0].value

    assert isinstance(unary, UnaryOp)
    assert unary.op == "not"
    assert isinstance(boolean, BooleanOp)
    assert boolean.op == "and"
    assert isinstance(compare, CompareOp)
    assert compare.ops == ("<", "<=")


def test_core_operation_nodes_verify_and_dump():
    core = Module(
        body=(
            BinaryOp(
                left=Literal(value=1),
                op="+",
                right=Literal(value=2),
            ),
        )
    )

    verify_core(core, strict=True)

    assert "BinaryOp('+')" in dump_core(core)


def test_core_to_python_ast_lowers_operation_nodes():
    core = Module(
        body=(
            BooleanOp(
                op="or",
                values=(
                    CompareOp(
                        left=Literal(value=1),
                        ops=("<",),
                        comparators=(Literal(value=2),),
                    ),
                    UnaryOp(op="not", operand=Literal(value=False)),
                ),
            ),
        )
    )

    tree = core_to_python_ast(core)
    dumped = py_ast.dump(tree, include_attributes=False, indent=2)

    assert "BoolOp" in dumped
    assert "Compare" in dumped
    assert "UnaryOp" in dumped
