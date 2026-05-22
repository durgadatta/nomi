import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[4]
GRAMMAR_DIR = REPO_ROOT / "tools" / "parser_spikes" / "tree_sitter_nomi"
DEMO = REPO_ROOT / "samples" / "demo.nomi"


def _tree_sitter_binary() -> str | None:
    return (
        shutil.which("tree-sitter")
        or os.environ.get("TREE_SITTER_BIN")
        or _cargo_tree_sitter()
    )


def _cargo_tree_sitter() -> str | None:
    candidate = Path.home() / ".cargo" / "bin" / "tree-sitter"
    return str(candidate) if candidate.exists() else None


def test_tree_sitter_spike_parses_demo_without_errors(tmp_path):
    tree_sitter = _tree_sitter_binary()
    if tree_sitter is None:
        pytest.skip("tree-sitter CLI is not installed")

    env = os.environ.copy()
    env["HOME"] = str(tmp_path)
    result = subprocess.run(
        [
            tree_sitter,
            "parse",
            "--grammar-path",
            str(GRAMMAR_DIR),
            str(DEMO),
            "--json-summary",
        ],
        cwd=GRAMMAR_DIR,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )

    output_start = result.stdout.find("{")
    assert output_start >= 0, result.stdout + result.stderr
    summary = json.loads(result.stdout[output_start:])
    parse_summary = summary["parse_summaries"][0]

    assert parse_summary["successful"] is True
    assert parse_summary["file"] == str(DEMO)
