"""Research navigation/shape checks, not foreign or target language conformance."""

import csv
import json
import re
from pathlib import Path

DOSSIER = Path("docs/research/data_workflows")
TARGETS = Path("docs/design/targets/research")
DOCUMENTS = [
    *sorted(DOSSIER.glob("*.md")),
    Path("docs/research/notation_atlas.md"),
    TARGETS / "README.md",
]


def test_research_extension_local_links_resolve():
    for document in DOCUMENTS:
        text = document.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", text):
            if target.startswith(("https:", "http:", "mailto:")):
                continue
            assert (document.parent / target).is_file(), (document, target)


def test_research_tables_have_consistent_cell_counts():
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


def test_research_target_modules_are_indexed_and_marked_unexecuted():
    index = (TARGETS / "README.md").read_text(encoding="utf-8")
    fixtures = sorted(TARGETS.glob("*.nomi"))
    assert fixtures
    for fixture in fixtures:
        header = "\n".join(fixture.read_text(encoding="utf-8").splitlines()[:8])
        assert "# Status: target-only research candidate;" in header
        assert "not runnable" in header
        assert f"]({fixture.name})" in index


def test_research_extension_routes_to_existing_cognitive_packet():
    registry = json.loads(Path("config/design_passes.json").read_text())
    packet = next(
        item for item in registry["passes"] if item["id"] == "cognitive-interfaces"
    )
    research = Path(packet["artifacts"]["research"])
    index = research.read_text(encoding="utf-8")
    assert "../data_workflows/README.md" in index
    assert "../notation_atlas.md" in index
