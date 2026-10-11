"""Standalone replay of one exact formal fragment. Imports no Nomi tools/engines."""

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re

PROFILE = "formal-rational-polynomial-v1"


class ReplayError(ValueError):
    pass


def canonical(value):
    try:
        result = json.dumps(
            value, sort_keys=True, separators=(",", ":"), allow_nan=False
        )
    except (TypeError, ValueError, RecursionError) as error:
        raise ReplayError("invalid bounded artifact") from error
    if len(result.encode()) > 1_000_000:
        raise ReplayError("artifact exceeds byte budget")

    def inert(item, depth=0):
        if depth > 64:
            raise ReplayError("artifact exceeds depth budget")
        if type(item) is dict:
            for key, child in item.items():
                if type(key) is not str:
                    raise ReplayError("nontext artifact key")
                inert(child, depth + 1)
        elif type(item) is list:
            for child in item:
                inert(child, depth + 1)
        elif type(item) not in (str, int, bool, type(None)):
            raise ReplayError("unsupported artifact value")

    inert(value)
    return result


def identifier(value):
    if type(value) is not str or not re.fullmatch(
        r"[A-Za-z_][A-Za-z_0-9.-]{0,127}", value
    ):
        raise ReplayError("invalid identity")
    return value


def exact(record, fields):
    if type(record) is not dict or set(record) != set(fields):
        raise ReplayError("invalid record fields")


def dimensions(raw):
    if type(raw) is not dict or len(raw) > 16:
        raise ReplayError("invalid dimension")
    for key, value in raw.items():
        identifier(key)
        if type(value) is not int or not value or not -128 <= value <= 128:
            raise ReplayError("invalid dimension exponent")
    return dict(sorted(raw.items()))


def dimension_sum(left, right, scale=1):
    counter = Counter(left)
    for key, value in right.items():
        counter[key] += scale * value
    return dimensions({key: value for key, value in counter.items() if value})


def reduce_terms(terms):
    result = {}
    for factors, coefficient in terms:
        key = tuple(sorted(factors))
        result[key] = result.get(key, Fraction(0)) + coefficient
    result = {key: value for key, value in result.items() if value}
    if len(result) > 256:
        raise ReplayError("monomial capacity")
    for factors, coefficient in result.items():
        if len(factors) > 32:
            raise ReplayError("degree capacity")
        if (
            max(
                abs(coefficient.numerator).bit_length(),
                coefficient.denominator.bit_length(),
            )
            > 4096
        ):
            raise ReplayError("coefficient capacity")
    return result


def product(left, right):
    return reduce_terms(
        (p + q, a * b) for p, a in left.items() for q, b in right.items()
    )


def export(poly, symbols):
    rows = []
    for factors, coefficient in poly.items():
        counts = Counter(factors)
        rows.append(
            (
                tuple(counts[s] for s in symbols),
                {
                    "coefficient": [coefficient.numerator, coefficient.denominator],
                    "powers": dict(sorted(counts.items())),
                },
            )
        )
    return [row for _, row in sorted(rows)]


def expected_receipt(source):
    # Snapshot first: callers cannot mutate checked facts while replay proceeds.
    source = json.loads(canonical(source))
    exact(
        source,
        (
            "version",
            "id",
            "revision",
            "profile",
            "derivation",
            "objects",
            "relations",
            "claims",
        ),
    )
    if (
        type(source["version"]) is not int
        or source["version"] != 1
        or source["profile"] != PROFILE
    ):
        raise ReplayError("unsupported fragment")
    identifier(source["id"])
    identifier(source["revision"])
    derivation = source["derivation"]
    exact(derivation, ("id", "dimension", "images"))
    identifier(derivation["id"])
    variable_dimension = dimensions(derivation["dimension"])
    if not variable_dimension or type(derivation["images"]) is not dict:
        raise ReplayError("invalid formal derivation")
    if type(source["objects"]) is not list or not 1 <= len(source["objects"]) <= 128:
        raise ReplayError("invalid expression collection")
    nodes = {}
    edges = {}
    for node in source["objects"]:
        if type(node) is not dict:
            raise ReplayError("invalid expression")
        identity = identifier(node.get("id"))
        if identity in nodes:
            raise ReplayError("duplicate expression")
        operation = node.get("op")
        if operation == "symbol":
            exact(node, ("id", "op", "label", "dimension"))
            if type(node["label"]) is not str or not 1 <= len(node["label"]) <= 128:
                raise ReplayError("invalid display label")
            refs = []
        elif operation == "rational":
            exact(node, ("id", "op", "numerator", "denominator", "dimension"))
            n, d = node["numerator"], node["denominator"]
            if type(n) is not int or type(d) is not int or d <= 0:
                raise ReplayError("invalid exact rational")
            if max(abs(n).bit_length(), d.bit_length()) > 4096:
                raise ReplayError("source rational capacity")
            refs = []
        elif operation in ("add", "multiply"):
            exact(node, ("id", "op", "args"))
            refs = node["args"]
            if type(refs) is not list or not 2 <= len(refs) <= 16:
                raise ReplayError("invalid operand list")
        elif operation == "differentiate":
            exact(node, ("id", "op", "arg"))
            refs = [node["arg"]]
        else:
            raise ReplayError("unsupported operation")
        nodes[identity] = node
        edges[identity] = tuple(identifier(ref) for ref in refs)
    symbols = tuple(
        sorted(key for key, node in nodes.items() if node["op"] == "symbol")
    )
    if not 1 <= len(symbols) <= 16:
        raise ReplayError("generator capacity")
    depth, contains_derivative, visiting = {}, {}, set()

    def structure(identity):
        if identity not in nodes:
            raise ReplayError("unknown expression")
        if identity in depth:
            return depth[identity]
        if identity in visiting:
            raise ReplayError("cyclic expression")
        visiting.add(identity)
        if len(visiting) > 64:
            raise ReplayError("expression depth capacity")
        height = 1 + max((structure(ref) for ref in edges[identity]), default=0)
        if height > 64:
            raise ReplayError("expression depth capacity")
        depth[identity] = height
        contains_derivative[identity] = nodes[identity]["op"] == "differentiate" or any(
            contains_derivative[ref] for ref in edges[identity]
        )
        visiting.remove(identity)
        return height

    for identity in nodes:
        structure(identity)
    images = derivation["images"]
    for symbol, image in images.items():
        if symbol not in symbols or (
            image is not None
            and (
                type(image) is not str
                or image not in nodes
                or contains_derivative[image]
            )
        ):
            raise ReplayError("invalid derivative image")
    values, spaces = {}, {}

    def value(identity):
        if identity in values:
            return values[identity]
        node = nodes[identity]
        op = node["op"]
        for ref in edges[identity]:
            value(ref)
        if op == "symbol":
            result = {(identity,): Fraction(1)}
            dim = dimensions(node["dimension"])
        elif op == "rational":
            result = reduce_terms(
                [((), Fraction(node["numerator"], node["denominator"]))]
            )
            dim = dimensions(node["dimension"])
        elif op == "multiply":
            result, dim = {(): Fraction(1)}, {}
            for ref in node["args"]:
                result = product(result, values[ref])
                dim = dimension_sum(dim, spaces[ref])
        elif op == "add":
            result, dim = {}, spaces[node["args"][0]]
            for ref in node["args"]:
                if spaces[ref] != dim:
                    raise ReplayError("addition dimension mismatch")
                result = reduce_terms([*result.items(), *values[ref].items()])
        else:
            dim = dimension_sum(spaces[node["arg"]], variable_dimension, -1)
            result = {}
            # Different representation/algorithm: replace each factor occurrence.
            for factors, coefficient in values[node["arg"]].items():
                for index, symbol in enumerate(factors):
                    if symbol not in images:
                        raise ReplayError("missing derivative premise")
                    image = images[symbol]
                    if image is not None:
                        remaining = factors[:index] + factors[index + 1 :]
                        contribution = product({remaining: coefficient}, value(image))
                        result = reduce_terms([*result.items(), *contribution.items()])
        values[identity], spaces[identity] = result, dim
        return result

    for identity in nodes:
        value(identity)
    for symbol, image in images.items():
        if image is not None and spaces[image] != dimension_sum(
            spaces[symbol], variable_dimension, -1
        ):
            raise ReplayError("derivative dimension mismatch")

    def difference(record):
        a, b = record["left"], record["right"]
        if type(a) is not str or type(b) is not str or a not in nodes or b not in nodes:
            raise ReplayError("unknown statement subject")
        if spaces[a] != spaces[b]:
            raise ReplayError("statement dimension mismatch")
        return spaces[a], reduce_terms(
            [
                *values[a].items(),
                *((power, -coefficient) for power, coefficient in values[b].items()),
            ]
        )

    def records(raw):
        if type(raw) is not list or len(raw) > 128:
            raise ReplayError("record capacity")
        for record in raw:
            if type(record) is not dict:
                raise ReplayError("invalid record")
            identifier(record.get("id"))
        return raw

    relations = {}
    for record in records(source["relations"]):
        exact(record, ("id", "left", "right"))
        if record["id"] in nodes or record["id"] in relations:
            raise ReplayError("duplicate relation")
        relations[record["id"]] = difference(record)
    contradictions = [
        key for key, (_, poly) in relations.items() if poly and set(poly) == {()}
    ]
    claims, seen = [], set()
    for record in records(source["claims"]):
        exact(record, ("id", "left", "right", "witness"))
        if record["id"] in nodes or record["id"] in relations or record["id"] in seen:
            raise ReplayError("duplicate claim")
        seen.add(record["id"])
        dim, residual = difference(record)
        if type(record["witness"]) is not list or len(record["witness"]) > 128:
            raise ReplayError("witness capacity")
        for term in record["witness"]:
            exact(term, ("relation", "multiplier"))
            rel, factor = term["relation"], term["multiplier"]
            if (
                type(rel) is not str
                or type(factor) is not str
                or rel not in relations
                or factor not in nodes
            ):
                raise ReplayError("unknown witness subject")
            relation_dim, polynomial = relations[rel]
            if dimension_sum(relation_dim, spaces[factor]) != dim:
                raise ReplayError("witness dimension mismatch")
            contribution = product(polynomial, values[factor])
            residual = reduce_terms(
                [
                    *residual.items(),
                    *(
                        (powers, -coefficient)
                        for powers, coefficient in contribution.items()
                    ),
                ]
            )
        claims.append(
            {
                "id": record["id"],
                "status": "inconsistent-premises"
                if contradictions
                else "conditional-identity"
                if not residual
                else "unknown",
                "witness": record["witness"],
                "residual": export(residual, symbols),
            }
        )
    return {
        "version": 1,
        "profile": PROFILE,
        "context": hashlib.sha256(
            canonical(
                {"domain": "nomi.formal-polynomial-1", "artifact": source}
            ).encode()
        ).hexdigest(),
        "objects": [
            {
                "id": key,
                "dimension": spaces[key],
                "normal": export(values[key], symbols),
            }
            for key in nodes
        ],
        "relations": [
            {"id": key, "dimension": dim, "normal": export(poly, symbols)}
            for key, (dim, poly) in relations.items()
        ],
        "claims": claims,
        "scope": {
            "inputs": "none",
            "derivation": "declared formal generator images",
            "premise_consistency": "direct-contradiction"
            if contradictions
            else "not-checked",
            "direct_contradictions": contradictions,
            "physical_validity": "not-established",
            "solver": "not-run",
            "independent": False,
        },
    }


def replay(source, receipt):
    if canonical(expected_receipt(source)) != canonical(receipt):
        raise ReplayError("receipt does not match independently checked formal facts")
    return {
        "status": "replayed",
        "independent": True,
        "context": receipt["context"],
        "scope": "checked dimension, normal-form and witness outcomes; no physical or analytic validity",
    }


def load(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ReplayError("duplicate JSON key")
            result[key] = value
        return result

    with Path(path).open("rb") as source:
        raw = source.read(1_000_001)
    if len(raw) > 1_000_000:
        raise ReplayError("artifact byte capacity")
    return json.loads(raw.decode("utf-8"), object_pairs_hook=pairs)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model")
    parser.add_argument("receipt")
    args = parser.parse_args(argv)
    try:
        result = replay(load(args.model), load(args.receipt))
    except (ReplayError, OSError, ValueError, RecursionError) as error:
        print(json.dumps({"status": "refused", "message": str(error)}))
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
