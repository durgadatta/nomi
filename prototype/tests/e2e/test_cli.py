import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "scripts/cli.py", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=20,
    )


def test_cli_help_prints_usage():
    result = run_cli("--help")

    assert result.returncode == 0
    assert "Usage: nomi [filename]" in result.stdout
    assert result.stderr == ""


def test_cli_reports_missing_file():
    result = run_cli("does-not-exist.nomi")

    assert result.returncode == 1
    assert "Error: File 'does-not-exist.nomi' not found." in result.stdout


def test_cli_runs_nomi_demo():
    result = run_cli("scripts/demo.nomi")

    assert result.returncode == 0
    assert "Nomi Demo: Key Features" in result.stdout
    assert "8. Data pipeline:" in result.stdout
    assert "filtered: [30, 60, 84, 16]" in result.stdout


def test_cli_runs_python_file(tmp_path):
    source = tmp_path / "program.py"
    source.write_text("x = 2\nprint(f'value={x}')\n", encoding="utf-8")

    result = run_cli(str(source))

    assert result.returncode == 0
    assert "value=2" in result.stdout
    assert "x: 2" in result.stdout
