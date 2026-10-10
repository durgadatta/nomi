"""Inspect or prove declared plans, with no input data or execution engine."""

import argparse
import json
import sys

from .model import Plan, PlanError, catalog, load_document


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser(
        "catalog", help="show implemented ports and catalog-only families"
    )
    for command in ("check", "inspect", "prove"):
        sub = commands.add_parser(command)
        sub.add_argument("plan", help="schema-only JSON plan; no dataset bindings")
        if command == "inspect":
            sub.add_argument("node")
        if command == "prove":
            sub.add_argument("left")
            sub.add_argument("right")
    args = parser.parse_args(argv)
    try:
        if args.command == "catalog":
            result = catalog()
        else:
            plan = Plan.from_document(load_document(args.plan))
            if args.command == "check":
                result = plan.check()
            elif args.command == "inspect":
                result = plan.inspect(args.node)
            else:
                result = plan.prove(args.left, args.right)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1 if result.get("status") == "unknown" else 0
    except (PlanError, OSError) as exc:
        print(json.dumps({"status": "invalid", "error": str(exc)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
