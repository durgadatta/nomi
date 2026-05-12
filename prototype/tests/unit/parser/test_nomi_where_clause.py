"""Parser tests for where clause: verify AST shapes before desugar."""

import ast

from prototype.parser.nomi.usage import generate_ast


def test_where_assign_has_where_body_attr():
    tree = generate_ast(code="result = x where:\n    x = 10\n")
    stmt = tree.body[0]
    assert isinstance(stmt, ast.Assign)
    assert hasattr(stmt, "_nomi_where_body")
    assert len(stmt._nomi_where_body) == 1


def test_where_body_contains_assign():
    tree = generate_ast(code="result = x + y where:\n    x = 10\n    y = 20\n")
    stmt = tree.body[0]
    where = stmt._nomi_where_body
    assert len(where) == 2
    assert isinstance(where[0], ast.Assign)


def test_where_on_func_equation():
    tree = generate_ast(code='greet(name) = prefix + name where:\n    prefix = "Hi"\n')
    stmt = tree.body[0]
    assert isinstance(stmt, ast.FunctionDef)
    assert hasattr(stmt, "_nomi_where_body")
    assert len(stmt._nomi_where_body) == 1


def test_where_no_where_body_on_normal_assign():
    tree = generate_ast(code="x = 10\n")
    stmt = tree.body[0]
    assert not hasattr(stmt, "_nomi_where_body")
