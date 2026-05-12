import pytest

from prototype.interpreter.helpers import get_run_eval_loop


def test_func_keyword_defines_callable_function(interpreter_mode):
    if interpreter_mode == "python":
        pytest.skip("func keyword requires Nomi parser")
    run = get_run_eval_loop(interpreter_mode)
    bindings = run(code="func add(a, b=2):\n    return a + b\nresult = add(3)\n")
    assert bindings["result"] == 5


def test_arrow_function_expression_defines_callable_function(interpreter_mode):
    if interpreter_mode == "python":
        pytest.skip("arrow function requires Nomi parser")
    run = get_run_eval_loop(interpreter_mode)
    bindings = run(code="inc = (x) => x + 1\nresult = inc(4)\n")
    assert bindings["result"] == 5


def test_annotated_assignment_accepts_valid_constraints(interpreter_mode):
    if interpreter_mode == "python":
        pytest.skip("constraints require Nomi interpreter")
    run = get_run_eval_loop(interpreter_mode)
    bindings = run(code="age: int, age > 0 = 5\n")
    assert bindings["age"] == 5


def test_annotated_assignment_rejects_failed_constraints(interpreter_mode):
    if interpreter_mode == "python":
        pytest.skip("constraints require Nomi interpreter")
    run = get_run_eval_loop(interpreter_mode)
    with pytest.raises(RuntimeError, match="Constraint 'age > 0' failed"):
        run(code="age: int, age > 0 = -1\n")


def test_match_statement_executes_first_matching_case(interpreter_mode):
    if interpreter_mode == "python":
        pytest.skip("match statement requires Nomi parser")
    run = get_run_eval_loop(interpreter_mode)
    bindings = run(
        code=(
            "match 2:\n"
            "    case 1:\n"
            "        label = 'one'\n"
            "    case _:\n"
            "        label = 'other'\n"
        )
    )
    assert bindings["label"] == "other"
