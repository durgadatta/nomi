"""Cross-lab source identity and independent conceptual counterexamples."""

from fractions import Fraction as F

import pytest

from tools import finite_inquiry as q
from tools import intelligence_examples as examples
from tools.scoped_terms import Source


def test_source_hypotheses_feed_exact_inquiry_without_executing_measurement():
    prior, experiment, objective, result, artifacts = examples.scientific_inquiry()
    assert result.net_value == F(1, 8)
    assert q.verify_inquiry(prior, experiment, objective, result)
    assert [x.revision for x in prior.space.members] == [
        x["fingerprint"] for x in artifacts
    ]
    assert len({x["fingerprint"] for x in artifacts}) == 2


def test_changed_source_content_with_same_revision_invalidates_inquiry_basis():
    old = examples.scientific_inquiry()
    revised = examples.scientific_inquiry(
        (
            Source(
                "damped-mechanism",
                "1",
                "lambda position, velocity: -2 * position - 3 * velocity",
            ),
            Source(
                "undamped-mechanism", "1", "lambda position, velocity: -2 * position"
            ),
        )
    )
    assert old[0].space.members[0] != revised[0].space.members[0]
    assert old[0].space.members[1] == revised[0].space.members[1]
    with pytest.raises(q.Refused, match="stale"):
        q.verify_inquiry(*revised[:3], old[3])


def test_source_family_refuses_mixed_callable_contracts():
    with pytest.raises(q.Refused, match="shared checked"):
        examples.hypothesis_family(
            (
                Source("one", "1", "lambda x: x"),
                Source("two", "1", "lambda x, y: x + y"),
            )
        )


def test_causal_vectors_match_independently_executed_binary_assignments():
    vectors = examples.causal_comparison()
    worlds = tuple((x, y) for x in (0, 1) for y in (0, 1))

    def distribution(pairs):
        return tuple(F(pairs.count(world), 2) for world in worlds)

    # Execute the supplied structural equations, without finite kernel methods.
    forward, reverse, do_forward, do_reverse = [], [], [], []
    for u in (0, 1):
        x = u
        y = x
        forward.append((x, y))
        y = u
        x = y
        reverse.append((x, y))
        x = 0
        y = x
        do_forward.append((x, y))
        y = u
        x = 0
        do_reverse.append((x, y))
    assert vectors["forward_observed"] == distribution(forward)
    assert vectors["reverse_observed"] == distribution(reverse)
    assert vectors["forward_observed"] == vectors["reverse_observed"]
    assert vectors["forward_intervened"] == distribution(do_forward)
    assert vectors["reverse_intervened"] == distribution(do_reverse)
    assert sum(vectors["forward_intervened"][1::2]) == 0
    assert sum(vectors["reverse_intervened"][1::2]) == F(1, 2)


def test_example_fit_is_not_a_semantics_preserving_abstraction():
    result = examples.abstraction_comparison()
    assert result["fits_declared_examples"]
    assert result["counterexample_at_2"] == (F(4), F(2))
    assert result["replacement_refuted"]
    assert result["checked_beta_extraction"]
