"""Supplied study-fixture facts; no participants, graders, or interface execution."""

import json
from pathlib import Path
import re
import runpy

import pytest


ROOT = Path(__file__).resolve().parents[4]
DOSSIER = ROOT / "docs/research/interfaces"


@pytest.fixture(scope="module")
def study():
    return json.loads((DOSSIER / "study_cases.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def tasks(study):
    return {task["id"]: task for task in study["tasks"]}


def test_study_tasks_are_indexed_and_explicitly_unperformed(study):
    assert study["status"] == "prepared_unperformed"
    for field in ("human_execution", "nomi_execution", "browser_execution"):
        assert study[field] is False
    assert [task["id"] for task in study["tasks"]] == [
        f"U{index:02d}" for index in range(1, 8)
    ]
    document = (DOSSIER / "composition_cases.md").read_text(encoding="utf-8")
    assert re.findall(r"^\| (U\d+):", document, flags=re.MULTILINE) == [
        task["id"] for task in study["tasks"]
    ]
    assert "](study_cases.json)" in document
    assert {condition["id"] for condition in study["conditions"]} == {"A", "B"}
    assert all(
        condition["semantic_contract"] == condition["command_contract"] == "shared"
        for condition in study["conditions"]
    )


def test_study_prediction_and_sort_controls_preserve_line_identity(tasks):
    prediction = tasks["U01"]
    inputs = prediction["provided"]
    before = sum(
        line["quantity"] * line["unit_price_minor"] for line in inputs["lines"]
    )
    totals = {
        line["id"]: (
            inputs["change"]["quantity"]
            if line["id"] == inputs["change"]["id"]
            else line["quantity"]
        )
        * line["unit_price_minor"]
        for line in inputs["lines"]
    }
    assert prediction["expected"] == {
        "before_total": before,
        "after_line_totals": totals,
        "after_total": sum(totals.values()),
    }
    sorted_task = tasks["U03"]
    provided = sorted_task["provided"]
    after = dict(provided["before_quantities"])
    after[provided["selected_id"]] = provided["quantity"]
    assert provided["displayed_ids"][0] != provided["selected_id"]
    assert sorted_task["expected"]["after_quantities"] == after


def test_study_draft_control_agrees_with_its_named_finite_probe(tasks):
    module = runpy.run_path(str(DOSSIER / "probe_interactions.py"))
    history = module["draft_commit"]()["candidate"]
    task = tasks["U02"]
    assert task["provided"]["raw_drafts"] == [step["raw_draft"] for step in history]
    assert task["expected"]["raw_drafts_retained"] == task["provided"]["raw_drafts"]
    assert task["expected"]["quantities_after_attempted_commit"] == [
        step["committed_quantity"] for step in history
    ]
    assert task["expected"]["revisions_after_attempted_commit"] == [
        step["revision"] for step in history
    ]


def test_history_control_preserves_the_same_counter_in_different_histories(tasks):
    task = tasks["U04"]
    old = task["provided"]["prepared_for"]
    current = task["provided"]["current"]
    assert old["revision"] == current["revision"]
    assert old["incarnation"] != current["incarnation"]
    assert task["expected"] == {
        "commit": False,
        "reason": "different_history",
        "current_model_unchanged": True,
    }


def test_unknown_outcome_controls_keep_internal_facts_out_of_visible_evidence(tasks):
    module = runpy.run_path(str(DOSSIER / "probe_interactions.py"))
    probe = module["observationally_indistinguishable_outcomes"]()
    task = tasks["U05"]
    assert (
        task["provided"]["publication_observation"]
        == probe["candidate"]["visible_observation"]
    )
    worlds = task["facilitator_only"]["compatible_worlds"]
    assert [world["action_count"] for world in worlds] == [0, 1]
    assert task["expected"]["remote_action_count"] == "unknown"
    assert task["expected"]["compatible_counts_in_supplied_worlds"] == [0, 1]
    assert "action_count" not in json.dumps(task["provided"])
    assert task["provided"]["reviewed_action"] != task["provided"]["changed_action"]
    assert task["expected"]["changed_action_review_matches"] is False


def test_partial_and_complete_trace_controls_have_distinct_evidence(tasks):
    task = tasks["U06"]
    for name, record in task["provided"].items():
        expected = task["expected"][name]
        shown = record["trace_shown"]
        assert len({event["id"] for event in shown}) == len(shown)
        omitted = record["trace_total"] - len(shown)
        assert expected["execution_complete"] == record["execution_complete"]
        assert expected["omitted"] == omitted
        assert expected["trace_complete"] == (omitted == 0)
        if omitted:
            assert expected["all_failure_count"] == "unknown"
        else:
            assert expected["all_failure_count"] == sum(
                event["kind"] == "handled_failure" for event in shown
            )
    assert (
        task["provided"]["partial"]["trace_shown"]
        == task["provided"]["complete"]["trace_shown"][:3]
    )


def test_transfer_control_exposes_the_domain_decision_before_arithmetic(tasks):
    task = tasks["U07"]
    values = task["provided"]["totals"]
    assert len({value["currency"] for value in values}) == 2
    assert task["provided"]["conversion_policy"] is None
    assert task["expected"]["unqualified_sum_allowed"] is False
    assert task["expected"]["arithmetic_sum_without_domain_meaning"] == sum(
        value["minor_units"] for value in values
    )


def test_study_references_resolve_to_registered_composition_and_probe_cases(study):
    atlas = (DOSSIER / "edge_cases.md").read_text(encoding="utf-8")
    composition = (DOSSIER / "composition_cases.md").read_text(encoding="utf-8")
    module = runpy.run_path(str(DOSSIER / "probe_interactions.py"))
    atlas_ids = set(re.findall(r"^\| (H\d+) \|", atlas, flags=re.MULTILINE))
    composition_ids = set(re.findall(r"^## (C\d+)\. ", composition, flags=re.MULTILINE))
    probe_ids = {probe_id for probe_id, _, _ in module["PROBES"]}
    for task in study["tasks"]:
        assert set(task["atlas_cases"]) <= atlas_ids
        assert set(task["composition_cases"]) <= composition_ids
        assert set(task["probe_ids"]) <= probe_ids
        assert task["prompt"] and task["provided"] and task["expected"]
        assert task["critical_incidents"]
