from prototype.interpreter.helpers import get_run_eval_loop


def test_inclusive_range_without_step(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="result = list(1..5)\n")
    assert bindings["result"] == [1, 2, 3, 4, 5]


def test_exclusive_range_without_step(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="result = list(1..<5)\n")
    assert bindings["result"] == [1, 2, 3, 4]


def test_inclusive_range_step(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="result = list(1..10 by 2)\n")
    assert bindings["result"] == [1, 3, 5, 7, 9]


def test_exclusive_range_step(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="result = list(1..<10 by 2)\n")
    assert bindings["result"] == [1, 3, 5, 7, 9]


def test_by_remains_usable_as_identifier(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="by = 3\nresult = by + 1\n")
    assert bindings["result"] == 4
