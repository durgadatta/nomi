"""Runtime tests for Nomi operator sections and function composition."""

from prototype.interpreter.helpers import get_run_eval_loop


def test_section_left(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="add2 = (+2)\nresult = add2(5)\n")
    assert bindings["result"] == 7


def test_section_right(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="double = (2*)\nresult = double(5)\n")
    assert bindings["result"] == 10


def test_section_operator_value(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="plus = (+)\nresult = plus(3, 4)\n")
    assert bindings["result"] == 7


def test_section_nested_in_call(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="result = list(map((+2), [1, 2, 3]))\n")
    assert bindings["result"] == [3, 4, 5]


def test_section_regular_parens_still_work(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="result = (3 + 4) * 2\n")
    assert bindings["result"] == 14


def test_compose_forward(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="dbl(x) = x * 2\ninc(x) = x + 1\nf = dbl >>> inc\nresult = f(5)\n")
    assert bindings["result"] == 11


def test_compose_backward(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="dbl(x) = x * 2\ninc(x) = x + 1\nf = inc <<< dbl\nresult = f(5)\n")
    assert bindings["result"] == 11


def test_compose_chain(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="inc(x) = x + 1\ndbl(x) = x * 2\nsq(x) = x * x\nf = inc >>> dbl >>> sq\nresult = f(3)\n")
    assert bindings["result"] == 64
