#!/usr/bin/env python3
"""
Nomi CLI - Run Nomi or Python files
"""

import sys
import argparse
from pathlib import Path

from prototype.parser.nomi.frontend import DEFAULT_FRONTEND


def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="nomi",
        description="Run Nomi or Python files",
    )
    parser.add_argument(
        "filename",
        nargs="?",
        default="scripts/demo.nomi",
        help=".nomi or .py file (default: scripts/demo.nomi)",
    )
    parser.add_argument(
        "--parser-frontend",
        default=DEFAULT_FRONTEND,
        help=(
            "Nomi parser frontend to preflight before execution "
            f"(default: {DEFAULT_FRONTEND})"
        ),
    )
    return parser.parse_args(argv)


def main():
    args = parse_args(sys.argv[1:])
    filename = args.filename
    file_path = Path(filename)
    
    if not file_path.exists():
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    
    if file_path.suffix == '.nomi' or file_path.name.endswith('.nomi.nb'):
        mode = "nomi"
    else:
        mode = "python"
    
    print(f"Running: {filename}")
    print("-" * 40)

    from prototype.runtime import execute

    result = execute(
        filename=file_path,
        mode=mode,
        parser_frontend=args.parser_frontend,
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    bindings = result.bindings
    
    print("-" * 40)
    print("Global Environment:")
    for key, value in bindings.items():
        if key not in ('__builtins__', 'builtins'):
            print(f"{key}: {value}")

if __name__ == "__main__":
    main()
