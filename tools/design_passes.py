"""Inspect and validate Nomi's registered language-design passes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "config/design_passes.json"

SCHEMA_VERSION = 1
ARTIFACT_KEYS = ("research", "design", "target", "bridge")
ALLOWED_STATUSES = {
    "researching",
    "designing",
    "design-accepted",
    "implementing",
    "validated",
    "paused",
    "rejected",
}
RETROSPECTIVE_HEADINGS = (
    "## Pass Retrospective",
    "### Evidence That Changed The Design",
    "### Workflow Friction",
    "### Durable Improvement",
    "### Next Pass",
)


def load_registry(path: Path = DEFAULT_REGISTRY) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_registry(root: Path = ROOT, path: Path | None = None) -> list[str]:
    root = root.resolve()
    registry_path = (path or root / "config/design_passes.json").resolve()
    try:
        registry = load_registry(registry_path)
    except Exception as exc:
        return [f"cannot load {display_path(registry_path, root)}: {exc}"]

    errors: list[str] = []
    if registry.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")

    passes = registry.get("passes")
    if not isinstance(passes, list) or not passes:
        errors.append("passes must be a non-empty list")
        return errors

    seen_ids: set[str] = set()
    for index, design_pass in enumerate(passes):
        label = f"passes[{index}]"
        if not isinstance(design_pass, dict):
            errors.append(f"{label} must be an object")
            continue

        pass_id = design_pass.get("id")
        if not isinstance(pass_id, str) or not re.fullmatch(
            r"[a-z0-9]+(?:-[a-z0-9]+)*", pass_id
        ):
            errors.append(f"{label}.id must be a kebab-case string")
            pass_id = label
        elif pass_id in seen_ids:
            errors.append(f"duplicate pass id: {pass_id}")
        else:
            seen_ids.add(pass_id)
        prefix = f"pass {pass_id!r}"

        for field in ("topic", "owner"):
            if (
                not isinstance(design_pass.get(field), str)
                or not design_pass[field].strip()
            ):
                errors.append(f"{prefix}: {field} must be a non-empty string")

        status = design_pass.get("status")
        if status not in ALLOWED_STATUSES:
            errors.append(
                f"{prefix}: status must be one of {', '.join(sorted(ALLOWED_STATUSES))}"
            )

        reviewed = design_pass.get("last_reviewed")
        if not isinstance(reviewed, str) or not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}", reviewed
        ):
            errors.append(f"{prefix}: last_reviewed must use YYYY-MM-DD")

        keywords = design_pass.get("keywords")
        errors.extend(validate_string_list(prefix, "keywords", keywords))
        if isinstance(keywords, list):
            folded = [value.casefold() for value in keywords if isinstance(value, str)]
            if len(folded) != len(set(folded)):
                errors.append(f"{prefix}: keywords must be unique ignoring case")

        artifacts = design_pass.get("artifacts")
        artifact_paths: dict[str, str] = {}
        if not isinstance(artifacts, dict):
            errors.append(f"{prefix}: artifacts must be an object")
        else:
            missing = set(ARTIFACT_KEYS) - artifacts.keys()
            extra = artifacts.keys() - set(ARTIFACT_KEYS)
            if missing:
                errors.append(f"{prefix}: missing artifacts: {', '.join(sorted(missing))}")
            if extra:
                errors.append(f"{prefix}: unknown artifacts: {', '.join(sorted(extra))}")
            for kind in ARTIFACT_KEYS:
                rel_path = artifacts.get(kind)
                if not isinstance(rel_path, str) or not rel_path:
                    continue
                artifact_paths[kind] = rel_path
                errors.extend(validate_artifact_path(root, prefix, kind, rel_path))

        canonical_updates = design_pass.get("canonical_updates")
        errors.extend(validate_string_list(prefix, "canonical_updates", canonical_updates))
        if isinstance(canonical_updates, list):
            for rel_path in canonical_updates:
                if isinstance(rel_path, str):
                    errors.extend(
                        validate_existing_path(
                            root, prefix, "canonical update", rel_path
                        )
                    )

        for field in ("validation", "next_actions"):
            errors.extend(validate_string_list(prefix, field, design_pass.get(field)))

        if len(artifact_paths) == len(ARTIFACT_KEYS):
            errors.extend(validate_packet_links(root, prefix, artifact_paths))
            bridge = root / artifact_paths["bridge"]
            if bridge.is_file():
                bridge_text = bridge.read_text(encoding="utf-8")
                errors.extend(validate_retrospective(prefix, bridge_text))

    return errors


def validate_string_list(prefix: str, field: str, value: Any) -> list[str]:
    if not isinstance(value, list) or not value:
        return [f"{prefix}: {field} must be a non-empty list"]
    if any(not isinstance(item, str) or not item.strip() for item in value):
        return [f"{prefix}: {field} entries must be non-empty strings"]
    return []


def validate_existing_path(root: Path, prefix: str, kind: str, rel_path: str) -> list[str]:
    path = Path(rel_path)
    if path.is_absolute():
        return [f"{prefix}: {kind} path must be repository-relative: {rel_path}"]
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root):
        return [f"{prefix}: {kind} path escapes the repository: {rel_path}"]
    if not resolved.is_file():
        return [f"{prefix}: {kind} does not exist: {rel_path}"]
    return []


def validate_artifact_path(
    root: Path, prefix: str, kind: str, rel_path: str
) -> list[str]:
    errors = validate_existing_path(root, prefix, kind, rel_path)
    expected = {
        "research": ("docs/research/", ".md"),
        "design": ("docs/design/", ".md"),
        "target": ("docs/design/", ".nomi"),
        "bridge": ("docs/review/", ".md"),
    }[kind]
    if not rel_path.startswith(expected[0]) or not rel_path.endswith(expected[1]):
        errors.append(
            f"{prefix}: {kind} must be a {expected[1]} file under {expected[0]}"
        )
    return errors


def validate_packet_links(
    root: Path, prefix: str, artifact_paths: dict[str, str]
) -> list[str]:
    errors: list[str] = []
    for kind, rel_path in artifact_paths.items():
        path = root / rel_path
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for other_kind, other_path in artifact_paths.items():
            if other_kind != kind and other_path not in text:
                errors.append(
                    f"{prefix}: {kind} artifact must link {other_kind} artifact {other_path}"
                )
    return errors


def validate_retrospective(prefix: str, text: str) -> list[str]:
    errors: list[str] = []
    positions = []
    for heading in RETROSPECTIVE_HEADINGS:
        position = text.find(heading)
        if position == -1:
            errors.append(f"{prefix}: bridge is missing {heading!r}")
        positions.append(position)
    if errors:
        return errors
    if positions != sorted(positions):
        return [f"{prefix}: retrospective headings are out of order"]

    for index, heading in enumerate(RETROSPECTIVE_HEADINGS[1:], start=1):
        body_start = positions[index] + len(heading)
        body_end = (
            positions[index + 1]
            if index + 1 < len(RETROSPECTIVE_HEADINGS)
            else len(text)
        )
        if not text[body_start:body_end].strip():
            errors.append(f"{prefix}: retrospective section {heading!r} is empty")
    return errors


def find_pass(registry: dict[str, Any], pass_id: str) -> dict[str, Any] | None:
    return next(
        (item for item in registry.get("passes", []) if item.get("id") == pass_id),
        None,
    )


def matching_passes(registry: dict[str, Any], prompt: str) -> list[dict[str, Any]]:
    folded = prompt.casefold()
    matches = []
    for design_pass in registry.get("passes", []):
        if not isinstance(design_pass, dict):
            continue
        keywords = design_pass.get("keywords", [])
        if not isinstance(keywords, list):
            continue
        if any(
            isinstance(keyword, str)
            and re.search(
                rf"(?<!\w){re.escape(keyword.casefold())}(?!\w)",
                folded,
            )
            for keyword in keywords
        ):
            matches.append(design_pass)
    return matches


def format_pass(design_pass: dict[str, Any]) -> str:
    artifacts = design_pass["artifacts"]
    lines = [
        f"{design_pass['id']} [{design_pass['status']}] - {design_pass['topic']}",
        f"  research: {artifacts['research']}",
        f"  design:   {artifacts['design']}",
        f"  target:   {artifacts['target']}",
        f"  bridge:   {artifacts['bridge']}",
    ]
    if design_pass.get("next_actions"):
        lines.append("  next:     " + design_pass["next_actions"][0])
    return "\n".join(lines)


def display_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("list", help="List registered design passes.")
    show = subparsers.add_parser("show", help="Show one design-pass packet.")
    show.add_argument("pass_id")
    subparsers.add_parser(
        "check", help="Validate the registry and linked packet artifacts."
    )
    args = parser.parse_args()

    command = args.command or "list"
    if command == "check":
        errors = validate_registry()
        if errors:
            for error in errors:
                print(f"FAIL {error}")
            raise SystemExit(1)
        count = len(load_registry().get("passes", []))
        print(f"PASS {count} design pass packet(s) are coherent.")
        return

    registry = load_registry()
    if command == "show":
        design_pass = find_pass(registry, args.pass_id)
        if design_pass is None:
            raise SystemExit(f"Unknown design pass: {args.pass_id}")
        print(format_pass(design_pass))
        return

    for design_pass in registry.get("passes", []):
        print(format_pass(design_pass))


if __name__ == "__main__":
    main()
