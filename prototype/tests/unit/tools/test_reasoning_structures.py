"""Common ports do not erase domain laws or confer observation authority."""

from dataclasses import replace
from fractions import Fraction as F

import pytest

from tools import finite_inquiry as q
from tools import nomi_terms as n
from tools import reasoning_structures as s
from tools import scoped_terms as t


def function(text, owner="function"):
    return s.rational(n.parse(t.Source(owner, "1", text)))


def test_closed_function_composition_has_independent_arithmetic_meaning():
    first = function("(x, y) => x + y")
    second = function("(x) => x * x", "square")
    composed = s.compose(first, second)
    for x, y in ((F(2), F(-3)), (F(1, 2), F(1, 3))):
        assert t.realize(composed.description, (x, y)) == (x + y) ** 2
    assert composed.source == s.RationalPort(2)
    assert composed.identity != first.identity


def test_finite_composition_retains_exact_ports_and_independent_path_sum():
    prior, kernel, _ = q.example()
    described = s.stochastic(kernel)
    assert s.equivalent(s.compose(s.stochastic(q.identity_kernel(prior.space)), described), described)
    twice = s.compose(described, s.stochastic(q.identity_kernel(kernel.destination)))
    for i, row in enumerate(twice.description.rows):
        for k, value in enumerate(row):
            expected = sum(kernel.rows[i][j] * F(j == k) for j in range(2))
            assert value == expected
    stale = replace(kernel.destination, identity=t.Identity("outcomes", "new", "space"))
    with pytest.raises(t.Refused, match="matching"):
        s.compose(described, s.stochastic(q.identity_kernel(stale)))


def test_provider_mixing_and_forged_ports_are_refused():
    _, kernel, _ = q.example()
    with pytest.raises(t.Refused, match="matching"):
        s.compose(function("(x) => x"), s.stochastic(kernel))
    with pytest.raises(t.Refused, match="contract"):
        replace(function("(x) => x"), source=s.RationalPort(2))
    with pytest.raises(t.Refused, match="revision"):
        replace(function("(x) => x"), provider=replace(s.RATIONAL, equality="universal-proof"))
    with pytest.raises(t.Refused, match="callable"):
        s.rational(t.literal(1))


def test_source_programs_produce_a_finite_prediction_for_existing_inquiry():
    family = s.ProgramFamily((function("(x) => x", "line"), function("(x) => x * x", "square")))
    prediction = s.predict(family, (F(2),))
    assert prediction.outcomes == (F(2), F(4))
    assert prediction.kernel.rows == ((F(1), F(0)), (F(0), F(1)))
    prior = q.Measure(t.Identity("prior", "1", "measure"), family.space, (F(1, 2), F(1, 2)))
    objective = q.Objective(t.Identity("objective", "1", "loss"), family.space, family.space, ((F(0), F(1)), (F(1), F(0))))
    inquiry = q.query_value(prior, prediction.kernel, objective)
    assert inquiry.net_value == F(1, 2)
    assert q.verify_inquiry(prior, prediction.kernel, objective, inquiry)
    uninformative = s.predict(family, (F(1),))
    assert q.query_value(prior, uninformative.kernel, objective).net_value == 0


def test_family_contract_and_identity_are_content_bound():
    one = function("(x) => x", "same-owner")
    two = function("(x) => x + 1", "same-owner")
    assert one.identity != two.identity
    with pytest.raises(t.Refused, match="duplicate"):
        s.ProgramFamily((one, one))
    with pytest.raises(t.Refused, match="shared"):
        s.ProgramFamily((one, function("(x, y) => x + y")))
    view = s.describe(one)
    view["provider"]["laws"].append("world-truth")
    assert "world-truth" not in s.describe(one)["provider"]["laws"]
