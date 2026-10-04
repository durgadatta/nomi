"""Generic-operation counterexamples and evidence integrity, not conformance."""

import csv
from datetime import date
import json
from pathlib import Path
import re
import runpy
import subprocess
import sys
from urllib.parse import unquote, urlsplit

import pytest


ROOT = Path(__file__).resolve().parents[4]
RESEARCH = ROOT / "docs/research/generic_operations.md"
SCRIPT = ROOT / "docs/research/features/probe_generic_operations.py"
CAPTURE = SCRIPT.with_name("generic_probe_results.json")
TARGET = ROOT / "docs/design/targets/research/generic_operations.nomi"


@pytest.fixture(scope="module")
def model():
    return runpy.run_path(str(SCRIPT))


def check_capture(path, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--check", str(path), *args],
        text=True,
        capture_output=True,
        cwd=ROOT,
    )


def test_strict_map_fusion_preserves_values_but_not_failure_prefix(model):
    strict = model["map_trace"](fused=False)
    fused = model["map_trace"](fused=True)
    assert strict["values"] == fused["values"] == [3, 5, 7]
    assert strict["events"] == ["f:1", "f:2", "f:3", "g:2", "g:4", "g:6"]
    assert fused["events"] == ["f:1", "g:2", "f:2", "g:4", "f:3", "g:6"]
    assert model["map_trace"](fused=False, fail_at=2) == {
        "error": "first_failed",
        "events": ["f:1", "f:2"],
    }
    assert model["map_trace"](fused=True, fail_at=2) == {
        "error": "first_failed",
        "events": ["f:1", "g:2", "f:2"],
    }


def test_seed_direction_and_history_are_independent_reduction_contracts(model):
    observed = model["fold_and_scan"]()
    assert observed["left_subtract"] == 7
    assert observed["right_subtract"] == 9
    assert observed["empty_unseeded_error"] == "TypeError"
    assert observed["empty_seeded"] == 10
    assert observed["seeded_scan"] == [0, 1, 3]
    assert observed["empty_seeded_scan"] == [0]
    arithmetic = model["reassociation"]()
    assert arithmetic["subtraction"] == [4, 6]
    assert arithmetic["floating_addition"] == [1.0, 0.0]


def test_row_results_do_not_implicitly_stop_traversal(model):
    assert model["assess_rows"](fail_fast=False) == {
        "outcome": [("ok", 2), ("err", -1), ("ok", 6)],
        "invoked": [1, -1, 3],
    }
    assert model["assess_rows"](fail_fast=True) == {
        "outcome": ("err", -1),
        "invoked": [1, -1],
    }


def test_passthrough_reference_does_not_promise_unchanged_state_or_success(model):
    values = []
    assert model["tap"](values, lambda item: item.append(1)) is values
    assert values == [1]

    def fail(_):
        raise ValueError("observer_failed")

    with pytest.raises(ValueError, match="observer_failed"):
        model["tap"](values, fail)
    assert model["tap_outcomes"]()["events"] == ["observer"]


def test_lazy_construction_and_partial_demand_do_not_invoke_remaining_callbacks(model):
    observed = model["lazy_demand"]()
    assert observed["construction_calls"] == []
    assert observed["partial_calls"] == [1]
    assert observed["first"] == 2 and observed["remainder"] == [4, 6]
    assert observed["all_calls"] == [1, 2, 3]


def test_repeat_value_fresh_calls_and_state_iteration_differ(model):
    observed = model["repetition"]()
    assert observed["repeated_share_reference"] is True
    assert observed["fresh_share_reference"] is False
    assert observed["repeated_after_mutation"] == [[1], [1], [1]]
    assert observed["iteration_history"] == [1, 2, 4, 8]
    assert observed["zero_repeat"] == []


@pytest.mark.parametrize(
    ("step", "seed", "budget", "expected"),
    [
        (lambda x: x, 5, 8, {"reason": "criterion_satisfied", "value": 5, "steps": 1}),
        (
            lambda x: min(x + 1, 3),
            0,
            8,
            {"reason": "criterion_satisfied", "value": 3, "steps": 4},
        ),
        (lambda x: 1 - x, 0, 8, {"reason": "cycle", "value": 0, "steps": 2}),
        (lambda x: x + 1, 0, 3, {"reason": "budget_exhausted", "value": 3, "steps": 3}),
        (lambda x: x + 1, 5, 0, {"reason": "budget_exhausted", "value": 5, "steps": 0}),
    ],
)
def test_bounded_iteration_returns_specific_stopping_evidence(
    model, step, seed, budget, expected
):
    assert model["iterate_bounded"](step, seed, budget) == expected


def test_zero_iteration_never_invokes_step_or_test(model):
    def fail(*_):
        raise AssertionError("zero budget must not invoke callbacks")

    assert model["iterate_bounded"](fail, 7, 0, same=fail) == {
        "reason": "budget_exhausted",
        "value": 7,
        "steps": 0,
    }


@pytest.mark.parametrize("budget", [True, -1, 1.5, "1"])
def test_iteration_model_rejects_invalid_budget_before_step(model, budget):
    with pytest.raises(ValueError, match="nonnegative integer"):
        model["iterate_bounded"](lambda x: x + 1, 0, budget)


def test_iteration_model_does_not_silently_use_truthiness_or_noninteger_states(model):
    with pytest.raises(ValueError, match="Bool"):
        model["iterate_bounded"](lambda x: x + 1, 0, 3, same=lambda old, new: 1)
    with pytest.raises(ValueError, match="integer states"):
        model["iterate_bounded"](lambda x: "next", 0, 3)
    with pytest.raises(ValueError, match="integer states"):
        model["iterate_bounded"](lambda x: x, True, 3)
    assert model["stopping_policies"]()["loose_test"] == {
        "reason": "criterion_satisfied",
        "value": 1,
        "steps": 1,
    }


def test_cache_does_not_infer_captured_dependencies_or_observer_multiplicity(model):
    observed = model["caching_context"]()
    assert observed["initial_stale_direct"] == [4, 4, 20]
    assert observed["tap_outside_cache"] == [4, 4]
    assert observed["tap_inside_cache"] == [4]


def test_hash_equality_and_selected_codec_support_are_separate(model):
    observed = model["hash_eligibility"]()
    assert observed["equal_hashes"] is True and observed["equal_objects"] is False
    assert (
        observed["distinct_entries"] == 2 and observed["list_hash_error"] == "TypeError"
    )
    encoded = model["encoding_profiles"]()
    assert encoded["ordinary_encodings"][0] != encoded["ordinary_encodings"][1]
    assert encoded["sorted_key_encodings"][0] == encoded["sorted_key_encodings"][1]
    assert encoded["list_roundtrip_equal"] is True
    assert encoded["tuple_roundtrip_equal"] is False


def test_scan_history_requires_owned_snapshots_and_output_can_differ_from_state(model):
    observed = model["accumulated_state"]()
    assert observed["aliased_history"] == [[1, 2], [1, 2], [1, 2]]
    assert observed["copied_history"] == [[], [1], [1, 2]]
    assert observed["map_accum"] == {
        "final_state": 3,
        "emitted": ["total:1", "total:3"],
    }


def test_capture_reproduces_and_explicitly_bounds_execution(model):
    captured = json.loads(CAPTURE.read_text(encoding="utf-8"))
    current = model["report"](date.fromisoformat(captured["observed_on"]))
    assert model["comparable"](captured) == model["comparable"](current)
    assert len(captured["probes"]) == 12
    assert captured["execution"] == {
        "nomi": False,
        "foreign_library": False,
        "parallel_executor": False,
        "remote_service": False,
        "human": False,
    }
    assert all(type(value) is bool for value in captured["execution"].values())
    assert all(probe["limit"] for probe in captured["probes"])


def test_capture_check_never_writes_expected_evidence():
    before = CAPTURE.read_bytes()
    completed = check_capture(CAPTURE)
    assert completed.returncode == 0, completed.stderr
    assert "Verified 12" in completed.stdout
    assert CAPTURE.read_bytes() == before


@pytest.mark.parametrize("drift", ["outcome", "execution", "json_type", "extra_field"])
def test_capture_check_rejects_semantic_or_scope_drift_without_writing(tmp_path, drift):
    captured = json.loads(CAPTURE.read_text(encoding="utf-8"))
    if drift == "outcome":
        captured["probes"][0]["strict"]["values"] = []
    elif drift == "execution":
        captured["execution"]["nomi"] = True
    elif drift == "json_type":
        captured["execution"]["nomi"] = 0
    else:
        captured["unperformed_claim"] = True
    path = tmp_path / "drift.json"
    path.write_text(json.dumps(captured), encoding="utf-8")
    before = path.read_bytes()
    assert check_capture(path).returncode != 0
    assert path.read_bytes() == before


@pytest.mark.parametrize(
    "source",
    [
        '{"schema":1,"schema":2}',
        '{"nested":{"flag":false,"flag":true}}',
        "[]",
        "null",
        "{",
    ],
)
def test_capture_check_reports_ambiguous_or_malformed_json(tmp_path, source):
    path = tmp_path / "malformed.json"
    path.write_text(source, encoding="utf-8")
    before = path.read_bytes()
    completed = check_capture(path)
    assert completed.returncode != 0
    assert "Cannot read capture" in completed.stderr
    assert "Traceback" not in completed.stderr and path.read_bytes() == before


@pytest.mark.parametrize(
    "environment",
    [
        None,
        ["python"],
        {},
        {"python": 1},
        {"python": ""},
        {"python": "old", "extra": "1"},
    ],
)
def test_capture_check_validates_historical_environment_shape(tmp_path, environment):
    captured = json.loads(CAPTURE.read_text(encoding="utf-8"))
    captured["environment"] = environment
    path = tmp_path / "environment.json"
    path.write_text(json.dumps(captured), encoding="utf-8")
    completed = check_capture(path)
    assert completed.returncode != 0
    assert (
        "Cannot read capture" in completed.stderr
        and "Traceback" not in completed.stderr
    )


def test_historical_python_version_is_provenance_not_outcome(tmp_path):
    captured = json.loads(CAPTURE.read_text(encoding="utf-8"))
    captured["environment"]["python"] = "historical-version"
    path = tmp_path / "historical.json"
    path.write_text(json.dumps(captured), encoding="utf-8")
    assert check_capture(path).returncode == 0


def test_capture_modes_reject_optimization_and_generation_during_check(tmp_path):
    output = tmp_path / "new.json"
    for args in (
        ["-O", str(SCRIPT), "--check", str(CAPTURE)],
        [str(SCRIPT), "--check", str(CAPTURE), "--output", str(output)],
        [str(SCRIPT), "--check", str(CAPTURE), "--observed-on", "2026-10-04"],
    ):
        completed = subprocess.run(
            [sys.executable, *args], capture_output=True, text=True
        )
        assert completed.returncode != 0
    assert not output.exists()


def test_research_ids_links_tables_and_target_boundary_are_consistent(model):
    text = RESEARCH.read_text(encoding="utf-8")
    experiments = set(re.findall(r"^\| (GA\d+) \|", text, re.MULTILINE))
    assert experiments == {f"GA{number}" for number in range(1, 9)}
    probe_rows = re.findall(r"^\| (GP\d+) \|", text, re.MULTILINE)
    assert probe_rows == [name for name, _, _ in model["PROBES"]]
    for _, _, related in model["PROBES"]:
        assert set(related) <= experiments
    for reference in re.findall(r"\]\(([^)]+)\)", text):
        target = urlsplit(reference)
        if target.scheme or target.netloc:
            continue
        path = RESEARCH.parent / unquote(target.path) if target.path else RESEARCH
        assert path.is_file(), reference
        if target.fragment:
            anchors = {
                re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
                for heading in re.findall(
                    r"^#{1,6} (.+)$", path.read_text(), re.MULTILINE
                )
            }
            assert unquote(target.fragment) in anchors, reference
    width = None
    for line in text.splitlines():
        if not line.startswith("| "):
            width = None
            continue
        structural = re.sub(r"`[^`]*`", lambda m: m.group().replace("|", ""), line)
        cells = next(
            csv.reader(
                [structural], delimiter="|", escapechar="\\", quoting=csv.QUOTE_NONE
            )
        )[1:-1]
        if width is None:
            width = len(cells)
        assert len(cells) == width, line
    assert "not runnable or typechecked" in TARGET.read_text().splitlines()[0]
    assert "](generic_operations.nomi)" in (TARGET.parent / "README.md").read_text()
    assert not (ROOT / "samples/generic_operations.nomi").exists()
