"""Checked support-preserving restriction of a captured program vocabulary.

Dropping hypotheses is not free evidence. This bridge transports a measure only
when removed alternatives already have zero mass. It never renormalizes away
positive mass or compares new functions by empirical fit.
"""

from dataclasses import dataclass
from fractions import Fraction as F

from tools import finite_inquiry as q
from tools import reasoning_structures as s
from tools import scoped_terms as t

PROFILE = "finite-program-support-restriction-v1"


@dataclass(frozen=True)
class Restriction:
    source: s.ProgramFamily
    destination: s.ProgramFamily

    def __post_init__(self):
        if (
            type(self.source) is not s.ProgramFamily
            or type(self.destination) is not s.ProgramFamily
        ):
            raise t.Refused("restriction requires captured program families")
        if self.source.programs[0].source != self.destination.programs[0].source:
            raise t.Refused("restriction requires identical callable contracts")
        if not set(self.destination.space.members) <= set(self.source.space.members):
            raise t.Refused(
                "restriction cannot introduce or reinterpret program artifacts"
            )

    @property
    def fingerprint(self):
        return q.fingerprint(PROFILE, self.source.space, self.destination.space)


@dataclass(frozen=True)
class Assessment:
    context: str
    status: str
    removed_mass: F
    transported: q.Measure | None


def _context(restriction, measure):
    if (
        type(restriction) is not Restriction
        or type(measure) is not q.Measure
        or measure.space != restriction.source.space
    ):
        raise t.Refused("restriction requires identical source measure context")
    return q.fingerprint(PROFILE, restriction.fingerprint, measure)


def restrict(restriction, measure):
    context = _context(restriction, measure)
    positions = {member: i for i, member in enumerate(measure.space.members)}
    masses = tuple(
        measure.masses[positions[x]] for x in restriction.destination.space.members
    )
    removed = F(1) - sum(masses)
    if removed:
        return Assessment(context, "positive-mass-loss", removed, None)
    transported = q.Measure(
        t.Identity("model-restriction", context, "measure"),
        restriction.destination.space,
        masses,
    )
    return Assessment(context, "support-preserving", F(0), transported)


def verify(restriction, measure, assessment):
    """Independent retained-set and mass replay; no producer restriction call."""
    context = _context(restriction, measure)
    if type(assessment) is not Assessment or assessment.context != context:
        raise t.Refused("stale model restriction assessment")
    selected = set(restriction.destination.space.members)
    retained = {
        member: mass
        for member, mass in zip(measure.space.members, measure.masses, strict=True)
        if member in selected
    }
    removed = sum(
        (
            mass
            for member, mass in zip(measure.space.members, measure.masses, strict=True)
            if member not in selected
        ),
        F(0),
    )
    if type(assessment.removed_mass) is not F or assessment.removed_mass != removed:
        raise t.Refused("restriction mass failed replay")
    if removed:
        if (
            assessment.status != "positive-mass-loss"
            or assessment.transported is not None
        ):
            raise t.Refused("restriction cannot discard positive mass")
    else:
        expected = q.Measure(
            t.Identity("model-restriction", context, "measure"),
            restriction.destination.space,
            tuple(retained[x] for x in restriction.destination.space.members),
        )
        if (
            assessment.status != "support-preserving"
            or assessment.transported != expected
        ):
            raise t.Refused("restricted measure failed replay")
    return True


def restrict_kernel(restriction, kernel):
    if (
        type(restriction) is not Restriction
        or type(kernel) is not q.Kernel
        or kernel.source != restriction.source.space
    ):
        raise t.Refused("kernel restriction requires identical source context")
    positions = {member: i for i, member in enumerate(kernel.source.members)}
    rows = tuple(
        kernel.rows[positions[x]] for x in restriction.destination.space.members
    )
    context = q.fingerprint(PROFILE, restriction.fingerprint, kernel)
    return q.Kernel(
        t.Identity("model-restriction", context, "kernel"),
        restriction.destination.space,
        kernel.destination,
        rows,
    )


def restrict_objective(restriction, objective):
    """Restrict modeled states; preserve the entire original decision space."""
    if (
        type(restriction) is not Restriction
        or type(objective) is not q.Objective
        or objective.states != restriction.source.space
    ):
        raise t.Refused("objective restriction requires identical state context")
    indices = tuple(
        objective.states.members.index(x) for x in restriction.destination.space.members
    )
    losses = tuple(tuple(row[i] for i in indices) for row in objective.losses)
    context = q.fingerprint(PROFILE, restriction.fingerprint, objective)
    return q.Objective(
        t.Identity("model-restriction", context, "objective"),
        restriction.destination.space,
        objective.decisions,
        losses,
    )
