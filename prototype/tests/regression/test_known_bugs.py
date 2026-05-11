import ast
import pytest

from prototype.interpreter.helpers import get_run_eval_loop
from prototype.parser.nomi.usage import generate_ast
from prototype.parser.nomi.usage import get_parser


def test_regression_single_underscore_is_name_outside_match_pattern():
    parser = get_parser()

    assert list(parser.lex("_\n"))[0].type == "NAME"

    node = generate_ast(code="_ = 1\nvalue = _\n")
    first, second = node.body

    assert first.targets[0].id == "_"
    assert second.value.id == "_"


def test_regression_single_underscore_match_pattern_does_not_bind(interpreter_mode):
    run_eval_loop = get_run_eval_loop(interpreter_mode)
    bindings = run_eval_loop(code="_ = 'existing'\nmatch 10:\n    case _:\n        value = _\n")

    assert bindings["_"] == "existing"
    assert bindings["value"] == "existing"


def test_regression_double_underscore_match_pattern_still_captures(interpreter_mode):
    run_eval_loop = get_run_eval_loop(interpreter_mode)
    bindings = run_eval_loop(code="match 10:\n    case __:\n        value = __\n")

    assert bindings["__"] == 10
    assert bindings["value"] == 10


def test_regression_case_guard_underscore_is_name_load():
    node = generate_ast(code="match 1:\n    case 1 if _:\n        value = 1\n")
    guard = node.body[0].cases[0].guard

    assert isinstance(guard, ast.Name)
    assert guard.id == "_"
