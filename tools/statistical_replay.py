"""Independent replay of exact statistical receipts; standard library only.

This consumer does not import the planner, its type inference, or its rules.
It reconstructs typed terms with structural interning instead of comparing
planner fingerprints alone. It supports the closed exact fragment, not floats.
"""

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import sys


CATALOG_PATH = Path(__file__).resolve().parents[1] / "config/data_interface.json"
NAME = re.compile(r"[A-Za-z_][A-Za-z_0-9.-]{0,127}\Z")
SIGNATURES = {
    "input": (0, "input", ("schema",)),
    "column": (1, "column", ("field",)),
    "alias": (1, "alias", ()),
    "filter": (2, "filter", ()),
    "add": (2, "numeric", ()),
    "subtract": (2, "numeric", ()),
    "multiply": (2, "numeric", ()),
    "greater": (2, "compare", ()),
    "sum": (1, "sum", ()),
    "count_valid": (1, "count_valid", ()),
    "count_rows": (1, "count_rows", ()),
    "mean": (1, "mean", ()),
    "safe_divide": (2, "safe_divide", ()),
}
EXACT = {"ExactInt", "ExactRational"}
THEORY_FINGERPRINT = "af1eb30bd0a236a5dcb6f8f454756e4559b64be3a22effbe089dfda8baaf443c"


class ReplayError(ValueError):
    pass


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def fingerprint(value):
    return hashlib.sha256(encoded(value).encode()).hexdigest()


def _json_value(value, depth=0):
    if depth > 64:
        raise ReplayError("nesting budget exceeded")
    if type(value) is dict:
        for key, child in value.items():
            if type(key) is not str:
                raise ReplayError("non-string object key")
            _json_value(child, depth + 1)
    elif type(value) is list:
        for child in value:
            _json_value(child, depth + 1)
    elif type(value) not in (str, int, bool, type(None)):
        raise ReplayError("non-inert or unsupported value")


def _record(value, keys):
    if type(value) is not dict or set(value) != set(keys):
        raise ReplayError("contract attributes disagree")


def _identifier(value):
    if type(value) is not str or not NAME.fullmatch(value):
        raise ReplayError("invalid identifier")
    return value


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ReplayError("duplicate JSON key")
        result[key] = value
    return result


def read(path):
    with Path(path).open("rb") as stream:
        data = stream.read(1_000_001)
    if len(data) > 1_000_000:
        raise ReplayError("byte budget exceeded")
    try:
        result = json.loads(data, object_pairs_hook=_pairs)
        _json_value(result)
        return result
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise ReplayError(f"invalid artifact: {exc}") from exc


@dataclass(frozen=True)
class Shape:
    kind: str
    dtype: str | None = None
    nullable: bool = False
    domain: int | None = None
    fields: tuple = ()


def verify(document, receipt, catalog_document):
    """Return verified/refused; never evaluate a row or resolve a source."""
    try:
        for value in (document, receipt, catalog_document):
            _json_value(value)
            if len(encoded(value).encode()) > 1_000_000:
                raise ReplayError("byte budget exceeded")
        _record(document, ("version", "profile", "nodes", "outputs"))
        if type(document["version"]) is not int or document["version"] != 1:
            raise ReplayError("unsupported plan version")
        if document["profile"] != "exact-rational-v1":
            raise ReplayError(
                "this independent consumer supports only the exact profile"
            )
        if type(receipt) is not dict or receipt.get("status") != "equivalent":
            raise ReplayError("receipt does not claim established equality")
        core = {
            key: catalog_document.get(key) for key in ("profiles", "laws", "operations")
        }
        if fingerprint(core) != THEORY_FINGERPRINT:
            raise ReplayError(
                "catalog semantics changed without a supported theory revision"
            )
        expected_ops = {
            op: {"arity": arity, "type_rule": rule, "attributes": list(attrs)}
            for op, (arity, rule, attrs) in SIGNATURES.items()
        }
        if (
            type(catalog_document.get("version")) is not int
            or catalog_document["version"] != 1
            or encoded(catalog_document.get("operations")) != encoded(expected_ops)
        ):
            raise ReplayError(
                "catalog revision or ports disagree with the closed theory"
            )
        expected_profile = {
            "arithmetic": "unbounded exact integer/rational",
            "missing": "skip declared nulls in aggregates",
            "sum_empty": "zero",
            "mean_empty": "Missing",
            "divide_zero": "Missing",
            "nan": "unsupported",
            "units": "dimensionless fragment",
        }
        if (
            catalog_document.get("profiles", {}).get("exact-rational-v1")
            != expected_profile
        ):
            raise ReplayError(
                "catalog numeric definition disagrees with the closed theory"
            )
        if (
            type(document["nodes"]) is not list
            or not 1 <= len(document["nodes"]) <= 512
        ):
            raise ReplayError("node budget exceeded")
        nodes = {}
        for node in document["nodes"]:
            if type(node) is not dict:
                raise ReplayError("node must be an object")
            name = _identifier(node.get("id"))
            op = node.get("op")
            if type(op) is not str or op not in SIGNATURES or name in nodes:
                raise ReplayError("unsupported operator or duplicate identity")
            arity, _, attributes = SIGNATURES[op]
            _record(node, ("id", "op", "args", *attributes))
            if type(node["args"]) is not list or len(node["args"]) != arity:
                raise ReplayError("port arity disagrees")
            for arg in node["args"]:
                _identifier(arg)
            nodes[name] = node
        outputs = document["outputs"]
        if type(outputs) is not list or not outputs:
            raise ReplayError("outputs must be nonempty")
        for output in outputs:
            _identifier(output)
            if output not in nodes:
                raise ReplayError("unknown output")
        if len(set(outputs)) != len(outputs):
            raise ReplayError("duplicate output")
        for node in nodes.values():
            if any(arg not in nodes for arg in node["args"]):
                raise ReplayError("unknown dependency")

        # Intern keys contain child IDs, retaining linear DAG storage. Equality
        # uses these structural identities, not SHA-256 equality as an oracle.
        interned, hashes = {}, []

        def term(key, wire):
            if key not in interned:
                interned[key] = len(hashes)
                hashes.append(fingerprint(wire))
            return interned[key]

        def application(op, children):
            return term((op, *children), [op, *(hashes[child] for child in children)])

        shapes, terms, depths, steps = {}, {}, {}, []
        remaining = list(nodes)
        while remaining:
            progress = []
            for name in remaining:
                node = nodes[name]
                if any(arg not in terms for arg in node["args"]):
                    continue
                op = node["op"]
                args = [shapes[arg] for arg in node["args"]]
                children = [terms[arg] for arg in node["args"]]
                depths[name] = 1 + max((depths[arg] for arg in node["args"]), default=0)
                if depths[name] > 64:
                    raise ReplayError("dependency depth exceeded")
                normal = (
                    application(op, children)
                    if op not in ("input", "column", "alias", "mean")
                    else None
                )
                if op == "input":
                    schema = node["schema"]
                    if type(schema) is not list or not 1 <= len(schema) <= 128:
                        raise ReplayError("field budget exceeded")
                    fields = []
                    for field in schema:
                        _record(field, ("name", "dtype", "nullable"))
                        _identifier(field["name"])
                        if (
                            type(field["dtype"]) is not str
                            or field["dtype"]
                            not in (
                                "ExactInt",
                                "ExactRational",
                                "Float64",
                                "Bool",
                                "Text",
                            )
                            or type(field["nullable"]) is not bool
                        ):
                            raise ReplayError("invalid field contract")
                        fields.append(
                            (field["name"], field["dtype"], field["nullable"])
                        )
                    if len({field[0] for field in fields}) != len(fields):
                        raise ReplayError("duplicate field")
                    normal = term(
                        ("input", name, tuple(fields)), ["input", name, schema]
                    )
                    shape = Shape("relation", domain=normal, fields=tuple(fields))
                elif op == "alias":
                    shape, normal = args[0], children[0]
                    steps.append({"node": name, "rule": "alias-reference-v1"})
                elif op == "column":
                    _identifier(node["field"])
                    matches = [
                        field for field in args[0].fields if field[0] == node["field"]
                    ]
                    if args[0].kind != "relation" or not matches:
                        raise ReplayError("unknown relation field")
                    field = matches[0]
                    normal = term(
                        ("column", children[0], field[0]),
                        ["column", hashes[children[0]], field[0]],
                    )
                    shape = Shape("column", field[1], field[2], args[0].domain)
                elif op == "filter":
                    source, mask = args
                    if (
                        source.kind != "relation"
                        or mask.kind != "column"
                        or mask.dtype != "Bool"
                        or mask.nullable
                        or source.domain != mask.domain
                    ):
                        raise ReplayError("filter domain or mask disagrees")
                    shape = Shape("relation", domain=normal, fields=source.fields)
                elif op == "count_rows":
                    if args[0].kind != "relation":
                        raise ReplayError("row count requires a relation")
                    shape = Shape("scalar", "ExactInt")
                elif op in ("mean", "sum", "count_valid"):
                    source = args[0]
                    if source.kind != "column":
                        raise ReplayError("aggregation requires a column")
                    if op == "count_valid":
                        shape = Shape("scalar", "ExactInt")
                    else:
                        if source.dtype not in EXACT:
                            raise ReplayError(
                                "exact numeric law cannot consume this column"
                            )
                        shape = Shape("scalar", "ExactRational", op == "mean")
                    if op == "mean":
                        total = application("sum", children)
                        count = application("count_valid", children)
                        normal = application("safe_divide", [total, count])
                        steps.append({"node": name, "rule": "mean-valid-exact-v1"})
                elif op == "safe_divide":
                    if any(
                        arg.kind != "scalar" or arg.dtype not in EXACT for arg in args
                    ):
                        raise ReplayError("exact division requires exact scalars")
                    shape = Shape("scalar", "ExactRational", True)
                else:
                    first, second = args
                    if (
                        first.kind != "column"
                        or second.kind != "column"
                        or first.domain != second.domain
                        or first.dtype not in EXACT
                        or second.dtype not in EXACT
                    ):
                        raise ReplayError(
                            "exact column operation or alignment disagrees"
                        )
                    shape = Shape(
                        "column",
                        "Bool" if op == "greater" else "ExactRational",
                        first.nullable or second.nullable,
                        first.domain,
                    )
                shapes[name], terms[name] = shape, normal
                progress.append(name)
            if not progress:
                raise ReplayError("cyclic dependency")
            remaining = [name for name in remaining if name not in progress]

        left, right = receipt.get("left"), receipt.get("right")
        _identifier(left)
        _identifier(right)
        if (
            left not in terms
            or right not in terms
            or shapes[left] != shapes[right]
            or terms[left] != terms[right]
        ):
            raise ReplayError("typed structural terms do not establish equality")
        relevant, pending = set(), [left, right]
        while pending:
            name = pending.pop()
            if name not in relevant:
                relevant.add(name)
                pending.extend(nodes[name]["args"])
        # Planner traversal order may differ; the receipt's ordered steps must
        # each be present exactly once, with the same node/rule association.
        expected_steps = [step for step in steps if step["node"] in relevant]
        actual_steps = receipt.get("steps")
        if type(actual_steps) is not list or sorted(
            actual_steps, key=encoded
        ) != sorted(expected_steps, key=encoded):
            raise ReplayError("derivation steps disagree")
        expected = {
            "version": 1,
            "status": "equivalent",
            "context": fingerprint(
                {"plan": document, "catalog": catalog_document, "checker": 1}
            ),
            "profile": "exact-rational-v1",
            "theory": "statistical-interface-v1",
            "left": left,
            "right": right,
            "normal_forms": [hashes[terms[left]], hashes[terms[right]]],
            "steps": actual_steps,
            "reason": "same typed normal form",
        }
        if encoded(receipt) != encoded(expected):
            raise ReplayError("receipt context or derivation fingerprints disagree")
        return {
            "status": "verified",
            "consumer": "independent-exact-v1",
            "left": left,
            "right": right,
        }
    except (ReplayError, TypeError, KeyError, AttributeError) as exc:
        return {"status": "refused", "reason": str(exc)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan")
    parser.add_argument("receipt")
    args = parser.parse_args(argv)
    try:
        result = verify(read(args.plan), read(args.receipt), read(CATALOG_PATH))
    except (OSError, ReplayError) as exc:
        result = {"status": "refused", "reason": str(exc)}
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "verified" else 1


if __name__ == "__main__":
    sys.exit(main())
