"""Runtime tests for spread in literals."""

from prototype.interpreter.helpers import get_run_eval_loop


def test_spread_list(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="a = [1, 2]\nresult = [0, *a, 3]\n")
    assert bindings["result"] == [0, 1, 2, 3]


def test_spread_tuple(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="a = (3, 4)\nresult = (1, 2, *a)\n")
    assert bindings["result"] == (1, 2, 3, 4)
