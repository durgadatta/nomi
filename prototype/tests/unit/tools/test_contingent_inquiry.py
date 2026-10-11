"""Two-step information synergy, budget honesty and independent policy replay."""

from dataclasses import replace
from fractions import Fraction as F
import itertools

import pytest

from tools import adaptive_inquiry as a
from tools import inquiry_policy as p
from tools import inquiry_policy_replay as replay
from tools import scoped_terms as t


def test_one_step_stops_but_two_step_composition_finds_useful_information():
    journal, questions, objective = p.example()
    greedy = a.plan(journal, questions, objective)
    assert greedy.status == "stop"
    shallow = p.solve(journal, questions, objective, horizon=1)
    assert shallow.root.upper == F(1, 2)
    assert shallow.root.incumbents[0].slot == "stop"
    policy = p.solve(journal, questions, objective, horizon=2)
    assert policy.coverage == "complete"
    assert policy.root.lower == policy.root.upper == F(1, 8)
    assert policy.root.incumbents == tuple(x.identity for x in questions)
    assert replay.verify(journal, questions, objective, policy)


def test_optimum_matches_independent_exhaustive_contingent_strategies():
    journal, questions, objective = p.example()
    worlds = tuple(itertools.product((0, 1), repeat=2))
    costs = [F(1, 2)]  # Stop and choose a parity without observations.
    for first in (0, 1):
        for continuations in itertools.product((None, 0, 1), repeat=2):
            risk = F(1, 16)
            for outcome in (0, 1):
                matched = [world for world in worlds if world[first] == outcome]
                next_bit = continuations[outcome]
                if next_bit is None:
                    odd = sum(x ^ y for x, y in matched)
                    risk += F(min(odd, len(matched) - odd), 4)
                else:
                    risk += F(len(matched), 4) * F(1, 16)
                    for answer in (0, 1):
                        group = [world for world in matched if world[next_bit] == answer]
                        odd = sum(x ^ y for x, y in group)
                        risk += F(min(odd, len(group) - odd), 4)
            costs.append(risk)
    assert p.solve(journal, questions, objective).root.upper == min(costs)


def test_exhausted_budget_reports_conservative_bounds_and_feasible_incumbent():
    journal, questions, objective = p.example()
    partial = p.solve(journal, questions, objective, budget=1)
    assert partial.coverage == "incomplete" and partial.expanded == 1
    assert partial.root.lower <= F(1, 8) <= partial.root.upper
    assert partial.root.upper == F(1, 2)
    assert replay.verify(journal, questions, objective, partial, budget=1)
    with pytest.raises(t.Refused, match="coverage"):
        replay.verify(journal, questions, objective, replace(partial, coverage="complete"), budget=1)


def test_stale_policy_and_forged_deep_costs_fail_independent_replay():
    journal, questions, objective = p.example()
    policy = p.solve(journal, questions, objective)
    changed = a.revise(journal, prior=replace(journal.prior, masses=(F(1), F(0), F(0), F(0))))
    with pytest.raises(t.Refused, match="stale"):
        replay.verify(changed, questions, objective, policy)
    option = policy.root.options[0]
    child = option.children[0]
    forged_child = replace(child, upper=F(0))
    forged_option = replace(option, children=(forged_child, *option.children[1:]))
    forged = replace(policy, root=replace(policy.root, options=(forged_option, *policy.root.options[1:])))
    with pytest.raises(t.Refused, match="bounds"):
        replay.verify(journal, questions, objective, forged)


def test_terminal_and_empty_query_profiles_preserve_stopping():
    journal, questions, objective = p.example()
    terminal = p.solve(journal, questions, objective, horizon=0)
    assert terminal.expanded == 0 and terminal.root.complete
    assert replay.verify(journal, questions, objective, terminal, horizon=0)
    empty = p.solve(journal, (), objective)
    assert empty.coverage == "complete" and empty.root.upper == F(1, 2)
    assert replay.verify(journal, (), objective, empty)


def test_zero_mass_outcomes_have_no_child_and_unsupported_evidence_has_no_policy():
    journal, questions, objective = p.example()
    certain = a.revise(journal, prior=replace(journal.prior, masses=(F(1), F(0), F(0), F(0))))
    policy = p.solve(certain, questions, objective)
    assert policy.root.upper == 0
    assert all(option.children[1] is None for option in policy.root.options)
    assert replay.verify(certain, questions, objective, policy)
    unsupported = a.observe(certain, questions[0], questions[0].kernel.destination.members[1], occurrence=t.Identity("impossible", "1", "trial"), identity=t.Identity("impossible", "1", "report"), origin=t.Identity("impossible", "1", "source"), endorse=True)
    repair = p.solve(unsupported, questions, objective)
    assert repair.coverage == "no-supported-model" and repair.root is None
    assert replay.verify(unsupported, questions, objective, repair)
