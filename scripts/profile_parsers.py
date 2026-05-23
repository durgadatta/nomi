#!/usr/bin/env python3
"""Benchmark Nomi parser frontends and print a comparison table.

Usage: python3 scripts/profile_parsers.py [filename]

Defaults to samples/demo.nomi if no filename is given.
"""

import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent


def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else "samples/comprehensive.nomi"
    file_path = _REPO / filename

    if not file_path.exists():
        print(f"Error: file not found: {file_path}")
        sys.exit(1)

    bench = _REPO / "tools" / "perf" / "bench_parsers.py"
    subprocess.run(
        [sys.executable, str(bench), "--file", str(file_path), "--open"],
        cwd=str(_REPO),
    )


if __name__ == "__main__":
    main()
