"""CLI setup failures respect the selected output contract before execution."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]


def invoke(path, output, *options, env=None):
    return subprocess.run(
        [sys.executable, "scripts/cli.py", str(path), "--output", output, *options],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
        env=env,
    )


@pytest.mark.parametrize("output", ["json", "program"])
@pytest.mark.parametrize("failure", ["missing-file", "frontend", "backend"])
def test_setup_failures_have_no_program_output_or_traceback(tmp_path, output, failure):
    path = tmp_path / "source.nomi"
    options = ()
    env = dict(os.environ)
    env.pop("NOMI_EVAL_BACKEND", None)
    if failure != "missing-file":
        path.write_text("print('must not execute')\n", encoding="utf-8")
    if failure == "frontend":
        options = ("--parser-frontend", "not-a-frontend")
    if failure == "backend":
        env["NOMI_EVAL_BACKEND"] = "not-a-backend"
    result = invoke(path, output, *options, env=env)
    assert result.returncode == 1
    assert "must not execute" not in result.stdout
    assert "Traceback" not in result.stderr
    if output == "json":
        record = json.loads(result.stdout)
        assert record["schema"] == "nomi.cli-inspection"
        assert record["ok"] is False
        assert record["stdout"] == ""
        assert record["pipeline"] is None
        assert record["diagnostics"][0]["code"] == "NOMI-CLI"
        assert record["diagnostics"][0]["phase"] == "setup"
        assert result.stderr == ""
    else:
        assert result.stdout == ""
        assert "NOMI-CLI" in result.stderr


def test_default_missing_file_keeps_legacy_debug_output(tmp_path):
    path = tmp_path / "missing.nomi"
    result = invoke(path, "debug")
    assert result.returncode == 1
    assert result.stdout == f"Error: File '{path}' not found.\n"
    assert result.stderr == ""
