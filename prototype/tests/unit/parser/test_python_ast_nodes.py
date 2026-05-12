import ast

from prototype.parser.python.utils import generate_ast
from prototype.tests.shared_utils import parse_stmt


def test_operator_precedence_builds_nested_binop():
    stmt = parse_stmt(generate_ast, "x = 1 + 2 * 3\n")

    assert isinstance(stmt, ast.Assign)
    assert isinstance(stmt.value, ast.BinOp)
    assert isinstance(stmt.value.op, ast.Add)
    assert isinstance(stmt.value.right, ast.BinOp)
    assert isinstance(stmt.value.right.op, ast.Mult)


def test_list_comprehension_keeps_target_iter_and_filter():
    stmt = parse_stmt(generate_ast, "values = [x * 2 for x in range(4) if x % 2 == 0]\n")
    comp = stmt.value

    assert isinstance(comp, ast.ListComp)
    assert isinstance(comp.elt, ast.BinOp)
    assert comp.generators[0].target.id == "x"
    assert comp.generators[0].iter.func.id == "range"
    assert isinstance(comp.generators[0].ifs[0], ast.Compare)


def test_function_definition_preserves_defaults_and_return():
    stmt = parse_stmt(generate_ast, "def add(a, b=2):\n    return a + b\n")

    assert isinstance(stmt, ast.FunctionDef)
    assert stmt.name == "add"
    assert [arg.arg for arg in stmt.args.args] == ["a", "b"]
    assert ast.literal_eval(stmt.args.defaults[0]) == 2
    assert isinstance(stmt.body[0], ast.Return)


def test_try_except_finally_ast_shape():
    stmt = parse_stmt(generate_ast,
        "try:\n"
        "    risky()\n"
        "except ValueError as exc:\n"
        "    handled = exc\n"
        "finally:\n"
        "    cleaned = True\n"
    )

    assert isinstance(stmt, ast.Try)
    assert stmt.handlers[0].type.id == "ValueError"
    assert stmt.handlers[0].name == "exc"
    assert isinstance(stmt.finalbody[0], ast.Assign)


def test_with_statement_preserves_optional_vars():
    stmt = parse_stmt(generate_ast, "with manager() as resource:\n    value = resource\n")

    assert isinstance(stmt, ast.With)
    assert stmt.items[0].context_expr.func.id == "manager"
    assert stmt.items[0].optional_vars.id == "resource"
