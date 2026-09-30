import subprocess
import sys
from pathlib import Path

import pytest

from prototype.runtime import inspect

ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.parametrize(
    "stage",
    [
        "python-ast",
        "core",
        "core-json",
        "core-verify",
        "core-to-python",
        "backend-lowered",
        "runtime-cache-key",
        "features",
        "capabilities",
        "target-alignment",
        "parser-frontends",
        "eval-backends",
        "host-capabilities",
        "resolved-pipelines",
        "passes",
        "expansions",
    ],
)
def test_inspection_cli_preserves_runtime_output_and_legacy_all_passes(stage, tmp_path):
    source = "x = 2\nprint(x + 3)\n"
    filename = tmp_path / "example.nomi"
    filename.write_text(source)
    runtime_stage = "python_ast" if stage == "python-ast" else stage
    mode = "reduced" if stage in {"passes", "expansions"} else "nomi"
    expected = inspect(
        source=source, filename=filename, stage=runtime_stage, mode=mode
    ).output
    result = subprocess.run(
        [sys.executable, "-m", "tools.syntax.inspect", str(filename), "--stage", stage],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == expected + "\n"


def test_inspection_help_does_not_load_parser_or_runtime(tmp_path):
    script = ROOT / "tools/syntax/inspect.py"
    result = subprocess.run(
        [sys.executable, "-I", "-S", str(script), "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "--stage" in result.stdout


def test_inspection_stage_argument_requires_a_value():
    result = subprocess.run(
        [sys.executable, "-m", "tools.syntax.inspect", "--stage"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert result.returncode != 0
    assert "expected one argument" in result.stderr


def test_source_inspection_script_does_not_shadow_stdlib_inspect(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools/syntax/inspect.py"),
            "--stage",
            "target-alignment",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == inspect(stage="target_alignment").output + "\n"
