import ast

from prototype.parser.nomi.usage import generate_ast
from prototype.tests.shared_utils import parse_stmt


def test_parameter_constraint_group_lowers_to_tuple_annotation():
    stmt = parse_stmt(generate_ast, "func gate(age:(int, age >= 13)):\n    return age\n")

    annotation = stmt.args.args[0].annotation
    assert isinstance(annotation, ast.Tuple)
    assert len(annotation.elts) == 2
    assert ast.unparse(annotation.elts[1]) == "age >= 13"


def test_parameter_constraint_message_lowers_to_metadata_marker():
    stmt = parse_stmt(generate_ast, 'func gate(age:(int, age >= 13 else "Too young")):\n    return age\n')

    annotation = stmt.args.args[0].annotation
    assert isinstance(annotation, ast.Tuple)
    message_constraint = annotation.elts[1]
    assert isinstance(message_constraint, ast.Call)
    assert isinstance(message_constraint.func, ast.Name)
    assert message_constraint.func.id == "__constraint_message__"
    assert ast.unparse(message_constraint.args[0]) == "age >= 13"
    assert message_constraint.args[1].value == "Too young"
