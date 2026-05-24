import json
import shutil
import subprocess
from pathlib import Path

import pytest

from prototype.runtime import create_session


ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")
CORE_FROM_SOURCE = ROOT / "prototype" / "runtime" / "js" / "core_from_source.js"
WASM_PARSER = ROOT / "prototype" / "runtime" / "js" / "pkg" / "nomi_parser_bg.wasm"


CORE_PARITY_SNIPPETS = {
    "assignment": "x = 1 + 2\n",
    "expression": "1 + 2\n",
    "call": "print(1 + 2)\n",
    "function": "func add(a, b):\n    return a + b\nresult = add(1, 2)\n",
    "function-default": "func add(a, b = 1):\n    return a + b\nresult = add(2)\n",
    "list-literal": "xs = [1, 2, 3]\n",
    "dict-literal": 'm = {"a": 1, "b": 2}\n',
    "if-else": "if True:\n    x = 1\nelse:\n    x = 2\n",
    "pipeline": "x = [1, 2, 3] |> sum\n",
}


EXPECTED_CORE_GAPS = {
    "while-loop": {
        "source": "x = 0\nwhile x < 3:\n    x = x + 1\n",
        "capability": "js-lowerer.loop-core-shape",
        "diagnostic": False,
    },
    "for-loop": {
        "source": "total = 0\nfor x in [1, 2, 3]:\n    total = total + x\n",
        "capability": "js-lowerer.foreach-core-shape",
        "diagnostic": False,
    },
    "range": {
        "source": "x = 1..5\n",
        "capability": "js-lowerer.range-core-shape",
        "diagnostic": False,
    },
    "with": {
        "source": 'with open("x") as f:\n    x = 1\n',
        "capability": "js-lowerer.with",
        "diagnostic": True,
    },
}


def _normalized(value):
    if isinstance(value, dict):
        return {
            key: _normalized(item)
            for key, item in value.items()
            if not (key == "block" and item is None)
        }
    if isinstance(value, list):
        return [_normalized(item) for item in value]
    return value


def _core_from_python_session(source: str):
    return json.loads(create_session(mode="nomi").core_json(source=source))["root"]


def _core_from_wasm_js(source: str):
    completed = subprocess.run(
        [NODE, str(CORE_FROM_SOURCE)],
        input=source,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["schema"] == "nomi.core-ir"
    assert payload["version"] == 1
    assert payload["diagnosticCount"] == 0
    return payload["root"]


def _core_payload_from_wasm_js(source: str):
    completed = subprocess.run(
        [NODE, str(CORE_FROM_SOURCE)],
        input=source,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["schema"] == "nomi.core-ir"
    assert payload["version"] == 1
    return payload


@pytest.mark.skipif(NODE is None, reason="node is not installed")
@pytest.mark.skipif(not WASM_PARSER.exists(), reason="WASM parser artifact is missing")
@pytest.mark.parametrize("name", tuple(CORE_PARITY_SNIPPETS), ids=tuple(CORE_PARITY_SNIPPETS))
def test_wasm_js_source_to_core_matches_python_session_for_stable_slice(name):
    source = CORE_PARITY_SNIPPETS[name]

    assert _normalized(_core_from_wasm_js(source)) == _normalized(
        _core_from_python_session(source)
    )


@pytest.mark.skipif(NODE is None, reason="node is not installed")
@pytest.mark.skipif(not WASM_PARSER.exists(), reason="WASM parser artifact is missing")
def test_wasm_js_lowering_diagnostic_is_structured_for_unsupported_construct():
    payload = _core_payload_from_wasm_js("import math\n")

    assert payload["diagnosticCount"] == 1
    diagnostic = payload["diagnostics"][0]
    assert diagnostic["phase"] == "lower"
    assert diagnostic["severity"] == "error"
    assert diagnostic["source_excerpt"] == "import math"
    assert diagnostic["capability"] == "js-lowerer.raw-expression"
    assert diagnostic["frontend"] == "rust-fast-ast-wasm"
    assert diagnostic["backend"] == "js-core-runtime"


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_wasm_js_lowerer_rejects_unknown_rust_ast_payload_contract():
    completed = subprocess.run(
        [
            NODE,
            "-e",
            (
                f"const lowerer = require({str(CORE_FROM_SOURCE.parent / 'lower_to_core_ir.js')!r});"
                "const payload = lowerer.lowerRustAstToCoreIr({schema: 'nomi.other-ast', version: 1, type: 'Module', body: []});"
                "process.stdout.write(JSON.stringify(payload));"
            ),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["diagnosticCount"] == 1
    assert payload["diagnostics"][0]["capability"] == "rust-ast-json.contract"


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_wasm_js_lowerer_accepts_structured_rust_slice_payload():
    completed = subprocess.run(
        [
            NODE,
            "-e",
            (
                f"const lowerer = require({str(CORE_FROM_SOURCE.parent / 'lower_to_core_ir.js')!r});"
                "const payload = lowerer.lowerRustAstToCoreIr({"
                "schema: 'nomi.rust-ast', version: 1, type: 'Module', body: [{"
                "type: 'Assign', target: 'y', value: {"
                "type: 'Subscript', value: {type: 'Name', id: 'xs'},"
                "slice: {type: 'Slice', start: {type: 'Number', value: '1'}, end: {type: 'Number', value: '3'}, step: null}"
                "}}]});"
                "process.stdout.write(JSON.stringify(payload));"
            ),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["diagnosticCount"] == 0
    value = payload["root"]["body"][0]["value"]
    assert value["type"] == "Call"
    assert value["func"] == {"type": "Load", "name": "slice"}
    assert [arg["type"] for arg in value["args"]] == [
        "Load",
        "Literal",
        "Literal",
        "Literal",
    ]


@pytest.mark.skipif(NODE is None, reason="node is not installed")
@pytest.mark.skipif(not WASM_PARSER.exists(), reason="WASM parser artifact is missing")
@pytest.mark.parametrize("name", tuple(EXPECTED_CORE_GAPS), ids=tuple(EXPECTED_CORE_GAPS))
def test_wasm_js_source_to_core_differences_are_named_capability_gaps(name):
    gap = EXPECTED_CORE_GAPS[name]
    payload = _core_payload_from_wasm_js(gap["source"])

    if gap["diagnostic"]:
        assert payload["diagnosticCount"] > 0
        assert payload["diagnostics"][0]["capability"] == gap["capability"]
        return

    assert payload["diagnosticCount"] == 0
    assert _normalized(payload["root"]) != _normalized(
        _core_from_python_session(gap["source"])
    )
    assert gap["capability"].startswith("js-lowerer.")
