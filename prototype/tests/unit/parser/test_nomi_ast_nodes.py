import ast

from prototype.parser.nomi.usage import generate_ast
from prototype.tests.shared_utils import parse_stmt


def test_func_keyword_builds_function_def():
    stmt = parse_stmt(generate_ast, "func add(a, b=2):\n    return a + b\n")

    assert isinstance(stmt, ast.FunctionDef)
    assert stmt.name == "add"
    assert [arg.arg for arg in stmt.args.args] == ["a", "b"]
    assert ast.literal_eval(stmt.args.defaults[0]) == 2


def test_arrow_function_expression_builds_anonymous_function_def():
    stmt = parse_stmt(generate_ast, "inc = (x) => x + 1\n")

    assert isinstance(stmt, ast.Assign)
    assert stmt.targets[0].id == "inc"
    assert isinstance(stmt.value, ast.FunctionDef)
    assert stmt.value.name is None
    assert [arg.arg for arg in stmt.value.args.args] == ["x"]
    assert isinstance(stmt.value.body[0], ast.Return)


def test_annotated_assignment_allows_constraint_list():
    stmt = parse_stmt(generate_ast, "age: int, age > 0 = 42\n")

    assert isinstance(stmt, ast.AnnAssign)
    assert stmt.target.id == "age"
    assert isinstance(stmt.annotation, ast.Tuple)
    assert len(stmt.annotation.elts) == 2
    assert ast.literal_eval(stmt.value) == 42


def test_block_call_attaches_block_keyword():
    stmt = parse_stmt(generate_ast, "retry(3):\n    value = 1\n")

    assert isinstance(stmt, ast.Expr)
    assert isinstance(stmt.value, ast.Call)
    assert stmt.value.func.id == "retry"
    assert stmt.value.keywords[-1].arg == "__block__"


def test_match_statement_builds_match_cases():
    stmt = parse_stmt(generate_ast, "match value:\n    case 1:\n        result = 'one'\n    case _:\n        result = 'any'\n")

    assert isinstance(stmt, ast.Match)
    assert len(stmt.cases) == 2
    assert isinstance(stmt.cases[0].pattern, ast.MatchValue)
    assert isinstance(stmt.cases[1].pattern, ast.MatchAs)
    assert stmt.cases[1].pattern.name is None


def test_inline_match_expression_builds_iife_call():
    stmt = parse_stmt(generate_ast, "result = match value: case 1 => 'one'; case _ => 'many'\n")

    assert isinstance(stmt, ast.Assign)
    assert isinstance(stmt.value, ast.Call)
    assert isinstance(stmt.value.func, ast.FunctionDef)
    match_stmt = stmt.value.func.body[0]
    assert isinstance(match_stmt, ast.Match)
    assert len(match_stmt.cases) == 2
    assert isinstance(match_stmt.cases[0].body[0], ast.Return)


def test_indented_match_expression_builds_iife_call():
    stmt = parse_stmt(generate_ast, "result = match value:\n    case 1: 'one'\n    case _: 'many'\n")

    assert isinstance(stmt, ast.Assign)
    assert isinstance(stmt.value, ast.Call)
    assert isinstance(stmt.value.func, ast.FunctionDef)
    match_stmt = stmt.value.func.body[0]
    assert isinstance(match_stmt, ast.Match)
    assert len(match_stmt.cases) == 2
    assert isinstance(match_stmt.cases[0].body[0], ast.Return)
