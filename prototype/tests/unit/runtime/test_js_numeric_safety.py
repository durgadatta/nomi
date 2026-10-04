"""The JS prototype must reject loss, not pretend to implement target numbers."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from prototype.runtime import create_session

NODE = shutil.which("node")
ROOT = Path(__file__).resolve().parents[4]
pytestmark = pytest.mark.skipif(NODE is None, reason="node is not installed")


@pytest.mark.parametrize(
    "source",
    [
        "print('must not execute')\nprint(9007199254740993)\n",
        "print('must not execute')\nfunc unused():\n    return -9007199254740992\n",
    ],
)
def test_unsafe_literal_fails_before_effects(source):
    payload = create_session().core_json(source=source)
    script = "const {CoreRuntime}=require('./prototype/runtime/js/core_runtime.js'); const r=new CoreRuntime(); try{r.evaluate(JSON.parse(process.argv[1]));process.exit(2)}catch(e){process.stdout.write(JSON.stringify({code:e.code,stdout:r.stdout.join('')}))}"
    result = subprocess.run(
        [NODE, "-e", script, payload],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(result.stdout) == {"code": "NOMI-NUMERIC-RANGE", "stdout": ""}


@pytest.mark.parametrize(
    "expression",
    [
        "9007199254740991 + 1",
        "-9007199254740991 - 1",
        "9007199254740991 * 2",
        "2 ** 53",
        "2 ** 9007199254740991",
        "1 << 53",
        "1 << 9007199254740991",
        "sum([9007199254740991, 1, -1])",
        "int('9007199254740993')",
    ],
)
def test_integer_overflow_is_reported(expression):
    result = create_session(eval_backend="js-core-runtime").run(
        source=f"print({expression})\n", capture_output=True, raise_on_error=False
    )
    assert not result.ok
    assert "exact range" in str(result.exception)
    assert result.diagnostics


@pytest.mark.parametrize(
    "expression",
    [
        "9007199254740991",
        "-9007199254740991",
        "9007199254740991 // 7",
        "-7 // 3",
        "7 // -3",
        "-7 % 3",
        "7 % -3",
        "2 ** 52",
        "1 << 40",
        "1099511627776 >> 8",
        "1099511627776 | 3",
        "~1099511627776",
        "-1 ** 9007199254740991",
        "0 << 9007199254740991",
        "-2 >> 9007199254740991",
        "list(range(9007199254740989, 9007199254740991))",
        "float('2')",
    "sum([1.0, 2.0])",
    "'ha' * 3",
    "3 * 'ha'",
    "[1, 2] * 3",
    ],
)
def test_supported_numbers_match_python(expression):
    source = f"print({expression})\n"
    reference = create_session().run(source=source, capture_output=True)
    result = create_session(eval_backend="js-core-runtime").run(
        source=source, capture_output=True
    )
    assert result.stdout == reference.stdout


@pytest.mark.parametrize(
    "expression",
    ["1 / 0", "1 // 0", "1 % 0", "range(0, 4, 0)", "int('1.5')", "1 << -1", "1.0 & 2"],
)
def test_invalid_numeric_operations_fail(expression):
    result = create_session(eval_backend="js-core-runtime").run(
        source=f"print({expression})\n", raise_on_error=False
    )
    assert not result.ok


def test_browser_lowering_rejects_raw_unsafe_integer_before_number_conversion():
    script = "const l=require('./prototype/runtime/js/lower_to_core_ir.js'); const p=l.lowerRustAstToCoreIr({schema:'nomi.rust-ast',version:1,body:[{type:'Expr',value:{type:'Number',value:'9007199254740993'}}]}); process.stdout.write(JSON.stringify(p));"
    result = subprocess.run(
        [NODE, "-e", script], cwd=ROOT, capture_output=True, text=True, check=True
    )
    record = json.loads(result.stdout)
    assert record["diagnosticCount"] == 1
    assert record["diagnostics"][0]["code"] == "NOMI-NUMERIC-RANGE"


def test_persistent_runtime_output_is_scoped_to_one_execution():
    first = create_session().core_json(source="print('first')\nx = 3\n")
    second = create_session().core_json(source="print(x)\n")
    script = "const {CoreRuntime}=require('./prototype/runtime/js/core_runtime.js'); const r=new CoreRuntime(); const a=r.evaluate(JSON.parse(process.argv[1])); const b=r.evaluate(JSON.parse(process.argv[2])); process.stdout.write(JSON.stringify([a.stdout,b.stdout]));"
    result = subprocess.run(
        [NODE, "-e", script, first, second],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(result.stdout) == ["first\n", "3\n"]
