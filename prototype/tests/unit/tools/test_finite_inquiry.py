"""Law and independent arithmetic checks for finite inquiry compositions."""

from dataclasses import replace
from fractions import Fraction as F
import random

import pytest

from tools import finite_inquiry as q
from tools.scoped_terms import Identity


def key(name, revision="1"):
    return Identity("test", revision, name)


def space(name, size=2):
    return q.Space(key(name), tuple(key(f"{name}:{i}") for i in range(size)))


def test_query_has_exact_cost_and_decision_value_without_execution():
    prior, experiment, objective = q.example()
    result = q.query_value(prior, experiment, objective, cost=F(1, 8))
    assert result.baseline_loss == F(1, 2)
    assert result.residual_loss == F(1, 4)
    assert result.net_value == F(1, 8)
    assert q.verify_inquiry(prior, experiment, objective, result)


def test_finite_kernel_identity_associativity_and_pushforward_composition():
    rng = random.Random(83)
    spaces = [space(name, 3) for name in ("a", "b", "c", "d")]

    def masses():
        counts = [rng.randrange(1, 9) for _ in range(3)]
        return tuple(F(x, sum(counts)) for x in counts)

    for _ in range(24):
        kernels = [
            q.Kernel(key(str(i)), left, right, tuple(masses() for _ in left.members))
            for i, (left, right) in enumerate(zip(spaces, spaces[1:]))
        ]
        first, second, third = kernels
        assert q.compose(q.identity_kernel(first.source), first).rows == first.rows
        assert q.compose(first, q.identity_kernel(first.destination)).rows == first.rows
        left = q.compose(q.compose(first, second), third)
        right = q.compose(first, q.compose(second, third))
        assert left.rows == right.rows
        prior = q.Measure(key("prior"), first.source, masses())
        direct = q.pushforward(prior, q.compose(first, second))
        staged = q.pushforward(q.pushforward(prior, first), second)
        assert direct.masses == staged.masses
        # Independent path enumeration for the first state to final states.
        expected = tuple(
            sum(
                first.rows[0][j] * second.rows[j][k] * third.rows[k][destination]
                for j in range(3)
                for k in range(3)
            )
            for destination in range(3)
        )
        assert left.rows[0] == expected
        assert sum(direct.masses) == 1


def test_event_conditioning_is_idempotent_and_origin_does_not_imply_independence():
    states = space("joint", 3)
    model = q.Measure(key("prior"), states, (F(1, 2), F(1, 3), F(1, 6)))
    event = q.Observation(key("report"), key("sensor"), states.members[:2])
    first = q.condition(q.Basis(model, (event,)))
    repeated = q.condition(
        q.Basis(model, (event, replace(event, identity=key("copy"))))
    )
    assert first.normalizer == repeated.normalizer == F(5, 6)
    assert (
        first.posterior.masses == repeated.posterior.masses == (F(3, 5), F(2, 5), F(0))
    )
    assert first.context != repeated.context
    with pytest.raises(q.Refused, match="duplicate"):
        q.Basis(model, (event, event))


def test_withdrawal_recomputes_from_original_model_instead_of_inverting_update():
    states = space("joint", 3)
    model = q.Measure(key("prior"), states, (F(1, 2), F(1, 3), F(1, 6)))
    one = q.Observation(key("one"), key("sensor"), states.members[:2])
    two = q.Observation(key("two"), key("other"), states.members[1:])
    both = q.Basis(model, (one, two))
    assert q.condition(both).posterior.masses == (F(0), F(1), F(0))
    remaining = q.condition(replace(both, observations=(two,)))
    assert remaining.posterior.masses == (F(0), F(2, 3), F(1, 3))
    assert remaining.context != q.condition(both).context


def test_zero_probability_observation_returns_no_fabricated_posterior():
    states = space("world")
    model = q.Measure(key("prior"), states, (F(1), F(0)))
    basis = q.Basis(
        model, (q.Observation(key("zero"), key("sensor"), (states.members[1],)),)
    )
    result = q.condition(basis)
    assert result.status == "impossible-evidence"
    assert result.normalizer == 0 and result.posterior is None


def test_zero_mass_experiment_outcome_needs_no_conditional_posterior():
    prior, experiment, objective = q.example()
    constant = replace(experiment, rows=((F(1), F(0)), (F(1), F(0))))
    result = q.query_value(prior, constant, objective)
    assert result.outcome_masses == (F(1), F(0))
    assert result.net_value == 0
    assert q.verify_inquiry(prior, constant, objective, result)


def test_perfect_but_irrelevant_information_has_no_decision_value():
    prior, experiment, objective = q.example()
    perfect = replace(experiment, rows=((F(1), F(0)), (F(0), F(1))))
    assert q.query_value(prior, perfect, objective).net_value == F(1, 2)
    irrelevant = replace(objective, losses=((F(0), F(0)), (F(1), F(1))))
    assert q.query_value(prior, perfect, irrelevant).net_value == 0
    assert q.query_value(prior, perfect, irrelevant, cost=F(1, 8)).net_value == -F(1, 8)


def test_decision_preserves_ties_instead_of_silently_choosing_an_action():
    prior, _, objective = q.example()
    decision = q.decide(prior, objective)
    assert decision.alternatives == objective.decisions.members
    assert decision.expected_loss == F(1, 2)


def test_revised_model_kernel_or_objective_refuses_old_inquiry():
    prior, experiment, objective = q.example()
    result = q.query_value(prior, experiment, objective)
    for changes in (
        (replace(prior, identity=key("prior", "2")), experiment, objective),
        (prior, replace(experiment, rows=((F(1), F(0)), (F(0), F(1)))), objective),
        (prior, experiment, replace(objective, identity=key("goal", "2"))),
    ):
        with pytest.raises(q.Refused, match="stale"):
            q.verify_inquiry(*changes, result)
    with pytest.raises(q.Refused, match="replay"):
        q.verify_inquiry(prior, experiment, objective, replace(result, net_value=F(9)))


def test_expected_information_value_matches_integer_joint_loss_oracle():
    rng = random.Random(91)
    states, observations, decisions = (
        space("world", 3),
        space("obs", 3),
        space("act", 3),
    )
    for _ in range(32):
        counts = [rng.randrange(1, 7) for _ in range(3)]
        prior = q.Measure(
            key("model"), states, tuple(F(x, sum(counts)) for x in counts)
        )
        rows = [[rng.randrange(1, 7) for _ in range(3)] for _ in range(3)]
        kernel = q.Kernel(
            key("experiment"),
            states,
            observations,
            tuple(tuple(F(x, sum(row)) for x in row) for row in rows),
        )
        losses = [[rng.randrange(7) for _ in range(3)] for _ in range(3)]
        objective = q.Objective(
            key("objective"),
            states,
            decisions,
            tuple(tuple(F(x) for x in row) for row in losses),
        )
        result = q.query_value(prior, kernel, objective)
        # Exhaustive deterministic contingent policies: choose one action for
        # each outcome, compare joint losses without constructing posteriors.
        from itertools import product

        policy_losses = [
            sum(
                F(counts[w], sum(counts))
                * F(rows[w][o], sum(rows[w]))
                * losses[policy[o]][w]
                for w in range(3)
                for o in range(3)
            )
            for policy in product(range(3), repeat=3)
        ]
        assert result.residual_loss == min(policy_losses)
        assert result.net_value >= 0
        assert q.verify_inquiry(prior, kernel, objective, result)


def test_profile_limits_and_exact_nominal_spaces_are_not_labels():
    prior, experiment, objective = q.example()
    with pytest.raises(q.Refused, match="exact rationals"):
        replace(prior, masses=(0.5, 0.5))
    with pytest.raises(q.Refused, match="sum exactly"):
        replace(prior, masses=(F(1), F(1)))
    stale = replace(experiment.source, identity=key("same-label", "2"))
    with pytest.raises(q.Refused, match="identical"):
        q.pushforward(prior, replace(experiment, source=stale))
    with pytest.raises(q.Refused):
        replace(objective, losses=((F(-1), F(0)), (F(1), F(1))))
