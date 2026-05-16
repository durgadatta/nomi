#!/usr/bin/env python3
"""Profile the Nomi pipeline for a file and open the HTML report.

Usage: python3 scripts/profile.py [filename]

Defaults to samples/demo.nomi if no filename is given.
"""

import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent


def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else "samples/demo.nomi"
    file_path = _REPO / filename

    if not file_path.exists():
        print(f"Error: file not found: {file_path}")
        sys.exit(1)

    profiler = _REPO / "tools" / "perf" / "profiler.py"
    subprocess.run(
        [sys.executable, str(profiler), "--file", str(file_path)],
        cwd=str(_REPO),
    )


if __name__ == "__main__":
    main()
