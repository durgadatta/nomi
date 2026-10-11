"""Module entry points retain canonical receipt classes during replay."""

import json
from pathlib import Path
import subprocess
import sys


def run(module, *arguments):
    return subprocess.run([sys.executable, "-m", module, *arguments], cwd=Path(__file__).resolve().parents[4], capture_output=True, text=True)


def test_program_induction_module_can_replay_its_own_receipt():
    result = run("tools.program_search")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["matches"] == 2


def test_contingent_cli_distinguishes_shallow_stop_and_deeper_information():
    shallow = run("tools.inquiry_policy", "--horizon", "1")
    deeper = run("tools.inquiry_policy", "--horizon", "2")
    assert shallow.returncode == deeper.returncode == 0, (shallow.stderr, deeper.stderr)
    assert "Proposed first choices: stop" in shallow.stdout
    assert "Expected loss plus query costs: [1/8, 1/8]" in deeper.stdout
    partial = run("tools.inquiry_policy", "--budget", "1", "--json")
    assert partial.returncode == 0, partial.stderr
    assert json.loads(partial.stdout)["coverage"] == "incomplete"
