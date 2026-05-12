"""End-to-end tests for all function definition styles."""

import pytest

from prototype.interpreter.helpers import get_run_eval_loop


# ── underscore hole-filling ───────────────────────────────────────

def test_hole_attribute_upper(interpreter_mode):
    if interpreter_mode == "python":
        pytest.skip("Nomi-specific syntax")
    run = get_run_eval_loop(interpreter_mode)
    bindings = run(code='up = _.upper()\nresult = up("hello")\n')
    assert bindings["result"] == "HELLO"


def test_hole_binop_add(interpreter_mode):
    if interpreter_mode == "python":
        pytest.skip("Nomi-specific syntax")
    run = get_run_eval_loop(interpreter_mode)
    bindings = run(code="inc = _ + 1\nresult = inc(5)\n")
    assert bindings["result"] == 6


def test_hole_binop_subscript(interpreter_mode):
    if interpreter_mode == "python":
        pytest.skip("Nomi-specific syntax")
    run = get_run_eval_loop(interpreter_mode)
    bindings = run(code='get = _["k"]\nresult = get({"k": 99})\n')
    assert bindings["result"] == 99


def test_hole_two_params(interpreter_mode):
    if interpreter_mode == "python":
        pytest.skip("Nomi-specific syntax")
    run = get_run_eval_loop(interpreter_mode)
    bindings = run(code="add = _ + _\nresult = add(3, 4)\n")
    assert bindings["result"] == 7


def test_hole_larger_expression(interpreter_mode):
    if interpreter_mode == "python":
        pytest.skip("Nomi-specific syntax")
    run = get_run_eval_loop(interpreter_mode)
    bindings = run(code="f = _ * 2 + 1\nresult = f(3)\n")
    assert bindings["result"] == 7


def test_hole_not_wrapped_when_underscore_bound(interpreter_mode):
    if interpreter_mode == "python":
        pytest.skip("Nomi-specific syntax")
    run = get_run_eval_loop(interpreter_mode)
    bindings = run(code="_ = 3\nvalue = _ + 4\n")
    assert bindings["value"] == 7


def test_hole_for_loop_target_not_hole(interpreter_mode):
    if interpreter_mode == "python":
        pytest.skip("Nomi-specific syntax")
    run = get_run_eval_loop(interpreter_mode)
    bindings = run(code="total = 0\nfor _ in range(3):\n    total = total + _\n")
    assert bindings["total"] == 3


# ── piecewise functions ───────────────────────────────────────────

def test_piecewise_factorial(interpreter_mode):
    if interpreter_mode == "python":
        pytest.skip("Nomi-specific syntax")
    run = get_run_eval_loop(interpreter_mode)
    bindings = run(code="\n".join([
        "fact(1) = 1",
        "fact(n) = fact(n - 1) * n",
        "r5 = fact(5)",
        "",
    ]))
    assert bindings["r5"] == 120


def test_piecewise_fibonacci(interpreter_mode):
    if interpreter_mode == "python":
        pytest.skip("Nomi-specific syntax")
    run = get_run_eval_loop(interpreter_mode)
    bindings = run(code="\n".join([
        "fib(0) = 0",
        "fib(1) = 1",
        "fib(n) = fib(n - 1) + fib(n - 2)",
        "r6 = fib(6)",
        "",
    ]))
    assert bindings["r6"] == 8


def test_piecewise_first_match_wins(interpreter_mode):
    if interpreter_mode == "python":
        pytest.skip("Nomi-specific syntax")
    run = get_run_eval_loop(interpreter_mode)
    bindings = run(code="\n".join([
        "f(1) = 10",
        "f(n) = n",
        "r = f(1)",
        "",
    ]))
    assert bindings["r"] == 10


def test_piecewise_three_cases(interpreter_mode):
    if interpreter_mode == "python":
        pytest.skip("Nomi-specific syntax")
    run = get_run_eval_loop(interpreter_mode)
    bindings = run(code="\n".join([
        "sign(0) = 0",
        "sign(n) = 1 if n > 0 else -1",
        "neg = sign(-5)",
        "zer = sign(0)",
        "pos = sign(5)",
        "",
    ]))
    assert bindings["neg"] == -1
    assert bindings["zer"] == 0
    assert bindings["pos"] == 1


def test_piecewise_capture_name(interpreter_mode):
    if interpreter_mode == "python":
        pytest.skip("Nomi-specific syntax")
    run = get_run_eval_loop(interpreter_mode)
    bindings = run(code="\n".join([
        "f(1) = 1",
        "f(n) = n",
        "r = f(99)",
        "",
    ]))
    assert bindings["r"] == 99


# ── where clause ──────────────────────────────────────────────────

def test_where_simple_binding(interpreter_mode):
    if interpreter_mode == "python":
        pytest.skip("Nomi-specific syntax")
    run = get_run_eval_loop(interpreter_mode)
    bindings = run(code="result = x + y where:\n    x = 10\n    y = 20\n")
    assert bindings["result"] == 30


def test_where_local_function(interpreter_mode):
    if interpreter_mode == "python":
        pytest.skip("Nomi-specific syntax")
    run = get_run_eval_loop(interpreter_mode)
    bindings = run(code="result = double(x) where:\n    double(n) = n * 2\n    x = 5\n")
    assert bindings["result"] == 10


def test_where_on_func_equation(interpreter_mode):
    if interpreter_mode == "python":
        pytest.skip("Nomi-specific syntax")
    run = get_run_eval_loop(interpreter_mode)
    bindings = run(code='greet(name) = prefix + name where:\n    prefix = "Hi, "\nr = greet("Nomi")\n')
    assert bindings["r"] == "Hi, Nomi"


def test_where_not_leak_bindings(interpreter_mode):
    if interpreter_mode == "python":
        pytest.skip("Nomi-specific syntax")
    run = get_run_eval_loop(interpreter_mode)
    bindings = run(code="result = x where:\n    x = 42\n")
    assert bindings["result"] == 42
    assert "x" not in bindings


# ── operator sections ─────────────────────────────────────────────

def test_section_left(interpreter_mode):
    if interpreter_mode == "python":
        pytest.skip("Nomi-specific syntax")
    run = get_run_eval_loop(interpreter_mode)
    bindings = run(code="add2 = (+2)\nresult = add2(5)\n")
    assert bindings["result"] == 7


def test_section_right(interpreter_mode):
    if interpreter_mode == "python":
        pytest.skip("Nomi-specific syntax")
    run = get_run_eval_loop(interpreter_mode)
    bindings = run(code="double = (2*)\nresult = double(5)\n")
    assert bindings["result"] == 10


def test_section_operator_value(interpreter_mode):
    if interpreter_mode == "python":
        pytest.skip("Nomi-specific syntax")
    run = get_run_eval_loop(interpreter_mode)
    bindings = run(code="plus = (+)\nresult = plus(3, 4)\n")
    assert bindings["result"] == 7


def test_section_nested_in_call(interpreter_mode):
    if interpreter_mode == "python":
        pytest.skip("Nomi-specific syntax")
    run = get_run_eval_loop(interpreter_mode)
    bindings = run(code="result = list(map((+2), [1, 2, 3]))\n")
    assert bindings["result"] == [3, 4, 5]


def test_section_regular_parens_still_work(interpreter_mode):
    if interpreter_mode == "python":
        pytest.skip("Nomi-specific syntax")
    run = get_run_eval_loop(interpreter_mode)
    bindings = run(code="result = (3 + 4) * 2\n")
    assert bindings["result"] == 14


# ── cross-feature interactions ────────────────────────────────────

def test_where_with_hole(interpreter_mode):
    if interpreter_mode == "python":
        pytest.skip("Nomi-specific syntax")
    run = get_run_eval_loop(interpreter_mode)
    bindings = run(code="result = scaled where:\n    scale = _ * 3\n    scaled = scale(7)\n")
    assert bindings["result"] == 21


def test_piecewise_standalone_equation(interpreter_mode):
    """Single equation (not merged) should still work as a standalone function."""
    if interpreter_mode == "python":
        pytest.skip("Nomi-specific syntax")
    run = get_run_eval_loop(interpreter_mode)
    bindings = run(code="square(x) = x * x\nresult = square(9)\n")
    assert bindings["result"] == 81


def test_hole_two_params_reversed(interpreter_mode):
    if interpreter_mode == "python":
        pytest.skip("Nomi-specific syntax")
    run = get_run_eval_loop(interpreter_mode)
    bindings = run(code="sub = _ - _\nresult = sub(10, 3)\n")
    assert bindings["result"] == 7


def test_piecewise_not_merged_when_not_contiguous(interpreter_mode):
    if interpreter_mode == "python":
        pytest.skip("Nomi-specific syntax")
    run = get_run_eval_loop(interpreter_mode)
    bindings = run(code="\n".join([
        "f(1) = 1",
        "g() = 0",
        "f(n) = n",
        "r1 = f(1)",
        "r2 = f(99)",
        "",
    ]))
    assert bindings["r1"] == 1
    assert bindings["r2"] == 99


def test_where_not_pollute_namespace(interpreter_mode):
    if interpreter_mode == "python":
        pytest.skip("Nomi-specific syntax")
    run = get_run_eval_loop(interpreter_mode)
    # x and y are local to where, should not be available globally
    bindings = run(code="result = x + y where:\n    x = 10\n    y = 20\n")
    assert bindings["result"] == 30
    assert "x" not in bindings
    assert "y" not in bindings

