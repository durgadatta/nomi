"""User entry points expose real source capture and a useful discovery loop."""

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[4]


def command(module, *arguments):
    return subprocess.run([sys.executable, "-m", module, *map(str, arguments)], cwd=ROOT, capture_output=True, text=True)


def test_capture_user_authored_nomi_file_without_running_it(tmp_path):
    source = tmp_path / "force.nomi"
    source.write_text("func force(position, velocity):\n    return -2 * position - velocity\n", encoding="utf-8")
    result = command("tools.nomi_terms", source, "--identity", "my-force")
    assert result.returncode == 0, result.stderr
    artifact = json.loads(result.stdout)
    assert artifact["producer"] == "nomi-pure-rational-source-v1"
    assert artifact["artifact"]["type"]["parameters"] == ["Rational", "Rational"]
    assert artifact["artifact"]["nodes"][0]["origin"]["source"] == "my-force"


def test_capture_refuses_effectful_file_with_a_short_diagnostic(tmp_path):
    source = tmp_path / "effect.nomi"
    source.write_text("(x) => print(x)", encoding="utf-8")
    result = command("tools.nomi_terms", source)
    assert result.returncode == 2
    assert "unresolved source name" in result.stderr
    assert "Traceback" not in result.stderr
    assert not result.stdout


def test_discovery_cli_is_readable_and_full_artifacts_are_optional():
    result = command("tools.intelligence_loop", "--observe", "4")
    assert result.returncode == 0, result.stderr
    assert "Proposed queries: 2, 3" in result.stdout
    assert "Posterior under the declared model: [0, 1]" in result.stdout
    assert "Next step: stop" in result.stdout
    full = command("tools.intelligence_loop", "--observe", "3", "--json")
    assert full.returncode == 0, full.stderr
    report = json.loads(full.stdout)
    assert report["after"]["plan"]["status"] == "needs-model-or-evidence-repair"


def test_discovery_cli_rejects_non_rational_inputs_without_traceback():
    result = command("tools.intelligence_loop", "--observe", "unknown")
    assert result.returncode == 2
    assert "Traceback" not in result.stderr
