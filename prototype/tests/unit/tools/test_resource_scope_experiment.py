import copy
import itertools
import json
import subprocess
import sys

import pytest

from tools.resource_scope_experiment import (
    FIXTURES,
    assess_escape,
    check_packet,
    load_cases,
    run_case,
)

PACKET = load_cases()


def test_registered_symbolic_expectations_match_both_candidates():
    results, failures = check_packet(PACKET)
    assert failures == []
    assert len(results) == 32


@pytest.mark.parametrize("case", PACKET["cases"], ids=lambda case: case["id"])
def test_release_runs_once_and_failed_enter_is_never_released(case):
    result = run_case(case)
    assert all(not active for active in result["leases_after"].values())
    for resource in case.get("resources", []):
        expected_count = int(resource["name"] in result["acquired"])
        assert result["trace"].count(f"close:{resource['name']}") == expected_count
    assert result["trace"][-1].startswith("observe:")


@pytest.mark.parametrize(
    "body,exit_kind",
    list(
        itertools.product(
            ["ok", "return", "break", "continue", "err", "panic", "cancel"],
            ["ok", "err", "panic", "cancel"],
        )
    ),
)
def test_all_exit_pairs_preserve_every_distinct_cause(body, exit_kind):
    case = {
        "id": "pair",
        "body": {"kind": body, "cause": "body"},
        "resources": [{"name": "reader", "exit": {"kind": exit_kind, "cause": "exit"}}],
    }
    result = run_case(case)
    outcome = result["outcome"]
    causes = ([outcome["primary"]["cause"]] if outcome["primary"] else []) + [
        i["cause"] for i in outcome["secondary"]
    ]
    expected = []
    if body in {"err", "panic", "cancel"}:
        expected.append("body")
    if exit_kind in {"err", "panic", "cancel"} and not (body == exit_kind == "cancel"):
        expected.append("exit")
    assert sorted(causes) == sorted(expected)
    assert result["trace"].count("close:reader") == 1
    if "panic" in (body, exit_kind):
        assert outcome["channel"] == "panic"
    elif "cancel" in (body, exit_kind):
        assert outcome["channel"] == "cancel"


def test_cleanup_failure_distinguishes_typed_result_from_out_of_band_envelope():
    case = next(c for c in PACKET["cases"] if c["id"] == "read-error-close-error")
    typed = run_case(case, "typed")["outcome"]
    envelope = run_case(case, "envelope")["outcome"]
    assert typed["channel"] == "result"
    assert envelope["channel"] == "scope-failure"
    assert typed["primary"] == envelope["primary"]
    assert typed["secondary"] == envelope["secondary"]


def test_static_escape_comparison_is_not_a_claim_of_lifetime_inference():
    for case in PACKET["escapes"]:
        for policy in ("static", "dynamic"):
            result = assess_escape(case, policy)
            assert [result["check"], result["use"]] == case["expected"][policy]


def test_close_failure_never_reactivates_lease():
    case = next(c for c in PACKET["cases"] if c["id"] == "successful-body-close-error")
    assert run_case(case)["leases_after"] == {"reader": False}


def test_fixture_mutation_is_detected_not_silently_accepted():
    packet = copy.deepcopy(PACKET)
    packet["cases"][0]["expected"]["causes"] = ["invented"]
    _, failures = check_packet(packet)
    assert any("cause mismatch" in failure for failure in failures)


def test_experiment_rejects_unknown_policy_and_outcome():
    with pytest.raises(ValueError, match="unknown cleanup candidate"):
        run_case(PACKET["cases"][0], "magic")
    case = copy.deepcopy(PACKET["cases"][0])
    case["body"]["kind"] = "magic"
    with pytest.raises(ValueError, match="unknown outcome"):
        run_case(case)
    with pytest.raises(ValueError, match="unknown escape policy"):
        assess_escape(PACKET["escapes"][0], "magic")


def test_experiment_rejects_duplicate_resources_and_schema_drift(tmp_path):
    case = copy.deepcopy(PACKET["cases"][0])
    case["resources"] *= 2
    with pytest.raises(ValueError, match="unique"):
        run_case(case)
    packet = json.loads(FIXTURES.read_text(encoding="utf-8"))
    packet["schema_version"] = 2
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(packet), encoding="utf-8")
    with pytest.raises(ValueError, match="schema version"):
        load_cases(path)


def test_diagnostic_uses_passive_runtime_record_without_claiming_source_analysis():
    case = next(c for c in PACKET["cases"] if c["id"] == "read-error-close-error")
    result = run_case(case)
    diagnostic = result["diagnostic"]
    assert diagnostic["phase"] == "design-experiment"
    assert diagnostic["span"] is None
    assert diagnostic["details"]["primary"]["cause"] == "read"
    assert diagnostic["details"]["secondary"][0]["cause"] == "close"


def test_json_cli_emits_valid_candidate_records():
    completed = subprocess.run(
        [sys.executable, "-m", "tools.resource_scope_experiment", "--json"],
        capture_output=True,
        text=True,
        check=True,
        cwd=FIXTURES.parents[3],
    )
    record = json.loads(completed.stdout)
    assert record["failures"] == []
    assert len(record["results"]) == 32
    assert len(record["escapes"]) == 14
