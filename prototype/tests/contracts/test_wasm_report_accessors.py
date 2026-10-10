"""Token-spaced branch access lowers to the same ordinary GetItem contract."""

import json
from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")
pytestmark = [
    pytest.mark.contract,
    pytest.mark.browser_pipeline,
    pytest.mark.skipif(NODE is None, reason="node is not installed"),
]


@pytest.mark.parametrize(
    "expression",
    [
        'record["ok"]',
        'not record["ok"]',
        'record["nested"][0]',
        'record["a>b"]',
        'record["a:b"]',
        'record["ok"] == True',
    ],
)
def test_wasm_branch_postfix_access_preserves_quotes_and_operator_precedence(
    expression,
):
    source = (
        'record = {"ok": True, "nested": [True], "a>b": True, "a:b": True}\nvalue = 0\nif '
        + expression
        + ":\n    value = 1\n"
    )
    lowered = subprocess.run(
        [NODE, "prototype/runtime/js/core_from_source.js"],
        cwd=ROOT,
        input=source,
        text=True,
        capture_output=True,
        check=True,
        timeout=15,
    )
    core = json.loads(lowered.stdout)
    assert core["diagnosticCount"] == 0, core["diagnostics"]
    test = core["root"]["body"][-1]["test"]
    if expression.startswith("not "):
        assert test["type"] == "UnaryOp" and test["operand"]["type"] == "GetItem"
    elif " == " in expression:
        assert test["type"] == "CompareOp" and test["left"]["type"] == "GetItem"
    else:
        assert test["type"] == "GetItem"
    evaluated = subprocess.run(
        [NODE, "prototype/runtime/js/core_runtime.js"],
        cwd=ROOT,
        input=lowered.stdout,
        text=True,
        capture_output=True,
        check=True,
        timeout=15,
    )
    result = json.loads(evaluated.stdout)
    assert result["ok"], result["diagnostics"]
    assert result["bindings"]["value"] == (0 if expression.startswith("not ") else 1)
