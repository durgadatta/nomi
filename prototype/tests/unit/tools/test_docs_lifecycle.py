from pathlib import Path
import re


DOCS_ROOT = Path("docs")


CANONICAL_DESIGN_DOCS = [
    "docs/design/README.md",
    "docs/design/syntax.md",
    "docs/design/semantics.md",
    "docs/design/pattern_matching.md",
    "docs/design/industrial.md",
    "docs/design/decisions.md",
    "docs/research/README.md",
    "docs/research/families.md",
    "docs/research/convergences.md",
    "docs/research/pattern_matching.md",
    "docs/research/open_questions.md",
    "docs/orientation/design_pass_workflow.md",
]


def test_docs_mark_lifecycle_status_near_top():
    missing = []
    for path in sorted(DOCS_ROOT.rglob("*.md")):
        header = "\n".join(path.read_text(encoding="utf-8").splitlines()[:10])
        if "> Status:" not in header:
            missing.append(str(path))

    assert missing == []


def test_dated_improvement_reviews_stay_evidence_not_live_backlogs():
    for path in sorted((DOCS_ROOT / "orientation").glob("*improvement_review_*.md")):
        text = path.read_text(encoding="utf-8")

        assert "Keep this file as evidence, not as a second backlog." in text
        assert "| Action |" not in text
        assert "Acceptance for the next pass" not in text


def test_docs_readme_complete_inventory_links_every_doc():
    readme = DOCS_ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    linked_docs = set()
    for match in re.finditer(r"\]\(([^)#]+)", text):
        target = match.group(1)
        if target.startswith(("http:", "https:", "mailto:")):
            continue
        path = (DOCS_ROOT / target).resolve()
        try:
            relative = path.relative_to(Path.cwd())
        except ValueError:
            continue
        if relative.exists() and relative.suffix == ".md":
            linked_docs.add(str(relative))

    expected = {
        str(path)
        for path in DOCS_ROOT.rglob("*.md")
        if path != readme
    }
    assert sorted(expected - linked_docs) == []


def test_canonical_design_docs_exist_and_are_indexed():
    readme_text = (DOCS_ROOT / "README.md").read_text(encoding="utf-8")
    missing = []
    unindexed = []
    for rel_path in CANONICAL_DESIGN_DOCS:
        path = Path(rel_path)
        if not path.exists():
            missing.append(rel_path)
        if rel_path.removeprefix("docs/") not in readme_text:
            unindexed.append(rel_path)

    assert missing == []
    assert unindexed == []
