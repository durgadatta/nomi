"""The full mechanism shares programs, finite kernels and qualified revisions."""

from fractions import Fraction as F

from tools import intelligence_loop as loop


def test_without_observation_workflow_only_proposes_and_keeps_ambiguity():
    report = loop.run()
    assert report["search"]["matches"] == 2
    assert report["before"]["plan"]["status"] == "propose-inquiry"
    assert len(report["before"]["plan"]["alternatives"]) == 2
    assert "after" not in report
    assert report["assumptions"]["world_actions"] == []
    assert not report["before"]["journal"]["reports"]


def test_supplied_observation_updates_beliefs_and_learning_then_stops():
    report = loop.run(observed=F(4))
    assert report["after"]["plan"]["estimate"]["posterior"]["masses"] == [
        {"numerator": 0, "denominator": 1}, {"numerator": 1, "denominator": 1},
    ]
    assert report["after"]["plan"]["status"] == "stop"
    assert report["revised_search"]["matches"] == 1
    assert report["before"]["plan"]["context"] != report["after"]["plan"]["context"]
    assert report["posterior_transport_to_new_family"] == "not-performed"


def test_unexpected_output_is_retained_and_requests_model_repair():
    report = loop.run(observed=F(3))
    assert report["after"]["plan"]["status"] == "needs-model-or-evidence-repair"
    assert report["after"]["plan"]["estimate"]["status"] == "impossible-under-model"
    assert report["after"]["plan"]["estimate"]["posterior"] is None
    assert report["supplied_observation"]["value"] == {"numerator": 3, "denominator": 1}
    assert report["revised_search"]["matches"] == 0
    assert report["after"]["journal"]["reports"]


def test_irrelevant_observation_does_not_reduce_hypothesis_ambiguity():
    report = loop.run(observed=F(1), at=F(1))
    assert report["revised_search"]["matches"] == 2
    assert report["after"]["plan"]["estimate"]["posterior"]["masses"] == [
        {"numerator": 1, "denominator": 2}, {"numerator": 1, "denominator": 2},
    ]
    assert report["after"]["plan"]["status"] == "propose-inquiry"
