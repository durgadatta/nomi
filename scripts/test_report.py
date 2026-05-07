#!/usr/bin/env python3
"""Generate clickable pytest and coverage HTML reports."""

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
COVERAGE_DIR = REPORTS / "coverage"
PYTEST_REPORT = REPORTS / "pytest.html"
INDEX = REPORTS / "index.html"


def write_index():
    INDEX.write_text(
        """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Nomi Test Reports</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 2rem; line-height: 1.5; }
    a { display: block; margin: 0.75rem 0; font-size: 1.1rem; }
    code { background: #f2f2f2; padding: 0.1rem 0.25rem; border-radius: 3px; }
  </style>
</head>
<body>
  <h1>Nomi Test Reports</h1>
  <a href="pytest.html">Pytest HTML Report</a>
  <a href="coverage/index.html">Coverage HTML Report</a>
  <p>Regenerate with <code>python3 scripts/test_report.py</code>.</p>
</body>
</html>
""",
        encoding="utf-8",
    )


def main():
    REPORTS.mkdir(exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "pytest",
        "--cov=prototype",
        f"--cov-report=html:{COVERAGE_DIR}",
        "--cov-report=term-missing",
        f"--html={PYTEST_REPORT}",
        "--self-contained-html",
    ]
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode == 0:
        write_index()
        print()
        print(f"Reports written to: {INDEX.relative_to(ROOT)}")
        print(f"Coverage report:    {(COVERAGE_DIR / 'index.html').relative_to(ROOT)}")
        print(f"Pytest report:      {PYTEST_REPORT.relative_to(ROOT)}")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
