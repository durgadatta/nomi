import ast

from prototype.parser.nomi.usage import generate_ast


def _first_case_pattern(code):
    node = generate_ast(code=code)
    return node.body[0].cases[0].pattern


def test_single_underscore_case_pattern_is_wildcard():
    pattern = _first_case_pattern("match value:\n    case _:\n        pass\n")

    assert isinstance(pattern, ast.MatchAs)
    assert pattern.pattern is None
    assert pattern.name is None


def test_double_underscore_case_pattern_is_capture():
    pattern = _first_case_pattern("match value:\n    case __:\n        pass\n")

    assert isinstance(pattern, ast.MatchAs)
    assert pattern.pattern is None
    assert pattern.name == "__"


def test_underscore_in_case_guard_is_regular_name_load():
    node = generate_ast(code="match value:\n    case 1 if _:\n        pass\n")
    guard = node.body[0].cases[0].guard

    assert isinstance(guard, ast.Name)
    assert guard.id == "_"
    assert isinstance(guard.ctx, ast.Load)
