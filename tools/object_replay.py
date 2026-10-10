"""Independent passive replay for the pinned engine-free object lab vocabulary.

Standard library only; no planner, shared inference, normalizer or backend.
Other vocabularies require independently admitted consumer rules, not an
automatic reinterpretation of supplied definitions as new trusted laws.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

VOCABULARY = "261a416c00ab73b7849ce085ed9c4436b9fe941fcc4414dd384216d6552d782a"
LIMIT = 1_000_000
IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z_0-9.-]{0,127}\Z")

# These rules are reviewed independently of producer metadata/implementation.
RULES = {
    "exact.input": ("ExactInt", "input", ()),
    "exact.literal": ("ExactInt", "literal", ()),
    "exact.alias": ("ExactInt", "alias", ("target",)),
    "exact.add": ("ExactInt", "apply", ("left", "right")),
    "exact.multiply": ("ExactInt", "apply", ("left", "right")),
    "exact.double": ("ExactInt", "double", ("value",)),
    "exact.square": ("ExactInt", "square", ("value",)),
    "text.input": ("Text", "input", ()),
    "text.literal": ("Text", "literal", ()),
    "text.alias": ("Text", "alias", ("target",)),
    "text.concat": ("Text", "apply", ("left", "right")),
    "document.describe": ("Document", "description", ("body", "title")),
}


class ReplayError(ValueError):
    pass


def _encode(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError, RecursionError) as exc:
        raise ReplayError("invalid artifact encoding") from exc


def _digest(value):
    return hashlib.sha256(_encode(value).encode()).hexdigest()


def _inert(value, depth=0):
    if depth > 64:
        raise ReplayError("artifact nesting budget exceeded")
    if type(value) is dict:
        for key, child in value.items():
            if type(key) is not str:
                raise ReplayError("invalid record key")
            _inert(child, depth + 1)
    elif type(value) is list:
        for child in value:
            _inert(child, depth + 1)
    elif type(value) not in (str, int, bool, type(None)):
        raise ReplayError("non-inert artifact value")


def _artifact(value):
    _inert(value)
    if len(_encode(value).encode()) > LIMIT:
        raise ReplayError("artifact byte budget exceeded")


def _keys(value, expected):
    if type(value) is not dict or set(value) != set(expected):
        raise ReplayError(f"expected exact record fields {expected}")


def _identity(value):
    if type(value) is not str or not IDENTIFIER.fullmatch(value):
        raise ReplayError("invalid reference identity")
    return value


def _unique_names(values):
    if type(values) is not list or not values:
        raise ReplayError("expected nonempty reference list")
    for value in values:
        _identity(value)
    if len(values) != len(set(values)):
        raise ReplayError("duplicate reference")


def replay(vocabulary, graph, receipt):
    for artifact in (vocabulary, graph, receipt):
        _artifact(artifact)
    if _digest(vocabulary) != VOCABULARY:
        raise ReplayError("independent consumer does not admit this vocabulary")
    _keys(graph, ("version", "vocabulary", "objects", "outputs"))
    if (
        type(graph["version"]) is not int
        or graph["version"] != 1
        or graph["vocabulary"] != VOCABULARY
    ):
        raise ReplayError("unsupported object graph context")
    if type(graph["objects"]) is not list or not 1 <= len(graph["objects"]) <= 512:
        raise ReplayError("object count budget exceeded")
    objects = {}
    for raw in graph["objects"]:
        _keys(raw, ("id", "op", "ports", "attributes"))
        identity, op = _identity(raw["id"]), raw["op"]
        if identity in objects:
            raise ReplayError("duplicate object identity")
        if type(op) is not str or op not in RULES:
            raise ReplayError("unknown operation")
        family, role, port_names = RULES[op]
        _keys(raw["ports"], port_names)
        for ref in raw["ports"].values():
            _identity(ref)
        attributes = raw["attributes"]
        if role == "literal":
            _keys(attributes, ("value",))
            expected = int if family == "ExactInt" else str
            if type(attributes["value"]) is not expected:
                raise ReplayError("literal value disagrees with nominal family")
        elif role == "description":
            _keys(attributes, ("purpose",))
            if type(attributes["purpose"]) is not str:
                raise ReplayError("invalid document purpose")
        else:
            _keys(attributes, ())
        objects[identity] = raw
    _unique_names(graph["outputs"])
    if set(graph["outputs"]) - objects.keys():
        raise ReplayError("unknown output")
    for raw in objects.values():
        family, _, _ = RULES[raw["op"]]
        for ref in raw["ports"].values():
            if ref not in objects:
                raise ReplayError("unknown dependency")
            required = "Text" if family == "Document" else family
            if RULES[objects[ref]["op"]][0] != required:
                raise ReplayError("incompatible nominal port families")
    # Preserve source order within topological layers so published term IDs
    # can also be checked; structural interning is the equality oracle.
    order, depths, pending = [], {}, dict(objects)
    while pending:
        ready = [
            identity
            for identity, raw in pending.items()
            if set(raw["ports"].values()) <= depths.keys()
        ]
        if not ready:
            raise ReplayError("cyclic object composition")
        for identity in ready:
            depths[identity] = 1 + max(
                (depths[ref] for ref in pending[identity]["ports"].values()), default=0
            )
            if depths[identity] > 64:
                raise ReplayError("composition depth budget exceeded")
            order.append(identity)
            del pending[identity]
    terms, index, normal = [], {}, {}

    def intern(term):
        if term not in index:
            if len(terms) >= 512:
                raise ReplayError("normalized term budget exceeded")
            index[term] = len(terms)
            terms.append(term)
        return index[term]

    for identity in order:
        raw = objects[identity]
        op = raw["op"]
        family, role, _ = RULES[op]
        ports = tuple(
            (port, (normal[ref],)) for port, ref in sorted(raw["ports"].items())
        )
        if role == "alias":
            normal[identity] = ports[0][1][0]
            continue
        if role in ("square", "double"):
            operand = ports[0][1][0]
            op = "exact.multiply" if role == "square" else "exact.add"
            ports = (("left", (operand,)), ("right", (operand,)))
        normal[identity] = intern(
            (
                op,
                family,
                identity if role in ("input", "description") else None,
                ports,
                _encode(raw["attributes"]),
            )
        )
    _keys(
        receipt,
        (
            "version",
            "context",
            "vocabulary",
            "left",
            "right",
            "status",
            "basis",
            "normal_forms",
        ),
    )
    for side in ("left", "right"):
        if type(receipt[side]) is not str or receipt[side] not in normal:
            raise ReplayError("unknown comparison reference")
    left, right = receipt["left"], receipt["right"]
    if normal[left] != normal[right]:
        raise ReplayError("structural equivalence was not established")

    def projection(identity):
        reachable, stack = set(), [normal[identity]]
        while stack:
            item = stack.pop()
            if item not in reachable:
                reachable.add(item)
                stack.extend(ref for _, refs in terms[item][3] for ref in refs)
        return {
            "root": normal[identity],
            "terms": [
                {
                    "id": i,
                    "op": term[0],
                    "type": term[1],
                    "identity": term[2],
                    "ports": {port: list(refs) for port, refs in term[3]},
                    "attributes": json.loads(term[4]),
                }
                for i, term in enumerate(terms)
                if i in reachable
            ],
        }

    context = _digest({"graph": graph, "envelope": "nomi.object-graph-1"})
    expected = {
        "version": 1,
        "context": context,
        "vocabulary": VOCABULARY,
        "left": left,
        "right": right,
        "status": "equivalent",
        "basis": "structural identity after declared pure definitions and aliases",
        "normal_forms": [projection(left), projection(right)],
    }
    if _encode(receipt) != _encode(expected):
        raise ReplayError(
            "comparison receipt disagrees with independently reconstructed evidence"
        )
    return {
        "status": "verified",
        "context": context,
        "vocabulary": VOCABULARY,
        "independent_checker": True,
        "scope": "pinned object lab vocabulary; no engine conformance claim",
    }


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ReplayError("duplicate JSON key")
        result[key] = value
    return result


def load(path):
    with Path(path).open("rb") as stream:
        data = stream.read(LIMIT + 1)
    if len(data) > LIMIT:
        raise ReplayError("artifact byte budget exceeded")
    try:
        result = json.loads(data, object_pairs_hook=_pairs)
        _artifact(result)
        return result
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise ReplayError("invalid JSON artifact") from exc


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("vocabulary")
    parser.add_argument("graph")
    parser.add_argument("receipt")
    args = parser.parse_args(argv)
    try:
        print(
            json.dumps(
                replay(load(args.vocabulary), load(args.graph), load(args.receipt)),
                indent=2,
            )
        )
        return 0
    except (ReplayError, OSError) as exc:
        print(json.dumps({"status": "refused", "message": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
