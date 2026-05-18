"""Runtime tests for implicit multiplication notation."""

from prototype.interpreter.helpers import get_run_eval_loop


def test_implicit_mul_name(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="x = 5\nresult = 2x + 1\n")
    assert bindings["result"] == 11


def test_implicit_mul_float(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="r = 2\nresult = 3.14r + 1\n")
    assert abs(bindings["result"] - 7.28) < 0.01


def test_implicit_mul_power_binds_tighter(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="x = 3\nresult = 2x**2\n")
    assert bindings["result"] == 18  # 2 * 9, not (2*3)**2 = 36


def test_implicit_mul_parens(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="x = 3\ny = 4\nresult = 2(x + y)\n")
    assert bindings["result"] == 14  # 2 * 7


def test_implicit_mul_negation(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="x = 5\nresult = -2x\n")
    assert bindings["result"] == -10


def test_implicit_mul_no_break_regular(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="result = x + y where:\n    x = 10\n    y = 20\n")
    assert bindings["result"] == 30
