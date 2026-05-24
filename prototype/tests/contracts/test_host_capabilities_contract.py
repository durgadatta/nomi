import json
import shutil
import subprocess
from pathlib import Path

import pytest

from prototype.runtime.backends.core_runtime import CoreRuntimeEvaluator


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "prototype" / "runtime" / "host_capabilities.json"
JS_RUNTIME = ROOT / "prototype" / "runtime" / "js" / "core_runtime.js"
NODE = shutil.which("node")


def _manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _manifest_names_for(runtime_name):
    payload = _manifest()
    assert payload["schema"] == "nomi.host-capabilities"
    assert payload["version"] == 1
    return {
        capability["name"]
        for capability in payload["capabilities"]
        if runtime_name in capability["runtimes"]
    }


def test_host_capability_names_are_unique():
    names = [capability["name"] for capability in _manifest()["capabilities"]]

    assert names == sorted(set(names), key=names.index)


def test_python_core_runtime_host_calls_are_declared():
    names = set(CoreRuntimeEvaluator()._default_host_calls())

    assert names == _manifest_names_for("core-runtime")


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_js_core_runtime_host_calls_are_declared():
    completed = subprocess.run(
        [
            NODE,
            "-e",
            (
                f"const runtime = require({str(JS_RUNTIME)!r});"
                "const names = Object.keys(new runtime.CoreRuntime().defaultHostCalls());"
                "process.stdout.write(JSON.stringify(names.sort()));"
            ),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert set(json.loads(completed.stdout)) == _manifest_names_for("js-core-runtime")
