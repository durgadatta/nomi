"""Bounded formal polynomial reasoning, not analytic calculus or a physics engine."""

import argparse
from fractions import Fraction
import json

from tools.object_interface.documents import (
    ContractError,
    Frozen,
    digest,
    keys,
    load_document,
    name,
    ordered,
    snapshot,
)

PROFILE = "formal-rational-polynomial-v1"
MAX_TERMS = 256
MAX_DEGREE = 32
MAX_BITS = 4096
OPERATIONS = {
    "symbol": ("id", "op", "label", "dimension"),
    "rational": ("id", "op", "numerator", "denominator", "dimension"),
    "add": ("id", "op", "args"),
    "multiply": ("id", "op", "args"),
    "differentiate": ("id", "op", "arg"),
}


def dimension(raw):
    if type(raw) is not dict or len(raw) > 16:
        raise ContractError("expected at most 16 named dimension exponents")
    for key, exponent in raw.items():
        name(key, "dimension")
        if type(exponent) is not int or not -128 <= exponent <= 128 or not exponent:
            raise ContractError("dimension exponents must be nonzero bounded integers")
    return dict(sorted(raw.items()))


def combine_dimension(left, right, sign=1):
    result = dict(left)
    for key, value in right.items():
        result[key] = result.get(key, 0) + sign * value
    return dimension({key: value for key, value in result.items() if value})


class Algebra:
    """Sparse exponent vectors over named formal generators."""

    def __init__(self, symbols):
        self.symbols = tuple(sorted(symbols))
        self.unit = (0,) * len(symbols)

    def checked(self, polynomial):
        result = {
            power: coefficient
            for power, coefficient in polynomial.items()
            if coefficient
        }
        if len(result) > MAX_TERMS:
            raise ContractError("formal polynomial exceeds monomial budget")
        for power, coefficient in result.items():
            if sum(power) > MAX_DEGREE:
                raise ContractError("formal polynomial exceeds degree budget")
            if (
                max(
                    abs(coefficient.numerator).bit_length(),
                    coefficient.denominator.bit_length(),
                )
                > MAX_BITS
            ):
                raise ContractError("formal coefficient exceeds exact capacity")
        return result

    def add(self, left, right, scale=Fraction(1)):
        result = dict(left)
        for power, coefficient in right.items():
            result[power] = result.get(power, Fraction(0)) + scale * coefficient
        return self.checked(result)

    def multiply(self, left, right):
        result = {}
        for p, a in left.items():
            for q, b in right.items():
                power = tuple(x + y for x, y in zip(p, q))
                result[power] = result.get(power, Fraction(0)) + a * b
        return self.checked(result)

    def derivative(self, source, images):
        result = {}
        for power, coefficient in source.items():
            for index, exponent in enumerate(power):
                if not exponent:
                    continue
                symbol = self.symbols[index]
                if symbol not in images:
                    raise ContractError(f"missing formal derivative image for {symbol}")
                reduced = list(power)
                reduced[index] -= 1
                term = self.multiply(
                    {tuple(reduced): coefficient * exponent}, images[symbol]
                )
                result = self.add(result, term)
        return result

    def export(self, polynomial):
        return [
            {
                "coefficient": [coefficient.numerator, coefficient.denominator],
                "powers": {
                    symbol: power[i]
                    for i, symbol in enumerate(self.symbols)
                    if power[i]
                },
            }
            for power, coefficient in sorted(polynomial.items())
        ]


class Model(Frozen):
    """Immutable source snapshot; all results are detached, bounded artifacts."""

    __slots__ = ("_source",)

    def __init__(self, document):
        self._source = snapshot(document)
        self.check()
        self._sealed = True

    @property
    def document(self):
        return json.loads(self._source)

    def explain_claim(self, identity):
        """Expose the supplied basis; this is not a complete premise-use analysis."""
        name(identity)
        source = self.document
        authored = next(
            (row for row in source["claims"] if row["id"] == identity), None
        )
        if authored is None:
            raise ContractError("unknown claim identity")
        receipt = self.check()
        checked = next(row for row in receipt["claims"] if row["id"] == identity)
        messages = {
            "conditional-identity": "The supplied formal witness establishes this equality under the declared relations.",
            "unknown": "The supplied witness leaves a nonzero residual; another witness may work.",
            "inconsistent-premises": "A directly contradictory relation blocks this claim.",
        }
        return json.loads(
            snapshot(
                {
                    "claim": identity,
                    "context": receipt["context"],
                    "status": checked["status"],
                    "explanation": messages[checked["status"]],
                    "statement": {"left": authored["left"], "right": authored["right"]},
                    "declared_derivation": source["derivation"],
                    "supplied_witness": checked["witness"],
                    "residual": checked["residual"],
                    "declared_relations": source["relations"],
                    "premise_usage": "full context pinned; minimal/comprehensive used-premise analysis not established",
                    "scope": receipt["scope"],
                }
            )
        )

    def check(self):
        document = self.document
        keys(
            document,
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
            type(document["version"]) is not int
            or document["version"] != 1
            or document["profile"] != PROFILE
        ):
            raise ContractError("unsupported scientific fragment/profile")
        name(document["id"])
        name(document["revision"])
        derivation = document["derivation"]
        keys(derivation, ("id", "dimension", "images"), "derivation")
        name(derivation["id"])
        step_dimension = dimension(derivation["dimension"])
        if not step_dimension:
            raise ContractError("derivation requires a nonempty variable dimension")
        if type(derivation["images"]) is not dict:
            raise ContractError("expected named formal generator images")
        rows = document["objects"]
        if type(rows) is not list or not 1 <= len(rows) <= 128:
            raise ContractError("expected 1..128 named expressions")
        objects, dependencies = {}, {}
        for row in rows:
            if (
                type(row) is not dict
                or type(row.get("op")) is not str
                or row["op"] not in OPERATIONS
            ):
                raise ContractError("unsupported formal expression operation")
            keys(row, OPERATIONS[row["op"]], "expression")
            identity = name(row["id"])
            if identity in objects:
                raise ContractError("duplicate expression identity")
            objects[identity] = row
            if row["op"] in ("add", "multiply"):
                refs = row["args"]
                if type(refs) is not list or not 2 <= len(refs) <= 16:
                    raise ContractError("expected 2..16 ordered operands")
            elif row["op"] == "differentiate":
                refs = [row["arg"]]
            else:
                refs = []
            dependencies[identity] = tuple(name(ref) for ref in refs)
        symbols = [key for key, row in objects.items() if row["op"] == "symbol"]
        if not 1 <= len(symbols) <= 16:
            raise ContractError("expected 1..16 formal generators")
        algebra = Algebra(symbols)
        order = ordered(dependencies)
        polynomials, dimensions, derived = {}, {}, {}
        images = derivation["images"]
        for symbol, image in images.items():
            if symbol not in symbols:
                raise ContractError("derivation image key is not a declared generator")
            if image is not None:
                name(image)
                if image not in objects:
                    raise ContractError("unknown derivative image expression")

        # Images must be ordinary polynomials; they never recursively evaluate D.
        def build(identity):
            row = objects[identity]
            for ref in dependencies[identity]:
                evaluate(ref)
            op = row["op"]
            derived[identity] = op == "differentiate" or any(
                derived[ref] for ref in dependencies[identity]
            )
            if op == "symbol":
                if type(row["label"]) is not str or not 1 <= len(row["label"]) <= 128:
                    raise ContractError("expected bounded generator display label")
                power = list(algebra.unit)
                power[algebra.symbols.index(identity)] = 1
                polynomial = {tuple(power): Fraction(1)}
                actual_dimension = dimension(row["dimension"])
            elif op == "rational":
                n, d = row["numerator"], row["denominator"]
                if type(n) is not int or type(d) is not int or d <= 0:
                    raise ContractError(
                        "expected exact rational with positive denominator"
                    )
                if max(abs(n).bit_length(), d.bit_length()) > MAX_BITS:
                    raise ContractError("rational source exceeds exact capacity")
                polynomial = algebra.checked({algebra.unit: Fraction(n, d)})
                actual_dimension = dimension(row["dimension"])
            elif op == "add":
                actual_dimension = dimensions[row["args"][0]]
                polynomial = {}
                for ref in row["args"]:
                    if dimensions[ref] != actual_dimension:
                        raise ContractError(
                            f"{identity}: cannot add incompatible dimensions"
                        )
                    polynomial = algebra.add(polynomial, polynomials[ref])
            elif op == "multiply":
                actual_dimension, polynomial = {}, {algebra.unit: Fraction(1)}
                for ref in row["args"]:
                    actual_dimension = combine_dimension(
                        actual_dimension, dimensions[ref]
                    )
                    polynomial = algebra.multiply(polynomial, polynomials[ref])
            else:
                actual_dimension = combine_dimension(
                    dimensions[row["arg"]], step_dimension, -1
                )
                admitted_images = {}
                for symbol, image in images.items():
                    if image is None:
                        admitted_images[symbol] = {}
                    else:
                        if image == identity or image in evaluating:
                            raise ContractError(
                                "formal derivative image depends on differentiation"
                            )
                        evaluate(image)
                        if derived[image]:
                            raise ContractError(
                                "formal derivative images must be ordinary polynomials"
                            )
                        admitted_images[symbol] = polynomials[image]
                polynomial = algebra.derivative(
                    polynomials[row["arg"]], admitted_images
                )
            polynomials[identity] = polynomial
            dimensions[identity] = actual_dimension
            return polynomial

        # Additional image dependencies can otherwise recurse outside the DAG.
        evaluating = set()

        def evaluate(identity):
            if identity in polynomials:
                return polynomials[identity]
            if identity in evaluating:
                raise ContractError(
                    "formal derivative image depends on differentiation"
                )
            evaluating.add(identity)
            try:
                return build(identity)
            finally:
                evaluating.remove(identity)

        for identity in order:
            evaluate(identity)
        for symbol, image in images.items():
            if image is not None:
                expected = combine_dimension(dimensions[symbol], step_dimension, -1)
                if derived[image] or dimensions[image] != expected:
                    raise ContractError(
                        f"{symbol}: incompatible formal derivative image"
                    )

        def difference_of(row):
            left, right = row["left"], row["right"]
            if (
                type(left) is not str
                or type(right) is not str
                or left not in objects
                or right not in objects
            ):
                raise ContractError("unknown statement expression")
            if dimensions[left] != dimensions[right]:
                raise ContractError(f"{row['id']}: incompatible statement dimensions")
            return dimensions[left], algebra.add(
                polynomials[left], polynomials[right], Fraction(-1)
            )

        relations = {}
        for row in self._records(document["relations"], "relation"):
            keys(row, ("id", "left", "right"), "relation")
            if row["id"] in relations or row["id"] in objects:
                raise ContractError("duplicate relation identity")
            dim, difference = difference_of(row)
            relations[row["id"]] = (dim, difference)
        contradictions = [
            identity
            for identity, (_, poly) in relations.items()
            if poly and set(poly) == {algebra.unit}
        ]

        claims, claim_ids = [], set()
        for row in self._records(document["claims"], "claim"):
            keys(row, ("id", "left", "right", "witness"), "claim")
            if row["id"] in objects or row["id"] in relations or row["id"] in claim_ids:
                raise ContractError("duplicate claim identity")
            claim_ids.add(row["id"])
            dim, residual = difference_of(row)
            if type(row["witness"]) is not list or len(row["witness"]) > 128:
                raise ContractError("expected bounded relation-multiplier witness")
            for term in row["witness"]:
                keys(term, ("relation", "multiplier"), "witness term")
                relation, multiplier = term["relation"], term["multiplier"]
                if (
                    type(relation) is not str
                    or type(multiplier) is not str
                    or relation not in relations
                    or multiplier not in objects
                ):
                    raise ContractError("unknown witness reference")
                relation_dim, relation_poly = relations[relation]
                if combine_dimension(relation_dim, dimensions[multiplier]) != dim:
                    raise ContractError("witness product has incompatible dimension")
                residual = algebra.add(
                    residual,
                    algebra.multiply(relation_poly, polynomials[multiplier]),
                    Fraction(-1),
                )
            claims.append(
                {
                    "id": row["id"],
                    "status": "inconsistent-premises"
                    if contradictions
                    else "conditional-identity"
                    if not residual
                    else "unknown",
                    "witness": row["witness"],
                    "residual": algebra.export(residual),
                }
            )
        receipt = {
            "version": 1,
            "profile": PROFILE,
            "context": digest(
                {"domain": "nomi.formal-polynomial-1", "artifact": document}
            ),
            "objects": [
                {
                    "id": identity,
                    "dimension": dimensions[identity],
                    "normal": algebra.export(polynomials[identity]),
                }
                for identity in objects
            ],
            "relations": [
                {"id": identity, "dimension": dim, "normal": algebra.export(poly)}
                for identity, (dim, poly) in relations.items()
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
        return json.loads(snapshot(receipt))

    @staticmethod
    def _records(raw, kind):
        if type(raw) is not list or len(raw) > 128:
            raise ContractError(f"expected at most 128 {kind} records")
        for row in raw:
            if type(row) is not dict:
                raise ContractError(f"expected {kind} record")
            name(row.get("id"), kind)
        return raw


def envelope_graph(document):
    """Compare structural envelopes only; this deliberately performs no math check.

    The source context and authored operations survive as inert metadata. This
    graph cannot establish dimensions, derivation laws, or relation entailment.
    """
    from tools.object_interface.model import Graph, Vocabulary

    source = json.loads(snapshot(document))
    context = digest({"domain": "nomi.formal-polynomial-1", "artifact": source})
    vocabulary = Vocabulary.from_document(
        {
            "version": 1,
            "id": "nomi.scientific-envelope-comparison",
            "revision": "v1",
            "types": {"MathDescription": {"value": None}},
            "operations": {
                "math.describe": {
                    "role": "description",
                    "ports": {
                        "dependencies": {
                            "accepts": ["MathDescription"],
                            "multiplicity": "many",
                        }
                    },
                    "attributes": {
                        "authored": {"kind": "json"},
                        "scientific_context": {"kind": "text"},
                    },
                    "result": "MathDescription",
                    "effects": [],
                    "definition": None,
                }
            },
        }
    )
    objects = []
    for row in source["objects"]:
        refs = (
            row["args"]
            if row["op"] in ("add", "multiply")
            else [row["arg"]]
            if row["op"] == "differentiate"
            else []
        )
        objects.append(
            {
                "id": row["id"],
                "op": "math.describe",
                "ports": {"dependencies": refs},
                "attributes": {"authored": row, "scientific_context": context},
            }
        )
    return Graph.from_document(
        {
            "version": 1,
            "vocabulary": vocabulary.fingerprint,
            "objects": objects,
            "outputs": [objects[-1]["id"]],
        },
        vocabulary,
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model")
    parser.add_argument(
        "--claim", help="explain one named claim and its supplied basis"
    )
    args = parser.parse_args(argv)
    try:
        model = Model(load_document(args.model))
        receipt = model.check()
        output = model.explain_claim(args.claim) if args.claim else receipt
    except (ContractError, OSError, ValueError, RecursionError) as error:
        print(json.dumps({"status": "refused", "message": str(error)}))
        return 2
    print(json.dumps(output, indent=2))
    statuses = (
        [output["status"]]
        if args.claim
        else [claim["status"] for claim in receipt["claims"]]
    )
    return 1 if any(status != "conditional-identity" for status in statuses) else 0


if __name__ == "__main__":
    raise SystemExit(main())
