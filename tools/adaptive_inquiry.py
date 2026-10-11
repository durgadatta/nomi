"""Revision-bound observations and one-step adaptive inquiry.

Distinct trials explicitly assume conditional independence given the captured
state. Copies of one trial's report are idempotent. No query runs a measurement,
and no proposed action grants authority to act.
"""

from dataclasses import dataclass
from fractions import Fraction as F

from tools import finite_inquiry as q
from tools import scoped_terms as t

PROFILE = "finite-adaptive-inquiry-v1"
DEPENDENCE = "conditionally-independent-trials-given-state-v1"


def _ids(values, limit):
    if (
        type(values) is not tuple
        or len(values) > limit
        or any(type(x) is not t.Identity for x in values)
    ):
        raise t.Refused("expected bounded immutable qualified identities")
    if len(set(values)) != len(values):
        raise t.Refused("duplicate qualified identity")


@dataclass(frozen=True)
class Question:
    identity: t.Identity
    kernel: q.Kernel
    cost: F

    def __post_init__(self):
        if type(self.identity) is not t.Identity or type(self.kernel) is not q.Kernel:
            raise t.Refused("question requires captured identity and likelihood kernel")
        q._numbers((self.cost,), 1)


@dataclass(frozen=True)
class Trial:
    identity: t.Identity
    question: Question

    def __post_init__(self):
        if type(self.identity) is not t.Identity or type(self.question) is not Question:
            raise t.Refused(
                "trial requires an occurrence identity and captured question"
            )

    @property
    def fingerprint(self):
        return q.fingerprint(PROFILE, self)


@dataclass(frozen=True)
class Report:
    identity: t.Identity
    origin: t.Identity
    trial: t.Identity
    trial_context: str
    outcome: t.Identity

    def __post_init__(self):
        _ids((self.identity,), 1)
        for value in (self.origin, self.trial, self.outcome):
            _ids((value,), 1)
        if (
            type(self.trial_context) is not str
            or len(self.trial_context) != 64
            or any(x not in "0123456789abcdef" for x in self.trial_context)
        ):
            raise t.Refused("report requires the captured trial fingerprint")


@dataclass(frozen=True)
class Journal:
    identity: t.Identity
    prior: q.Measure
    dependence: str
    trials: tuple[Trial, ...] = ()
    reports: tuple[Report, ...] = ()
    endorsed: tuple[t.Identity, ...] = ()
    parent: str | None = None

    def __post_init__(self):
        if type(self.identity) is not t.Identity or type(self.prior) is not q.Measure:
            raise t.Refused("journal requires captured identity and prior")
        if self.dependence != DEPENDENCE:
            raise t.Refused("declare the admitted conditional-independence profile")
        for values, kind, limit in (
            (self.trials, Trial, 16),
            (self.reports, Report, 32),
        ):
            if (
                type(values) is not tuple
                or len(values) > limit
                or any(type(x) is not kind for x in values)
            ):
                raise t.Refused("journal contains unsupported records")
            _ids(tuple(x.identity for x in values), limit)
        _ids(self.endorsed, 32)
        if self.parent is not None and (
            type(self.parent) is not str
            or len(self.parent) != 64
            or any(x not in "0123456789abcdef" for x in self.parent)
        ):
            raise t.Refused("journal parent requires a context fingerprint")
        trials = {x.identity: x for x in self.trials}
        if any(x.question.kernel.source != self.prior.space for x in self.trials):
            raise t.Refused("trial requires identical prior state space/revision")
        for report in self.reports:
            trial = trials.get(report.trial)
            if trial is None or report.trial_context != trial.fingerprint:
                raise t.Refused("report references an absent or stale trial law")
            if report.outcome not in trial.question.kernel.destination.members:
                raise t.Refused("report outcome outside captured trial space")
        if not set(self.endorsed) <= {x.identity for x in self.reports}:
            raise t.Refused("endorse only captured reports")

    @property
    def fingerprint(self):
        return q.fingerprint(PROFILE, self)


def revise(journal, *, prior=None, trials=None, reports=None, endorsed=None):
    """Atomic immutable replacement, retaining the original prior on withdrawal."""
    if type(journal) is not Journal:
        raise t.Refused("revision requires captured journal")
    values = (
        journal.prior if prior is None else prior,
        journal.trials if trials is None else trials,
        journal.reports if reports is None else reports,
        journal.endorsed if endorsed is None else endorsed,
    )
    revision = q.fingerprint(PROFILE, journal.fingerprint, values)
    return Journal(
        t.Identity(journal.identity.owner, revision, journal.identity.slot),
        values[0],
        journal.dependence,
        *values[1:],
        parent=journal.fingerprint,
    )


@dataclass(frozen=True)
class Support:
    trial: t.Identity
    outcomes: tuple[t.Identity, ...]
    reports: tuple[t.Identity, ...]


@dataclass(frozen=True)
class Estimate:
    context: str
    status: str
    normalizer: F | None
    posterior: q.Measure | None
    supports: tuple[Support, ...]


def infer(journal):
    if type(journal) is not Journal:
        raise t.Refused("inference requires captured journal")
    active = set(journal.endorsed)
    supports = []
    weights = list(journal.prior.masses)
    conflicting = False
    for trial in journal.trials:
        reports = tuple(
            x
            for x in journal.reports
            if x.identity in active and x.trial == trial.identity
        )
        if not reports:
            continue
        outcomes = tuple(sorted({x.outcome for x in reports}))
        supports.append(
            Support(trial.identity, outcomes, tuple(x.identity for x in reports))
        )
        if len(outcomes) != 1:
            conflicting = True
            continue
        column = trial.question.kernel.destination.members.index(outcomes[0])
        for i, row in enumerate(trial.question.kernel.rows):
            weights[i] *= row[column]
    context = journal.fingerprint
    if conflicting:
        return Estimate(context, "conflicting-reports", None, None, tuple(supports))
    normalizer = sum(weights, F(0))
    if not normalizer:
        return Estimate(context, "impossible-under-model", F(0), None, tuple(supports))
    posterior = q.Measure(
        t.Identity("adaptive-inference", context, "posterior"),
        journal.prior.space,
        tuple(x / normalizer for x in weights),
    )
    return Estimate(
        context, "exact-under-declared-model", normalizer, posterior, tuple(supports)
    )


@dataclass(frozen=True)
class Assessment:
    question: t.Identity
    inquiry: q.Inquiry


@dataclass(frozen=True)
class Plan:
    context: str
    status: str
    estimate: Estimate
    assessments: tuple[Assessment, ...]
    alternatives: tuple[t.Identity, ...]
    stop_allowed: bool


def plan_context(journal, questions, objective):
    if (
        type(journal) is not Journal
        or type(objective) is not q.Objective
        or objective.states != journal.prior.space
    ):
        raise t.Refused("planning requires identical journal/objective state space")
    if (
        type(questions) is not tuple
        or len(questions) > 8
        or any(type(x) is not Question for x in questions)
    ):
        raise t.Refused("plan requires up to eight captured questions")
    _ids(tuple(x.identity for x in questions), 8)
    if any(x.kernel.source != journal.prior.space for x in questions):
        raise t.Refused("question requires identical journal state space/revision")
    return q.fingerprint(PROFILE, "one-step", journal.fingerprint, questions, objective)


def plan(journal, questions, objective):
    context = plan_context(journal, questions, objective)
    estimate = infer(journal)
    if estimate.posterior is None:
        return Plan(context, "needs-model-or-evidence-repair", estimate, (), (), True)
    assessments = tuple(
        Assessment(
            x.identity,
            q.query_value(estimate.posterior, x.kernel, objective, cost=x.cost),
        )
        for x in questions
    )
    best = max((F(0), *(x.inquiry.net_value for x in assessments)))
    alternatives = tuple(x.question for x in assessments if x.inquiry.net_value == best)
    status = (
        "propose-inquiry"
        if best > 0
        else ("stop-or-tied-inquiry" if alternatives else "stop")
    )
    return Plan(context, status, estimate, assessments, alternatives, best == 0)


def observe(journal, question, outcome, *, occurrence, identity, origin, endorse=False):
    """Capture a supplied observation; defaults to inert quotation, no sampling."""
    if type(endorse) is not bool:
        raise t.Refused("endorsement must be explicit boolean")
    trial = Trial(occurrence, question)
    report = Report(identity, origin, occurrence, trial.fingerprint, outcome)
    return revise(
        journal,
        trials=journal.trials + (trial,),
        reports=journal.reports + (report,),
        endorsed=journal.endorsed + ((identity,) if endorse else ()),
    )
