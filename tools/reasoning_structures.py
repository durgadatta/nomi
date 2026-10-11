"""Shared transformation boundary with explicit, carrier-specific providers.

Closed rational functions and finite probability kernels share inspection and
composition entry points. Ports and laws stay carrier-specific. Nothing here
turns a declaration into proof or carries effects/execution authority.
"""

from dataclasses import dataclass
from fractions import Fraction as F
import json

from tools import finite_inquiry as q
from tools import scoped_terms as t

PROFILE = "reasoning-transformation-boundary-v1"


@dataclass(frozen=True)
class Provider:
    identity: t.Identity
    carrier: str
    equality: str
    laws: tuple[str, ...]


RATIONAL = Provider(
    t.Identity(PROFILE, "1", "rational"),
    "closed-rational-function",
    "alpha-normal-form",
    ("typed-composition", "pure-application"),
)
FINITE = Provider(
    t.Identity(PROFILE, "1", "finite"),
    "finite-probability-kernel",
    "exact-rows-and-ports",
    ("normalization", "identity", "associativity"),
)
PROVIDERS = (RATIONAL, FINITE)


@dataclass(frozen=True)
class RationalPort:
    arity: int

    def __post_init__(self):
        if type(self.arity) is not int or not 1 <= self.arity <= 8:
            raise t.Refused("rational port requires one to eight coordinates")


@dataclass(frozen=True)
class Transformation:
    provider: Provider
    source: RationalPort | q.Space
    destination: RationalPort | q.Space
    description: object

    def __post_init__(self):
        if self.provider == RATIONAL:
            sort = t.infer(self.description)
            if (
                type(self.description) is not t.Lambda
                or type(sort) is not t.FunctionType
                or any(x != "Rational" for x in sort.parameters)
                or sort.result != "Rational"
                or self.source != RationalPort(len(sort.parameters))
                or self.destination != RationalPort(1)
            ):
                raise t.Refused("provider requires a closed rational callable contract")
        elif self.provider == FINITE:
            if (
                type(self.description) is not q.Kernel
                or self.source != self.description.source
                or self.destination != self.description.destination
            ):
                raise t.Refused("provider requires captured finite kernel ports")
        else:
            raise t.Refused("unsupported structure provider revision")

    @property
    def fingerprint(self):
        if self.provider == RATIONAL:
            return q.fingerprint(PROFILE, self.provider, t.describe(self.description))
        return q.fingerprint(PROFILE, self.provider, self.description)

    @property
    def identity(self):
        return t.Identity("transformation", self.fingerprint, "description")


def rational(term):
    sort = t.infer(term)
    if type(sort) is not t.FunctionType:
        raise t.Refused("provider requires a closed rational callable contract")
    return Transformation(
        RATIONAL, RationalPort(len(sort.parameters)), RationalPort(1), term
    )


def stochastic(kernel):
    if type(kernel) is not q.Kernel:
        raise t.Refused("expected finite kernel description")
    return Transformation(FINITE, kernel.source, kernel.destination, kernel)


def compose(first, second):
    if (
        type(first) is not Transformation
        or type(second) is not Transformation
        or first.provider != second.provider
        or first.destination != second.source
    ):
        raise t.Refused("composition requires matching provider and captured ports")
    if first.provider == FINITE:
        return stochastic(q.compose(first.description, second.description))
    revision = q.fingerprint(first.fingerprint, second.fingerprint)
    parameters = tuple(
        t.Binding(t.Identity("structure-composition", revision, f"arg:{i}"), f"arg{i}")
        for i in range(first.source.arity)
    )
    applied = t.Application(
        first.description, tuple(t.Reference(x.identity) for x in parameters)
    )
    return rational(t.Lambda(parameters, t.Application(second.description, (applied,))))


def equivalent(first, second):
    """The provider's declared equality, not cross-provider or empirical truth."""
    if type(first) is not Transformation or type(second) is not Transformation:
        raise t.Refused("expected transformation descriptions")
    if (first.provider, first.source, first.destination) != (
        second.provider,
        second.source,
        second.destination,
    ):
        return False
    if first.provider == RATIONAL:
        return t.alpha_equivalent(first.description, second.description)
    return first.description.rows == second.description.rows


def describe(transformation):
    if type(transformation) is not Transformation:
        raise t.Refused("expected transformation description")
    payload = (
        t.describe(transformation.description)
        if transformation.provider == RATIONAL
        else transformation.description
    )
    return json.loads(
        json.dumps(
            {
                "profile": PROFILE,
                "identity": transformation.identity,
                "provider": transformation.provider,
                "source": transformation.source,
                "destination": transformation.destination,
                "payload": payload,
            },
            default=lambda x: (
                {"numerator": x.numerator, "denominator": x.denominator}
                if type(x) is F
                else x.__dict__
            ),
        )
    )


@dataclass(frozen=True)
class ProgramFamily:
    programs: tuple[Transformation, ...]

    def __post_init__(self):
        if type(self.programs) is not tuple or not 1 <= len(self.programs) <= 8:
            raise t.Refused(
                "program family requires one to eight immutable alternatives"
            )
        if any(
            type(x) is not Transformation or x.provider != RATIONAL
            for x in self.programs
        ):
            raise t.Refused("family requires rational callable providers")
        if any(x.source != self.programs[0].source for x in self.programs):
            raise t.Refused("family requires one shared checked callable contract")
        if len({x.fingerprint for x in self.programs}) != len(self.programs):
            raise t.Refused("duplicate program artifact")

    @property
    def space(self):
        members = tuple(x.identity for x in self.programs)
        return q.Space(
            t.Identity("program-family", q.fingerprint(members), "space"), members
        )


@dataclass(frozen=True)
class Prediction:
    family: ProgramFamily
    arguments: tuple[F, ...]
    outcomes: tuple[F | None, ...]
    kernel: q.Kernel


def predict(family, arguments, *, include_other=False):
    """Explicit exact realization; returns a finite observation description."""
    if type(family) is not ProgramFamily or type(arguments) is not tuple:
        raise t.Refused("prediction requires captured family and immutable arguments")
    if any(type(x) is not F for x in arguments):
        raise t.Refused("prediction requires exact rational inputs")
    if type(include_other) is not bool:
        raise t.Refused("outside-support bucket requires explicit boolean")
    values = tuple(t.realize(x.description, arguments) for x in family.programs)
    outcomes = tuple(sorted(set(values)))
    if include_other:
        if len(outcomes) >= 8:
            raise t.Refused("outside-support bucket exceeds finite outcome capacity")
        outcomes += (None,)
    revision = q.fingerprint(family.space, arguments, outcomes)
    destination = q.Space(
        t.Identity("program-prediction", revision, "outcomes"),
        tuple(
            t.Identity("program-prediction", revision, f"outcome:{i}")
            for i in range(len(outcomes))
        ),
    )
    kernel = q.Kernel(
        t.Identity("program-prediction", revision, "kernel"),
        family.space,
        destination,
        tuple(tuple(F(value == outcome) for outcome in outcomes) for value in values),
    )
    return Prediction(family, arguments, outcomes, kernel)
