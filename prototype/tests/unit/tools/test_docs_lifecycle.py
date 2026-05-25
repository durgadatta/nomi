from pathlib import Path


def test_docs_mark_lifecycle_status_near_top():
    missing = []
    for path in sorted(Path("docs").rglob("*.md")):
        header = "\n".join(path.read_text(encoding="utf-8").splitlines()[:10])
        if "> Status:" not in header:
            missing.append(str(path))

    assert missing == []
