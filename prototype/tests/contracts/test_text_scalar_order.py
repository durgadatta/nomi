"""Independent Unicode scalar ordering vectors for Text, without normalization."""

import json

import pytest

from prototype.runtime import execute
from prototype.tests.contracts.test_calculation_scalar_boundaries import js_result


pytestmark = pytest.mark.contract


@pytest.mark.parametrize("left, right, relation", [
    ("\ue000", "\U0001f600", "less"),
    ("\U0001f600", "\U00020000", "less"),
    ("a\ue000", "a\U0001f600", "less"),
    ("\U0001f600", "\U0001f600a", "less"),
    ("e\u0301", "\u00e9", "less"),
    ("\U0001f600a", "\U0001f600", "greater"),
    ("\U0001f600", "\U0001f600", "equal"),
    ("", "a", "less"),
])
def test_text_order_uses_scalar_values_and_prefixes(left, right, relation):
    expected = {
        "less": "True\nTrue\nFalse\nFalse\nFalse\n",
        "greater": "False\nFalse\nTrue\nTrue\nFalse\n",
        "equal": "False\nTrue\nFalse\nTrue\nTrue\n",
    }[relation]
    # Literal characters exercise the source producer as well as Core values.
    source = "".join(
        f"print({json.dumps(left, ensure_ascii=False)} {operator} "
        f"{json.dumps(right, ensure_ascii=False)})\n"
        for operator in ("<", "<=", ">", ">=", "==")
    )
    for backend in ("python-ast", "core-runtime", "js-core-runtime"):
        result = execute(source=source, eval_backend=backend)
        assert result.stdout == expected
    result = js_result(source, "wasm")
    assert result["ok"], result
    assert result["stdout"] == expected
