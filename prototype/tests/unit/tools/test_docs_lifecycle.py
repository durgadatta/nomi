from pathlib import Path


def test_docs_mark_lifecycle_status_near_top():
    missing = []
    for path in sorted(Path("docs").rglob("*.md")):
        header = "\n".join(path.read_text(encoding="utf-8").splitlines()[:10])
        if "> Status:" not in header:
            missing.append(str(path))

    assert missing == []


def test_dated_improvement_reviews_stay_evidence_not_live_backlogs():
    for path in sorted(Path("docs/orientation").glob("*improvement_review_*.md")):
        text = path.read_text(encoding="utf-8")

        assert "Keep this file as evidence, not as a second backlog." in text
        assert "| Action |" not in text
        assert "Acceptance for the next pass" not in text
