"""
Underscore semantics: parser, match patterns, and runtime behaviour.

Covers ``_`` as a regular name token, soft-keyword handling
(match/case as identifiers), ``_`` vs ``__`` in match patterns
(wildcard vs capture), and the runtime semantics of each.
"""

import ast

from prototype.parser.nomi.usage import generate_ast, get_parser
from prototype.interpreter.helpers import get_run_eval_loop


# ── parser: lexing and AST shape ───────────────────────────────────

def test_underscore_lexes_as_name_token():
    tokens = list(get_parser().lex("_\n"))
    assert tokens[0].type == "NAME"
    assert tokens[0].value == "_"


def test_underscore_names_parse_as_assignment_targets():
    node = generate_ast(code="_ = 1\n__ = 2\n")
    first, second = node.body
    assert isinstance(first, ast.Assign)
    assert first.targets[0].id == "_"
    assert isinstance(second, ast.Assign)
    assert second.targets[0].id == "__"


def test_soft_keywords_parse_as_regular_names():
    node = generate_ast(code="match = 1\ncase = 2\n")
    first, second = node.body
    assert first.targets[0].id == "match"
    assert second.targets[0].id == "case"


def test_underscore_parses_as_loop_and_comprehension_target():
    node = generate_ast(code="for _ in range(2):\n    pass\nvalues = [_ for _ in range(2)]\n")
    loop = node.body[0]
    assign = node.body[1]
    list_comp = assign.value

    assert isinstance(loop, ast.For)
    assert loop.target.id == "_"
    assert isinstance(list_comp, ast.ListComp)
    assert list_comp.elt.id == "_"
    assert list_comp.generators[0].target.id == "_"


# ── parser: match pattern AST shaping ──────────────────────────────

def _first_case_pattern(code):
    return generate_ast(code=code).body[0].cases[0].pattern


def test_single_underscore_case_is_wildcard():
    pattern = _first_case_pattern("match value:\n    case _:\n        pass\n")
    assert isinstance(pattern, ast.MatchAs)
    assert pattern.pattern is None
    assert pattern.name is None


def test_double_underscore_case_is_capture():
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


# ── runtime: interpreter behaviour ─────────────────────────────────

def test_underscore_assignment_and_read_at_runtime(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="_ = 3\nvalue = _ + 4\n")
    assert bindings["_"] == 3
    assert bindings["value"] == 7


def test_underscore_loop_target_binds_like_regular_name(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="total = 0\nfor _ in range(3):\n    total += _\n")
    assert bindings["_"] == 2
    assert bindings["total"] == 3


def test_underscore_match_wildcard_does_not_rebind(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="_ = 'sentinel'\nmatch 10:\n    case _:\n        value = _\n")
    assert bindings["_"] == "sentinel"
    assert bindings["value"] == "sentinel"


def test_double_underscore_match_capture_binds(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="match 10:\n    case __:\n        value = __\n")
    assert bindings["__"] == 10
    assert bindings["value"] == 10
