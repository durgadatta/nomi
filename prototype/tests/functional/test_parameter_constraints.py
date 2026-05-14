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


def test_vararg_constraint_validates_collected_tuple(nomi_mode):
    run = get_run_eval_loop(nomi_mode)

    with pytest.raises(RuntimeError, match="At least one age is required"):
        run(
            code=(
                'func collect(*ages:(tuple, len(ages) > 0 else "At least one age is required")):\n'
                "    return ages\n"
                "result = collect()\n"
            )
        )


def test_kwarg_constraint_validates_collected_mapping(nomi_mode):
    run = get_run_eval_loop(nomi_mode)

    with pytest.raises(RuntimeError, match="At least one option is required"):
        run(
            code=(
                'func configure(**opts:(dict, len(opts) > 0 else "At least one option is required")):\n'
                "    return opts\n"
                "result = configure()\n"
            )
        )


def test_keyword_only_parameter_constraint_validates_default(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="func gate(*, age:(int, age >= 13)=14):\n    return age\nresult = gate()\n")

    assert bindings["result"] == 14


def test_keyword_only_parameter_constraint_rejects_invalid_keyword(nomi_mode):
    run = get_run_eval_loop(nomi_mode)

    with pytest.raises(RuntimeError, match="Too young"):
        run(
            code=(
                'func gate(*, age:(int, age >= 13 else "Too young")=14):\n'
                "    return age\n"
                "result = gate(age=12)\n"
            )
        )


def test_positional_only_parameter_constraint_rejects_invalid_argument(nomi_mode):
    run = get_run_eval_loop(nomi_mode)

    with pytest.raises(RuntimeError, match="Too young"):
        run(
            code=(
                'func gate(age:(int, age >= 13 else "Too young"), /):\n'
                "    return age\n"
                "result = gate(12)\n"
            )
        )


def test_positional_only_parameter_is_not_bound_from_keyword(nomi_mode):
    run = get_run_eval_loop(nomi_mode)

    with pytest.raises(RuntimeError, match="age"):
        run(
            code=(
                'func gate(age:(int, age >= 13 else "Too young"), /):\n'
                "    return age\n"
                "result = gate(age=14)\n"
            )
        )
