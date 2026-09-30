#!/usr/bin/env python3
"""
Nomi CLI - Run Nomi or Python files
"""

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="nomi",
        description="Run Nomi or Python files",
    )
    parser.add_argument(
        "filename",
        nargs="?",
        default=None,
        help=".nomi or .py file (default: scripts/demo.nomi)",
    )
    parser.add_argument(
        "--parser-frontend",
        default=None,
        help=("Optional Nomi parser frontend; omitted uses the runtime default"),
    )
    return parser.parse_args(argv)


def main():
    args = parse_args(sys.argv[1:])
    filename = args.filename or str(Path(__file__).with_name("demo.nomi"))
    file_path = Path(filename)

    if not file_path.exists():
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)

    if file_path.suffix == ".nomi" or file_path.name.endswith(".nomi.nb"):
        mode = "nomi"
    else:
        mode = "python"

    print(f"Running: {filename}")
    print("-" * 40)

    from prototype.runtime import execute

    options = {"parser_frontend": args.parser_frontend} if args.parser_frontend else {}
    result = execute(filename=file_path, mode=mode, **options)
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    bindings = result.bindings

    print("-" * 40)
    print("Global Environment:")
    for key, value in bindings.items():
        if key not in ("__builtins__", "builtins"):
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()
