"""Finite messaging discriminators and honest capture routing, not broker conformance."""

from datetime import date
from itertools import combinations
import json
from pathlib import Path
import re
import runpy
import subprocess
import sys
from urllib.parse import unquote, urlsplit

import pytest


ROOT = Path(__file__).resolve().parents[4]
DOSSIER = ROOT / "docs/research/data_workflows"
SCRIPT = DOSSIER / "probe_messaging.py"
CAPTURE = DOSSIER / "messaging_probe_results.json"
TARGET = ROOT / "docs/design/targets/research/messaging.nomi"


@pytest.fixture(scope="module")
def model():
    return runpy.run_path(str(SCRIPT))


def test_frontier_never_passes_an_unresolved_delivered_obligation(model):
    delivered = [10, 12, 13]
    for size in range(4):
        for completed in combinations(delivered, size):
            position = model["frontier"](delivered, completed, 14)
            assert all(p in completed for p in delivered if p < position)
            assert position == next((p for p in delivered if p not in completed), 14)
    assert model["frontier"](delivered, [10, 12], 14) == 13
    assert model["frontier"]([], [], 14) == 14


@pytest.mark.parametrize(
    ("delivered", "completed", "end"),
    [
        ([12, 10], [], 14),
        ([10, 10], [], 14),
        ([10], [11], 14),
        ([10], [], 10),
        ([-1], [], 14),
        ([True], [], 14),
        ([10], [10.0], 14),
        ([], [], -1),
        ([], [], True),
    ],
)
def test_frontier_rejects_malformed_or_foreign_positions(
    model, delivered, completed, end
):
    with pytest.raises(ValueError):
        model["frontier"](delivered, completed, end)


def test_atomic_local_commit_keeps_duplicate_effect_and_outbox_together(model):
    state = {"inbox": {}, "effects": 0, "outbox": []}
    apply = model["inbox_attempt"]
    assert apply(state, "a", "e", "reserve", 8, 8) == "committed"
    assert apply(state, "a", "e", "reserve", 8, 8) == "duplicate"
    assert state == {
        "inbox": {("a", "e"): "reserve"},
        "effects": 1,
        "outbox": [("a", "e")],
    }


def test_stale_owner_and_conflicting_payload_do_not_mutate_state(model):
    state = {"inbox": {}, "effects": 0, "outbox": []}
    apply = model["inbox_attempt"]
    assert apply(state, "a", "e", "reserve", 7, 8) == "stale_owner"
    assert not state["inbox"]
    assert apply(state, "a", "e", "reserve", 8, 8) == "committed"
    assert apply(state, "a", "e", "release", 8, 8) == "payload_conflict"
    assert state["effects"] == 1 and state["inbox"][("a", "e")] == "reserve"
    assert apply(state, "b", "e", "reserve", 8, 8) == "committed"
    assert state["effects"] == 2


def test_each_non_atomic_crash_cut_names_loss_or_duplicate(model):
    trace = model["crash_cuts"]()
    assert [
        case["effects_after_retry"] for case in trace["non_atomic_effect_first"]
    ] == [1, 2, 1, 1]
    assert trace["ack_first_crash"] == {"delivery_removed": True, "effect_done": False}
    assert trace["mark_first_crash"] == {
        "duplicate_suppressed": True,
        "effect_done": False,
    }


def test_retention_boundary_and_relay_retry_do_not_promise_single_effect(model):
    assert model["dedup_expiry"]()["total_effects"] == [1, 1, 2, 2]
    observation = model["outbox_response_loss"]()
    assert observation["local_intents"] == 1
    assert observation["accepted_publications"] == ["event-1", "event-1"]


def test_partition_order_and_replay_preserve_distinct_laws(model):
    assert {item["value"] for item in model["partition_order"]()["outcomes"]} == {0, 1}
    replay = model["replay_and_edition"]()
    assert replay["pure_projection"] == [4, 4]
    assert replay["effectful_notifications_after_two_runs"] == 6
    assert replay["compatible"] is False


@pytest.mark.parametrize(
    ("active", "queued", "payload_bytes", "accepted"),
    [
        (1, 2, [2, 2, 2], True),
        (1, 3, [1, 1, 1, 1], False),
        (1, 1, [1, 9], False),
        (0, 0, [], True),
    ],
)
def test_budget_checks_waiting_count_and_bytes_not_only_workers(
    model, active, queued, payload_bytes, accepted
):
    assert model["budget_admits"](active, queued, payload_bytes, 3, 6) is accepted


@pytest.mark.parametrize("invalid", [-1, True, 1.5])
def test_budget_units_reject_negative_boolean_and_fractional_usage(model, invalid):
    with pytest.raises(ValueError):
        model["budget_admits"](1, 0, [invalid], 3, 6)


@pytest.mark.parametrize("payloads", [[], [2, 3]])
def test_incomplete_or_extra_payload_accounting_cannot_claim_a_byte_bound(
    model, payloads
):
    with pytest.raises(ValueError, match="per admitted item"):
        model["budget_admits"](1, 0, payloads, 3, 6)


def test_bounded_deadlock_unknown_observation_and_revoked_authority_remain_distinct(
    model,
):
    assert model["budgets_and_feedback"]()["feedback"]["enabled_next_actions"] == 0
    facts = model["observation_and_authority"]()
    assert facts["remote_truth"] == "accepted"
    assert facts["local_observation_after_cancel"] == "unknown"
    assert facts["replayed_command_authorized"] is False


def test_checked_capture_matches_outcomes_without_becoming_execution_evidence(model):
    before = CAPTURE.read_bytes()
    model["verify_capture"](CAPTURE)
    assert CAPTURE.read_bytes() == before
    captured = json.loads(before)
    assert len(captured["probes"]) == 10
    assert all(value is False for value in captured["execution"].values())
    assert all(probe["limit"] for probe in captured["probes"])


@pytest.mark.parametrize(
    "mutation", ["outcome", "scope", "type", "date", "version", "extra"]
)
def test_capture_rejects_changed_outcomes_scope_types_and_provenance(
    model, tmp_path, mutation
):
    captured = model["report"](date(2026, 10, 4))
    if mutation == "outcome":
        captured["probes"][0]["end"] = 15
    elif mutation == "scope":
        captured["execution"]["broker"] = True
    elif mutation == "type":
        captured["execution"]["broker"] = 0
    elif mutation == "date":
        captured["observed_on"] = "not-a-date"
    elif mutation == "version":
        captured["environment"]["python"] = " "
    else:
        captured["environment"]["kafka"] = "4.1"
    path = tmp_path / "capture.json"
    path.write_text(json.dumps(captured), encoding="utf-8")
    before = path.read_bytes()
    with pytest.raises(ValueError):
        model["verify_capture"](path)
    assert path.read_bytes() == before


def test_historical_python_version_is_not_rewritten_or_treated_as_broker_evidence(
    model, tmp_path
):
    captured = model["report"](date(2026, 10, 4))
    captured["environment"]["python"] = "3.13.0"
    path = tmp_path / "capture.json"
    path.write_text(json.dumps(captured), encoding="utf-8")
    model["verify_capture"](path)
    assert json.loads(path.read_text())["environment"]["python"] == "3.13.0"


def test_duplicate_capture_fields_are_rejected_at_every_depth(model):
    with pytest.raises(ValueError, match="Duplicate"):
        json.loads(
            '{"execution":{"broker":false,"broker":true}}',
            object_pairs_hook=model["capture_object"],
        )


def test_cli_check_is_read_only_and_optimized_execution_is_rejected():
    before = CAPTURE.read_bytes()
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--check", str(CAPTURE)],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert completed.returncode == 0, completed.stderr
    assert CAPTURE.read_bytes() == before
    optimized = subprocess.run(
        [sys.executable, "-O", str(SCRIPT)], capture_output=True, text=True, cwd=ROOT
    )
    assert optimized.returncode != 0 and "assertions are required" in optimized.stderr


def test_dossier_links_resolve_and_target_is_not_a_supported_sample():
    chapter = DOSSIER / "messaging_and_events.md"
    text = chapter.read_text(encoding="utf-8")
    for link in re.findall(r"\]\(([^)]+)\)", text):
        parsed = urlsplit(link)
        if not parsed.scheme and parsed.path:
            assert (chapter.parent / unquote(parsed.path)).resolve().exists(), link
    assert "fictional lab APIs, not runnable" in TARGET.read_text()
    assert not (ROOT / "samples/messaging.nomi").exists()
    assert "](messaging.nomi)" in (TARGET.parent / "README.md").read_text()
    assert all(f"MSG{i}" in text for i in range(1, 7))
    assert all(f"ME{i:02}" in text for i in range(1, 25))


def test_registered_synthesis_routes_messaging_evidence_and_validation():
    packets = json.loads((ROOT / "config/design_passes.json").read_text())["passes"]
    owner = next(packet for packet in packets if packet["id"] == "language-coherence")
    assert "messaging" in owner["keywords"] and owner["status"] == "designing"
    assert any(
        "probe_messaging.py --check" in command for command in owner["validation"]
    )
    assert any(Path(__file__).name in command for command in owner["validation"])
