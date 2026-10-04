"""The legacy adapter preserves execution facts rather than guessing a host."""

import asyncio
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def run_bridge(source):
    spec = importlib.util.spec_from_file_location(
        "nomi_web_result_contract", ROOT / "web/nomi_web.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return asyncio.run(module.run_nomi(source))


def test_pyodide_success_reports_actual_pipeline_and_output():
    result = run_bridge("print(42)\n")
    assert result["ok"] is True
    assert result["stdout"] == result["output"] == "42\n"
    assert result["backend"] == result["pipeline"]["eval_backend"] == "python-ast"
    assert result["pipeline"]["parser_frontend"].startswith("lark-")
    assert result["pipeline"]["host"] == "browser-worker-pyodide"
    assert result["diagnostics"] == []


def test_pyodide_parse_failure_preserves_known_source_diagnostics():
    result = run_bridge("x =\n")
    assert result["ok"] is False
    diagnostic = result["diagnostics"][0]
    assert diagnostic["code"] == "NOMI-PARSE"
    assert diagnostic["span"]["line"] == 1
    assert diagnostic["span"]["coordinate_unit"] == "unicode-code-point"


def test_pyodide_runtime_failure_keeps_stdout_without_internal_traceback():
    result = run_bridge("print('before')\nmissing\n")
    assert result["ok"] is False
    assert result["stdout"] == "before\n"
    assert result["diagnostics"][0]["code"] == "NOMI-RUNTIME"
    assert "missing" in result["error"]
    assert "Traceback" not in result["error"]
