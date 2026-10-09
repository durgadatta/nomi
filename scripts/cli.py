#!/usr/bin/env python3
"""
Nomi CLI - Run Nomi or Python files
"""

import argparse
import json
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
        "--output",
        choices=("debug", "program", "json"),
        default="debug",
        help="Output format (default: legacy debug; program prints only program output)",
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
    parser.add_argument(
        "--check", action="store_true",
        help="Preview experimental source facts and obligations without execution",
    )
    parser.add_argument(
        "--require", action="append", default=[], metavar="RESTRICTION",
        help="Require an analysis restriction with --check (known-types or pure; repeatable)",
    )
    args = parser.parse_args(argv)
    if args.require and not args.check:
        parser.error("--require needs --check; restrictions do not change ordinary execution")
    return args


def report_check(result, output):
    record = result.to_record()
    if output == "json":
        print(json.dumps(record))
        return 0 if result.ok else 1
    label = record["source"]["filename"]
    analysis = record["analysis"]
    if analysis is None:
        for diagnostic in record["diagnostics"]:
            print(f"{label}: {diagnostic['code']}: {diagnostic['message']}", file=sys.stderr)
        return 1
    print(f"Checking {label} (experimental module-execution analysis; no code ran)")
    for fact in analysis["facts"]:
        if fact["kind"] == "binding" and fact.get("scope") == "module":
            print(f"  {fact['name']}: {fact['type'] or 'unknown'}")
    print("Effects: " + (", ".join(analysis["effects"]) or "none known"))
    for obligation in analysis["obligations"]:
        span = obligation.get("span") or {}
        position = f":{span['line']}:{span['column']}" if span.get("line") else ""
        print(f"{label}{position}: {obligation['code']}: {obligation['message']}")
        print(f"  {obligation['repair']}")
    for restriction in analysis["restrictions"]:
        status = "satisfied" if restriction["satisfied"] else "unfulfilled"
        print(f"{restriction['name']}: {status}")
    if not analysis["restrictions"]:
        print("Preview only; no restrictions selected.")
    return 0 if result.ok else 1


def report_setup_error(message, output):
    from prototype.runtime.diagnostics import Diagnostic

    diagnostic = Diagnostic(message=message, code="NOMI-CLI", phase="setup")
    if output == "json":
        print(
            json.dumps(
                {
                    "schema": "nomi.cli-inspection",
                    "version": 1,
                    "ok": False,
                    "stdout": "",
                    "stderr": "",
                    "bindings": {},
                    "diagnostics": [diagnostic.to_record()],
                    "pipeline": None,
                }
            )
        )
    else:
        print(f"NOMI-CLI: {message}", file=sys.stderr)
    return 1


def main():
    args = parse_args(sys.argv[1:])
    filename = args.filename or str(Path(__file__).with_name("demo.nomi"))
    file_path = Path(filename)

    if not file_path.exists():
        message = f"File '{filename}' not found."
        if args.output == "debug":
            print(f"Error: {message}")
            return 1
        return report_setup_error(message, args.output)

    if file_path.suffix == ".nomi" or file_path.name.endswith(".nomi.nb"):
        mode = "nomi"
    else:
        mode = "python"

    if args.output == "debug" and not args.check:
        print(f"Running: {filename}")
        print("-" * 40)

    from prototype.runtime import check, execute

    options = {"parser_frontend": args.parser_frontend} if args.parser_frontend else {}
    try:
        if args.check:
            return report_check(
                check(filename=file_path, mode=mode, requirements=tuple(args.require), **options),
                args.output,
            )
        result = execute(filename=file_path, mode=mode, raise_on_error=False, **options)
    except (ValueError, LookupError, OSError, ImportError) as error:
        return report_setup_error(str(error), args.output)
    if args.output == "json":
        print(
            json.dumps(
                {
                    "schema": "nomi.cli-inspection",
                    "version": 1,
                    "ok": result.ok,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "bindings": {
                        key: repr(value) for key, value in result.bindings.items()
                    },
                    "diagnostics": [
                        diagnostic.to_record() for diagnostic in result.diagnostics
                    ],
                    "pipeline": {
                        "parser_frontend": result.pipeline.parser_frontend,
                        "eval_backend": result.pipeline.eval_backend,
                    },
                }
            )
        )
        return 0 if result.ok else 1
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    if not result.ok:
        for diagnostic in result.diagnostics:
            span = diagnostic.span or {}
            position = f":{span['line']}:{span['column']}" if span.get("line") else ""
            print(
                f"{filename}{position}: {diagnostic.code}: {diagnostic.message}",
                file=sys.stderr,
            )
        return 1
    bindings = result.bindings

    if args.output == "debug":
        print("-" * 40)
        print("Global Environment:")
        for key, value in bindings.items():
            if key not in ("__builtins__", "builtins"):
                print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
