"""Foundational composition laws and independent arithmetic counterexamples."""

from dataclasses import FrozenInstanceError
from fractions import Fraction
import json
import random
import subprocess
import sys

import pytest

from tools.reasoning_algebra import (
    Mapping,
    Polynomial,
    Refused,
    Space,
    compare,
    compose,
    constant,
    coordinates,
    describe,
    directional,
    identity,
    partial,
    realize,
    tangent,
    tangent_space,
    truncate,
    verify_inverse,
)
from tools.reasoning_examples import examples


def test_compact_input_free_workflows_close_their_exact_identities():
    assert len(examples()) == 14
    assert all(x["status"] == "identity" for x in examples().values())


@pytest.mark.parametrize(
    "intermediate",
    [
        Space("other-meaning", ("x",)),
        Space("line", ("x",), "2"),
        Space("line", ("different-coordinate",)),
    ],
)
def test_equal_shape_and_spelling_do_not_grant_composition(intermediate):
    line = Space("line", ("x",))
    with pytest.raises(Refused, match="intermediate space"):
        compose(identity(line), identity(intermediate))


def test_equal_coordinate_spelling_does_not_capture_another_scope():
    a, b = Space("A", ("x",)), Space("B", ("x",))
    (x,) = coordinates(a)
    (y,) = coordinates(b)
    with pytest.raises(Refused, match="context mismatch"):
        _ = x + y
    with pytest.raises(Refused, match="bound to its domain"):
        Mapping("bad", a, b, (y,))
    rename = Mapping("rename", a, b, (x,))
    square = Mapping("square", b, b, (y**2,))
    assert realize(compose(rename, square), (3,)) == (9,)


def test_tangent_preserves_base_identity_without_becoming_the_base():
    line = Space("line", ("x",))
    lifted = tangent_space(line)
    assert lifted.base == line and lifted != Space("line", lifted.axes)
    with pytest.raises(Refused, match="base space"):
        Space("line", ("x",), base=line)
    with pytest.raises(Refused, match="base revision"):
        Space("line", lifted.axes, "2", line)


def test_tangent_identity_and_associativity_are_exact():
    a, b, c = [Space(name, ("x",)) for name in ("A", "B", "C")]
    (x,) = coordinates(a)
    (y,) = coordinates(b)
    (z,) = coordinates(c)
    f, g, h = (
        Mapping("f", a, b, (x + 1,)),
        Mapping("g", b, c, (y**2,)),
        Mapping("h", c, a, (z - 2,)),
    )
    assert (
        compare(tangent(identity(a)), identity(tangent_space(a)))["status"]
        == "identity"
    )
    assert (
        compare(compose(compose(f, g), h), compose(f, compose(g, h)))["status"]
        == "identity"
    )


def test_seeded_tangent_and_composition_match_independent_hand_arithmetic():
    rng = random.Random(10410)
    a, b = Space("A", ("x",)), Space("B", ("x",))
    (x,) = coordinates(a)
    (y,) = coordinates(b)

    def value(coefficients, argument):
        result = Fraction(0)
        for coefficient in reversed(coefficients):
            result = result * argument + coefficient
        return result

    def slope(coefficients, argument):
        return sum(i * c * argument ** (i - 1) for i, c in enumerate(coefficients) if i)

    for _ in range(30):
        fc, gc = [tuple(rng.randint(-3, 3) for _ in range(4)) for _ in range(2)]
        f = Mapping("f", a, b, (sum(c * x**i for i, c in enumerate(fc)),))
        g = Mapping("g", b, a, (sum(c * y**i for i, c in enumerate(gc)),))
        argument, delta = (
            Fraction(rng.randint(-4, 4), 3),
            Fraction(rng.randint(-4, 4), 2),
        )
        primal = value(fc, argument)
        expected = (value(gc, primal), slope(gc, primal) * slope(fc, argument) * delta)
        assert realize(tangent(compose(f, g)), (argument, delta)) == expected
        assert realize(compose(tangent(f), tangent(g)), (argument, delta)) == expected


def test_multivariate_tangent_keeps_primal_and_direction_separate():
    plane = Space("plane", ("x", "y"))
    x, y = coordinates(plane)
    mapping = Mapping("mixed", plane, plane, (x * y, x**2 + 3 * y))
    # J(2,3) = [[3,2],[4,3]], applied to (5,7).
    assert realize(tangent(mapping), (2, 3, 5, 7)) == (6, 13, 29, 41)


def test_degenerate_legendre_candidate_fails_both_inverse_obligations():
    state, phase = Space("state", ("q", "v")), Space("phase", ("q", "p"))
    q, _ = coordinates(state)
    Q, p = coordinates(phase)
    singular = Mapping(
        "singular-fiber-derivative", state, phase, (q, constant(state, 0))
    )
    guess = Mapping("unjustified-inverse", phase, state, (Q, p))
    assert all(
        x["status"] == "not-an-identity" for x in verify_inverse(singular, guess)
    )


def test_one_sided_shape_compatibility_is_not_inverse_evidence():
    line = Space("line", ("x",))
    (x,) = coordinates(line)
    square = Mapping("square", line, line, (x**2,))
    assert all(
        x["status"] == "not-an-identity" for x in verify_inverse(square, identity(line))
    )


def test_damping_breaks_the_conservation_identity_without_inputs():
    state, scalar = Space("state", ("q", "v")), Space("scalar", ("value",))
    q, v = coordinates(state)
    field = Mapping("damped", state, state, (v, -q - v))
    rate = directional(q**2 + v**2, field)
    result = Mapping("rate", state, scalar, (rate,))
    assert (
        compare(result, Mapping("zero", state, scalar, (constant(state, 0),)))["status"]
        == "not-an-identity"
    )
    assert (
        compare(result, Mapping("dissipation", state, scalar, (-2 * v**2,)))["status"]
        == "identity"
    )


def test_stationarity_alone_does_not_imply_a_minimum():
    plane = Space("plane", ("x", "y"))
    x, y = coordinates(plane)
    saddle = x**2 - y**2
    gradient = Mapping(
        "stationary-test", plane, plane, (partial(saddle, "x"), partial(saddle, "y"))
    )
    assert realize(gradient, (0, 0)) == (0, 0)
    value = Mapping("value", plane, Space("scalar", ("value",)), (saddle,))
    assert realize(value, (0, Fraction(1, 100))) < realize(value, (0, 0))
    assert realize(value, (Fraction(1, 100), 0)) > realize(value, (0, 0))


def test_exact_truncation_retains_remainder_and_derivative_loss():
    plane = Space("perturbation", ("x", "epsilon"))
    x, epsilon = coordinates(plane)
    expansion = truncate((x + epsilon) ** 3, "epsilon", 1)
    assert expansion.retained == x**3 + 3 * x**2 * epsilon
    assert expansion.remainder == 3 * x * epsilon**2 + epsilon**3
    assert partial(expansion.remainder, "epsilon") == 6 * x * epsilon + 3 * epsilon**2
    assert expansion.original != expansion.retained


def test_description_is_detached_and_context_changes_invalidate_judgment():
    line = Space("line", ("x",))
    mapping = identity(line)
    detached = describe(mapping)
    detached["components"][0][0][1][0] = 99
    assert realize(mapping, (2,)) == (2,)
    with pytest.raises(FrozenInstanceError):
        mapping.identity = "changed"
    revised = identity(Space("line", ("x",), "2"))
    assert compare(mapping, mapping)["context"] != compare(revised, revised)["context"]


@pytest.mark.parametrize("bad", [True, 1.5, "1", None])
def test_exact_profile_refuses_silent_scalar_conversion(bad):
    line = Space("line", ("x",))
    with pytest.raises(Refused, match="exact Int or Fraction"):
        constant(line, bad)
    with pytest.raises(Refused, match="exact Int or Fraction"):
        realize(identity(line), (bad,))


@pytest.mark.parametrize(
    "construct",
    [
        lambda: Space("line", ["x"]),
        lambda: Space("line", ("x", "x")),
        lambda: Space("many", tuple(str(i) for i in range(9))),
        lambda: constant(Space("line", ("x",)), 2**256),
        lambda: coordinates(Space("line", ("x",)))[0] ** 13,
        lambda: Polynomial(Space("line", ("x",)), (((True,), Fraction(1)),)),
        lambda: Polynomial(Space("line", ("x",)), (((1,), Fraction(0)),)),
    ],
)
def test_closed_profile_refuses_malformed_or_over_capacity_descriptions(construct):
    with pytest.raises(Refused):
        construct()


def test_checking_and_transforming_do_not_request_realization(monkeypatch):
    import tools.reasoning_algebra as algebra

    def forbidden(*args):
        raise AssertionError("unexpected realization")

    monkeypatch.setattr(algebra, "realize", forbidden)
    assert all(x["status"] == "identity" for x in examples().values())


def test_cli_states_the_limits_of_all_input_free_examples():
    result = subprocess.run(
        [sys.executable, "-m", "tools.reasoning_examples"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    scope = json.loads(result.stdout)["scope"]
    assert scope["supplied_inputs"] is False and scope["solver_run"] is False
    assert scope["asymptotic_validity"] == "not-checked"
    assert scope["independent_replay"] == "not-implemented"
