"""Prepared linguistic stimuli and routing integrity, not comprehension or NLP tests."""

import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

import pytest


ROOT = Path(__file__).resolve().parents[4]
CHAPTER = ROOT / "docs/research/interfaces/natural_language.md"
CASES = CHAPTER.with_name("language_cases.json")
TARGET = ROOT / "docs/design/targets/research/natural_language.nomi"


def reject_duplicate_fields(pairs):
    fields = {}
    for key, value in pairs:
        if key in fields:
            raise ValueError(f"duplicate field: {key}")
        fields[key] = value
    return fields


@pytest.fixture(scope="module")
def dossier():
    return json.loads(
        CASES.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_fields
    )


@pytest.fixture(scope="module")
def cases(dossier):
    return {case["id"]: case for case in dossier["cases"]}


def test_study_is_unperformed_and_separates_facilitator_facts(dossier):
    assert dossier["schema"] == "nomi.research.natural-language-study.v1"
    assert dossier["status"] == "prepared_unperformed"
    for field in (
        "human_execution",
        "nomi_execution",
        "nlp_execution",
        "browser_execution",
    ):
        assert dossier[field] is False
    assert "not participant responses" in dossier["scope"]
    assert "facilitator-only" in dossier["presentation_rule"]
    assert "analyzed separately" in dossier["presentation_rule"]


@pytest.mark.parametrize("case_id", [f"N{i:02}" for i in range(1, 11)])
def test_each_case_names_facts_comparison_kind_and_incidents(cases, case_id):
    case = cases[case_id]
    assert case["kind"] in {
        "meaning_preserving",
        "ambiguity_control",
        "vocabulary_discovery",
    }
    assert case["prompt"].strip()
    assert set(case["variants"]) == {"A", "B"}
    assert all(
        isinstance(text, str) and text.strip() for text in case["variants"].values()
    )
    assert isinstance(case["visible_facts"], dict) and case["visible_facts"]
    assert isinstance(case["control_facts"], dict)
    assert isinstance(case["expected"], dict) and case["expected"]
    assert case["critical_incidents"]
    assert all(re.fullmatch(r"NL[1-6]", item) for item in case["experiments"])
    assert all(
        re.fullmatch(r"LN(0[1-9]|1[0-9]|20)", item) for item in case["edge_cases"]
    )


def test_case_ids_are_unique_and_all_forks_have_prepared_pressure(dossier):
    case_list = dossier["cases"]
    assert [case["id"] for case in case_list] == [f"N{i:02}" for i in range(1, 11)]
    assert {fork for case in case_list for fork in case["experiments"]} == {
        f"NL{i}" for i in range(1, 7)
    }
    assert len({case["id"] for case in case_list}) == len(case_list)


def test_role_fixture_holds_contract_constant_without_transferring(cases):
    case = cases["N01"]
    facts = case["visible_facts"]
    assert facts["parameter_order"] == ["amount_minor", "source", "destination"]
    for role in facts["parameter_order"]:
        assert case["expected"][role] == facts[role]
    assert facts["source"] != facts["destination"]
    assert case["expected"]["effect_occurred"] is False


def test_mixed_and_empty_quantifier_oracles_without_running_nomi(cases):
    case = cases["N02"]
    values = case["visible_facts"]["approval_values"]
    assert all(type(value) is bool for value in values)
    assert case["expected"]["not_all_approved"] is (not all(values))
    assert case["expected"]["all_not_approved"] is all(not value for value in values)
    assert case["expected"]["not_all_approved"] != case["expected"]["all_not_approved"]
    empty = cases["N03"]
    values = empty["visible_facts"]["approval_values"]
    assert not values and empty["visible_facts"]["business_requires_nonempty"] is True
    assert empty["expected"] == {
        "all_approved": all(values),
        "recipient_exists": bool(values),
        "eligible": bool(values) and all(values),
    }


@pytest.mark.parametrize("case_id", ["N04", "N05", "N06", "N10"])
def test_ambiguity_controls_never_fill_missing_intent_or_evidence(cases, case_id):
    case = cases[case_id]
    assert case["kind"] == "ambiguity_control"
    assert any(value == "not supplied" for value in case["control_facts"].values())
    if "execute" in case["expected"]:
        assert case["expected"]["execute"] is False
    else:
        assert case["expected"]["selection_justified"] is False


def test_changed_reference_and_support_do_not_supply_intent_or_authority(cases):
    referent = cases["N05"]
    assert (
        referent["visible_facts"]["selection_when_draft_started"]
        != referent["visible_facts"]["selection_now"]
    )
    assert referent["expected"]["clarification_needed"] is True
    modality = cases["N06"]
    assert modality["visible_facts"]["adapter_supports_publication"] is True
    assert modality["visible_facts"]["current_grant"] is False
    assert modality["expected"]["support_is_authority"] is False


def test_hidden_remote_truth_cannot_be_graded_as_observed_rejection(cases):
    case = cases["N07"]
    assert case["visible_facts"]["remote_response"] is None
    assert case["control_facts"]["remote_truth"] == "accepted"
    assert case["expected"]["remote_outcome_known"] is False
    assert case["expected"]["remote_rejection_established"] is False
    assert case["visible_facts"]["operation"] in case["expected"]["next"]


def test_alias_discovery_keeps_choices_without_rewriting_bindings(cases):
    case = cases["N08"]
    candidates = case["visible_facts"]["alias_candidates"]
    assert case["kind"] == "vocabulary_discovery"
    assert (
        len(candidates)
        == len(set(candidates))
        == case["expected"]["candidate_count"]
        == 2
    )
    assert case["expected"]["choice_needed"] is True
    assert case["expected"]["compiler_bindings_changed"] is False
    assert case["expected"]["execute"] is False


def test_locale_fixture_changes_labels_not_identity_or_target(cases):
    case = cases["N09"]
    facts = case["visible_facts"]
    assert facts["labels"]["en"] != facts["labels"]["fr"]
    assert set(facts["labels"]) == set(facts["accessible_names"])
    assert all(
        label in facts["accessible_names"][locale]
        for locale, label in facts["labels"].items()
    )
    for field in ("command_id", "target_report", "revision"):
        assert facts[field] == case["expected"][field]
    assert "not professionally validated" in facts["translation_status"]


def test_dossier_links_resolve_and_tables_have_consistent_columns():
    text = CHAPTER.read_text(encoding="utf-8")
    for link in re.findall(r"\]\(([^)]+)\)", text):
        parsed = urlsplit(link)
        if not parsed.scheme and parsed.path:
            assert (CHAPTER.parent / unquote(parsed.path)).resolve().exists(), link
    width = None
    for line in text.splitlines():
        if not line.startswith("|"):
            width = None
            continue
        cells = len(re.split(r"(?<!\\)\|", line)) - 2
        if width is None:
            width = cells
        assert cells == width, line
    assert all(f"LN{i:02}" in text for i in range(1, 21))
    assert all(f"NL{i}" in text for i in range(1, 7))


def test_target_is_fictional_with_explicit_suspension_review_and_authority():
    text = TARGET.read_text(encoding="utf-8")
    assert "fictional lab APIs, not runnable" in text
    assert "pub async func submit_reviewed" in text
    assert "return await commands.publish_current" in text
    assert "review=review, grant=grant" in text
    assert "Interpretation.NeedsClarification" in text
    assert "](natural_language.nomi)" in (TARGET.parent / "README.md").read_text()
    assert not (ROOT / "samples/natural_language.nomi").exists()


def test_cognitive_packet_routes_the_dossier_and_maintained_checks():
    packets = json.loads((ROOT / "config/design_passes.json").read_text())["passes"]
    packet = next(item for item in packets if item["id"] == "cognitive-interfaces")
    assert packet["status"] == "designing"
    assert "natural language" in packet["keywords"]
    assert any(Path(__file__).name in command for command in packet["validation"])
    for path in (
        "docs/research/interfaces/README.md",
        "docs/design/interaction_model.md",
        "docs/review/2026-09-30-cognitive-interfaces.md",
    ):
        assert "natural_language.md" in (ROOT / path).read_text()


@pytest.mark.parametrize("name", ["natural_language.nomi", "messaging.nomi"])
def test_recent_target_challengers_keep_the_canonical_match_arm_shape(name):
    text = (TARGET.parent / name).read_text()
    assert not re.search(r"^\s*case\s+", text, re.MULTILINE)
