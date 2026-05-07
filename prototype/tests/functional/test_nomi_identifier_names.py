import ast

from prototype.parser.nomi.usage import generate_ast
from prototype.parser.nomi.usage import get_parser


def test_underscore_lexes_as_name_token():
    parser = get_parser()

    tokens = list(parser.lex("_\n"))

    assert tokens[0].type == "NAME"
    assert tokens[0].value == "_"


def test_single_and_double_underscore_parse_as_regular_assignment_names():
    node = generate_ast(code="_ = 1\n__ = 2\n")

    first, second = node.body

    assert isinstance(first, ast.Assign)
    assert first.targets[0].id == "_"
    assert isinstance(second, ast.Assign)
    assert second.targets[0].id == "__"


def test_soft_keywords_still_parse_as_regular_assignment_names():
    node = generate_ast(code="match = 1\ncase = 2\n")

    first, second = node.body

    assert first.targets[0].id == "match"
    assert second.targets[0].id == "case"


def test_underscore_parse_as_loop_and_comprehension_target():
    node = generate_ast(code="for _ in range(2):\n    pass\nvalues = [_ for _ in range(2)]\n")

    loop = node.body[0]
    assign = node.body[1]
    list_comp = assign.value

    assert isinstance(loop, ast.For)
    assert loop.target.id == "_"
    assert isinstance(list_comp, ast.ListComp)
    assert list_comp.elt.id == "_"
    assert list_comp.generators[0].target.id == "_"
