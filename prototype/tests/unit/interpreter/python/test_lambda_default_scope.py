"""Legacy lambdas retain the prototype's lexical, call-time default contract."""

import pytest

from prototype.interpreter.python.usage import run_eval_loop


@pytest.mark.parametrize(
    "source, expected",
    (
        (
            "value = 1\ncalculate = lambda result=value: result\n"
            "def caller():\n    value = 2\n    return calculate()\nanswer = caller()\n",
            1,
        ),
        (
            "calculate = lambda first, second=first, third=second + 1: third\n"
            "answer = calculate(7)\n",
            8,
        ),
        (
            "value = 4\ncalculate = lambda result: result + value\nanswer = calculate(3)\n",
            7,
        ),
        (
            "calculate = lambda result=missing: result\nanswer = calculate(7)\n",
            7,
        ),
        (
            "value = 1\ncalculate = lambda result=value: result\nvalue = 2\n"
            "answer = calculate()\n",
            2,
        ),
    ),
    ids=(
        "lexical-default",
        "earlier-parameters",
        "closure",
        "supplied-default",
        "call-time",
    ),
)
def test_lambda_defaults_use_the_lexical_call_frame(source, expected):
    assert run_eval_loop(code=source)["answer"] == expected
