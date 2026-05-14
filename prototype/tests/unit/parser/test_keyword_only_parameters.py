import ast

from prototype.parser.nomi.usage import generate_ast as generate_nomi_ast
from prototype.parser.python.utils import generate_ast as generate_python_ast
from prototype.tests.shared_utils import parse_stmt


def test_python_parser_preserves_keyword_only_parameters():
    stmt = parse_stmt(
        generate_python_ast,
        "def combine(a, *args, scale=1, **kwargs):\n    return scale\n",
    )

    assert isinstance(stmt, ast.FunctionDef)
    assert [arg.arg for arg in stmt.args.args] == ["a"]
    assert stmt.args.vararg.arg == "args"
    assert [arg.arg for arg in stmt.args.kwonlyargs] == ["scale"]
    assert ast.literal_eval(stmt.args.kw_defaults[0]) == 1
    assert stmt.args.kwarg.arg == "kwargs"


def test_nomi_parser_preserves_constrained_keyword_only_parameters():
    stmt = parse_stmt(
        generate_nomi_ast,
        "func gate(*, age:(int, age >= 13)=14):\n    return age\n",
    )

    assert isinstance(stmt, ast.FunctionDef)
    assert stmt.args.args == []
    assert [arg.arg for arg in stmt.args.kwonlyargs] == ["age"]
    assert isinstance(stmt.args.kwonlyargs[0].annotation, ast.Tuple)
    assert ast.literal_eval(stmt.args.kw_defaults[0]) == 14
