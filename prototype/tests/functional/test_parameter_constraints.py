import pytest

from prototype.interpreter.helpers import get_run_eval_loop


def test_parameter_constraint_group_accepts_valid_argument(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="func gate(age:(int, age >= 13)):\n    return age\nresult = gate(14)\n")

    assert bindings["result"] == 14


def test_parameter_constraint_group_rejects_invalid_argument(nomi_mode):
    run = get_run_eval_loop(nomi_mode)

    with pytest.raises(RuntimeError, match="Constraint 'age >= 13' failed"):
        run(code="func gate(age:(int, age >= 13)):\n    return age\nresult = gate(12)\n")


def test_parameter_constraint_message_reports_user_message(nomi_mode):
    run = get_run_eval_loop(nomi_mode)

    with pytest.raises(RuntimeError, match="Too young"):
        run(code='func gate(age:(int, age >= 13 else "Too young")):\n    return age\nresult = gate(12)\n')
