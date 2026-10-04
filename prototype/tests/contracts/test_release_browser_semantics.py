"""Actual committed WASM -> JS lowering, not Python-lowered Node execution."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from prototype.runtime import execute

ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")
pytestmark = [
    pytest.mark.contract,
    pytest.mark.browser_pipeline,
    pytest.mark.skipif(NODE is None, reason="node is not installed"),
]


@pytest.mark.parametrize(
    "source",
    [
        "print(False and missing)\nprint(True or missing)\n",
        "print(1 < 2 and 2 < 3)\nprint(1 > 2 or 3 < 4)\n",
        "func observe(n):\n    print(n)\n    return n\nprint(observe(0) or observe(2))\nprint(observe(0) and observe(3))\n",
        "print(len({'a': 1, 'b': 2}))\n",
        "print(len('a\U0001f600e\u0301'))\nfunc append_text(state, ch):\n    return state + ch\nprint(fold('a\U0001f600', '', append_text))\n",
        (ROOT / "samples/data_pipeline.nomi").read_text(encoding="utf-8"),
        (ROOT / "samples/text_pipeline.nomi.nb").read_text(encoding="utf-8"),
    ],
)
def test_browser_output_matches_reference_for_release_slice(source):
    lower = subprocess.run(
        [NODE, "prototype/runtime/js/core_from_source.js"],
        input=source,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=20,
    )
    payload = json.loads(lower.stdout)
    assert payload["diagnosticCount"] == 0
    result = subprocess.run(
        [NODE, "prototype/runtime/js/core_runtime.js"],
        input=lower.stdout,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=20,
    )
    reference = execute(source=source)
    assert json.loads(result.stdout)["stdout"] == reference.stdout
