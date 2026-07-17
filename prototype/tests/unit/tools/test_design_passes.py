import json
import subprocess
import sys
from pathlib import Path

from tools.design_passes import load_registry, matching_passes, validate_registry


ROOT = Path(__file__).resolve().parents[4]


def test_registered_design_passes_are_coherent():
    assert validate_registry(ROOT) == []


def test_design_pass_cli_shows_pattern_packet():
    completed = subprocess.run(
        [sys.executable, "-m", "tools.design_passes", "show", "pattern-matching"],
        text=True,
        capture_output=True,
        check=True,
        cwd=ROOT,
    )

    assert "pattern-matching [implementing]" in completed.stdout
    assert "docs/design/pattern_matching_target.nomi" in completed.stdout


def test_registry_keywords_route_pattern_prompt():
    registry = load_registry(ROOT / "config/design_passes.json")

    matches = matching_passes(
        registry,
        "Review exhaustiveness and guard scope in pattern matching.",
    )

    assert [item["id"] for item in matches] == ["pattern-matching"]


def test_registry_keywords_do_not_match_substrings():
    registry = load_registry(ROOT / "config/design_passes.json")

    assert matching_passes(registry, "Fix a mismatched payload field.") == []


def test_validator_rejects_an_unlinked_packet(tmp_path):
    registry = make_registry(tmp_path)
    research = tmp_path / registry["passes"][0]["artifacts"]["research"]
    research.write_text("# Research\n\n> Status: evidence.\n", encoding="utf-8")

    errors = validate_registry(tmp_path)

    assert any("research artifact must link design artifact" in error for error in errors)


def test_validator_rejects_an_empty_retrospective_section(tmp_path):
    registry = make_registry(tmp_path)
    bridge = tmp_path / registry["passes"][0]["artifacts"]["bridge"]
    text = bridge.read_text(encoding="utf-8")
    bridge.write_text(
        text.replace(
            "### Durable Improvement\nA durable improvement.",
            "### Durable Improvement",
        ),
        encoding="utf-8",
    )

    errors = validate_registry(tmp_path)

    assert any(
        "retrospective section '### Durable Improvement' is empty" in error
        for error in errors
    )


def make_registry(root: Path) -> dict:
    artifacts = {
        "research": "docs/research/topic.md",
        "design": "docs/design/topic.md",
        "target": "docs/design/topic_target.nomi",
        "bridge": "docs/review/2026-07-16-topic.md",
    }
    all_paths = list(artifacts.values())
    for rel_path in all_paths:
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        linked = "\n".join(other for other in all_paths if other != rel_path)
        content = f"# Packet\n\n> Status: test.\n\n{linked}\n"
        if rel_path == artifacts["bridge"]:
            content += "\n" + "\n\n".join(
                [
                    "## Pass Retrospective",
                    "### Evidence That Changed The Design\nEvidence changed the design.",
                    "### Workflow Friction\nThe workflow had friction.",
                    "### Durable Improvement\nA durable improvement.",
                    "### Next Pass\nTake the next pass.",
                ]
            )
        path.write_text(content, encoding="utf-8")

    canonical_updates = [
        "docs/design/syntax.md",
        "docs/design/semantics.md",
        "docs/design/decisions.md",
        "docs/design/target.nomi",
    ]
    for rel_path in canonical_updates:
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text("fixture\n", encoding="utf-8")

    registry = {
        "schema_version": 1,
        "passes": [
            {
                "id": "topic",
                "topic": "Topic",
                "owner": "language-design",
                "status": "designing",
                "last_reviewed": "2026-07-16",
                "keywords": ["topic"],
                "artifacts": artifacts,
                "canonical_updates": canonical_updates,
                "validation": ["pytest focused"],
                "next_actions": ["Decide the topic."],
            }
        ],
    }
    config = root / "config/design_passes.json"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text(json.dumps(registry), encoding="utf-8")
    return registry
