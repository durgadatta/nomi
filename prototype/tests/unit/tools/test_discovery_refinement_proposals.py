"""Checked transport proposals retain the active journal and withdrawal basis."""

from fractions import Fraction as F

from tools import intelligence_loop as loop


def test_discovery_checks_a_restriction_without_publishing_a_new_active_prior():
    result = loop.run(observed=F(4))
    proposal = result["refinement_proposal"]
    assert proposal["assessment"]["status"] == "support-preserving"
    assert proposal["assessment"]["transported"]["masses"] == [{"numerator": 1, "denominator": 1}]
    assert proposal["basis_journal"] == result["after"]["plan"]["estimate"]["context"]
    assert proposal["publication"] == "not-performed"
    assert result["after"]["journal"]["prior"]["masses"] == [
        {"numerator": 1, "denominator": 2}, {"numerator": 1, "denominator": 2},
    ]


def test_impossible_evidence_does_not_propose_an_empty_or_fabricated_model():
    result = loop.run(observed=F(3))
    assert result["refinement_proposal"]["status"] == "no-supported-refinement"
    assert "assessment" not in result["refinement_proposal"]
