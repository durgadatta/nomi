"""Explicit Nomi-source producer for the bounded pure rational term profile.

Uses the existing frontend and lowering, with no evaluation or grammar fork.
The position collector is a removable bridge until typed Surface carries spans
for all expressions. It does not certify ordinary Nomi numeric semantics.
"""

import argparse
import ast
import hashlib
import json
from pathlib import Path

from lark import Token
from lark.exceptions import LarkError

from prototype.parser.nomi.ast_ import NomiToPythonAST
from prototype.parser.nomi.usage import parse_raw_tree, parse_transformed_tree
from tools import scoped_terms as t

PRODUCER = "nomi-pure-rational-source-v1"
RULES = frozenset({
    "file_input", "expr_stmt", "func_expr", "funcdef", "parameters", "name",
    "suite", "return_stmt", "bin_expr", "factor", "var", "number",
    "paren_expr", "funccall", "arguments",
})


def parse(source, context=()):
    if type(source) is not t.Source:
        raise t.Refused("Nomi producer requires a captured source revision")
    code = source.text if source.text.endswith("\n") else source.text + "\n"
    spans = {}

    class Positioned(NomiToPythonAST):
        def _call_userfunc(self, tree, new_children=None):
            children = tree.children if new_children is None else new_children
            result = super()._call_userfunc(tree, new_children)
            if isinstance(result, ast.AST):
                if not tree.meta.empty:
                    span = (tree.meta.start_pos, tree.meta.end_pos)
                else:
                    # Precedence reduction rebuilds some trees without metadata.
                    # Retain the smallest contributor interval, not fake AST offsets.
                    contributors = [spans[id(x)] for x in children if id(x) in spans]
                    span = (
                        (min(x[0] for x in contributors), max(x[1] for x in contributors))
                        if contributors else None
                    )
                if span is not None:
                    spans[id(result)] = span
            return result

    try:
        raw = parse_raw_tree(code=code, preserve_positions=True)
        for tree in raw.iter_subtrees_topdown():
            if tree.data not in RULES:
                raise t.Refused(f"Nomi rational profile excludes source form: {tree.data}")
            if tree.data == "func_expr" and not code[tree.meta.start_pos:].startswith("("):
                raise t.Refused("anonymous Nomi parameters require parentheses")
        for token in raw.scan_values(lambda x: isinstance(x, Token)):
            if token.type == "STAR" and code[token.start_pos:token.end_pos] != "*":
                raise t.Refused("implicit multiplication is outside the source profile")
        module = Positioned().transform(
            parse_transformed_tree(code=code, preserve_positions=True)
        )
    except (LarkError, RecursionError) as error:
        raise t.Refused("invalid or oversized Nomi function draft") from error
    if type(module) is not ast.Module or len(module.body) != 1:
        raise t.Refused("capture exactly one Nomi function description")
    root = module.body[0]
    if type(root) is ast.Expr:
        root = root.value
    if type(root) is not ast.FunctionDef:
        raise t.Refused("expected named or anonymous Nomi function")

    def origin_for(node):
        if id(node) not in spans:
            raise t.Refused("frontend did not retain source correspondence")
        start, end = spans[id(node)]
        end = min(end, len(source.text))
        return t.Origin(
            source.identity, source.revision, source.digest,
            len(source.text[:start].encode()), len(source.text[:end].encode()),
        )

    return t.from_ast(source, root, context, origin_for=origin_for)


def describe(source, context=()):
    return {"producer": PRODUCER, "artifact": t.describe(parse(source, context), context)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", type=Path, help="one pure Nomi function; captured, never run")
    parser.add_argument("--identity", help="source owner (default: path-qualified filename)")
    parser.add_argument("--revision", help="revision label (default: content digest)")
    args = parser.parse_args()
    try:
        if args.source is None:
            source = t.Source("nomi-square", "1", "func square(x):\n    return x * x\n")
        else:
            code = args.source.read_text(encoding="utf-8")
            source = t.Source(
                args.identity or (args.source.name[:40] + "@" + hashlib.sha256(str(args.source.resolve()).encode()).hexdigest()),
                args.revision or hashlib.sha256(code.encode()).hexdigest(), code,
            )
        print(json.dumps(describe(source), indent=2))
    except (OSError, UnicodeError, t.Refused) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
