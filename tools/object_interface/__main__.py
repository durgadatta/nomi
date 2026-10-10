"""Inspect/check inert objects; explicitly choose an adapter to realize them."""

import argparse
import json
import sys

from . import ContractError, Graph, Requirements, Vocabulary, load_document
from .backend import BackendFailure, Cancelled
from .documents import ValueContractError
from .documentary import document_backend, document_vocabulary
from .examples import lab_vocabulary, python_backend


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--vocabulary", help="explicit vocabulary artifact; default: tracked lab"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("check", "inspect", "compare", "compile", "run", "requirements"):
        child = commands.add_parser(command)
        child.add_argument("graph")
        if command == "inspect":
            child.add_argument("object")
        if command == "compare":
            child.add_argument("left")
            child.add_argument("right")
        if command in ("compile", "run"):
            child.add_argument(
                "--backend",
                required=True,
                choices=("python-exact-text", "document-blocks", "document-stream"),
            )
            child.add_argument(
                "--output",
                action="append",
                help="select a named object; repeat for multiple outputs",
            )
            child.add_argument(
                "--requirements", help="explicit required input/literal conditions"
            )
            child.add_argument(
                "--include-condition-inputs",
                action="store_true",
                help="explicitly bind condition-only inputs without adding computation or outputs",
            )
        if command == "run":
            child.add_argument("bindings")
        if command == "requirements":
            child.add_argument("requirements")
            child.add_argument(
                "--bindings", help="explicit input snapshot; no backend execution"
            )
    args = parser.parse_args(argv)
    try:
        vocabulary = (
            Vocabulary.from_document(load_document(args.vocabulary))
            if args.vocabulary
            else lab_vocabulary()
        )
        graph = Graph.from_document(load_document(args.graph), vocabulary)
        if args.command == "check":
            result = graph.check()
        elif args.command == "inspect":
            result = graph.inspect(args.object)
        elif args.command == "compare":
            result = graph.compare(args.left, args.right)
        elif args.command == "requirements":
            requirements = Requirements.from_document(
                load_document(args.requirements), graph
            )
            result = requirements.check(
                None if args.bindings is None else load_document(args.bindings)
            )
        else:
            if args.include_condition_inputs and not args.requirements:
                raise ContractError(
                    "condition-input inclusion requires an explicit requirement artifact"
                )
            # This explicitly selected example adapter accepts only its pinned vocabulary.
            backend = (
                python_backend(lab_vocabulary())
                if args.backend == "python-exact-text"
                else document_backend(
                    document_vocabulary(), args.backend.removeprefix("document-")
                )
            )
            compiled = backend.compile(
                graph,
                None if args.output is None else [graph.ref(i) for i in args.output],
            )
            if args.requirements:
                compiled = compiled.require(
                    Requirements.from_document(load_document(args.requirements), graph),
                    include_condition_inputs=args.include_condition_inputs,
                )
            if args.command == "compile":
                result = compiled.inspect()
            else:
                realization = compiled.bind(load_document(args.bindings)).execute()
                result = {"values": realization.values, "receipt": realization.receipt}
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1 if result.get("status") in ("unknown", "pending", "refuted") else 0
    except ValueContractError as exc:
        report = exc.report
        print(
            json.dumps(
                {
                    "status": "refused",
                    "kind": "value-contract",
                    "message": str(exc),
                    "errors": report["errors"],
                    "complete": report["complete"],
                }
            ),
            file=sys.stderr,
        )
        return 2
    except (ContractError, BackendFailure, Cancelled, OSError) as exc:
        print(json.dumps({"status": "refused", "message": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
