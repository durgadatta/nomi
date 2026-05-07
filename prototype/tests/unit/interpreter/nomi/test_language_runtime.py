import pytest

from prototype.interpreter.nomi.usage import run_eval_loop


def test_func_keyword_defines_callable_function():
    bindings = run_eval_loop(code="func add(a, b=2):\n    return a + b\nresult = add(3)\n")

    assert bindings["result"] == 5


def test_arrow_function_expression_defines_callable_function():
    bindings = run_eval_loop(code="inc = (x) => x + 1\nresult = inc(4)\n")

    assert bindings["result"] == 5


def test_annotated_assignment_accepts_valid_constraints():
    bindings = run_eval_loop(code="age: int, age > 0 = 5\n")

    assert bindings["age"] == 5


def test_annotated_assignment_rejects_failed_constraints():
    with pytest.raises(RuntimeError, match="Constraint 'age > 0' failed"):
        run_eval_loop(code="age: int, age > 0 = -1\n")


def test_match_statement_executes_first_matching_case():
    bindings = run_eval_loop(
        code=(
            "match 2:\n"
            "    case 1:\n"
            "        label = 'one'\n"
            "    case _:\n"
            "        label = 'other'\n"
        )
    )

    assert bindings["label"] == "other"
