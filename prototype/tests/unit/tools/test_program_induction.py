"""Bounded learning claims: fit, counterexamples, exhaustive/prefix replay."""

from dataclasses import replace
from fractions import Fraction as F

import pytest

from tools import program_search as p
from tools import program_search_replay as replay
from tools import scoped_terms as t


def example(inputs, output, index=0):
    return p.Example(t.Identity("examples", "1", str(index)), tuple(F(x) for x in inputs), F(output))


def test_induction_retains_ambiguity_then_a_new_example_refutes_a_proposal():
    task = p.example()
    result = p.search(task)
    assert replay.verify(task, result)
    assert result.coverage == "complete"
    assert result.examined == result.matches == 2
    assert tuple(t.realize(x.description, (F(2),)) for x in result.proposals) == (F(2), F(4))
    revised = replace(task, examples=task.examples + (example((2,), 4),))
    learned = p.search(revised)
    assert replay.verify(revised, learned)
    assert len(learned.proposals) == 1
    assert t.realize(learned.proposals[0].description, (F(3),)) == 9
    with pytest.raises(t.Refused, match="stale"):
        replay.verify(revised, result)


@pytest.mark.parametrize("operators", [("add",), ("sub",), ("mul",), ("neg",), ("mul", "add", "neg")])
def test_separate_enumerators_agree_on_positive_and_negative_rational_examples(operators):
    grammar = p.Grammar(t.Identity("enumeration", "1", "grammar"), 2, (F(-1), F(1, 2)), operators, 4)
    task = p.Task(grammar, (example((2, -1), 1), example((0, 1), 1, 1)))
    assert replay.verify(task, p.search(task))


def test_small_budget_does_not_claim_no_fit_or_exhaustive_coverage():
    task = replace(p.example(), budget=1)
    result = p.search(task)
    assert result.coverage == "incomplete"
    assert replay.verify(task, result)
    with pytest.raises(t.Refused, match="coverage"):
        replay.verify(task, replace(result, coverage="complete"))


def test_retention_is_explicit_and_does_not_hide_search_match_count():
    grammar = p.Grammar(t.Identity("many", "1", "grammar"), 1, (F(0),), ("add",), 3)
    task = p.Task(grammar, (), retain=1)
    result = p.search(task)
    assert result.matches == 6
    assert result.retention == "truncated"
    assert len(result.proposals) == 1
    assert replay.verify(task, result)


def test_contradictory_examples_return_no_proposals_without_explosion():
    task = replace(p.example(), examples=(example((1,), 1), example((1,), 2, 1)))
    result = p.search(task)
    assert not result.proposals and result.coverage == "complete"
    assert replay.verify(task, result)


def test_independent_replay_rejects_forged_counts_and_proposal_order():
    task = p.example()
    result = p.search(task)
    for forged in (replace(result, matches=3), replace(result, examined=True), replace(result, proposals=tuple(reversed(result.proposals)))):
        with pytest.raises(t.Refused):
            replay.verify(task, forged)


def test_learning_can_propose_a_scientific_force_description():
    grammar = p.Grammar(t.Identity("force", "1", "grammar"), 2, (F(-2),), ("sub", "mul"), 5)
    task = p.Task(grammar, (
        example((1, 0), -2), example((0, 1), -1, 1), example((2, -1), -3, 2),
    ))
    result = p.search(task)
    assert replay.verify(task, result)
    assert result.proposals
    assert result.coverage == "complete"
    for proposal in result.proposals:
        for position, velocity in ((F(3), F(2)), (F(-1, 2), F(3, 2))):
            assert t.realize(proposal.description, (position, velocity)) == -2 * position - velocity


def test_description_is_detached_and_contract_limits_are_explicit():
    task = p.example()
    result = p.search(task)
    view = p.describe(result)
    view["proposals"].clear()
    assert result.proposals
    assert view["evidence"] == "supplied-examples-only"
    with pytest.raises(t.Refused):
        replace(task.grammar, arity=True)
    with pytest.raises(t.Refused):
        replace(task, budget=0)
    with pytest.raises(t.Refused, match="16 bits"):
        example((2**20,), 0)
