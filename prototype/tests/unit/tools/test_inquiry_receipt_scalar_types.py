"""Replay admits exact rational receipts, not Python's equal Bool/Int values."""

from dataclasses import replace
from fractions import Fraction as F

import pytest

from tools import finite_inquiry as q


def captured():
    prior, _, objective = q.example()
    prior = replace(prior, masses=(F(1), F(0)))
    kernel = q.identity_kernel(prior.space)
    return prior, kernel, objective, q.query_value(prior, kernel, objective)


@pytest.mark.parametrize("field", ["baseline_loss", "residual_loss", "net_value"])
def test_equal_boolean_or_integer_cannot_replace_exact_rational_loss(field):
    prior, kernel, objective, receipt = captured()
    assert getattr(receipt, field) == 0
    for value in (False, 0):
        with pytest.raises(q.Refused):
            q.verify_inquiry(
                prior, kernel, objective, replace(receipt, **{field: value})
            )


def test_outcome_probabilities_keep_exact_scalar_types():
    prior, kernel, objective, receipt = captured()
    with pytest.raises(q.Refused):
        q.verify_inquiry(
            prior, kernel, objective, replace(receipt, outcome_masses=(True, False))
        )


def test_branch_mass_and_decision_loss_keep_exact_scalar_types():
    prior, kernel, objective, receipt = captured()
    branch = receipt.branches[0]
    forged_branches = (
        replace(branch, mass=True),
        replace(branch, decision=replace(branch.decision, expected_loss=False)),
    )
    for forged in forged_branches:
        with pytest.raises(q.Refused):
            q.verify_inquiry(
                prior,
                kernel,
                objective,
                replace(receipt, branches=(forged, *receipt.branches[1:])),
            )
