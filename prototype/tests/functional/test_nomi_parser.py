import ast

from prototype.parser.nomi.usage import get_parser
from prototype.parser.nomi.usage import generate_ast


def test_lark_maps_underscore_to_name_everywhere():
    parser = get_parser()

    tokens = list(parser.lex("_\n"))
    expression_tree = parser.parse("_\n")
    guard_tree = parser.parse("match value:\n    case 1 if _:\n        pass\n")
    match_tree = parser.parse("match value:\n    case _:\n        pass\n")
    soft_keyword_tree = parser.parse("case = _\n")

    assert tokens[0].type == "NAME"
    assert "var\n      name\t_" in expression_tree.pretty()
    assert "var\n        name\t_" in guard_tree.pretty()
    assert "capture_pattern\t_" in match_tree.pretty()
    assert "var\n        name\t_" in soft_keyword_tree.pretty()

    node = generate_ast(code="match value:\n    case _:\n        pass\n")
    assert isinstance(node.body[0].cases[0].pattern, ast.MatchAs)
    assert node.body[0].cases[0].pattern.name is None


def test_nomi_parser_accepts_single_underscore_loop_target():
    code = "for _ in range(5):\n    print('fine')\n"

    node = generate_ast(code=code)

    loop = node.body[0]
    assert isinstance(loop, ast.For)
    assert isinstance(loop.target, ast.Name)
    assert loop.target.id == "_"


def test_nomi_parser_loads_grammar_independent_of_cwd(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    node = generate_ast(code='print("still works")\n')

    assert isinstance(node.body[0], ast.Expr)
