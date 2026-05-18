"""Runtime tests for try expressions."""

from prototype.interpreter.helpers import get_run_eval_loop


def test_try_expr_success(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="result = try 42 except ValueError: 0\n")
    assert bindings["result"] == 42


def test_try_expr_catch(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="result = try int('abc') except ValueError: 0\n")
    assert bindings["result"] == 0
