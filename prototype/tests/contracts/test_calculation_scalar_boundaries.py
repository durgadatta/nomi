"""Independent calculation vectors for the current compatibility profiles.

These do not claim target Int/Bool typing or complete exact-Int support.
The browser cases use the committed WASM producer, not Python lowering.
"""

import json
from pathlib import Path
import shutil
import subprocess

import pytest

from prototype.runtime import check, create_session, execute


ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")
INVOICE = (ROOT / "scripts/check_invoice.nomi").read_text(encoding="utf-8")
pytestmark = pytest.mark.contract


def js_result(source, producer):
    if NODE is None:
        pytest.skip("node is not installed")
    if producer == "wasm":
        lowered = subprocess.run(
            [NODE, "prototype/runtime/js/core_from_source.js"],
            input=source, cwd=ROOT, capture_output=True, text=True,
            check=True, timeout=20,
        ).stdout
    else:
        lowered = create_session().core_json(source=source)
    script = """
const fs = require('node:fs');
const {CoreRuntime} = require('./prototype/runtime/js/core_runtime.js');
const runtime = new CoreRuntime();
try {
  const result = runtime.evaluate(JSON.parse(fs.readFileSync(0, 'utf8')));
  process.stdout.write(JSON.stringify({ok: true, ...result}));
} catch (error) {
  process.stdout.write(JSON.stringify({ok: false, stdout: runtime.stdout.join(''),
    code: error.code || null, name: error.name, message: error.message}));
}
"""
    result = subprocess.run(
        [NODE, "-e", script], input=lowered, cwd=ROOT,
        capture_output=True, text=True, check=True, timeout=20,
    )
    return json.loads(result.stdout)


@pytest.mark.parametrize("quantity, expected", [(3, 3850), (4, 5050), (0, 250), (-1, -950)])
def test_invoice_values_and_edits_have_independent_expected_cents(quantity, expected):
    source = INVOICE.replace("subtotal(1200, 3)", f"subtotal(1200, {quantity})")
    for backend in ("python-ast", "core-runtime"):
        result = execute(source=source, eval_backend=backend)
        assert result.stdout == f"{expected}\n"
    for producer in ("python", "wasm"):
        result = js_result(source, producer)
        assert result["ok"], result
        assert result["stdout"] == f"{expected}\n"


def test_wrong_invoice_argument_fails_and_repair_runs_the_same_source_shape():
    wrong = INVOICE.replace("subtotal(1200, 3)", "subtotal(1200, 'three')")
    assert not check(source=wrong, requirements=("known-types",)).ok
    for backend in ("python-ast", "core-runtime"):
        result = execute(source=wrong, eval_backend=backend, raise_on_error=False)
        assert not result.ok
        assert result.stdout == ""
        assert result.diagnostics
    for producer in ("python", "wasm"):
        result = js_result(wrong, producer)
        assert not result["ok"], result
        assert result["stdout"] == ""
        assert result["name"] == "TypeError"
        assert "Text" in result["message"] and "Int" in result["message"]
        repaired = js_result(INVOICE, producer)
        assert repaired["ok"] and repaired["stdout"] == "3850\n"


@pytest.mark.parametrize("expression", [
    "1 + '2'", "'2' + 1", "7 - '2'", "'7' - 2", "7 / '2'",
    "7 // '2'", "7 % '2'", "7 ** '2'", "None + 1", "1 + None",
    "[1] + 2", "[1] * 1.5", "'a' * 1.5", "'a' * 'b'", "+'2'", "-'2'",
])
def test_arithmetic_never_borrows_javascript_operand_coercion(expression):
    source = f"print({expression})\n"
    reference = execute(source=source, raise_on_error=False)
    assert not reference.ok
    for producer in ("python", "wasm"):
        result = js_result(source, producer)
        assert not result["ok"], (expression, producer, result)
        assert result["name"] == "TypeError"
        assert result["stdout"] == ""


@pytest.mark.parametrize("expression, expected", [
    ("'a' + '\U0001f600'", "a\U0001f600\n"),
    ("7 * '2'", "2222222\n"), ("'ab' * 2", "abab\n"),
    ("[1] + [2]", "[1, 2]\n"), ("[1] * 2", "[1, 1]\n"),
    ("1 + 2.5", "3.5\n"), ("7 // -3", "-3\n"), ("7 % -3", "-2\n"),
])
def test_compatible_scalar_and_collection_operations_remain_defined(expression, expected):
    source = f"print({expression})\n"
    assert execute(source=source).stdout == expected
    for producer in ("python", "wasm"):
        result = js_result(source, producer)
        assert result["ok"], result
        assert result["stdout"] == expected


def test_bool_compatibility_is_visible_and_is_not_a_checked_int_argument():
    source = INVOICE.replace("subtotal(1200, 3)", "subtotal(1200, True)")
    assert execute(source=source).stdout == "1450\n"
    assert not check(source=source, requirements=("known-types",)).ok
    for producer in ("python", "wasm"):
        result = js_result(source, producer)
        assert result["ok"] and result["stdout"] == "1450\n"


def test_wide_int_is_exact_or_explicitly_refused_before_effects():
    source = "print('before')\nprint(9007199254740993 + 1)\n"
    assert execute(source=source).stdout == "before\n9007199254740994\n"
    for producer in ("python", "wasm"):
        result = js_result(source, producer)
        assert not result["ok"]
        assert result["stdout"] == ""
        assert "exact range" in result["message"]


def test_operands_run_once_in_source_order_and_failure_stops_later_output():
    source = (
        "func operand(label, value):\n    print(label)\n    return value\n"
        "total = operand('left', 1) + operand('right', '2')\nprint('after')\n"
    )
    reference = execute(source=source, raise_on_error=False)
    assert not reference.ok and reference.stdout == "left\nright\n"
    for producer in ("python", "wasm"):
        result = js_result(source, producer)
        assert not result["ok"] and result["stdout"] == "left\nright\n"


def test_list_concatenation_preserves_callable_values():
    source = "func increment(value):\n    return value + 1\nitems = [increment] + [increment]\nprint(items[0](3))\n"
    assert execute(source=source).stdout == "4\n"
    for producer in ("python", "wasm"):
        result = js_result(source, producer)
        assert result["ok"] and result["stdout"] == "4\n"
