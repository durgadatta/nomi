import json
import shutil
import subprocess
from pathlib import Path

import pytest

from prototype.runtime.backends.core_runtime import CoreRuntimeEvaluator
from prototype.runtime.host_capabilities import (
    declared_host_capability_names,
    validate_host_call_names,
)


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "prototype" / "runtime" / "host_capabilities.json"
JS_RUNTIME = ROOT / "prototype" / "runtime" / "js" / "core_runtime.js"
NODE = shutil.which("node")

REQUIRED_CAPABILITY_FIELDS = {
    "name",
    "runtimes",
    "arity",
    "argument_shape",
    "return_shape",
    "value_boxing",
    "error_kind",
    "determinism",
    "side_effects",
    "minimum_host",
    "expects_values",
    "pure",
    "may_print",
    "may_throw",
    "available_in_browser",
}


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


def test_declared_host_capability_names_reads_manifest():
    assert declared_host_capability_names("core-runtime") == _manifest_names_for(
        "core-runtime"
    )


def test_validate_host_call_names_rejects_manifest_drift():
    names = set(_manifest_names_for("core-runtime"))
    names.remove("print")

    with pytest.raises(ValueError, match="missing declared host call"):
        validate_host_call_names("core-runtime", names)

    with pytest.raises(ValueError, match="undeclared host call"):
        validate_host_call_names("core-runtime", names | {"print", "mystery"})


def test_host_capability_names_are_unique():
    names = [capability["name"] for capability in _manifest()["capabilities"]]

    assert names == sorted(set(names), key=names.index)


def test_host_capabilities_have_enforceable_metadata():
    for capability in _manifest()["capabilities"]:
        assert REQUIRED_CAPABILITY_FIELDS <= set(capability), capability["name"]
        assert isinstance(capability["argument_shape"], list)
        assert capability["return_shape"]
        assert capability["value_boxing"] in {"core-values", "host-values"}
        assert capability["error_kind"]
        assert capability["determinism"] in {
            "deterministic",
            "depends-on-callback",
        }
        assert isinstance(capability["side_effects"], list)
        assert capability["minimum_host"] in capability["runtimes"]


def test_host_capability_effect_metadata_matches_legacy_flags():
    for capability in _manifest()["capabilities"]:
        side_effects = set(capability["side_effects"])
        assert ("stdout" in side_effects) is capability["may_print"]
        if side_effects:
            assert capability["pure"] is False or side_effects == {"callback"}


def test_js_only_slice_is_declared_as_temporary_backend_helper():
    [slice_capability] = [
        capability
        for capability in _manifest()["capabilities"]
        if capability["name"] == "slice"
    ]

    assert slice_capability["runtimes"] == ["js-core-runtime"]
    assert slice_capability["minimum_host"] == "js-core-runtime"
    assert "Temporary JS lowerer helper" in slice_capability["notes"]


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
