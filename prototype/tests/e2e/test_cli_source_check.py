"""One unannotated invoice moves between execution and selected checks."""

import json
from pathlib import Path
import subprocess
import sys

import pytest

from prototype.tests.e2e.test_distribution_boundary import distribution  # noqa: F401


ROOT = Path(__file__).resolve().parents[3]
INVOICE = ROOT / "scripts/check_invoice.nomi"


def run_cli(*args):
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts/cli.py"), *map(str, args)],
        cwd=ROOT, capture_output=True, text=True, timeout=30,
    )


def test_invoice_executes_and_checks_without_rewriting_source():
    executed = run_cli(INVOICE, "--output", "program")
    assert executed.returncode == 0, executed.stderr
    assert executed.stdout == "3850\n"
    checked = run_cli(INVOICE, "--check", "--require", "known-types", "--output", "json")
    assert checked.returncode == 0, checked.stderr
    record = json.loads(checked.stdout)
    assert record["schema"] == "nomi.check"
    assert record["analysis"]["effects"] == ["ConsoleWrite"]
    assert any(f["name"] == "total" and f["type"] == "Int"
               for f in record["analysis"]["facts"])


def test_type_and_purity_requirements_are_independent():
    result = run_cli(INVOICE, "--check", "--require", "known-types",
                     "--require", "pure", "--output", "json")
    record = json.loads(result.stdout)
    assert result.returncode == 1
    assert {r["name"]: r["satisfied"] for r in record["analysis"]["restrictions"]} == {
        "known-types": True, "pure": False,
    }


def test_text_check_explains_facts_and_unfulfilled_purity():
    result = run_cli(INVOICE, "--check", "--require", "pure")
    assert result.returncode == 1
    assert "total: Int" in result.stdout
    assert "pure: unfulfilled" in result.stdout
    assert "ConsoleWrite" in result.stdout
    assert "3850\n" not in result.stdout


@pytest.mark.parametrize("requirement", ["unknown-policy", "pure"])
def test_invalid_or_misplaced_requirement_never_executes(requirement):
    args = [INVOICE, "--require", requirement, "--output", "json"]
    if requirement == "unknown-policy":
        args.append("--check")
    result = run_cli(*args)
    assert result.returncode != 0
    assert "3850" not in result.stdout


def test_unknown_dependency_is_previewable_but_not_proven(tmp_path):
    path = tmp_path / "dynamic.nomi"
    path.write_text("value = external_price()\n", encoding="utf-8")
    preview = run_cli(path, "--check", "--output", "json")
    assert preview.returncode == 0
    assert json.loads(preview.stdout)["analysis"]["obligations"]
    strict = run_cli(path, "--check", "--require", "pure", "--output", "json")
    assert strict.returncode == 1
    assert json.loads(strict.stdout)["analysis"]["obligations"]


def test_installed_invoice_checks_outside_checkout(distribution, tmp_path):
    installed, names = distribution
    assert "scripts/check_invoice.nomi" in names
    code = "\n".join([
        "import sys",
        f"sys.path.insert(0, {str(installed)!r})",
        "from pathlib import Path",
        "import prototype.analysis, scripts.cli",
        f"assert prototype.analysis.__file__.startswith({str(installed)!r})",
        "invoice = Path(scripts.cli.__file__).with_name('check_invoice.nomi')",
        "sys.argv = ['nomi', str(invoice), '--check', '--require', 'known-types', '--output', 'json']",
        "raise SystemExit(scripts.cli.main())",
    ])
    result = subprocess.run([sys.executable, "-I", "-c", code], cwd=tmp_path,
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["ok"] is True
