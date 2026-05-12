"""Parser tests for underscore hole-filling: verify AST shapes before desugar."""

import ast

from prototype.parser.nomi.usage import generate_ast


def test_hole_in_attribute_is_name_load():
    tree = generate_ast(code="f = _.upper()\n")
    call = tree.body[0].value
    assert isinstance(call, ast.Call)
    attr = call.func
    assert isinstance(attr, ast.Attribute)
    assert isinstance(attr.value, ast.Name)
    assert attr.value.id == "_"
    assert isinstance(attr.value.ctx, ast.Load)


def test_hole_in_binop_left():
    tree = generate_ast(code="f = _ + 1\n")
    stmt = tree.body[0]
    binop = stmt.value
    assert isinstance(binop.left, ast.Name)
    assert binop.left.id == "_"


def test_hole_in_binop_right():
    tree = generate_ast(code="f = 1 + _\n")
    stmt = tree.body[0]
    binop = stmt.value
    assert isinstance(binop.right, ast.Name)
    assert binop.right.id == "_"


def test_hole_two_in_binop():
    tree = generate_ast(code="f = _ + _\n")
    stmt = tree.body[0]
    binop = stmt.value
    assert binop.left.id == "_"
    assert binop.right.id == "_"


def test_hole_in_subscript():
    tree = generate_ast(code='f = _["key"]\n')
    stmt = tree.body[0]
    sub = stmt.value
    assert isinstance(sub, ast.Subscript)
    assert isinstance(sub.value, ast.Name)
    assert sub.value.id == "_"
