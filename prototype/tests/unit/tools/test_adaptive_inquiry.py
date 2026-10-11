"""Quoted observations, explicit dependence, withdrawal and independent replay."""

from dataclasses import replace
from fractions import Fraction as F
import itertools

import pytest

from tools import adaptive_inquiry as a
from tools import adaptive_inquiry_replay as replay
from tools import finite_inquiry as q
from tools import scoped_terms as t


def key(slot):
    return t.Identity("adaptive-test", "1", slot)


def example():
    prior, kernel, objective = q.example()
    question = a.Question(key("measurement"), kernel, F(1, 8))
    return a.Journal(key("journal"), prior, a.DEPENDENCE), question, objective


def observe(journal, question, trial="trial1", index=0, endorsed=True):
    return a.observe(journal, question, question.kernel.destination.members[index], occurrence=key(trial), identity=key(f"report-{trial}"), origin=key("sensor"), endorse=endorsed)


def test_quoted_observation_is_inert_until_endorsed():
    journal, question, _ = example()
    quoted = observe(journal, question, endorsed=False)
    estimate = a.infer(quoted)
    assert estimate.posterior.masses == journal.prior.masses
    assert not estimate.supports
    endorsed = a.revise(quoted, endorsed=(quoted.reports[0].identity,))
    estimate = a.infer(endorsed)
    assert estimate.posterior.masses == (F(3, 4), F(1, 4))
    assert estimate.normalizer == F(1, 2)
    assert replay.verify_estimate(endorsed, estimate)


def test_copied_report_is_idempotent_but_distinct_trials_update_under_declared_law():
    journal, question, _ = example()
    first = observe(journal, question)
    copied = replace(first.reports[0], identity=key("copied-report"), origin=key("other-source"))
    duplicate = a.revise(first, reports=first.reports + (copied,), endorsed=first.endorsed + (copied.identity,))
    assert a.infer(duplicate).posterior.masses == (F(3, 4), F(1, 4))
    second = observe(first, question, "trial2")
    estimate = a.infer(second)
    assert estimate.posterior.masses == (F(9, 10), F(1, 10))
    assert estimate.normalizer == F(5, 16)
    assert replay.verify_estimate(second, estimate)


def test_withdrawal_recomputes_original_prior_and_preserves_parent():
    journal, question, _ = example()
    first = observe(journal, question)
    second = observe(first, question, "trial2", 1)
    assert a.infer(second).posterior.masses == journal.prior.masses
    withdrawn = a.revise(second, endorsed=(first.reports[0].identity,))
    assert withdrawn.parent == second.fingerprint
    assert a.infer(withdrawn).posterior.masses == (F(3, 4), F(1, 4))
    assert replay.verify_estimate(withdrawn, a.infer(withdrawn))
    with pytest.raises(t.Refused, match="stale"):
        replay.verify_estimate(withdrawn, a.infer(second))


def test_conflicting_same_trial_reports_do_not_invent_independent_samples():
    journal, question, _ = example()
    first = observe(journal, question)
    conflicting = replace(first.reports[0], identity=key("conflicting"), outcome=question.kernel.destination.members[1])
    revised = a.revise(first, reports=first.reports + (conflicting,), endorsed=first.endorsed + (conflicting.identity,))
    estimate = a.infer(revised)
    assert estimate.status == "conflicting-reports"
    assert estimate.posterior is None and estimate.normalizer is None
    assert replay.verify_estimate(revised, estimate)


def test_zero_likelihood_is_model_failure_not_report_conflict():
    journal, question, objective = example()
    impossible = replace(question, kernel=replace(question.kernel, rows=((F(1), F(0)), (F(1), F(0)))))
    revised = observe(journal, impossible, index=1)
    estimate = a.infer(revised)
    assert estimate.status == "impossible-under-model" and estimate.normalizer == 0
    plan = a.plan(revised, (impossible,), objective)
    assert plan.status == "needs-model-or-evidence-repair"
    assert replay.verify_plan(revised, (impossible,), objective, plan)


def test_stale_trial_law_cannot_reinterpret_old_reports():
    journal, question, _ = example()
    first = observe(journal, question)
    changed = replace(first.trials[0], question=replace(question, cost=F(1, 4)))
    with pytest.raises(t.Refused, match="stale trial"):
        a.revise(first, trials=(changed,))
    with pytest.raises(t.Refused, match="independence"):
        replace(journal, dependence="implicitly-independent")


def test_plan_retains_query_ties_and_stop_ties_and_contexts():
    journal, question, objective = example()
    other = replace(question, identity=key("other-query"))
    questions = (question, other)
    plan = a.plan(journal, questions, objective)
    assert plan.alternatives == (question.identity, other.identity)
    assert not plan.stop_allowed and plan.status == "propose-inquiry"
    assert replay.verify_plan(journal, questions, objective, plan)
    neutral = replace(question, cost=F(1, 4))
    tied = a.plan(journal, (neutral,), objective)
    assert tied.stop_allowed and tied.alternatives == (neutral.identity,)
    assert replay.verify_plan(journal, (neutral,), objective, tied)
    with pytest.raises(t.Refused, match="stale"):
        replay.verify_plan(journal, (neutral,), objective, plan)
    for forged in (replace(plan, stop_allowed=True), replace(plan, alternatives=()), replace(plan, assessments=())):
        with pytest.raises(t.Refused):
            replay.verify_plan(journal, questions, objective, forged)


def test_likelihood_product_matches_independent_enumerated_joint_worlds():
    journal, question, _ = example()
    for observations in itertools.product(range(2), repeat=3):
        revised = journal
        for i, outcome in enumerate(observations):
            revised = observe(revised, question, f"trial{i}", outcome)
        weights = [F(0), F(0)]
        # Enumerate latent state and all three outcomes, retaining the event.
        for state, outcomes in itertools.product(range(2), itertools.product(range(2), repeat=3)):
            mass = journal.prior.masses[state]
            for outcome in outcomes:
                mass *= question.kernel.rows[state][outcome]
            if outcomes == observations:
                weights[state] += mass
        estimate = a.infer(revised)
        assert estimate.normalizer == sum(weights)
        assert estimate.posterior.masses == tuple(x / sum(weights) for x in weights)
        assert replay.verify_estimate(revised, estimate)
