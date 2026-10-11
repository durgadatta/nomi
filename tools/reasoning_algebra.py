"""Closed exact polynomial-map experiment; no general calculus or source feature.

Descriptions carry no engine. Composition, tangent lifting and judgments belong
to the named formal profile; realization is an explicit, separate adapter.
"""

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json

PROFILE = "scoped-rational-polynomial-maps-v1"
MAX_AXES = 8
MAX_TERMS = 128
MAX_DEGREE = 12
MAX_BITS = 256


class Refused(ValueError):
    """The closed profile does not admit this description or composition."""


def _name(value):
    if type(value) is not str or not value or len(value) > 128:
        raise Refused("expected a nonempty bounded identity")
    return value


def _rational(value):
    if type(value) not in (int, Fraction):
        raise Refused("expected exact Int or Fraction; Bool and Float are not admitted")
    result = Fraction(value)
    if (
        max(abs(result.numerator).bit_length(), result.denominator.bit_length())
        > MAX_BITS
    ):
        raise Refused("exact coefficient exceeds capacity")
    return result


@dataclass(frozen=True)
class Space:
    """Nominal finite affine formal coordinate space, not a manifold or unit system."""

    identity: str
    axes: tuple[str, ...]
    revision: str = "1"
    base: "Space | None" = None

    def __post_init__(self):
        _name(self.identity)
        _name(self.revision)
        if type(self.axes) is not tuple or not 1 <= len(self.axes) <= MAX_AXES:
            raise Refused("space requires 1..8 immutable coordinate names")
        for axis in self.axes:
            _name(axis)
        if len(set(self.axes)) != len(self.axes):
            raise Refused("duplicate coordinate name")
        if self.base is not None:
            if type(self.base) is not Space or self.axes != _tangent_axes(self.base):
                raise Refused("tangent coordinates must retain their base space")
            if (self.identity, self.revision) != (
                self.base.identity,
                self.base.revision,
            ):
                raise Refused("tangent identity must retain its base revision")


def _tangent_axes(space):
    return tuple("base:" + x for x in space.axes) + tuple(
        "delta:" + x for x in space.axes
    )


def tangent_space(space):
    return Space(space.identity, _tangent_axes(space), space.revision, space)


@dataclass(frozen=True)
class Polynomial:
    """Canonical finite polynomial with variables bound to exactly one Space."""

    space: Space
    terms: tuple[tuple[tuple[int, ...], Fraction], ...]

    def __post_init__(self):
        if type(self.space) is not Space or type(self.terms) is not tuple:
            raise Refused("expected a space and immutable canonical terms")
        if len(self.terms) > MAX_TERMS:
            raise Refused("polynomial exceeds term capacity")
        previous = None
        for term in self.terms:
            if type(term) is not tuple or len(term) != 2:
                raise Refused("expected exponent/coefficient pair")
            power, coefficient = term
            if type(power) is not tuple or len(power) != len(self.space.axes):
                raise Refused("exponent vector belongs to another space")
            if (
                any(type(x) is not int or x < 0 for x in power)
                or sum(power) > MAX_DEGREE
            ):
                raise Refused("polynomial exceeds degree capacity")
            if previous is not None and power <= previous:
                raise Refused("terms must have unique sorted exponents")
            if type(coefficient) is not Fraction or not coefficient:
                raise Refused("canonical coefficients must be nonzero Fractions")
            _rational(coefficient)
            previous = power

    def _coerce(self, other):
        if type(other) is Polynomial:
            if other.space != self.space:
                raise Refused("coordinate context mismatch; use an explicit map")
            return other
        return constant(self.space, other)

    def __add__(self, other):
        other = self._coerce(other)
        terms = dict(self.terms)
        for power, coefficient in other.terms:
            terms[power] = terms.get(power, Fraction(0)) + coefficient
        return _polynomial(self.space, terms)

    __radd__ = __add__

    def __neg__(self):
        return _polynomial(self.space, {p: -c for p, c in self.terms})

    def __sub__(self, other):
        return self + -self._coerce(other)

    def __rsub__(self, other):
        return self._coerce(other) + -self

    def __mul__(self, other):
        other = self._coerce(other)
        terms = {}
        for left, a in self.terms:
            for right, b in other.terms:
                power = tuple(x + y for x, y in zip(left, right))
                terms[power] = terms.get(power, Fraction(0)) + a * b
        return _polynomial(self.space, terms)

    __rmul__ = __mul__

    def __pow__(self, exponent):
        if type(exponent) is not int or not 0 <= exponent <= MAX_DEGREE:
            raise Refused("expected a bounded nonnegative integer power")
        result = constant(self.space, 1)
        for _ in range(exponent):
            result = result * self
        return result


def _polynomial(space, terms):
    return Polynomial(
        space, tuple(sorted((p, _rational(c)) for p, c in terms.items() if c))
    )


def constant(space, value):
    return _polynomial(space, {(0,) * len(space.axes): _rational(value)})


def coordinates(space):
    return tuple(
        _polynomial(
            space, {tuple(int(i == j) for j in range(len(space.axes))): Fraction(1)}
        )
        for i in range(len(space.axes))
    )


def partial(expression, axis):
    if type(axis) is not str or axis not in expression.space.axes:
        raise Refused("unknown bound coordinate")
    index = expression.space.axes.index(axis)
    terms = {}
    for power, coefficient in expression.terms:
        if power[index]:
            lowered = tuple(x - int(i == index) for i, x in enumerate(power))
            terms[lowered] = coefficient * power[index]
    return _polynomial(expression.space, terms)


@dataclass(frozen=True)
class Mapping:
    identity: str
    domain: Space
    codomain: Space
    components: tuple[Polynomial, ...]

    def __post_init__(self):
        _name(self.identity)
        if type(self.domain) is not Space or type(self.codomain) is not Space:
            raise Refused("mapping requires explicit spaces")
        if type(self.components) is not tuple or len(self.components) != len(
            self.codomain.axes
        ):
            raise Refused("mapping component count disagrees with codomain")
        if any(
            type(x) is not Polynomial or x.space != self.domain for x in self.components
        ):
            raise Refused("mapping components must be bound to its domain")


def identity(space):
    return Mapping("identity", space, space, coordinates(space))


def pullback(expression, mapping):
    """Capture-free substitution of a codomain-bound scalar along a map."""
    if expression.space != mapping.codomain:
        raise Refused("pullback requires the exact codomain context")
    result = constant(mapping.domain, 0)
    for power, coefficient in expression.terms:
        term = constant(mapping.domain, coefficient)
        for value, exponent in zip(mapping.components, power):
            term = term * value**exponent
        result = result + term
    return result


def compose(first, second, name="composition"):
    """Return second after first. Nothing is realized or sampled."""
    if first.codomain != second.domain:
        raise Refused("composition requires identical intermediate space and revision")
    return Mapping(
        name,
        first.domain,
        second.codomain,
        tuple(pullback(x, first) for x in second.components),
    )


def tangent(mapping, name="tangent"):
    """Formal T(f)(x, dx) = (f(x), J_f(x) dx), not numerical autodiff."""
    domain, codomain = tangent_space(mapping.domain), tangent_space(mapping.codomain)
    variables = coordinates(domain)
    size = len(mapping.domain.axes)
    projection = Mapping("base-projection", domain, mapping.domain, variables[:size])
    base_values = tuple(pullback(x, projection) for x in mapping.components)
    deltas = tuple(
        sum(
            (
                pullback(partial(component, axis), projection) * variables[size + i]
                for i, axis in enumerate(mapping.domain.axes)
            ),
            constant(domain, 0),
        )
        for component in mapping.components
    )
    return Mapping(name, domain, codomain, base_values + deltas)


def directional(expression, field):
    """Formal Lie derivative of a scalar along an affine coordinate field."""
    if field.domain != field.codomain or expression.space != field.domain:
        raise Refused("field must be an endomap over the expression's space")
    return sum(
        (
            partial(expression, axis) * value
            for axis, value in zip(field.domain.axes, field.components)
        ),
        constant(field.domain, 0),
    )


@dataclass(frozen=True)
class Expansion:
    original: Polynomial
    retained: Polynomial
    remainder: Polynomial
    parameter: str
    order: int


def truncate(expression, parameter, order):
    """Exact split by parameter degree; no analytic big-O or error estimate."""
    if type(parameter) is not str or parameter not in expression.space.axes:
        raise Refused("unknown expansion parameter")
    if type(order) is not int or not 0 <= order <= MAX_DEGREE:
        raise Refused("expected a bounded truncation order")
    index = expression.space.axes.index(parameter)
    retained = _polynomial(
        expression.space, {p: c for p, c in expression.terms if p[index] <= order}
    )
    return Expansion(expression, retained, expression - retained, parameter, order)


def _space_record(space):
    return {
        "id": space.identity,
        "revision": space.revision,
        "axes": space.axes,
        "base": _space_record(space.base) if space.base is not None else None,
    }


def describe(mapping):
    """Detached inert description; no callback, backend or capability handle."""
    return {
        "profile": PROFILE,
        "id": mapping.identity,
        "domain": _space_record(mapping.domain),
        "codomain": _space_record(mapping.codomain),
        "components": [
            [[list(p), [c.numerator, c.denominator]] for p, c in x.terms]
            for x in mapping.components
        ],
    }


def compare(left, right):
    """Decide identity only within the closed rational-polynomial profile."""
    if left.domain != right.domain or left.codomain != right.codomain:
        raise Refused("identity judgment requires identical domain and codomain")
    context = json.dumps(
        [describe(left), describe(right)], sort_keys=True, separators=(",", ":")
    )
    return {
        "status": "identity"
        if left.components == right.components
        else "not-an-identity",
        "profile": PROFILE,
        "context": hashlib.sha256(context.encode()).hexdigest(),
        "scope": "formal polynomial maps only; no analytic, physical or numerical claim",
    }


def verify_inverse(forward, candidate):
    """Check a supplied two-sided inverse; never solve for or assume one."""
    return (
        compare(compose(forward, candidate), identity(forward.domain)),
        compare(compose(candidate, forward), identity(forward.codomain)),
    )


def realize(mapping, values):
    """Explicit exact-rational adapter, separate from the passive description."""
    if type(values) is not tuple or len(values) != len(mapping.domain.axes):
        raise Refused("expected one exact binding per domain coordinate")
    values = tuple(_rational(x) for x in values)
    results = []
    for component in mapping.components:
        result = Fraction(0)
        for power, coefficient in component.terms:
            term = coefficient
            for value, exponent in zip(values, power):
                term = _rational(term * _rational(value**exponent))
            result = _rational(result + term)
        results.append(result)
    return tuple(results)
