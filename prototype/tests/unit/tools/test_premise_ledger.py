"""Finite-model oracle and independent premise-support/revision checks."""

from dataclasses import replace
from itertools import product
import random

import pytest

from tools.premise_ledger import (
    Ledger,
    Refused,
    Report,
    Rule,
    SignedAtom,
    Support,
    assess,
    derive,
    example,
    fingerprint,
    revise,
    verify,
)
from tools.scoped_terms import Identity


def identity(slot, owner="test"):
    return Identity(owner, "1", slot)


def setup():
    a, b, c = [SignedAtom(identity(x)) for x in "abc"]
    reports = tuple(
        Report(identity(str(i), "report"), a, identity(str(i), "source"))
        for i in range(2)
    )
    rule = Rule(identity("a-b", "rule"), (a,), b)
    ledger = Ledger("ledger", 0, (a.atom, b.atom, c.atom), (rule,), reports)
    return ledger, a, b, c


def model_intersection(ledger):
    """Exhaust all models with separate support flags for both literal signs.

    This does not run forward chaining or inspect producer justifications.
    Both signs may hold; these are not classical complementary truth values.
    """
    literals = tuple(
        SignedAtom(atom, positive)
        for atom in ledger.atoms
        for positive in (True, False)
    )
    seeds = {x.claim for x in ledger.reports if x.identity in ledger.endorsed}
    models = []
    for flags in product((False, True), repeat=len(literals)):
        world = {x for x, enabled in zip(literals, flags) if enabled}
        if seeds <= world and all(
            not set(r.premises) <= world or r.conclusion in world for r in ledger.rules
        ):
            models.append(world)
    assert models
    return set.intersection(*models)


def test_quotes_do_not_become_premises_and_missing_is_not_false():
    ledger, _, b, _ = setup()
    result = assess(ledger, derive(ledger), b)
    assert result["status"] == "not-established"
    assert result["support"] == result["opposition"] == []
    assert example()["quoted"]["status"] == "not-established"


def test_withdrawing_one_of_two_supports_retains_the_other_and_history():
    ledger, _, b, _ = setup()
    first, second = (x.identity for x in ledger.reports)
    endorsed = revise(ledger, endorsed=(first, second))
    old = derive(endorsed)
    assert len(assess(endorsed, old, b)["support"]) == 2
    withdrawn = revise(endorsed, endorsed=(second,))
    result = assess(withdrawn, derive(withdrawn), b)
    assert result["status"] == "supported" and len(result["support"]) == 1
    with pytest.raises(Refused, match="stale"):
        assess(withdrawn, old, b)
    assert assess(endorsed, old, b)["status"] == "supported"
    assert ledger.endorsed == () and withdrawn.parent == fingerprint(endorsed)


def test_all_support_withdrawn_means_unestablished_not_refuted():
    ledger, _, b, _ = setup()
    endorsed = revise(ledger, endorsed=tuple(x.identity for x in ledger.reports))
    withdrawn = revise(endorsed, endorsed=())
    assert assess(withdrawn, derive(withdrawn), b)["status"] == "not-established"
    assert fingerprint(ledger) != fingerprint(withdrawn)


def test_conflicting_reports_do_not_explode_into_unrelated_claims():
    ledger, a, _, c = setup()
    negative = Report(
        identity("negative", "report"), a.opposite(), identity("negative", "source")
    )
    ledger = revise(
        ledger,
        reports=(*ledger.reports, negative),
        endorsed=(ledger.reports[0].identity, negative.identity),
    )
    proof = derive(ledger)
    assert assess(ledger, proof, a)["status"] == "conflict"
    assert assess(ledger, proof, c)["status"] == "not-established"
    assert {x for x, _ in proof.facts} == model_intersection(ledger)


def test_same_origin_is_not_claimed_as_two_independent_observations():
    ledger, _, b, _ = setup()
    copied = replace(ledger.reports[1], origin=ledger.reports[0].origin)
    ledger = revise(
        ledger,
        reports=(ledger.reports[0], copied),
        endorsed=tuple(x.identity for x in ledger.reports),
    )
    answer = assess(ledger, derive(ledger), b)
    assert len(answer["support"]) == 2
    assert answer["support"][0]["origins"] == answer["support"][1]["origins"]


def test_independent_rules_with_the_same_premise_keep_separate_support_paths():
    ledger, a, b, _ = setup()
    second = Rule(identity("also-a-b", "rule"), (a,), b)
    ledger = revise(
        ledger, rules=(*ledger.rules, second), endorsed=(ledger.reports[0].identity,)
    )
    assert len(assess(ledger, derive(ledger), b)["support"]) == 2
    revised = revise(ledger, rules=(second,))
    assert len(assess(revised, derive(revised), b)["support"]) == 1


def test_cyclic_rules_need_a_seed_and_then_terminate():
    ledger, a, b, _ = setup()
    cycle = Rule(identity("b-a", "rule"), (b,), a)
    ledger = revise(ledger, rules=(*ledger.rules, cycle))
    assert derive(ledger).facts == ()
    seeded = revise(ledger, endorsed=(ledger.reports[0].identity,))
    result = derive(seeded)
    assert result.status == "complete"
    assert {x for x, _ in result.facts} == {a, b}


def test_budget_exhaustion_keeps_partial_support_without_fabricating_refutation():
    ledger, _, b, c = setup()
    ledger = revise(
        ledger,
        endorsed=(ledger.reports[0].identity,),
        rules=(*ledger.rules, Rule(identity("b-c", "rule"), (b,), c)),
    )
    partial = derive(ledger, budget=1)
    assert partial.status == "incomplete"
    assert assess(ledger, partial, c)["status"] == "search-incomplete"
    with pytest.raises(Refused, match="complete closure"):
        verify(ledger, replace(partial, status="complete"))
    assert assess(ledger, derive(ledger), c)["status"] == "supported"


def test_certificates_are_replayed_without_trusting_producer_status():
    ledger, a, b, c = setup()
    ledger = revise(ledger, endorsed=(ledger.reports[0].identity,))
    result = derive(ledger)
    support = dict(result.facts)[b][0]
    forged = replace(result, facts=(*result.facts, (c, (support,))))
    with pytest.raises(Refused, match="does not replay"):
        verify(ledger, forged)
    unendorsed = Support(frozenset((ledger.reports[1].identity,)), frozenset())
    with pytest.raises(Refused, match="unendorsed"):
        verify(ledger, replace(result, facts=((a, (unendorsed,)),)))
    with pytest.raises(Refused, match="different reasoning profile"):
        verify(ledger, replace(result, profile="classical"))


def test_seeded_rule_systems_match_an_exhaustive_model_oracle():
    rng = random.Random(1011)
    atoms = tuple(identity(x) for x in "abc")
    literals = tuple(SignedAtom(x, sign) for x in atoms for sign in (False, True))
    for trial in range(24):
        reports = tuple(
            Report(
                identity(f"{trial}:{i}", "report"),
                rng.choice(literals),
                identity(str(i), "source"),
            )
            for i in range(3)
        )
        rules = tuple(
            Rule(
                identity(f"{trial}:{i}", "rule"),
                tuple(rng.sample(literals, rng.randrange(3))),
                rng.choice(literals),
            )
            for i in range(5)
        )
        ledger = Ledger(
            "oracle",
            0,
            atoms,
            rules,
            reports,
            tuple(x.identity for x in reports if rng.choice((False, True))),
        )
        result = derive(ledger)
        assert result.status == "complete"
        assert verify(ledger, result)
        assert {x for x, _ in result.facts} == model_intersection(ledger)


def test_signature_revision_and_malformed_context_are_refused():
    ledger, a, _, _ = setup()
    with pytest.raises(Refused, match="signature"):
        replace(ledger, atoms=(Identity(a.atom.owner, "2", a.atom.slot),))
    with pytest.raises(Refused, match="endorsement"):
        revise(ledger, endorsed=(identity("not-captured"),))
    with pytest.raises(Refused, match="immutable"):
        replace(ledger, reports=list(ledger.reports))
    with pytest.raises(Refused, match="revision"):
        replace(ledger, revision=True)
    with pytest.raises(Refused, match="budget"):
        derive(ledger, budget=0)


def test_inspection_returns_detached_records():
    ledger, a, _, _ = setup()
    ledger = revise(ledger, endorsed=(ledger.reports[0].identity,))
    result = derive(ledger)
    view = assess(ledger, result, a)
    view["support"][0]["origins"][0]["slot"] = "changed"
    assert assess(ledger, result, a)["support"][0]["origins"][0]["slot"] == "0"
