"""Vocabulary refinement is a checked interpretation, not hidden conditioning."""

from dataclasses import replace
from fractions import Fraction as F

import pytest

from tools import finite_inquiry as q
from tools import model_refinement as r
from tools import program_search as p
from tools import reasoning_structures as s
from tools import scoped_terms as t


def example(masses=(F(0), F(1))):
    family = s.ProgramFamily(p.search(p.example()).proposals)
    destination = s.ProgramFamily((family.programs[1],))
    measure = q.Measure(t.Identity("refinement", "1", "measure"), family.space, masses)
    return r.Restriction(family, destination), measure


def test_zero_mass_removal_preserves_measure_predictions_and_decisions():
    restriction, measure = example()
    assessment = r.restrict(restriction, measure)
    assert r.verify(restriction, measure, assessment)
    assert assessment.status == "support-preserving"
    assert assessment.transported.masses == (F(1),)
    prediction = s.predict(restriction.source, (F(3),))
    transported_kernel = r.restrict_kernel(restriction, prediction.kernel)
    assert q.pushforward(measure, prediction.kernel).masses == q.pushforward(assessment.transported, transported_kernel).masses
    space = restriction.source.space
    objective = q.Objective(t.Identity("policy", "1", "loss"), space, space, ((F(0), F(1)), (F(1), F(0))))
    transported_objective = r.restrict_objective(restriction, objective)
    assert transported_objective.decisions == objective.decisions
    assert q.decide(measure, objective).alternatives == q.decide(assessment.transported, transported_objective).alternatives


def test_positive_mass_removal_does_not_silently_renormalize():
    restriction, measure = example((F(1, 2), F(1, 2)))
    assessment = r.restrict(restriction, measure)
    assert assessment.status == "positive-mass-loss"
    assert assessment.removed_mass == F(1, 2)
    assert assessment.transported is None
    assert r.verify(restriction, measure, assessment)
    forged = replace(assessment, status="support-preserving", removed_mass=F(0))
    with pytest.raises(t.Refused, match="mass"):
        r.verify(restriction, measure, forged)


def test_explicit_permutation_preserves_weights_and_refuses_stale_basis():
    restriction, measure = example((F(1, 3), F(2, 3)))
    permutation = r.Restriction(restriction.source, s.ProgramFamily(tuple(reversed(restriction.source.programs))))
    assessment = r.restrict(permutation, measure)
    assert assessment.transported.masses == (F(2, 3), F(1, 3))
    assert r.verify(permutation, measure, assessment)
    with pytest.raises(t.Refused, match="stale"):
        r.verify(permutation, replace(measure, masses=(F(1, 2), F(1, 2))), assessment)


def test_a_new_grammar_or_equal_outputs_cannot_bless_a_new_program_identity():
    restriction, _ = example()
    changed_task = replace(p.example(), grammar=replace(p.example().grammar, identity=t.Identity("new-vocabulary", "1", "grammar")))
    changed = s.ProgramFamily(p.search(changed_task).proposals)
    with pytest.raises(t.Refused, match="reinterpret"):
        r.Restriction(restriction.source, changed)
