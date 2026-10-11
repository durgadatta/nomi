"""Named hypothetical intermediates remain inspectable and independently checked."""

from dataclasses import FrozenInstanceError, replace
from fractions import Fraction as F
import json

import pytest

from tools import finite_inquiry as q


def test_every_supported_outcome_has_a_named_posterior_and_conditional_decision():
    model, experiment, objective = q.example()
    result = q.query_value(model, experiment, objective)
    assert tuple(x.outcome for x in result.branches) == experiment.destination.members
    assert tuple(x.mass for x in result.branches) == result.outcome_masses
    assert len({x.identity for x in result.branches}) == 2
    assert result.branches[0].posterior.masses == (F(3, 4), F(1, 4))
    assert result.branches[1].posterior.masses == (F(1, 4), F(3, 4))
    assert result.branches[0].decision.alternatives == (objective.decisions.members[0],)
    assert result.branches[1].decision.alternatives == (objective.decisions.members[1],)
    assert (
        sum(x.mass * x.decision.expected_loss for x in result.branches)
        == result.residual_loss
    )
    assert q.verify_inquiry(model, experiment, objective, result)


def test_forged_intermediate_cannot_hide_behind_correct_aggregate_loss():
    model, experiment, objective = q.example()
    result = q.query_value(model, experiment, objective)
    branch = result.branches[0]
    forged = replace(branch, posterior=replace(branch.posterior, masses=(F(1), F(0))))
    with pytest.raises(q.Refused, match="branches"):
        q.verify_inquiry(
            model,
            experiment,
            objective,
            replace(result, branches=(forged, result.branches[1])),
        )
    with pytest.raises(q.Refused, match="branches"):
        q.verify_inquiry(model, experiment, objective, replace(result, branches=()))


def test_zero_support_branch_is_named_but_has_no_invented_conditional_objects():
    model, experiment, objective = q.example()
    experiment = replace(experiment, rows=((F(1), F(0)), (F(1), F(0))))
    result = q.query_value(model, experiment, objective)
    branch = result.branches[1]
    assert branch.outcome == experiment.destination.members[1]
    assert branch.mass == 0
    assert branch.posterior is None and branch.decision is None
    assert q.verify_inquiry(model, experiment, objective, result)


def test_passive_inspection_is_detached_json_and_cannot_change_the_artifact():
    model, experiment, objective = q.example()
    result = q.query_value(model, experiment, objective)
    record = q.describe(result)
    json.dumps(record)
    assert record["branches"][0]["mass"] == {"numerator": 1, "denominator": 2}
    record["branches"][0]["posterior"]["masses"][0]["numerator"] = 999
    assert result.branches[0].posterior.masses[0] == F(3, 4)
    assert q.describe(result)["branches"][0]["posterior"]["masses"][0]["numerator"] == 3
    with pytest.raises(FrozenInstanceError):
        result.branches[0].mass = F(0)
