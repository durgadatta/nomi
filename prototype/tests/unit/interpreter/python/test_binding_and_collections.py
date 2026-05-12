import pytest

from prototype.interpreter.helpers import get_run_eval_loop


def test_tuple_unpacking_assigns_each_target(interpreter_mode):
    bindings = get_run_eval_loop(interpreter_mode)(code="a, b = [1, 2]\n")
    assert bindings["a"] == 1
    assert bindings["b"] == 2


def test_starred_unpacking_collects_middle_values(interpreter_mode):
    bindings = get_run_eval_loop(interpreter_mode)(code="head, *middle, tail = [1, 2, 3, 4]\n")
    assert bindings["head"] == 1
    assert bindings["middle"] == [2, 3]
    assert bindings["tail"] == 4


def test_unpacking_rejects_too_few_values(interpreter_mode):
    run = get_run_eval_loop(interpreter_mode)
    exc_type = RuntimeError if interpreter_mode != "python" else ValueError
    with pytest.raises(exc_type, match="Not enough values to unpack"):
        run(code="a, b, c = [1, 2]\n")


def test_unpacking_rejects_too_many_values(interpreter_mode):
    run = get_run_eval_loop(interpreter_mode)
    exc_type = RuntimeError if interpreter_mode != "python" else ValueError
    with pytest.raises(exc_type, match="Too many values to unpack"):
        run(code="a, b = [1, 2, 3]\n")


def test_augmented_assignment_updates_existing_binding(interpreter_mode):
    bindings = get_run_eval_loop(interpreter_mode)(code="total = 3\ntotal += 4\n")
    assert bindings["total"] == 7


def test_list_and_dict_literals_evaluate(interpreter_mode):
    bindings = get_run_eval_loop(interpreter_mode)(code="values = [1, 2]\nlookup = {'a': 1}\n")
    assert bindings["values"] == [1, 2]
    assert bindings["lookup"] == {"a": 1}


def test_comprehensions_evaluate_with_filters(interpreter_mode):
    bindings = get_run_eval_loop(interpreter_mode)(
        code=(
            "values = [x * 2 for x in range(5) if x % 2 == 0]\n"
            "lookup = {x: x + 1 for x in range(3)}\n"
            "unique = {x % 2 for x in range(4)}\n"
        )
    )
    assert bindings["values"] == [0, 4, 8]
    assert bindings["lookup"] == {0: 1, 1: 2, 2: 3}
    assert bindings["unique"] == {0, 1}
