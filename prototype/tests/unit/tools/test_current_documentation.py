"""Current records remain usable without reconstructing project chronology."""

import json
from pathlib import Path
import re

import pytest

from scripts.check_doc_links import default_documents
from scripts.report_pytest_failures import annotations
from tools.design_passes import validate_bridge


ROOT = Path(__file__).resolve().parents[4]


def test_summary_and_single_history_are_part_of_default_navigation_checks():
    documents = default_documents(ROOT)
    assert ROOT / "DIGEST.md" in documents
    assert ROOT / "HISTORY.md" in documents


def test_current_bridges_do_not_accumulate_dated_session_sections():
    registry = json.loads((ROOT / "config/design_passes.json").read_text())
    for packet in registry["passes"]:
        path = ROOT / packet["artifacts"]["bridge"]
        assert not re.match(r"\d{4}-\d{2}-\d{2}", path.name)
        source = path.read_text()
        assert not re.search(
            r"^#{1,6} .*?(?:\d{4}-\d{2}-\d{2}|Retrospective|Receipt|Checkpoint)",
            source,
            re.MULTILINE,
        ), path


@pytest.mark.parametrize("empty", ["Current Evidence", "Open Gaps", "Validation", "Next Actions"])
def test_every_current_bridge_section_requires_its_own_content(empty):
    source = "\n\n".join(
        f"## {title}\n" + ("" if title == empty else "Current scoped fact.")
        for title in ["Current Evidence", "Open Gaps", "Validation", "Next Actions"]
    )
    assert any(f"'## {empty}' is empty" in error for error in validate_bridge("topic", source))


def test_ci_annotations_preserve_failure_detail_without_injecting_commands(tmp_path):
    path = tmp_path / "results.xml"
    path.write_text(
        '<testsuites><testsuite><testcase classname="suite" name="case">'
        '<failure>assert 1 == 2\n::notice::injected 10%</failure>'
        '</testcase><testcase name="ok"/></testsuite></testsuites>'
    )
    assert annotations(path) == [
        "::error::suite.case: assert 1 == 2%0A::notice::injected 10%25"
    ]
    assert annotations(tmp_path / "missing.xml") == []
