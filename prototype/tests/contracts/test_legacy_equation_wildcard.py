"""Keep the supported legacy equation wildcard distinct from a None pattern."""

import pytest

from prototype.runtime import execute
from prototype.tests.contracts.test_calculation_scalar_boundaries import js_result


pytestmark = pytest.mark.contract


@pytest.mark.parametrize("argument, expected", [
    ("2", "positive"), ("0", "fallback"), ("-1", "fallback"),
    ("None", "missing"),
])
def test_legacy_equation_fallback_matches_non_nil_values(argument, expected):
    source = (
        'describe(None) = "missing"\n'
        'describe(n) when n > 0 = "positive"\n'
        'describe(_) = "fallback"\n'
        f'print(describe({argument}))\n'
    )
    reference = execute(source=source)
    assert reference.stdout == f"{expected}\n"
    result = js_result(source, "wasm")
    assert result["ok"], result
    assert result["stdout"] == reference.stdout


def test_wildcard_fallback_does_not_turn_a_missing_return_into_text():
    source = (
        'describe(n) when n > 0 = "positive"\n'
        'describe(_) = "zero or negative"\n'
        'print("description: " + describe(0))\n'
    )
    result = js_result(source, "wasm")
    assert result["ok"], result
    assert result["stdout"] == "description: zero or negative\n"
