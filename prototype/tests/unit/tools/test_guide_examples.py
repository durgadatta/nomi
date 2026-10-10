"""Published beginner programs remain executable without copied source fixtures."""

import pytest

from scripts.check_guide_examples import read_examples, run_example


@pytest.mark.parametrize("route", ["nomi", "reduced", "core-runtime"])
@pytest.mark.parametrize("example", read_examples(), ids=lambda item: item.title)
def test_beginner_program_matches_its_published_output(example, route):
    assert run_example(example, route) == example.stdout


@pytest.mark.parametrize("body", ["", "## Incomplete\n```nomi\nprint(1)\n```\n"])
def test_empty_or_unpaired_tutorial_cannot_pass_without_execution(tmp_path, body):
    guide = tmp_path / "lesson.md"
    guide.write_text(body)
    with pytest.raises(ValueError):
        read_examples(guide)
