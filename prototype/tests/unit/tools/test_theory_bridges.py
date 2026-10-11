"""Independent finite-model checks, not an assertion that theories are equivalent."""

from dataclasses import replace
from itertools import product
import random

import pytest

from tools import premise_ledger as ledger
from tools import theory_bridges as t
from tools.scoped_terms import Identity


def keys(owner, count=2):
    return tuple(Identity(owner, "1", str(i)) for i in range(count))


def theory(owner, atoms, axioms=()):
    return t.Theory(Identity(owner, "1", "theory"), atoms, axioms)


def truth_set(formula, signature):
    """Set algebra oracle: each formula denotes a subset of all worlds."""
    universe = set(product((False, True), repeat=len(signature)))
    if type(formula) is t.Constant:
        return universe if formula.value else set()
    if type(formula) is t.Atom:
        position = signature.index(formula.identity)
        return {world for world in universe if world[position]}
    if type(formula) is t.Not:
        return universe - truth_set(formula.value, signature)
    denotations = [truth_set(x, signature) for x in formula.values]
    if type(formula) is t.All:
        result = universe
        for value in denotations:
            result &= value
        return result
    return set().union(*denotations)


def model_set(description):
    return truth_set(t.All(description.axioms), description.signature)


def test_examples_separate_preservation_bijection_and_countermodel():
    examples = t.examples()
    assert t.check(examples["sound"]).status == "validated"
    assert t.check(examples["not-bijective"]).status == "refuted"
    bad = t.check(examples["bad-translation"])
    assert bad.status == "refuted"
    assert bad.witness == ((True, True), (True, False))


def test_renaming_is_bijective_only_under_explicit_interpretation():
    a, b = keys("old")
    x, y = keys("new")
    source = theory("old", (a, b), (t.implies(t.Atom(a), t.Atom(b)),))
    destination = theory("new", (x, y), (t.implies(t.Atom(y), t.Atom(x)),))
    bridge = t.Bridge(
        source, destination, ((a, t.Atom(y)), (b, t.Atom(x))), "model-bijection"
    )
    result = t.check(bridge)
    assert result.status == "validated"
    assert result.source_models == result.destination_models == 3


def test_composite_interpretation_detects_many_to_one_information_loss():
    (a,) = keys("source", 1)
    x, y = keys("destination")
    xor = t.Any(
        (t.All((t.Atom(x), t.Not(t.Atom(y)))), t.All((t.Not(t.Atom(x)), t.Atom(y))))
    )
    bridge = t.Bridge(
        theory("source", (a,)), theory("destination", (x, y)), ((a, xor),)
    )
    assert t.check(bridge).status == "validated"
    bijection = t.check(replace(bridge, claim="model-bijection"))
    assert bijection.status == "refuted"
    assert len(bijection.witness) == 2


@pytest.mark.parametrize("side", ["source", "destination"])
def test_inconsistent_theories_do_not_validate_vacuously(side):
    (a,) = keys("s", 1)
    (x,) = keys("d", 1)
    source = theory("s", (a,), (t.Constant(False),) if side == "source" else ())
    destination = theory(
        "d", (x,), (t.Constant(False),) if side == "destination" else ()
    )
    bridge = t.Bridge(source, destination, ((a, t.Atom(x)),))
    assert t.check(bridge).status == f"inconsistent-{side}"


def test_incomplete_enumeration_cannot_validate_universal_claim():
    bridge = t.examples()["sound"]
    result = t.check(bridge, budget=1)
    assert result.status == "search-incomplete"
    assert result.coverage == "incomplete"
    assert t.verify(bridge, result)
    with pytest.raises(t.Refused, match="replay"):
        t.verify(bridge, replace(result, status="validated"))


def test_assessment_is_bound_to_exact_context_and_constructor():
    bridge = t.examples()["sound"]
    result = t.check(bridge)
    assert t.verify(bridge, result)
    revised = replace(
        bridge,
        destination=replace(
            bridge.destination, identity=Identity("example", "3", "stronger")
        ),
    )
    with pytest.raises(t.Refused, match="stale"):
        t.verify(revised, result)
    all_theory = replace(bridge.source, axioms=(t.All(()),))
    any_theory = replace(bridge.source, axioms=(t.Any(()),))
    assert t.fingerprint(replace(bridge, source=all_theory)) != t.fingerprint(
        replace(bridge, source=any_theory)
    )


def test_seeded_theories_match_independent_set_semantics():
    rng = random.Random(53)
    source_atoms, destination_atoms = keys("s"), keys("d")

    def formula(atoms, depth=0):
        if depth == 2 or rng.random() < 0.4:
            return t.Atom(rng.choice(atoms))
        operation = rng.choice((t.All, t.Any, t.Not))
        if operation is t.Not:
            return operation(formula(atoms, depth + 1))
        return operation(
            tuple(formula(atoms, depth + 1) for _ in range(rng.randrange(3)))
        )

    for _ in range(48):
        source = theory("s", source_atoms, (formula(source_atoms),))
        destination = theory("d", destination_atoms, (formula(destination_atoms),))
        meanings = tuple((key, formula(destination_atoms)) for key in source_atoms)
        bridge = t.Bridge(
            source, destination, meanings, rng.choice(("sound", "model-bijection"))
        )
        source_models, destination_models = model_set(source), model_set(destination)
        images = [
            tuple(world in truth_set(value, destination_atoms) for _, value in meanings)
            for world in destination_models
        ]
        if not source_models or not destination_models:
            expected = (
                "inconsistent-source"
                if not source_models
                else "inconsistent-destination"
            )
        else:
            valid = set(images) <= source_models
            if bridge.claim == "model-bijection":
                valid &= set(images) == source_models and len(set(images)) == len(
                    images
                )
            expected = "validated" if valid else "refuted"
        assert t.check(bridge).status == expected


def test_ledger_export_requires_deliberate_consistent_classical_reinterpretation():
    (a,) = keys("reports", 1)
    positive = ledger.Report(
        Identity("reports", "1", "positive"), ledger.SignedAtom(a), a
    )
    negative = ledger.Report(
        Identity("reports", "1", "negative"), ledger.SignedAtom(a, False), a
    )
    context = ledger.Ledger("context", 0, (a,), reports=(positive, negative))
    exported = t.from_ledger(context)
    assert model_set(exported) == {(False,), (True,)}  # Quotes remain inert.
    conflict = ledger.revise(context, endorsed=(positive.identity, negative.identity))
    assert (
        ledger.assess(conflict, ledger.derive(conflict), positive.claim)["status"]
        == "conflict"
    )
    with pytest.raises(t.Refused, match="inconsistent"):
        t.from_ledger(conflict)


def test_malformed_unknown_and_capacity_exceeding_inputs_refuse():
    (a,) = keys("s", 1)
    with pytest.raises(t.Refused):
        theory("s", (a,), (t.Atom(Identity("s", "stale", "0")),))
    with pytest.raises(t.Refused):
        theory("large", keys("large", 9))
    with pytest.raises(t.Refused):
        theory("s", (a,), (t.Constant(1),))
    with pytest.raises(t.Refused):
        t.Bridge(theory("s", (a,)), theory("d", ()), ())
    with pytest.raises(t.Refused):
        t.check(t.examples()["sound"], budget=True)


def test_optional_established_adapter_replays_all_examples_when_installed():
    sympy = pytest.importorskip("sympy", reason="explicit reasoning-check extra")
    assert sympy.__version__ == "1.14.0"
    for bridge in t.examples().values():
        assert t.verify(bridge, t.check(bridge), adapter="sympy-1.14.0")
