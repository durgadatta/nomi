"""Contract: default web worker must not reference Pyodide.

The default web flow uses WASM + JS Core Runtime exclusively with no
fallback. Any Pyodide reference in the default worker is a regression.
"""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
WORKER_PATH = ROOT / "prototype" / "runtime" / "js" / "worker.js"
METADATA_PATH = ROOT / "web" / "manifest_metadata.json"
APP_JS_PATH = ROOT / "web" / "app.js"


def test_default_worker_has_no_pyodide_reference():
    """The default worker must not mention Pyodide at all."""
    text = WORKER_PATH.read_text(encoding="utf-8")
    lowered = text.lower()
    assert "pyodide" not in lowered, (
        "default worker.js must not reference Pyodide — "
        "use ?backend=pyodide and web/worker_pyodide.js for the opt-in path"
    )


def test_app_js_default_backend_is_wasm_js():
    """app.js must default to wasm-js backend (not pyodide)."""
    text = APP_JS_PATH.read_text(encoding="utf-8")
    assert '"wasm-js"' in text, (
        "app.js must default to wasm-js backend"
    )


def test_metadata_runtime_profile_is_wasm_js():
    """manifest_metadata.json must declare browser-wasm-js profile."""
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    assert metadata.get("runtime_profile") == "browser-wasm-js", (
        f"runtime_profile must be browser-wasm-js, got {metadata.get('runtime_profile')!r}"
    )
