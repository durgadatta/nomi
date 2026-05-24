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


@pytest.mark.skipif(NODE is None, reason="node is not installed")
@pytest.mark.skipif(not WASM_PARSER.exists(), reason="WASM parser artifact is missing")
@pytest.mark.parametrize("name", tuple(CORE_PARITY_SNIPPETS), ids=tuple(CORE_PARITY_SNIPPETS))
def test_wasm_js_source_to_core_matches_python_session_for_stable_slice(name):
    source = CORE_PARITY_SNIPPETS[name]

    assert _normalized(_core_from_wasm_js(source)) == _normalized(
        _core_from_python_session(source)
    )
