"""Input-free compositions for the foundational reasoning proposal."""

from fractions import Fraction
import json

from tools.reasoning_algebra import (
    Mapping,
    Space,
    compare,
    compose,
    constant,
    coordinates,
    directional,
    identity,
    partial,
    pullback,
    tangent,
    truncate,
    verify_inverse,
)


def examples():
    scalar = Space("scalar", ("value",))
    line = Space("configuration", ("q",))
    other = Space("intermediate", ("q",))
    (q,) = coordinates(line)
    (r,) = coordinates(other)
    f = Mapping("quadratic", line, other, (q**2 + q,))
    g = Mapping("cubic", other, scalar, (r**3,))
    results = {
        "chain-rule": compare(tangent(compose(f, g)), compose(tangent(f), tangent(g)))
    }

    # An explicit translation flow, with time carried as an ordinary parameter.
    timed = Space("timed-configuration", ("q", "t"))
    x, t = coordinates(timed)
    flow = Mapping("translation-flow", timed, line, (x + t,))
    times = Space("two-times", ("q", "s", "t"))
    x, s, t = coordinates(times)
    after_first = Mapping("advance-then-retain-time", times, timed, (x + s, t))
    together = Mapping("advance-by-total-time", times, line, (x + s + t,))
    results["flow-composition"] = compare(compose(after_first, flow), together)
    initial = Mapping("zero-time", line, timed, (q, constant(line, 0)))
    results["flow-initial"] = compare(compose(initial, flow), identity(line))

    # Normalized oscillator: m = 2, k = 2. No units or solver are inferred.
    state = Space("position-velocity", ("q", "v"))
    q, v = coordinates(state)
    lagrangian = v**2 - q**2
    field = Mapping("oscillator-field", state, state, (v, -q))
    energy = v**2 + q**2
    results["energy-conservation"] = compare(
        Mapping("energy-rate", state, scalar, (directional(energy, field),)),
        Mapping("zero-rate", state, scalar, (constant(state, 0),)),
    )

    # Preserve meaning under a supplied reversible coordinate description.
    chart = Space("scaled-position-velocity", ("q", "v"))
    Q, V = coordinates(chart)
    change = Mapping("scale-coordinates", state, chart, (2 * q, 2 * v))
    results["coordinate-energy"] = compare(
        Mapping("energy", state, scalar, (energy,)),
        compose(
            change,
            Mapping(
                "energy-in-scaled-chart",
                chart,
                scalar,
                (Fraction(1, 4) * (Q**2 + V**2),),
            ),
        ),
    )

    # Euler-Lagrange local residual from partials and a declared time derivation.
    jet = Space("local-path-jet", ("q", "v", "a"))
    x, velocity, acceleration = coordinates(jet)
    projection = Mapping("forget-acceleration", jet, state, (x, velocity))
    time_direction = Mapping(
        "declared-local-time-direction",
        jet,
        jet,
        (velocity, acceleration, constant(jet, 0)),
    )
    residual = directional(
        pullback(partial(lagrangian, "v"), projection), time_direction
    ) - pullback(partial(lagrangian, "q"), projection)
    results["euler-lagrange-residual"] = compare(
        Mapping("derived-residual", jet, scalar, (residual,)),
        Mapping("expected-residual", jet, scalar, (2 * (acceleration + x),)),
    )

    # A finite discrete path functional, not a continuum variational engine.
    paths = Space("three-point-path", ("q0", "q1", "q2"))
    q0, q1, q2 = coordinates(paths)
    action = (q1 - q0) ** 2 + (q2 - q1) ** 2
    endpoints = Space("fixed-endpoints", ("left", "right"))
    left, right = coordinates(endpoints)
    straight = Mapping(
        "stationary-candidate",
        endpoints,
        paths,
        (left, Fraction(1, 2) * (left + right), right),
    )
    results["discrete-stationarity"] = compare(
        compose(
            straight,
            Mapping(
                "interior-action-variation", paths, scalar, (partial(action, "q1"),)
            ),
        ),
        Mapping(
            "zero-interior-variation", endpoints, scalar, (constant(endpoints, 0),)
        ),
    )

    # Supply the inverse, check both sides, then construct H = p*v - L.
    phase = Space("position-momentum", ("q", "p"))
    Q, p = coordinates(phase)
    legendre = Mapping("fiber-derivative", state, phase, (q, partial(lagrangian, "v")))
    inverse = Mapping(
        "supplied-velocity-reconstruction", phase, state, (Q, Fraction(1, 2) * p)
    )
    forward, backward = verify_inverse(legendre, inverse)
    results["legendre-inverse-left"] = forward
    results["legendre-inverse-right"] = backward
    hamiltonian = p * inverse.components[1] - pullback(lagrangian, inverse)
    results["hamiltonian"] = compare(
        Mapping("derived-H", phase, scalar, (hamiltonian,)),
        Mapping("expected-H", phase, scalar, (Fraction(1, 4) * p**2 + Q**2,)),
    )

    # Translate in q: free L is invariant, and momentum is constant on its field.
    extended = Space("translated-state", ("q", "v", "s"))
    x, velocity, shift = coordinates(extended)
    translated = Mapping("translation", extended, state, (x + shift, velocity))
    original = Mapping("projection", extended, state, (x, velocity))
    free_lagrangian = Mapping("free-L", state, scalar, (v**2,))
    results["translation-symmetry"] = compare(
        compose(translated, free_lagrangian), compose(original, free_lagrangian)
    )
    free_field = Mapping("free-field", state, state, (v, constant(state, 0)))
    results["momentum-conservation"] = compare(
        Mapping("momentum-rate", state, scalar, (directional(2 * v, free_field),)),
        Mapping("zero-momentum-rate", state, scalar, (constant(state, 0),)),
    )

    # Exact remainder retained; not an asymptotic or numerical error certificate.
    perturbations = Space("perturbed-coordinate", ("x", "epsilon"))
    x, epsilon = coordinates(perturbations)
    expansion = truncate((x + epsilon) ** 3, "epsilon", 1)
    results["perturbation-reconstruction"] = compare(
        Mapping("full", perturbations, scalar, (expansion.original,)),
        Mapping(
            "reconstructed",
            perturbations,
            scalar,
            (expansion.retained + expansion.remainder,),
        ),
    )
    results["perturbation-remainder"] = compare(
        Mapping("remainder", perturbations, scalar, (expansion.remainder,)),
        Mapping(
            "expected-remainder",
            perturbations,
            scalar,
            (3 * x * epsilon**2 + epsilon**3,),
        ),
    )
    return results


def main():
    report = {
        "profile": "scoped-rational-polynomial-maps-v1",
        "judgments": examples(),
        "scope": {
            "supplied_inputs": False,
            "solver_run": False,
            "continuum_action": "not-checked",
            "asymptotic_validity": "not-checked",
            "independent_replay": "not-implemented",
            "physical_validity": "not-established",
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return (
        0 if all(x["status"] == "identity" for x in report["judgments"].values()) else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
