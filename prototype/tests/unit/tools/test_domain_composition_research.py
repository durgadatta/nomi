"""Bounded domain counterexamples and capture integrity, not Nomi conformance."""

import csv
from datetime import date
from fractions import Fraction
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
SCRIPT = DOSSIER / "probe_composition.py"
CAPTURE = DOSSIER / "composition_probe_results.json"
DOCUMENTS = [
    DOSSIER / "dependencies_and_time.md",
    DOSSIER / "ai_ml.md",
    DOSSIER / "composition_experiments.md",
    ROOT / "docs/research/domain_composition.md",
]


@pytest.fixture(scope="module")
def model():
    return runpy.run_path(str(SCRIPT))


def check_capture(path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--check", str(path)],
        text=True,
        capture_output=True,
        cwd=ROOT,
    )


def test_diamond_does_not_choose_one_sibling_order_or_accept_a_cycle(model):
    observation = model["dependency_order"]()
    assert observation["valid_orders"] == [
        ["source", "left", "right", "join"],
        ["source", "right", "left", "join"],
    ]
    assert observation["cycle_rejected"] is True


@pytest.mark.parametrize(
    ("valid_at", "known_at", "expected"),
    [
        (10, 1, [100]),
        (19, 2, [100]),
        (10, 3, [120]),
        (19, 100, [120]),
        (20, 100, []),
        (9, 100, []),
        (15, 0, []),
    ],
)
def test_temporal_queries_keep_validity_and_knowledge_bounds_separate(
    model,
    valid_at,
    known_at,
    expected,
):
    assert model["temporal_amount"](valid_at, known_at) == expected


@pytest.mark.parametrize(
    ("version", "error"), [("old", "expired_content"), ("unknown", "unknown_version")]
)
def test_historical_read_never_substitutes_latest_for_missing_content(
    model, version, error
):
    manifests = {"old": "expired", "latest": "retained"}
    blobs = {"retained": [120]}
    with pytest.raises(ValueError, match=error):
        model["read_snapshot"](manifests, blobs, version)
    assert model["read_snapshot"](manifests, blobs, "latest") == [120]


def test_signed_sum_law_does_not_supply_a_minimum_deletion_law(model):
    observation = model["change_algebra"]()
    assert observation["sum"] == {"before": 7, "delta": -2, "after": 5}
    assert observation["minimum"] == {
        "naive_subtraction": 0,
        "retained_alternatives": 5,
    }


@pytest.mark.parametrize("field", ["operation", "inputs", "schema", "profile"])
def test_cache_identity_includes_each_declared_fixture_dependency(model, field):
    context = {"operation": "sum-v1", "inputs": ["v1"], "schema": "s1", "profile": "p1"}
    changed = {**context, field: ["v2"] if field == "inputs" else "changed"}
    key = model["computation_key"](context)
    assert key != model["computation_key"](changed)
    assert key == model["computation_key"](dict(reversed(list(context.items()))))


def test_training_only_statistics_cannot_use_the_held_out_outlier(model):
    assert model["train_only_mean"]([1, 3]) == 2
    assert model["train_only_mean"]([1, 3, 100]) == Fraction(104, 3)
    assert model["train_only_mean"]([1, 3, 200]) == 68
    assert model["feature_availability"]()["available_at_original_prediction"] is False


def test_available_cache_does_not_bypass_current_supplied_read_policy(model):
    cache = {"key": "private-result"}
    with pytest.raises(ValueError, match="read_denied"):
        model["read_cached"](cache, "key", current_read_allowed=False)
    assert cache == {"key": "private-result"}
    assert (
        model["read_cached"](cache, "key", current_read_allowed=True)
        == "private-result"
    )


@pytest.mark.parametrize("missing", ["optimizer", "rng", "data_position", "step"])
def test_training_presence_contract_rejects_incomplete_checkpoint(model, missing):
    record = {field: "supplied" for field in model["TRAINING_FIELDS"]}
    del record[missing]
    assert model["missing_training_fields"](record) == [missing]


def test_axis_extent_and_reference_label_are_weaker_than_identity(model):
    axes = model["axis_identity"]()
    assert axes["extent_only_accepts"] is True
    assert axes["named_axis_contract_accepts"] is False
    references = model["reference_identity"]()
    assert references["resolved_before"] != references["resolved_after"]
    assert references["same_title_different_work_ids"] is True


def test_review_scope_and_current_grant_are_independent_required_facts(model):
    outcomes = model["publication_review"]()["outcomes"]
    assert len(outcomes) == 16
    accepted = [row for row in outcomes if row["candidate_accepts"]]
    assert len(accepted) == 1
    assert all(
        accepted[0][field]
        for field in (
            "payload_matches",
            "model_matches",
            "recipient_matches",
            "current_grant",
        )
    )


def test_capture_reproduces_outcomes_and_names_unperformed_execution(model):
    captured = json.loads(CAPTURE.read_text(encoding="utf-8"))
    current = model["report"](date.fromisoformat(captured["observed_on"]))
    for report in (captured, current):
        assert report["execution"] == {
            "nomi": False,
            "foreign_framework": False,
            "ml_engine": False,
            "device": False,
            "cloud": False,
            "human": False,
        }
        assert all(type(value) is bool for value in report["execution"].values())
        assert all(probe["limit"] for probe in report["probes"])

    def comparable(report):
        return json.dumps(
            {key: value for key, value in report.items() if key != "environment"},
            sort_keys=True,
        )

    assert comparable(captured) == comparable(current)


def test_check_mode_never_rewrites_capture():
    before = CAPTURE.read_bytes()
    completed = check_capture(CAPTURE)
    assert completed.returncode == 0, completed.stderr
    assert "Verified 13" in completed.stdout
    assert CAPTURE.read_bytes() == before


@pytest.mark.parametrize(
    "drift", ["outcome", "scope", "boolean_type", "environment_field"]
)
def test_check_rejects_drift_in_results_or_scope_without_writing(tmp_path, drift):
    captured = json.loads(CAPTURE.read_text(encoding="utf-8"))
    if drift == "outcome":
        captured["probes"][0]["valid_orders"] = []
    elif drift == "scope":
        captured["execution"]["ml_engine"] = True
    elif drift == "boolean_type":
        captured["execution"]["nomi"] = 0
    else:
        captured["environment"]["unreported_engine"] = "1.0"
    path = tmp_path / "drift.json"
    path.write_text(json.dumps(captured), encoding="utf-8")
    before = path.read_bytes()
    assert check_capture(path).returncode != 0
    assert path.read_bytes() == before


@pytest.mark.parametrize(
    "source",
    [
        '{"schema": 1, "schema": 2}',
        '{"nested": {"scope": false, "scope": true}}',
        "[]",
        "null",
    ],
)
def test_check_rejects_ambiguous_or_nonobject_capture(tmp_path, source):
    path = tmp_path / "malformed.json"
    path.write_text(source, encoding="utf-8")
    completed = check_capture(path)
    assert completed.returncode != 0
    assert "Cannot read capture" in completed.stderr


def test_historical_versions_are_provenance_not_expected_results(tmp_path):
    captured = json.loads(CAPTURE.read_text(encoding="utf-8"))
    captured["environment"] = {
        "python": "historical-python",
        "sqlite": "historical-sqlite",
    }
    path = tmp_path / "historical.json"
    path.write_text(json.dumps(captured), encoding="utf-8")
    assert check_capture(path).returncode == 0


@pytest.mark.parametrize(
    "environment", [["python", "sqlite"], None, "python", {"python": 1, "sqlite": "1"}]
)
def test_check_reports_malformed_environment_as_a_capture_error(tmp_path, environment):
    captured = json.loads(CAPTURE.read_text(encoding="utf-8"))
    captured["environment"] = environment
    path = tmp_path / "malformed-environment.json"
    path.write_text(json.dumps(captured), encoding="utf-8")
    completed = check_capture(path)
    assert completed.returncode != 0
    assert "Cannot read capture" in completed.stderr
    assert "Traceback" not in completed.stderr


def test_check_requires_assertions_and_separates_capture_write_mode(tmp_path):
    for args in (
        ["-O", str(SCRIPT), "--check", str(CAPTURE)],
        [str(SCRIPT), "--check", str(CAPTURE), "--output", str(tmp_path / "new.json")],
    ):
        completed = subprocess.run(
            [sys.executable, *args], capture_output=True, text=True, cwd=ROOT
        )
        assert completed.returncode != 0
    assert not (tmp_path / "new.json").exists()


def heading_anchors(text):
    headings = re.findall(r"^#{1,6} (.+)$", text, flags=re.MULTILINE)
    return {
        re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        for heading in headings
    }


def test_domain_research_links_and_anchors_resolve():
    for document in DOCUMENTS:
        for reference in re.findall(
            r"\]\(([^)]+)\)", document.read_text(encoding="utf-8")
        ):
            target = urlsplit(reference)
            if target.scheme or target.netloc:
                continue
            path = document.parent / unquote(target.path) if target.path else document
            assert path.is_file(), (document, reference)
            if target.fragment:
                assert unquote(target.fragment) in heading_anchors(
                    path.read_text(encoding="utf-8")
                ), (document, reference)


def test_domain_research_tables_have_consistent_cell_counts():
    for document in DOCUMENTS:
        width = None
        for line in document.read_text(encoding="utf-8").splitlines():
            if not line.startswith("| "):
                width = None
                continue
            structural = re.sub(
                r"`[^`]*`", lambda match: match.group().replace("|", ""), line
            )
            cells = next(
                csv.reader(
                    [structural], delimiter="|", escapechar="\\", quoting=csv.QUOTE_NONE
                )
            )[1:-1]
            if width is None:
                width = len(cells)
            assert len(cells) == width, (document, line)


def test_probes_reference_defined_experiments_and_targets_stay_aspirational(model):
    text = "\n".join(document.read_text(encoding="utf-8") for document in DOCUMENTS)
    experiments = set(re.findall(r"^\| ((?:DT|ML|DC)\d+) \|", text, flags=re.MULTILINE))
    for _, _, related in model["PROBES"]:
        assert set(related) <= experiments
    probe_rows = re.findall(
        r"^\| (CP\d+) \|",
        (DOSSIER / "composition_experiments.md").read_text(),
        re.MULTILINE,
    )
    assert probe_rows == [probe_id for probe_id, _, _ in model["PROBES"]]
    target = ROOT / "docs/design/targets/research/domain_layers.nomi"
    assert "fictional lab APIs, not runnable" in target.read_text().splitlines()[0]
    assert "](domain_layers.nomi)" in (target.parent / "README.md").read_text()
    assert not (ROOT / "samples/domain_layers.nomi").exists()
