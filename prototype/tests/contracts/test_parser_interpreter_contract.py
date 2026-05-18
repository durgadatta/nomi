import ast

import pytest

from prototype.interpreter.helpers import get_run_eval_loop
from prototype.parser.nomi.usage import generate_ast as generate_nomi_ast
from prototype.parser.python.utils import generate_ast as generate_python_ast


NOMI_PROGRAMS = [
    ("func add(a, b=2):\n    return a + b\nresult = add(3)\n", "result", 5),
    ("inc = (x) => x + 1\nresult = inc(10)\n", "result", 11),
    ("match 1:\n    case 1:\n        result = 'one'\n    case _:\n        result = 'other'\n", "result", "one"),
    ("value: int, value > 0 = 3\nresult = value * 2\n", "result", 6),
]

PYTHON_PROGRAMS = [
    ("a, b = [1, 2]\nresult = a + b\n", "result", 3),
    ("result = [x * 2 for x in range(4)]\n", "result", [0, 2, 4, 6]),
    ("def f(x):\n    return x + 1\nresult = f(4)\n", "result", 5),
    ("try:\n    1 / 0\nexcept ZeroDivisionError:\n    result = 'handled'\n", "result", "handled"),
]


@pytest.mark.parametrize("code,key,expected", NOMI_PROGRAMS)
def test_nomi_parser_output_runs_in_interpreter(code, key, expected, nomi_mode):
    tree = ast.fix_missing_locations(generate_nomi_ast(code=code))
    run_eval_loop = get_run_eval_loop(nomi_mode)
    bindings = run_eval_loop(tree=tree)
    assert bindings[key] == expected


@pytest.mark.parametrize("code,key,expected", PYTHON_PROGRAMS)
def test_python_parser_output_runs_in_interpreter(code, key, expected, interpreter_mode):
    tree = ast.fix_missing_locations(generate_python_ast(code=code))
    run_eval_loop = get_run_eval_loop(interpreter_mode)
    bindings = run_eval_loop(tree=tree)
    assert bindings[key] == expected
