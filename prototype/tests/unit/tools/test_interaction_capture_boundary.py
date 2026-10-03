"""Boundary checks for a local research capture, not a Nomi JSON decoder."""

import json
from pathlib import Path
import runpy
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[4]
DOSSIER = ROOT / "docs/research/interfaces"
CAPTURE = DOSSIER / "probe_results.json"
SCRIPT = DOSSIER / "probe_interactions.py"


def verify(path, *extra):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--check", str(path), *extra],
        text=True,
        capture_output=True,
        cwd=ROOT,
    )


def write_capture(tmp_path, payload):
    path = tmp_path / "capture.json"
    path.write_text(payload, encoding="utf-8")
    return path


def test_capture_explicitly_excludes_people_and_execution_integrations():
    payload = json.loads(CAPTURE.read_text(encoding="utf-8"))
    for field in (
        "human_execution",
        "nomi_execution",
        "browser_execution",
        "device_execution",
        "foreign_service_execution",
    ):
        assert payload[field] is False


def test_study_fixture_also_has_unambiguous_object_fields():
    module = runpy.run_path(str(SCRIPT))
    payload = json.loads(
        (DOSSIER / "study_cases.json").read_text(encoding="utf-8"),
        object_pairs_hook=module["capture_object"],
    )
    assert payload["human_execution"] is False
    assert payload["status"] == "prepared_unperformed"


def test_primary_probe_index_reports_the_actual_probe_inventory():
    module = runpy.run_path(str(SCRIPT))
    count = len(module["PROBES"])
    index = (DOSSIER / "README.md").read_text(encoding="utf-8")
    assert f"[{count} executed local research probes](experiments.md)" in index


@pytest.mark.parametrize(
    "key,value", [("nomi_execution", True), ("python_version", "3.12.0")]
)
def test_duplicate_root_fields_are_rejected_even_if_the_last_value_matches(
    tmp_path, key, value
):
    original = CAPTURE.read_text(encoding="utf-8")
    prefix = f"{{{json.dumps(key)}: {json.dumps(value)},"
    path = write_capture(tmp_path, prefix + original[1:])
    before = path.read_bytes()
    completed = verify(path)
    assert completed.returncode != 0
    assert "Duplicate capture field" in completed.stderr
    assert path.read_bytes() == before


def test_nested_duplicate_fields_are_rejected_before_outcome_comparison(tmp_path):
    original = CAPTURE.read_text(encoding="utf-8")
    # Raw JSON is necessary here: a dict cannot represent repeated field names.
    duplicate = original.replace(
        '"identity_target": "tea"',
        '"identity_target": "cup", "identity_target": "tea"',
        1,
    )
    assert duplicate != original
    path = write_capture(tmp_path, duplicate)
    completed = verify(path)
    assert completed.returncode != 0
    assert "Duplicate capture field" in completed.stderr


@pytest.mark.parametrize("payload", ["[]", "{", "{}"])
def test_invalid_capture_has_a_diagnostic_and_is_never_rewritten(tmp_path, payload):
    path = write_capture(tmp_path, payload)
    before = path.read_bytes()
    completed = verify(path)
    assert completed.returncode != 0
    assert "Cannot read capture" in completed.stderr
    assert "Traceback" not in completed.stderr
    assert path.read_bytes() == before


@pytest.mark.parametrize("field", ["nomi_execution", "human_execution"])
def test_numeric_zero_cannot_impersonate_a_false_execution_flag(tmp_path, field):
    payload = json.loads(CAPTURE.read_text(encoding="utf-8"))
    payload[field] = 0
    completed = verify(write_capture(tmp_path, json.dumps(payload)))
    assert completed.returncode != 0
    assert "Capture differs" in completed.stderr


def test_check_and_write_modes_cannot_be_combined(tmp_path):
    output = tmp_path / "unexpected-output.json"
    completed = verify(CAPTURE, "--output", str(output))
    assert completed.returncode != 0
    assert not output.exists()


def test_object_order_and_whitespace_do_not_change_capture_outcomes(tmp_path):
    payload = json.loads(CAPTURE.read_text(encoding="utf-8"))
    reordered = {key: payload[key] for key in reversed(payload)}
    path = write_capture(tmp_path, json.dumps(reordered, separators=(",", ":")))
    completed = verify(path)
    assert completed.returncode == 0, completed.stderr
