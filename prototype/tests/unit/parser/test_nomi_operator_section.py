"""Parser tests for operator sections: verify AST shapes."""

import ast

from prototype.parser.nomi.usage import generate_ast


def test_left_section_produces_lambda():
    tree = generate_ast(code="f = (+2)\n")
    fn = tree.body[0].value
    assert isinstance(fn, ast.FunctionDef)
    assert fn.name is None
    assert len(fn.args.args) == 1
    assert isinstance(fn.body[0], ast.Return)


def test_right_section_produces_lambda():
    tree = generate_ast(code="f = (2*)\n")
    fn = tree.body[0].value
    assert isinstance(fn, ast.FunctionDef)
    assert len(fn.args.args) == 1


def test_operator_value_produces_two_param_lambda():
    tree = generate_ast(code="f = (+)\n")
    fn = tree.body[0].value
    assert isinstance(fn, ast.FunctionDef)
    assert len(fn.args.args) == 2


def test_regular_parens_expression_not_a_section():
    tree = generate_ast(code="x = (3 + 4)\n")
    val = tree.body[0].value
    assert isinstance(val, ast.BinOp)


def test_section_can_be_argument():
    tree = generate_ast(code="result = list(map((+2), [1, 2]))\n")
    call = tree.body[0].value
    map_call = call.args[0]
    section = map_call.args[0]
    assert isinstance(section, ast.FunctionDef)
