"""Research integrity and finite-model checks, not Nomi or human conformance."""

import csv
from datetime import date
import json
from pathlib import Path
import platform
import re
import runpy
import subprocess
import sys
import unicodedata
from urllib.parse import unquote, urlsplit

import pytest


ROOT = Path(__file__).resolve().parents[4]
DOSSIER = ROOT / "docs/research/interfaces"
SCRIPT = DOSSIER / "probe_interactions.py"
CAPTURE = DOSSIER / "probe_results.json"
DOCUMENTS = [
    *sorted(DOSSIER.glob("*.md")),
    ROOT / "docs/research/cognition.md",
    ROOT / "docs/design/interaction_model.md",
]


@pytest.fixture(scope="module")
def probe_module():
    return runpy.run_path(str(SCRIPT))


def check_capture(path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--check", str(path)],
        text=True,
        capture_output=True,
        cwd=ROOT,
    )


def test_finite_models_reproduce_captured_outcomes(probe_module):
    captured = json.loads(CAPTURE.read_text(encoding="utf-8"))
    fresh = json.loads(
        json.dumps(probe_module["report"](date.fromisoformat(captured["observed_on"])))
    )
    assert fresh["python_version"] == platform.python_version()
    assert fresh["unicode_version"] == unicodedata.unidata_version
    for field in ("python_version", "unicode_version"):
        captured.pop(field)
        fresh.pop(field)
    assert fresh == captured


def test_probe_cli_verifies_capture_without_rewriting_it():
    before = CAPTURE.read_bytes()
    completed = check_capture(CAPTURE)
    assert completed.returncode == 0, completed.stderr
    assert "Verified" in completed.stdout
    assert CAPTURE.read_bytes() == before


def test_probe_cli_requires_assertions_even_when_checking_a_capture():
    completed = subprocess.run(
        [sys.executable, "-O", str(SCRIPT), "--check", str(CAPTURE)],
        text=True,
        capture_output=True,
        cwd=ROOT,
    )
    assert completed.returncode != 0
    assert "probe assertions are required" in completed.stderr


def test_capture_check_compares_outcomes_across_reported_host_versions(tmp_path):
    captured = json.loads(CAPTURE.read_text(encoding="utf-8"))
    captured["python_version"] = "3.12.0"
    captured["unicode_version"] = "15.0.0"
    path = tmp_path / "different-host-metadata.json"
    path.write_text(json.dumps(captured), encoding="utf-8")
    completed = check_capture(path)
    assert completed.returncode == 0, completed.stderr
    assert "3.12.0" in completed.stdout and "15.0.0" in completed.stdout
    assert "current Python" in completed.stdout


@pytest.mark.parametrize("drift", ["result", "execution_scope"])
def test_capture_check_rejects_drift_without_rewriting_it(tmp_path, drift):
    captured = json.loads(CAPTURE.read_text(encoding="utf-8"))
    if drift == "result":
        captured["probes"][0]["candidate"]["identity_target"] = "cup"
    else:
        captured["nomi_execution"] = True
    path = tmp_path / "changed-capture.json"
    path.write_text(json.dumps(captured), encoding="utf-8")
    before = path.read_bytes()
    completed = check_capture(path)
    assert completed.returncode != 0
    assert "Capture differs" in completed.stderr
    assert path.read_bytes() == before


def test_atlas_and_probe_ids_are_ordered_unique_and_linked(probe_module):
    atlas = (DOSSIER / "edge_cases.md").read_text(encoding="utf-8")
    cases = re.findall(r"^\| (H\d+) \|", atlas, flags=re.MULTILINE)
    assert cases == [f"H{index:02d}" for index in range(1, len(cases) + 1)]
    assert cases
    families = re.findall(r"^## (\d+)\. ", atlas, flags=re.MULTILINE)
    assert families == [str(index) for index in range(1, len(families) + 1)]
    assert f"{len(cases)} pressure cases across {len(families)} families" in atlas

    probes = probe_module["PROBES"]
    ids = [probe_id for probe_id, _, _ in probes]
    assert ids == [f"P{index:02d}" for index in range(1, len(probes) + 1)]
    assert all(
        references and set(references) <= set(cases) for _, _, references in probes
    )
    captured = json.loads(CAPTURE.read_text(encoding="utf-8"))
    assert [probe["id"] for probe in captured["probes"]] == ids
    experiments = (DOSSIER / "experiments.md").read_text(encoding="utf-8")
    documented = re.findall(r"^\| (P\d+):", experiments, flags=re.MULTILINE)
    assert documented == ids
    assert f"{len(probes)} independent probes" in experiments


def test_composition_references_resolve_to_cases_probes_and_experiments(probe_module):
    atlas = (DOSSIER / "edge_cases.md").read_text(encoding="utf-8")
    composition = (DOSSIER / "composition_cases.md").read_text(encoding="utf-8")
    cases = set(re.findall(r"^\| (H\d+) \|", atlas, flags=re.MULTILINE))
    probes = {probe_id for probe_id, _, _ in probe_module["PROBES"]}
    compositions = re.findall(r"^## (C\d+)\. ", composition, flags=re.MULTILINE)
    assert compositions == [
        f"C{index:02d}" for index in range(1, len(compositions) + 1)
    ]
    experiments = re.findall(r"^\| (HX\d+) \|", composition, flags=re.MULTILINE)
    assert experiments == [f"HX{index}" for index in range(1, len(experiments) + 1)]
    assert set(re.findall(r"\bH\d+\b", composition)) <= cases
    assert set(re.findall(r"\bP\d+\b", composition)) <= probes
    assert set(re.findall(r"\bC\d+\b", composition)) <= set(compositions)
    assert set(re.findall(r"\bHX\d+\b", composition)) <= set(experiments)


def heading_anchors(document):
    counts = {}
    anchors = set()
    for line in document.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^#{1,6} (.+)$", line)
        if not match:
            continue
        slug = re.sub(r"[^\w -]", "", match[1].lower()).replace(" ", "-")
        count = counts.get(slug, 0)
        anchors.add(f"{slug}-{count}" if count else slug)
        counts[slug] = count + 1
    return anchors


def test_interaction_dossier_local_links_and_heading_anchors_resolve():
    for document in DOCUMENTS:
        text = document.read_text(encoding="utf-8")
        for reference in re.findall(r"\]\(([^)]+)\)", text):
            target = urlsplit(reference)
            if target.scheme or target.netloc:
                continue
            path = document.parent / unquote(target.path) if target.path else document
            assert path.is_file(), (document, reference)
            if target.fragment:
                assert unquote(target.fragment) in heading_anchors(path), (
                    document,
                    reference,
                )


def test_interaction_dossier_tables_have_consistent_cell_counts():
    for document in DOCUMENTS:
        width = None
        for line in document.read_text(encoding="utf-8").splitlines():
            if not line.startswith("| "):
                width = None
                continue
            cells = next(
                csv.reader(
                    [line], delimiter="|", escapechar="\\", quoting=csv.QUOTE_NONE
                )
            )[1:-1]
            if width is None:
                width = len(cells)
            assert len(cells) == width, (document, line)
