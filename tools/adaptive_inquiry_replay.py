"""Independent likelihood-product replay, then existing joint-loss verification."""

from fractions import Fraction as F
from functools import reduce
from operator import mul

from tools import adaptive_inquiry as a
from tools import finite_inquiry as q
from tools import scoped_terms as t


def verify_estimate(journal, estimate):
    if type(journal) is not a.Journal or type(estimate) is not a.Estimate or estimate.context != journal.fingerprint:
        raise t.Refused("stale inference assessment")
    endorsed = {x.identity: x for x in journal.reports if x.identity in journal.endorsed}
    grouped = {
        trial.identity: tuple(x for x in endorsed.values() if x.trial == trial.identity)
        for trial in journal.trials
    }
    supports = tuple(
        a.Support(trial.identity, tuple(sorted({x.outcome for x in grouped[trial.identity]})), tuple(x.identity for x in grouped[trial.identity]))
        for trial in journal.trials if grouped[trial.identity]
    )
    if type(estimate.supports) is not tuple or estimate.supports != supports:
        raise t.Refused("inference report support failed replay")
    if any(len(x.outcomes) > 1 for x in supports):
        expected = ("conflicting-reports", None, None)
    else:
        columns = tuple(
            (trial.question.kernel.rows, trial.question.kernel.destination.members.index(grouped[trial.identity][0].outcome))
            for trial in journal.trials if grouped[trial.identity]
        )
        weights = tuple(
            prior * reduce(mul, (rows[i][column] for rows, column in columns), F(1))
            for i, prior in enumerate(journal.prior.masses)
        )
        normalizer = sum(weights, F(0))
        posterior = (
            q.Measure(t.Identity("adaptive-inference", journal.fingerprint, "posterior"), journal.prior.space, tuple(x / normalizer for x in weights))
            if normalizer else None
        )
        expected = ("exact-under-declared-model" if normalizer else "impossible-under-model", normalizer, posterior)
    if type(estimate.normalizer) not in (F, type(None)) or (estimate.status, estimate.normalizer, estimate.posterior) != expected:
        raise t.Refused("inference likelihood product failed replay")
    return True


def verify_plan(journal, questions, objective, plan):
    if type(plan) is not a.Plan or plan.context != a.plan_context(journal, questions, objective):
        raise t.Refused("stale inquiry plan")
    verify_estimate(journal, plan.estimate)
    if type(plan.assessments) is not tuple or type(plan.alternatives) is not tuple or type(plan.stop_allowed) is not bool:
        raise t.Refused("malformed inquiry plan")
    if plan.estimate.posterior is None:
        expected = ("needs-model-or-evidence-repair", (), True)
        if plan.assessments:
            raise t.Refused("unsupported posterior cannot forecast inquiries")
    else:
        if len(plan.assessments) != len(questions):
            raise t.Refused("incomplete question assessment coverage")
        for question, assessment in zip(questions, plan.assessments, strict=True):
            if type(assessment) is not a.Assessment or assessment.question != question.identity:
                raise t.Refused("question assessment mismatch")
            if type(assessment.inquiry.cost) is not F or assessment.inquiry.cost != question.cost:
                raise t.Refused("question cost mismatch")
            q.verify_inquiry(plan.estimate.posterior, question.kernel, objective, assessment.inquiry)
        positive = [x.inquiry.net_value for x in plan.assessments if x.inquiry.net_value > 0]
        best = max(positive) if positive else F(0)
        alternatives = tuple(x.question for x in plan.assessments if x.inquiry.net_value == best)
        expected = ("propose-inquiry" if positive else ("stop-or-tied-inquiry" if alternatives else "stop"), alternatives, not positive)
    if (plan.status, plan.alternatives, plan.stop_allowed) != expected:
        raise t.Refused("inquiry alternatives/stop choice failed replay")
    return True
