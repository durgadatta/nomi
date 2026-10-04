"""Partial Core call contracts must reject, rather than erase, richer shapes."""

import ast
import contextlib
import io
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from prototype.runtime.backends.core_runtime import CoreRuntimeEvaluator
from prototype.syntax.core import (
    CoreVerificationError,
    lower_python_ast_to_core,
    verify_core,
)

ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")


@pytest.mark.parametrize(
    "body",
    [
        "f(value=1)",
        "f(**{'value': 1})",
        "f(*[1])",
        "def f(value, /):\n    return value",
        "def f(*, value=1):\n    return value",
        "def f(*values):\n    return values",
        "def f(**values):\n    return values",
        "{'a': 1, **{'b': 2}}",
    ],
)
def test_python_ast_call_shapes_fail_before_program_effects(body):
    tree = ast.parse("print('before')\n" + body + "\n")
    core = lower_python_ast_to_core(tree)
    with pytest.raises(CoreVerificationError, match="unsupported Core"):
        verify_core(core, strict=True)
    output = io.StringIO()
    with contextlib.redirect_stdout(output), pytest.raises(CoreVerificationError):
        CoreRuntimeEvaluator().evaluate(core)
    assert output.getvalue() == ""


def test_positional_defaults_are_still_representable():
    core = lower_python_ast_to_core(
        ast.parse("def f(value=7):\n    return value\nx = f()\n")
    )
    verify_core(core, strict=True)
    assert CoreRuntimeEvaluator().evaluate(core).bindings["x"] == 7


@pytest.mark.parametrize(
    "statement",
    [
        {
            "type": "Expr",
            "value": {
                "type": "Call",
                "func": {"type": "Name", "id": "f"},
                "args": [],
                "keywords": [
                    {"arg": "value", "value": {"type": "Number", "value": "1"}}
                ],
            },
        },
        {
            "type": "Expr",
            "value": {
                "type": "Dict",
                "keys": [None],
                "values": [{"type": "Dict", "keys": [], "values": []}],
            },
        },
        {
            "type": "FunctionDef",
            "name": "f",
            "params": ["*values"],
            "body": {"type": "Number", "value": "1"},
        },
        {"type": "Suite", "kind": "Func", "head": "f(value, /)", "body": []},
        {
            "type": "Expr",
            "value": {
                "type": "Call",
                "func": {"type": "Name", "id": "f"},
                "args": [{"type": "Raw", "value": "value = 1"}],
            },
        },
        {"type": "Expr", "value": {"type": "Raw", "value": "f(value=1)"}},
        {"type": "Expr", "value": {"type": "Raw", "value": "f(*values)"}},
    ],
)
def test_js_lowerer_rejects_unrepresentable_shapes(statement):
    if NODE is None:
        pytest.skip("node unavailable")
    payload = {"schema": "nomi.rust-ast", "version": 1, "body": [statement]}
    script = """
const fs = require('node:fs');
const {lowerRustAstToCoreIr} = require('./prototype/runtime/js/lower_to_core_ir.js');
process.stdout.write(JSON.stringify(lowerRustAstToCoreIr(JSON.parse(fs.readFileSync(0, 'utf8')))));
"""
    result = subprocess.run(
        [NODE, "-e", script],
        input=json.dumps(payload),
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    record = json.loads(result.stdout)
    assert record["diagnosticCount"] > 0
    assert "unsupported Core" in json.dumps(record["diagnostics"])


def test_js_diagnostic_preflight_happens_before_any_effect():
    if NODE is None:
        pytest.skip("node unavailable")
    script = """
const {CoreRuntime} = require('./prototype/runtime/js/core_runtime.js');
const runtime = new CoreRuntime();
try { runtime.evaluate({type: 'Module', body: [
  {type: 'Call', func: {type: 'Load', name: 'print'}, args: [{type: 'Literal', value: 'before'}]},
  {type: 'Diagnostic', message: 'unsupported Core call shape'}
]}); process.exit(2); }
catch (error) { process.stdout.write(JSON.stringify({error: error.message, stdout: runtime.stdout.join('')})); }
"""
    result = subprocess.run(
        [NODE, "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    record = json.loads(result.stdout)
    assert "unsupported Core" in record["error"]
    assert record["stdout"] == ""
