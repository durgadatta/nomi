"""Bounded classical theory translations with separate model semantics.

Model bijection is a finite claim, not general equivalence of logics or theories.
This profile deliberately differs from the non-explosive premise ledger.
"""

from dataclasses import asdict, dataclass
import hashlib
from itertools import product
import json

from tools.scoped_terms import Identity

PROFILE = "finite-classical-theory-bridges-v1"
MAX_ATOMS = 8
MAX_WORLDS = 512


class Refused(ValueError):
    """Malformed description or unsupported semantic profile."""


@dataclass(frozen=True)
class Atom:
    identity: Identity


@dataclass(frozen=True)
class Constant:
    value: bool


@dataclass(frozen=True)
class Not:
    value: object


@dataclass(frozen=True)
class All:
    values: tuple


@dataclass(frozen=True)
class Any:
    values: tuple


def _validate(formula, signature, depth=0, count=None):
    count = [0] if count is None else count
    count[0] += 1
    if depth > 16 or count[0] > 128:
        raise Refused("formula exceeds finite profile capacity")
    if type(formula) is Atom:
        if type(formula.identity) is not Identity or formula.identity not in signature:
            raise Refused("atom outside exact signature/revision")
    elif type(formula) is Constant:
        if type(formula.value) is not bool:
            raise Refused("constant requires Boolean")
    elif type(formula) is Not:
        _validate(formula.value, signature, depth + 1, count)
    elif type(formula) in (All, Any):
        if type(formula.values) is not tuple or len(formula.values) > 16:
            raise Refused("connective requires bounded immutable arguments")
        for value in formula.values:
            _validate(value, signature, depth + 1, count)
    else:
        raise Refused("unknown formula constructor")


def implies(left, right):
    return Any((Not(left), right))


@dataclass(frozen=True)
class Theory:
    identity: Identity
    signature: tuple[Identity, ...]
    axioms: tuple = ()

    def __post_init__(self):
        if type(self.identity) is not Identity:
            raise Refused("theory requires qualified identity")
        if (
            type(self.signature) is not tuple
            or len(self.signature) > MAX_ATOMS
            or any(type(x) is not Identity for x in self.signature)
            or len(set(self.signature)) != len(self.signature)
        ):
            raise Refused("invalid finite signature")
        if type(self.axioms) is not tuple or len(self.axioms) > 32:
            raise Refused("invalid finite axioms")
        for axiom in self.axioms:
            _validate(axiom, self.signature)


@dataclass(frozen=True)
class Bridge:
    source: Theory
    destination: Theory
    interpretation: tuple[tuple[Identity, object], ...]
    claim: str = "sound"

    def __post_init__(self):
        if type(self.source) is not Theory or type(self.destination) is not Theory:
            raise Refused("bridge requires captured theories")
        if self.claim not in ("sound", "model-bijection"):
            raise Refused("unsupported bridge claim")
        if type(self.interpretation) is not tuple:
            raise Refused("interpretation requires immutable entries")
        if len(self.interpretation) != len(self.source.signature):
            raise Refused("interpretation must cover entire source signature")
        keys = []
        for entry in self.interpretation:
            if type(entry) is not tuple or len(entry) != 2:
                raise Refused("malformed interpretation entry")
            key, formula = entry
            if type(key) is not Identity:
                raise Refused("invalid interpreted identity")
            keys.append(key)
            _validate(formula, self.destination.signature)
        if set(keys) != set(self.source.signature) or len(set(keys)) != len(keys):
            raise Refused("interpretation must name exact distinct source owners")


def fingerprint(bridge):
    if type(bridge) is not Bridge:
        raise Refused("expected bridge")

    # Include constructor tags: dataclass fields alone cannot distinguish All/Any.
    def encode(value):
        if type(value) is tuple:
            return [encode(x) for x in value]
        if hasattr(value, "__dataclass_fields__"):
            return {
                "kind": type(value).__name__,
                **{k: encode(getattr(value, k)) for k in value.__dataclass_fields__},
            }
        return value

    record = {"profile": PROFILE, "bridge": encode(bridge)}
    return hashlib.sha256(json.dumps(record, sort_keys=True).encode()).hexdigest()


def _evaluate(formula, world):
    if type(formula) is Atom:
        return world[formula.identity]
    if type(formula) is Constant:
        return formula.value
    if type(formula) is Not:
        return not _evaluate(formula.value, world)
    values = (_evaluate(x, world) for x in formula.values)
    return all(values) if type(formula) is All else any(values)


def _sympy_evaluator(signature):
    try:
        import sympy
    except ImportError as error:
        raise Refused(
            "install the reasoning-check extra for the independent adapter"
        ) from error
    if sympy.__version__ != "1.14.0":
        raise Refused("independent adapter requires SymPy 1.14.0")
    symbols = {key: sympy.Symbol(f"atom_{i}") for i, key in enumerate(signature)}

    def translate(formula):
        if type(formula) is Atom:
            return symbols[formula.identity]
        if type(formula) is Constant:
            return sympy.true if formula.value else sympy.false
        if type(formula) is Not:
            return sympy.Not(translate(formula.value))
        operation = sympy.And if type(formula) is All else sympy.Or
        return operation(*(translate(x) for x in formula.values))

    def evaluate(formula, world):
        # Total symbol-to-Boolean replacement; arithmetic dummy substitution in
        # SymPy's simultaneous subs is not valid inside Boolean connectives.
        value = translate(formula).xreplace(
            {
                symbols[key]: sympy.true if value else sympy.false
                for key, value in world.items()
            }
        )
        if value not in (sympy.true, sympy.false):
            raise Refused("independent adapter left an unresolved Boolean")
        return value == sympy.true

    return evaluate


@dataclass(frozen=True)
class Assessment:
    context: str
    status: str
    coverage: str
    checked_worlds: int
    source_models: int
    destination_models: int
    witness: tuple[tuple[bool, ...], ...] = ()
    adapter: str = "truth-table"


def check(bridge, *, budget=MAX_WORLDS, adapter="truth-table"):
    if type(bridge) is not Bridge:
        raise Refused("expected captured bridge")
    if type(budget) is not int or not 1 <= budget <= MAX_WORLDS:
        raise Refused("invalid valuation budget")
    if adapter not in ("truth-table", "sympy-1.14.0"):
        raise Refused("unsupported checker adapter")
    source, destination = bridge.source, bridge.destination
    evaluate = (
        _evaluate
        if adapter == "truth-table"
        else _sympy_evaluator(
            tuple(dict.fromkeys((*source.signature, *destination.signature)))
        )
    )
    visited = 0
    model_sets = []
    complete = True
    for theory in (source, destination):
        models = []
        for bits in product((False, True), repeat=len(theory.signature)):
            if visited == budget:
                complete = False
                break
            visited += 1
            world = dict(zip(theory.signature, bits, strict=True))
            if all(evaluate(axiom, world) for axiom in theory.axioms):
                models.append(bits)
        model_sets.append(models)
    source_models, destination_models = model_sets
    result = dict(
        context=fingerprint(bridge),
        coverage="complete" if complete else "incomplete",
        checked_worlds=visited,
        source_models=len(source_models),
        destination_models=len(destination_models),
        adapter=adapter,
    )
    if complete and (not source_models or not destination_models):
        side = "source" if not source_models else "destination"
        return Assessment(status=f"inconsistent-{side}", **result)
    reduced = {}
    meanings = dict(bridge.interpretation)
    for bits in destination_models:
        world = dict(zip(destination.signature, bits, strict=True))
        image = tuple(evaluate(meanings[key], world) for key in source.signature)
        source_world = dict(zip(source.signature, image, strict=True))
        if not all(evaluate(axiom, source_world) for axiom in source.axioms):
            return Assessment(status="refuted", witness=(bits, image), **result)
        reduced.setdefault(image, []).append(bits)
    if not complete:
        return Assessment(status="search-incomplete", **result)
    if bridge.claim == "model-bijection":
        for image, preimages in reduced.items():
            if len(preimages) > 1:
                return Assessment(
                    status="refuted", witness=tuple(preimages[:2]), **result
                )
        missing = sorted(set(source_models) - set(reduced))
        if missing:
            return Assessment(status="refuted", witness=(missing[0],), **result)
    return Assessment(status="validated", **result)


def verify(bridge, assessment, *, adapter="truth-table"):
    """Replay a complete or bounded assessment against this exact context."""
    if type(assessment) is not Assessment or assessment.context != fingerprint(bridge):
        raise Refused("stale or malformed bridge assessment")
    if (
        type(assessment.checked_worlds) is not int
        or not 1 <= assessment.checked_worlds <= MAX_WORLDS
    ):
        raise Refused("invalid replay coverage")
    replay = check(bridge, budget=assessment.checked_worlds, adapter=adapter)
    fields = (
        "context",
        "status",
        "coverage",
        "checked_worlds",
        "source_models",
        "destination_models",
        "witness",
    )
    if any(getattr(replay, key) != getattr(assessment, key) for key in fields):
        raise Refused("assessment differs from independent semantic replay")
    return True


def from_ledger(ledger):
    """Explicit reinterpretation; no support certificate crosses this boundary."""
    from tools.premise_ledger import Ledger, fingerprint as ledger_fingerprint

    if type(ledger) is not Ledger or len(ledger.atoms) > MAX_ATOMS:
        raise Refused("ledger outside classical export capacity")

    def literal(value):
        atom = Atom(value.atom)
        return atom if value.positive else Not(atom)

    axioms = tuple(
        literal(x.claim) for x in ledger.reports if x.identity in ledger.endorsed
    )
    axioms += tuple(
        implies(All(tuple(literal(x) for x in rule.premises)), literal(rule.conclusion))
        for rule in ledger.rules
    )
    theory = Theory(
        Identity(ledger.owner, ledger_fingerprint(ledger), "classical-export"),
        ledger.atoms,
        axioms,
    )
    identity = Bridge(theory, theory, tuple((x, Atom(x)) for x in theory.signature))
    if check(identity).status != "validated":
        raise Refused(
            "classical export is inconsistent; signed support remains available"
        )
    return theory


def examples():
    a, b = (Identity("source", "1", name) for name in ("a", "b"))
    x, y = (Identity("destination", "2", name) for name in ("x", "y"))
    source = Theory(
        Identity("example", "1", "implication"), (a, b), (implies(Atom(a), Atom(b)),)
    )
    destination = Theory(
        Identity("example", "2", "stronger"), (x, y), (Atom(x), Atom(y))
    )
    interpretation = ((a, Atom(x)), (b, Atom(y)))
    return {
        "sound": Bridge(source, destination, interpretation),
        "not-bijective": Bridge(source, destination, interpretation, "model-bijection"),
        "bad-translation": Bridge(
            source, destination, ((a, Atom(x)), (b, Not(Atom(y))))
        ),
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sympy", action="store_true")
    args = parser.parse_args()
    adapter = "sympy-1.14.0" if args.sympy else "truth-table"
    records = {}
    for name, bridge in examples().items():
        assessment = check(bridge)
        verify(bridge, assessment, adapter=adapter)
        records[name] = {**asdict(assessment), "replay_adapter": adapter}
    print(json.dumps({"profile": PROFILE, "examples": records}, indent=2))


if __name__ == "__main__":
    main()
