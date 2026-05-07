import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def test_test_report_help_documents_no_open_flag():
    result = subprocess.run(
        [sys.executable, "scripts/test_report.py", "--help"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=10,
    )

    assert result.returncode == 0
    assert "Generate pytest and coverage HTML reports." in result.stdout
    assert "--no-open" in result.stdout
