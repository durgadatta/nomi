"""The Pyodide file manifest must carry required, explicitly registered data."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import make_web

ROOT = Path(__file__).resolve().parents[3]


def test_manifest_contains_host_capability_data():
    assert (
        "prototype/runtime/host_capabilities.json" in make_web.build_manifest()["files"]
    )


def test_manifest_alone_supports_python_runtime_initialization(tmp_path):
    for relative in make_web.build_manifest()["files"]:
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, destination)
    source = (
        "func add(state, item):\n    return state + item\nprint(fold([1, 2], 0, add))\n"
    )
    script = (
        "import sys; sys.path.insert(0, sys.argv[1]); "
        "from prototype.runtime import execute; "
        f"result=execute(source={source!r}); "
        "assert result.stdout == '3\\n', result.stdout"
    )
    result = subprocess.run(
        [sys.executable, "-I", "-c", script, str(tmp_path)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_missing_required_runtime_asset_fails_generation(monkeypatch):
    monkeypatch.setattr(
        make_web, "RUNTIME_ASSET_PATHS", ("missing-required.json",), raising=False
    )
    with pytest.raises(FileNotFoundError, match="missing-required.json"):
        make_web.build_manifest()


def test_arbitrary_json_is_not_collected_as_runtime_data(monkeypatch, tmp_path):
    prototype = tmp_path / "prototype"
    (prototype / "runtime").mkdir(parents=True)
    (prototype / "runtime/host_capabilities.json").write_text("{}", encoding="utf-8")
    (prototype / "unregistered.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(make_web, "ROOT", tmp_path)
    monkeypatch.setattr(make_web, "PROTOTYPE_DIR", prototype)
    monkeypatch.setattr(make_web, "SAMPLES_DIR", tmp_path / "samples")
    assert make_web.build_manifest()["files"] == [
        "prototype/runtime/host_capabilities.json"
    ]
