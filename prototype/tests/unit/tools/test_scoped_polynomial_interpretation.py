"""Source/constructor/symbolic structures compose without numeric samples."""

from dataclasses import replace
from fractions import Fraction as F

import pytest

from tools import nomi_terms as n
from tools import reasoning_algebra as algebra
from tools import reasoning_structures as s
from tools import scoped_polynomials as p
from tools import scoped_terms as t


def function(code, owner="function"):
    return s.rational(n.parse(t.Source(owner, "1", code)))


def test_scientific_source_has_exact_coefficients_and_a_formal_tangent():
    source = function("(position, velocity) => -2 * position - velocity")
    mapping = p.project(source).mapping
    assert mapping.components[0].terms == (((0, 1), F(-1)), ((1, 0), F(-2)))
    tangent = algebra.tangent(mapping)
    assert tangent.components[1].terms == (((0, 0, 0, 1), F(-1)), ((0, 0, 1, 0), F(-2)))


def test_interpretation_preserves_composition_and_tangent_chain_law():
    first = function("(x) => x * x")
    second = function("(x) => x + 3", "translate")
    projected = p.project(s.compose(first, second)).mapping
    composed = algebra.compose(p.project(first).mapping, p.project(second).mapping)
    assert algebra.compare(projected, composed)["status"] == "identity"
    assert algebra.compare(algebra.tangent(projected), algebra.compose(algebra.tangent(p.project(first).mapping), algebra.tangent(p.project(second).mapping)))["status"] == "identity"


def test_explicit_polynomial_interpretation_establishes_more_than_alpha_equality():
    first = function("(x) => x + 0")
    second = function("(y) => y", "identity")
    assert not s.equivalent(first, second)
    assert algebra.compare(p.project(first).mapping, p.project(second).mapping)["status"] == "identity"
    square = function("(x) => x * x", "square")
    assert algebra.compare(p.project(square).mapping, p.project(second).mapping)["status"] == "not-an-identity"


def test_nested_pure_applications_keep_bound_owners_and_source_context():
    source = function("(x) => ((y) => y * y)(x + 1)")
    projection = p.project(source)
    assert projection.mapping.components[0].terms == (((0,), F(1)), ((1,), F(2)), ((2,), F(1)))
    changed = function("(x) => ((y) => y * y)(x + 2)")
    assert projection.context != p.project(changed).context
    with pytest.raises(t.Refused, match="stale"):
        p.verify(changed, projection)


def test_reduction_and_polynomial_capacity_do_not_become_false_identity():
    source = function("(x) => ((y) => y * y)(x + 1)")
    with pytest.raises(t.Refused, match="exhausted"):
        p.project(source, budget=1)
    with pytest.raises(algebra.Refused, match="degree"):
        p.project(function("(x) => x*x*x*x*x*x*x*x*x*x*x*x*x"))


def test_independent_sympy_checks_source_meaning_and_derivative_and_rejects_forgery():
    sympy = pytest.importorskip("sympy")
    assert sympy.__version__ == "1.14.0"
    for code in ("(x) => ((x) => x * x)(x + 1)", "(position, velocity) => -2 * position - velocity"):
        source = function(code)
        projection = p.project(source)
        assert p.verify(source, projection)
        tangent = algebra.tangent(projection.mapping)
        assert p.verify_tangent(source, projection, tangent)
        wrong = replace(projection.mapping, components=(algebra.constant(projection.mapping.domain, 0),))
        with pytest.raises(t.Refused, match="replay"):
            p.verify(source, replace(projection, mapping=wrong))
        wrong_tangent = replace(tangent, components=(tangent.components[0], algebra.constant(tangent.domain, 0)))
        with pytest.raises(t.Refused, match="replay"):
            p.verify_tangent(source, projection, wrong_tangent)


@pytest.mark.parametrize("coefficient", [-3, -1, 0, 1, 2])
def test_independent_symbolic_replay_covers_cancellation_and_cross_terms(coefficient):
    pytest.importorskip("sympy")
    source = function(f"(x, y) => {coefficient} * x * y + x * x - y * y")
    projection = p.project(source)
    assert p.verify_tangent(source, projection, algebra.tangent(projection.mapping))


def test_invalid_provider_is_refused_before_coordinate_construction():
    with pytest.raises(t.Refused, match="rational"):
        p.project(None)


def test_induced_force_proposals_can_earn_an_independent_formal_identity():
    pytest.importorskip("sympy")
    from tools import program_search as search

    grammar = search.Grammar(t.Identity("force-learning", "1", "grammar"), 2, (F(-2),), ("sub", "mul"), 5)
    examples = tuple(search.Example(t.Identity("force-learning", "1", f"example:{i}"), inputs, output) for i, (inputs, output) in enumerate((
        ((F(1), F(0)), F(-2)), ((F(0), F(1)), F(-1)), ((F(2), F(-1)), F(-3)),
    )))
    source = function("(position, velocity) => -2 * position - velocity")
    target = p.project(source)
    assert p.verify(source, target)
    for proposal in search.search(search.Task(grammar, examples)).proposals:
        interpreted = p.project(proposal)
        assert p.verify(proposal, interpreted)
        assert algebra.compare(interpreted.mapping, target.mapping)["status"] == "identity"
