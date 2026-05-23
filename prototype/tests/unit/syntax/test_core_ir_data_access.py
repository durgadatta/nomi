"""Tests for Core IR data-access expression nodes."""

import ast as py_ast

from prototype.syntax.core import (
    ConditionalExpr,
    GetItem,
    Literal,
    MappingLiteral,
    Module,
    Sequence,
    Spread,
    core_to_python_ast,
    dump_core,
    lower_python_ast_to_core,
    verify_core,
)


def test_lower_python_ast_to_core_subscript_ifexp_dict_and_spread():
    subscript = lower_python_ast_to_core(py_ast.parse("x = data['name']")).body[0].value
    conditional = lower_python_ast_to_core(py_ast.parse("x = 1 if ok else 0")).body[0].value
    mapping = lower_python_ast_to_core(py_ast.parse("x = {'a': 1}")).body[0].value
    sequence = lower_python_ast_to_core(py_ast.parse("x = [1, *rest]")).body[0].value

    assert isinstance(subscript, GetItem)
    assert isinstance(conditional, ConditionalExpr)
    assert isinstance(mapping, MappingLiteral)
    assert isinstance(sequence, Sequence)
    assert isinstance(sequence.elements[1], Spread)


def test_core_data_access_nodes_verify_and_dump():
    core = Module(
        body=(
            GetItem(
                object_=MappingLiteral(
                    entries=((Literal(value="a"), Literal(value=1)),)
                ),
                key=Literal(value="a"),
            ),
        )
    )

    verify_core(core, strict=True)

    output = dump_core(core)
    assert "GetItem" in output
    assert "MappingLiteral" in output


def test_core_to_python_ast_lowers_data_access_nodes():
    core = Module(
        body=(
            ConditionalExpr(
                test=Literal(value=True),
                then_value=GetItem(
                    object_=MappingLiteral(
                        entries=((Literal(value="a"), Literal(value=1)),)
                    ),
                    key=Literal(value="a"),
                ),
                else_value=Sequence(
                    elements=(
                        Literal(value=0),
                        Spread(value=Sequence(elements=(Literal(value=2),))),
                    )
                ),
            ),
        )
    )

    tree = core_to_python_ast(core)
    dumped = py_ast.dump(tree, include_attributes=False, indent=2)

    assert "IfExp" in dumped
    assert "Subscript" in dumped
    assert "Dict" in dumped
    assert "Starred" in dumped
