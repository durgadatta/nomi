import csv
from pathlib import Path

RESEARCH = Path("docs/research")


def read_semantic_table(name):
    lines = [
        line
        for line in (RESEARCH / name).read_text().splitlines()
        if line.startswith("| ")
    ]
    # These two tables deliberately contain no literal pipe in any cell.
    assert all("\\|" not in line for line in lines)
    rows = [
        [cell.strip() for cell in row[1:-1]]
        for row in csv.reader(lines, delimiter="|", quoting=csv.QUOTE_NONE)
    ]
    assert all(len(row) == len(rows[0]) for row in rows)
    assert all(cell == "---" for cell in rows[1])
    return [rows[0], *rows[2:]]


def test_language_row_view_is_exact_transpose():
    original = read_semantic_table("language_feature_matrix.md")
    transposed = read_semantic_table("feature_language_matrix.md")
    expected = [list(row) for row in zip(*original, strict=True)]
    expected[0][0] = "Language / Review"
    assert transposed == expected


def test_semantic_views_cover_every_language_and_feature_review():
    table = read_semantic_table("language_feature_matrix.md")
    expected_languages = {
        path.name
        for path in (RESEARCH / "languages").glob("*.md")
        if path.name != "README.md"
    }
    expected_features = {
        path.name
        for path in (RESEARCH / "features").glob("*.md")
        if path.name != "README.md"
    }
    language_headers = table[0][2:-2]
    feature_headers = [row[0] for row in table[1:]]
    assert len(language_headers) == len(expected_languages)
    assert len(feature_headers) == len(expected_features)
    assert all(
        sum(f"](languages/{name})" in cell for cell in language_headers) == 1
        for name in expected_languages
    )
    assert all(
        sum(f"](features/{name})" in cell for cell in feature_headers) == 1
        for name in expected_features
    )
    assert table[0][-2:] == [
        "[Excel](interfaces/spreadsheets.md)",
        "[Keyboard commands](interfaces/keyboard_commands.md)",
    ]


def test_every_language_has_a_syntax_row_and_primary_reference():
    text = (RESEARCH / "syntax_matrix.md").read_text()
    for path in (RESEARCH / "languages").glob("*.md"):
        if path.name != "README.md":
            row = next(
                line
                for line in text.splitlines()
                if line.startswith("| [") and f"](languages/{path.name})" in line
            )
            assert "](https://" in row
    assert "[Nomi target](../design/syntax.md)" in text
    assert "[Excel](interfaces/spreadsheets.md)" in text
    assert "[Keyboard commands](interfaces/keyboard_commands.md)" in text
