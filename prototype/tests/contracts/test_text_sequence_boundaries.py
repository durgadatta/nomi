"""Prototype access laws; these do not admit a target Text/Bytes contract."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from prototype.runtime import create_session, execute

ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")
pytestmark = [
    pytest.mark.contract,
    pytest.mark.skipif(NODE is None, reason="node unavailable"),
]

RUN = """
const fs = require('node:fs');
const {CoreRuntime} = require('./prototype/runtime/js/core_runtime.js');
let payload = JSON.parse(fs.readFileSync(0, 'utf8'));
if (typeof payload === 'string') {
  const parser = require('./prototype/runtime/js/pkg/nomi_parser.js');
  parser.initSync({module: fs.readFileSync('./prototype/runtime/js/pkg/nomi_parser_bg.wasm')});
  payload = require('./prototype/runtime/js/lower_to_core_ir.js').lowerRustAstToCoreIr(JSON.parse(parser.parse_nomi(payload)));
  if (payload.diagnosticCount) throw new Error(JSON.stringify(payload.diagnostics));
}
const runtime = new CoreRuntime();
try {
  const result = runtime.evaluate(payload);
  process.stdout.write(JSON.stringify({ok: true, stdout: result.stdout}));
} catch (error) {
  process.stdout.write(JSON.stringify({ok: false, stdout: runtime.stdout.join(''), error: error.message, kind: error.name}));
}
"""


def run_js(source, route="wasm"):
    payload = (
        json.dumps(source)
        if route == "wasm"
        else create_session().core_json(source=source)
    )
    completed = subprocess.run(
        [NODE, "-e", RUN],
        input=payload,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=20,
    )
    return json.loads(completed.stdout)


@pytest.mark.parametrize("route", ["python-core", "wasm"])
@pytest.mark.parametrize(
    "expression",
    [
        "items[0]",
        "items[-1]",
        "items[-3]",
        "items[True]",
        "text[0]",
        "text[1]",
        "text[-1]",
        "text[-4]",
        "text[2]",
        "{'known': None}['known']",
        "[1.0][0]",
    ],
)
def test_indexing_matches_the_supported_reference(expression, route):
    source = f"items = [10, 20, 30]\ntext = 'a\U0001f600e\u0301'\nprint({expression})\n"
    reference = execute(source=source)
    assert reference.ok
    assert run_js(source, route) == {"ok": True, "stdout": reference.stdout}


@pytest.mark.parametrize("route", ["python-core", "wasm"])
@pytest.mark.parametrize(
    "expression, kind",
    [
        ("[1][1]", "IndexError"),
        ("[1][-2]", "IndexError"),
        ("[][0]", "IndexError"),
        ("'x'[1]", "IndexError"),
        ("''[-1]", "IndexError"),
        ("[1]['0']", "TypeError"),
        ("[1][1.0]", "TypeError"),
        ("'x'[None]", "TypeError"),
        ("42[0]", "TypeError"),
        ("{'known': None}['missing']", "KeyError"),
    ],
)
def test_invalid_indexing_is_failure_not_nil(expression, kind, route):
    result = run_js(f"print('before')\nprint({expression})\nprint('after')\n", route)
    assert not result["ok"]
    assert result["kind"] == kind
    assert result["stdout"] == "before\n"
    assert result["error"]


@pytest.mark.parametrize("collection", ["items", "text", "empty"])
@pytest.mark.parametrize(
    "bounds",
    [
        ":",
        "1:",
        ":2",
        "-2:",
        ":-1",
        "1:3",
        "-99:99",
        "99:-99",
        "::-1",
        "3:0:-1",
        "3:-1:-1",
        ":-1:-1",
        "::-2",
        "::2",
        "::9007199254740991",
        "::-9007199254740991",
    ],
)
def test_browser_slices_clip_bounds_and_preserve_code_points(collection, bounds):
    source = f"items = [1.0, 2, 3, 4]\ntext = 'a\U0001f600e\u0301'\nempty = []\nprint({collection}[{bounds}])\n"
    reference = execute(source=source)
    assert reference.ok
    assert run_js(source) == {"ok": True, "stdout": reference.stdout}


@pytest.mark.parametrize(
    "expression", ["items[::0]", "items[1.0:]", "items[:'2']", "items[::1.0]"]
)
def test_invalid_slice_is_fail_fast(expression):
    result = run_js(
        f"items = [1, 2]\nprint('before')\nprint({expression})\nprint('after')\n"
    )
    assert not result["ok"]
    assert result["stdout"] == "before\n"
    assert result["error"]


def test_slicing_is_shallow_and_keeps_callable_values():
    source = """func identity(value):
    return value
items = [[1], identity]
copy = items[:]
copy[0].append(2)
print(items[0])
print(copy[1](42))
"""
    reference = execute(source=source)
    assert run_js(source) == {"ok": True, "stdout": reference.stdout}


@pytest.mark.parametrize("bounds", [":2", "::2", ":", "1:"])
def test_raw_slice_fallback_keeps_empty_bound_positions(bounds):
    script = """
const lower = require('./prototype/runtime/js/lower_to_core_ir.js');
const {CoreRuntime} = require('./prototype/runtime/js/core_runtime.js');
const payload = lower.lowerRustAstToCoreIr({schema: 'nomi.rust-ast', version: 1, body: [
  {type: 'Assign', target: 'items', value: {type: 'List', elements: [1,2,3].map(n => ({type: 'Number', value: String(n)}))}},
  {type: 'Expr', value: {type: 'Raw', value: process.argv[1]}}
]});
if (payload.diagnosticCount) throw new Error(JSON.stringify(payload.diagnostics));
process.stdout.write(JSON.stringify(new CoreRuntime().evaluate(payload, {displayLastExpr: true}).value));
"""
    completed = subprocess.run(
        [NODE, "-e", script, f"items[{bounds}]"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=20,
    )
    reference = execute(source=f"result = [1, 2, 3][{bounds}]\n")
    assert json.loads(completed.stdout) == reference.bindings["result"]
