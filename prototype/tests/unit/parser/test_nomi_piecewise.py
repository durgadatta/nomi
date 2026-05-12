"""Parser tests for piecewise function definitions: verify AST shapes."""

import ast

from prototype.parser.nomi.usage import generate_ast


def test_piecewise_literal_arg_has_synthetic_param():
    tree = generate_ast(code="f(1) = 2\n")
    fn = tree.body[0]
    assert isinstance(fn, ast.FunctionDef)
    assert fn.name == "f"
    assert fn.args.args[0].arg == "__0"


def test_piecewise_name_arg_preserves_param_name():
    tree = generate_ast(code="f(n) = n * 2\n")
    fn = tree.body[0]
    assert fn.args.args[0].arg == "n"


def test_piecewise_body_is_return():
    tree = generate_ast(code="f(x) = x + 1\n")
    fn = tree.body[0]
    assert isinstance(fn.body[0], ast.Return)
    assert isinstance(fn.body[0].value, ast.BinOp)


def test_piecewise_has_eq_args_attr():
    tree = generate_ast(code="f(1) = 2\n")
    fn = tree.body[0]
    assert hasattr(fn, "_nomi_eq_args")
    assert len(fn._nomi_eq_args) == 1


def test_piecewise_contiguous_produce_multiple_function_defs():
    tree = generate_ast(code="f(1) = 2\nf(n) = n\n")
    assert len(tree.body) == 2
    assert all(isinstance(s, ast.FunctionDef) for s in tree.body)
    assert tree.body[0].name == "f"
    assert tree.body[1].name == "f"
