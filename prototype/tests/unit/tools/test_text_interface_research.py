"""Text-interface research integrity, not Nomi or foreign-system conformance."""

import csv
from datetime import date
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[4]
DOSSIER = ROOT / "docs/research/dsls"
CHAPTER = DOSSIER / "text_as_interface.md"
EXPERIMENTS = DOSSIER / "experiments.md"
SCRIPT = DOSSIER / "probe_boundaries.py"
CAPTURE = DOSSIER / "probe_results.json"
TARGET = ROOT / "docs/design/targets/research/text_boundaries.nomi"
DOCUMENTS = [
    CHAPTER,
    EXPERIMENTS,
    DOSSIER / "README.md",
    DOSSIER / "strings_and_embedding.md",
    ROOT / "docs/research/languages/powershell.md",
    ROOT / "docs/design/interaction_model.md",
]


def test_text_boundary_capture_reproduces_without_foreign_execution():
    captured = json.loads(CAPTURE.read_text(encoding="utf-8"))
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--observed-on",
            captured["observed_on"],
        ],
        text=True,
        capture_output=True,
        cwd=ROOT,
        check=True,
    )
    observed = json.loads(completed.stdout)
    assert observed["environment"].keys() == captured["environment"].keys()
    assert all(
        isinstance(value, str) and value for value in captured["environment"].values()
    )
    # Historical host versions are provenance; changed outcomes still fail.
    assert json.dumps(
        {key: value for key, value in observed.items() if key != "environment"},
        sort_keys=True,
    ) == json.dumps(
        {key: value for key, value in captured.items() if key != "environment"},
        sort_keys=True,
    )
    assert len(captured["cases"]) == 18
    assert (
        captured["scope"]
        == "local host-library and original finite-model observations only"
    )
    assert captured["cases"]["posix_argv_serialization"]["executed"] is False
    assert captured["cases"]["destination_specific_encoding"]["executed"] is False
    assert (
        captured["cases"]["delimiter_collision"]["external_protocol_executed"]
        is False
    )
    assert (
        captured["cases"]["unicode_visible_structure"][
            "grapheme_segmentation_performed"
        ]
        is False
    )


def test_text_chapter_has_complete_candidate_vocabulary_and_experiments():
    text = CHAPTER.read_text(encoding="utf-8")
    vocabulary = {
        "display",
        "inspect",
        "format",
        "render",
        "encode",
        "decode",
        "serialize",
        "deserialize",
        "parse",
        "check",
        "bind",
        "quote",
        "escape",
        "normalize",
        "canonicalize",
        "read_text",
        "write_text",
        "load",
        "save",
        "import",
        "export",
        "convert",
    }
    documented = set(
        re.findall(r"^\| `([^`]+)`(?: / `[^`]+`)? \|", text, flags=re.MULTILINE)
    )
    assert vocabulary <= documented
    experiments = re.findall(r"^\| (T\d+) \|", text, flags=re.MULTILINE)
    assert experiments == [f"T{index}" for index in range(1, 11)]
    for ecosystem in (
        "Python",
        "Rust",
        "Go",
        "ECMAScript",
        "Swift",
        "Java",
        ".NET",
        "Elixir",
        "PowerShell",
        "Ansible",
        "GitHub Actions",
        "Kubernetes",
        "Ninja",
    ):
        assert ecosystem in text


def test_text_research_local_links_resolve():
    for document in DOCUMENTS:
        text = document.read_text(encoding="utf-8")
        for reference in re.findall(r"\]\(([^)]+)\)", text):
            target = urlsplit(reference)
            if target.scheme or target.netloc:
                continue
            path = document.parent / unquote(target.path) if target.path else document
            assert path.is_file(), (document, reference)


def test_text_research_tables_have_consistent_cell_counts():
    for document in DOCUMENTS:
        width = None
        for line in document.read_text(encoding="utf-8").splitlines():
            if not line.startswith("| "):
                width = None
                continue
            structural_line = re.sub(
                r"`[^`]*`", lambda match: match.group().replace("|", ""), line
            )
            cells = next(
                csv.reader(
                    [structural_line],
                    delimiter="|",
                    escapechar="\\",
                    quoting=csv.QUOTE_NONE,
                )
            )[1:-1]
            if width is None:
                width = len(cells)
            assert len(cells) == width, (document, line)


def test_text_pressure_target_is_indexed_and_explicitly_unimplemented():
    header = "\n".join(TARGET.read_text(encoding="utf-8").splitlines()[:8])
    index = (TARGET.parent / "README.md").read_text(encoding="utf-8")
    chapter = CHAPTER.read_text(encoding="utf-8")
    assert "# Status: target-only research candidate;" in header
    assert "not runnable" in header
    assert f"]({TARGET.name})" in index
    assert f"](../../design/targets/research/{TARGET.name})" in chapter


def test_cognitive_packet_routes_text_work_without_new_authority():
    registry = json.loads((ROOT / "config/design_passes.json").read_text())
    packet = next(
        item for item in registry["passes"] if item["id"] == "cognitive-interfaces"
    )
    assert date.fromisoformat(packet["last_reviewed"]) >= date(2026, 10, 3)
    assert {"text interface", "Unicode", "PowerShell"} <= set(packet["keywords"])
    research = ROOT / packet["artifacts"]["research"]
    assert "../dsls/text_as_interface.md" in research.read_text(encoding="utf-8")
    assert any("test_text_interface_research.py" in item for item in packet["validation"])
