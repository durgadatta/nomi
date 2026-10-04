"""Selectable program output and diagnostic records, without backend tracebacks."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def run_cli(path, output):
    return subprocess.run(
        [sys.executable, "scripts/cli.py", str(path), "--output", output],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
    )


def test_program_output_has_no_debug_environment(tmp_path):
    path = tmp_path / "test.nomi"
    path.write_text("x = 42\nprint(x)\n", encoding="utf-8")
    result = run_cli(path, "program")
    assert result.returncode == 0
    assert result.stdout == "42\n"
    assert result.stderr == ""


def test_json_output_separates_program_output_and_inspected_bindings(tmp_path):
    path = tmp_path / "test.nomi"
    path.write_text("x = 42\nprint(x)\n", encoding="utf-8")
    result = run_cli(path, "json")
    record = json.loads(result.stdout)
    assert result.returncode == 0
    assert record["schema"] == "nomi.cli-inspection"
    assert record["stdout"] == "42\n"
    assert record["bindings"] == {"x": "42"}
    assert record["diagnostics"] == []


def test_json_parse_failure_has_nonzero_exit_and_source_location(tmp_path):
    path = tmp_path / "test.nomi"
    path.write_text("x =\n", encoding="utf-8")
    result = run_cli(path, "json")
    record = json.loads(result.stdout)
    assert result.returncode == 1
    assert record["ok"] is False
    assert record["diagnostics"][0]["code"] == "NOMI-PARSE"
    assert record["diagnostics"][0]["span"]["line"] == 1
    assert result.stderr == ""


def test_program_failure_has_diagnostic_and_no_internal_traceback(tmp_path):
    path = tmp_path / "test.nomi"
    path.write_text("print('before')\nmissing\n", encoding="utf-8")
    result = run_cli(path, "program")
    assert result.returncode == 1
    assert result.stdout == "before\n"
    assert "NOMI-RUNTIME" in result.stderr
    assert "Traceback" not in result.stderr
