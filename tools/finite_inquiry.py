"""Exact finite measures, lawful composition and decision-directed inquiry.

Descriptions contain no callbacks, RNG, solver or execution authority. The
adapter is intentionally finite: its numbers are conditional model answers,
never evidence that the model describes the actual world.
"""

from dataclasses import asdict, dataclass
from fractions import Fraction
import hashlib
import json

from tools.scoped_terms import Identity

PROFILE = "exact-finite-inquiry-v1"


class Refused(ValueError):
    """Malformed, stale or outside the finite profile."""


def _identity(value):
    if type(value) is not Identity:
        raise Refused("expected qualified identity")


def _numbers(values, count, *, normalized=False):
    if type(values) is not tuple or len(values) != count:
        raise Refused("wrong immutable scalar vector")
    if any(
        type(x) is not Fraction
        or x < 0
        or max(x.numerator.bit_length(), x.denominator.bit_length()) > 512
        for x in values
    ):
        raise Refused("expected bounded nonnegative exact rationals")
    if normalized and sum(values) != 1:
        raise Refused("probability mass must sum exactly to one")


@dataclass(frozen=True)
class Space:
    identity: Identity
    members: tuple[Identity, ...]

    def __post_init__(self):
        _identity(self.identity)
        if type(self.members) is not tuple or not 1 <= len(self.members) <= 8:
            raise Refused("space needs one to eight immutable members")
        for member in self.members:
            _identity(member)
        if len(set(self.members)) != len(self.members):
            raise Refused("space members must be distinct")


@dataclass(frozen=True)
class Measure:
    identity: Identity
    space: Space
    masses: tuple[Fraction, ...]

    def __post_init__(self):
        _identity(self.identity)
        if type(self.space) is not Space:
            raise Refused("measure needs captured finite space")
        _numbers(self.masses, len(self.space.members), normalized=True)


@dataclass(frozen=True)
class Kernel:
    identity: Identity
    source: Space
    destination: Space
    rows: tuple[tuple[Fraction, ...], ...]

    def __post_init__(self):
        _identity(self.identity)
        if type(self.source) is not Space or type(self.destination) is not Space:
            raise Refused("kernel needs captured source/destination spaces")
        if type(self.rows) is not tuple or len(self.rows) != len(self.source.members):
            raise Refused("wrong immutable kernel row count")
        for row in self.rows:
            _numbers(row, len(self.destination.members), normalized=True)


def fingerprint(*values):
    def encode(value):
        if type(value) is Fraction:
            return [value.numerator, value.denominator]
        if type(value) is tuple:
            return [encode(x) for x in value]
        if hasattr(value, "__dataclass_fields__"):
            return {
                "kind": type(value).__name__,
                **{
                    key: encode(getattr(value, key))
                    for key in value.__dataclass_fields__
                },
            }
        return value

    return hashlib.sha256(
        json.dumps(
            {"profile": PROFILE, "values": encode(values)}, sort_keys=True
        ).encode()
    ).hexdigest()


def _result_identity(owner, *values):
    return Identity(owner, fingerprint(*values), "result")


def identity_kernel(space):
    if type(space) is not Space:
        raise Refused("expected space")
    return Kernel(
        _result_identity("identity", space),
        space,
        space,
        tuple(
            tuple(Fraction(i == j) for j in range(len(space.members)))
            for i in range(len(space.members))
        ),
    )


def compose(first, second):
    if (
        type(first) is not Kernel
        or type(second) is not Kernel
        or first.destination != second.source
    ):
        raise Refused("composition requires identical intermediate space/revision")
    rows = tuple(
        tuple(
            sum(
                (
                    first.rows[i][j] * second.rows[j][k]
                    for j in range(len(first.destination.members))
                ),
                Fraction(0),
            )
            for k in range(len(second.destination.members))
        )
        for i in range(len(first.source.members))
    )
    return Kernel(
        _result_identity("composition", first, second),
        first.source,
        second.destination,
        rows,
    )


def pushforward(measure, kernel):
    if (
        type(measure) is not Measure
        or type(kernel) is not Kernel
        or measure.space != kernel.source
    ):
        raise Refused("pushforward requires identical source space/revision")
    masses = tuple(
        sum(
            (
                weight * row[j]
                for weight, row in zip(measure.masses, kernel.rows, strict=True)
            ),
            Fraction(0),
        )
        for j in range(len(kernel.destination.members))
    )
    return Measure(
        _result_identity("pushforward", measure, kernel), kernel.destination, masses
    )


@dataclass(frozen=True)
class Observation:
    identity: Identity
    origin: Identity
    allowed: tuple[Identity, ...]

    def __post_init__(self):
        _identity(self.identity)
        _identity(self.origin)
        if type(self.allowed) is not tuple or len(self.allowed) > 8:
            raise Refused("event requires bounded immutable members")
        for member in self.allowed:
            _identity(member)
        if len(set(self.allowed)) != len(self.allowed):
            raise Refused("event members must be distinct")


@dataclass(frozen=True)
class Basis:
    model: Measure
    observations: tuple[Observation, ...] = ()

    def __post_init__(self):
        if (
            type(self.model) is not Measure
            or type(self.observations) is not tuple
            or len(self.observations) > 16
        ):
            raise Refused("basis requires captured model and bounded observations")
        if any(type(x) is not Observation for x in self.observations):
            raise Refused("invalid observation")
        if len({x.identity for x in self.observations}) != len(self.observations):
            raise Refused("duplicate observation identity")
        if any(
            not set(x.allowed) <= set(self.model.space.members)
            for x in self.observations
        ):
            raise Refused("observation outside exact model space")


@dataclass(frozen=True)
class Inference:
    context: str
    status: str
    normalizer: Fraction
    posterior: Measure | None


def condition(basis):
    if type(basis) is not Basis:
        raise Refused("expected captured basis")
    # Events concern one shared joint world. Conjunction is idempotent; it does
    # not multiply reports as if they were independent repeated measurements.
    allowed = set(basis.model.space.members)
    for observation in basis.observations:
        allowed.intersection_update(observation.allowed)
    weights = tuple(
        mass if member in allowed else Fraction(0)
        for member, mass in zip(
            basis.model.space.members, basis.model.masses, strict=True
        )
    )
    normalizer = sum(weights)
    context = fingerprint(basis)
    if not normalizer:
        return Inference(context, "impossible-evidence", Fraction(0), None)
    posterior = Measure(
        Identity("conditioning", context, "posterior"),
        basis.model.space,
        tuple(x / normalizer for x in weights),
    )
    return Inference(context, "exact-under-model", normalizer, posterior)


@dataclass(frozen=True)
class Objective:
    identity: Identity
    states: Space
    decisions: Space
    losses: tuple[tuple[Fraction, ...], ...]

    def __post_init__(self):
        _identity(self.identity)
        if type(self.states) is not Space or type(self.decisions) is not Space:
            raise Refused("objective requires captured spaces")
        if type(self.losses) is not tuple or len(self.losses) != len(
            self.decisions.members
        ):
            raise Refused("objective requires one immutable row per decision")
        for row in self.losses:
            _numbers(row, len(self.states.members))


@dataclass(frozen=True)
class Decision:
    context: str
    expected_loss: Fraction
    alternatives: tuple[Identity, ...]


def decide(measure, objective):
    if (
        type(measure) is not Measure
        or type(objective) is not Objective
        or measure.space != objective.states
    ):
        raise Refused("decision requires identical model/objective state space")
    risks = tuple(
        sum(
            (p * loss for p, loss in zip(measure.masses, row, strict=True)), Fraction(0)
        )
        for row in objective.losses
    )
    best = min(risks)
    return Decision(
        fingerprint(measure, objective),
        best,
        tuple(
            key
            for key, risk in zip(objective.decisions.members, risks, strict=True)
            if risk == best
        ),
    )


@dataclass(frozen=True)
class Inquiry:
    context: str
    baseline_loss: Fraction
    residual_loss: Fraction
    cost: Fraction
    net_value: Fraction
    outcome_masses: tuple[Fraction, ...]


def query_value(measure, experiment, objective, *, cost=Fraction(0)):
    """One-step value of information for this loss, with adaptive decisions."""
    if (
        type(measure) is not Measure
        or type(experiment) is not Kernel
        or measure.space != experiment.source
    ):
        raise Refused("experiment requires identical model state space")
    _numbers((cost,), 1)
    baseline = decide(measure, objective).expected_loss
    predictive = pushforward(measure, experiment)
    residual = Fraction(0)
    for j, outcome_mass in enumerate(predictive.masses):
        if not outcome_mass:
            continue  # A zero-mass branch supplies no conditional answer.
        weights = tuple(
            p * row[j] / outcome_mass
            for p, row in zip(measure.masses, experiment.rows, strict=True)
        )
        hypothetical = Measure(
            _result_identity("hypothetical", measure, experiment, j),
            measure.space,
            weights,
        )
        residual += outcome_mass * decide(hypothetical, objective).expected_loss
    return Inquiry(
        fingerprint(measure, experiment, objective, cost),
        baseline,
        residual,
        cost,
        baseline - residual - cost,
        predictive.masses,
    )


def verify_inquiry(measure, experiment, objective, assessment):
    """Independent unnormalized-loss replay, without posterior construction."""
    if (
        type(measure) is not Measure
        or type(experiment) is not Kernel
        or type(objective) is not Objective
        or type(assessment) is not Inquiry
        or measure.space != experiment.source
        or measure.space != objective.states
    ):
        raise Refused("invalid inquiry replay context")
    _numbers((assessment.cost,), 1)
    if assessment.context != fingerprint(
        measure, experiment, objective, assessment.cost
    ):
        raise Refused("stale inquiry assessment")
    joint = tuple(
        tuple(
            p * row[j] for p, row in zip(measure.masses, experiment.rows, strict=True)
        )
        for j in range(len(experiment.destination.members))
    )
    masses = tuple(sum(row) for row in joint)
    baseline = min(
        sum(p * loss for p, loss in zip(measure.masses, row, strict=True))
        for row in objective.losses
    )
    residual = sum(
        min(
            sum(weight * loss for weight, loss in zip(branch, row, strict=True))
            for row in objective.losses
        )
        for branch in joint
    )
    if (
        assessment.baseline_loss != baseline
        or assessment.residual_loss != residual
        or assessment.net_value != baseline - residual - assessment.cost
        or assessment.outcome_masses != masses
    ):
        raise Refused("inquiry differs from independent loss replay")
    return True


def example():
    states = Space(
        Identity("hypotheses", "1", "space"),
        tuple(Identity("hypotheses", "1", x) for x in ("damped", "undamped")),
    )
    outcomes = Space(
        Identity("measurement", "1", "space"),
        tuple(Identity("measurement", "1", x) for x in ("decay", "flat")),
    )
    decisions = Space(
        Identity("decision", "1", "space"),
        tuple(Identity("decision", "1", x) for x in ("use-damped", "use-undamped")),
    )
    prior = Measure(
        Identity("model", "1", "prior"), states, (Fraction(1, 2), Fraction(1, 2))
    )
    experiment = Kernel(
        Identity("model", "1", "measurement-law"),
        states,
        outcomes,
        ((Fraction(3, 4), Fraction(1, 4)), (Fraction(1, 4), Fraction(3, 4))),
    )
    objective = Objective(
        Identity("policy", "1", "mismatch-loss"),
        states,
        decisions,
        ((Fraction(0), Fraction(1)), (Fraction(1), Fraction(0))),
    )
    return prior, experiment, objective


def main():
    prior, experiment, objective = example()
    result = query_value(prior, experiment, objective, cost=Fraction(1, 8))
    verify_inquiry(prior, experiment, objective, result)
    record = asdict(result)
    record = {
        key: str(value)
        if type(value) is Fraction
        else [str(x) for x in value]
        if type(value) is tuple
        else value
        for key, value in record.items()
    }
    print(
        json.dumps(
            {
                "profile": PROFILE,
                "question": "Is another measurement worth its declared cost?",
                "result": record,
                "execution": "no measurement performed",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
