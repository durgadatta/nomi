"""Read-only health checks for Nomi's AI-agent setup.

Codex is the canonical home for these project-level agent utilities. Other
agent configs should call or reference this script instead of duplicating the
checks.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: str
    detail: str


def main() -> None:
    parser = argparse.ArgumentParser(description="Check Nomi's AI-agent setup.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable results.")
    args = parser.parse_args()

    results = run_checks()
    if args.json:
        print(json.dumps([asdict(result) for result in results], indent=2))
    else:
        print_results(results)

    if any(result.status == "fail" for result in results):
        raise SystemExit(1)


def run_checks() -> list[CheckResult]:
    return [
        check_required_files(),
        check_codex_hooks_json(),
        check_claude_settings_jsonc(),
        check_hook_scripts_compile(),
        check_skills_frontmatter(),
        check_rag_index_freshness(),
    ]


def check_required_files() -> CheckResult:
    required = [
        "AGENTS.md",
        ".agents/README.md",
        ".agents/skills/nomi-ai-native/SKILL.md",
        ".codex/config.toml",
        ".codex/hooks.json",
        ".claude/settings.json",
        "docs/orientation/ai_collaboration.md",
        "docs/orientation/rag_mcp.md",
        "config/rag_sources.json",
    ]
    missing = [path for path in required if not (ROOT / path).exists()]
    if missing:
        return CheckResult("required-files", "fail", "Missing: " + ", ".join(missing))
    return CheckResult("required-files", "pass", f"{len(required)} expected agent files are present.")


def check_codex_hooks_json() -> CheckResult:
    path = ROOT / ".codex/hooks.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return CheckResult("codex-hooks-json", "fail", str(exc))

    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        return CheckResult("codex-hooks-json", "fail", "Missing top-level hooks object.")
    expected = {"SessionStart", "UserPromptSubmit", "PreToolUse"}
    missing = expected - hooks.keys()
    if missing:
        return CheckResult("codex-hooks-json", "fail", "Missing events: " + ", ".join(sorted(missing)))
    return CheckResult("codex-hooks-json", "pass", f"{len(hooks)} hook events configured.")


def check_claude_settings_jsonc() -> CheckResult:
    path = ROOT / ".claude/settings.json"
    try:
        data = json.loads(strip_jsonc_comments(path.read_text(encoding="utf-8")))
    except Exception as exc:
        return CheckResult("claude-settings-jsonc", "fail", str(exc))

    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        return CheckResult("claude-settings-jsonc", "fail", "Missing hooks object.")
    if "PreToolUse" not in hooks:
        return CheckResult("claude-settings-jsonc", "fail", "Missing PreToolUse hook.")
    return CheckResult("claude-settings-jsonc", "pass", "Claude settings parsed and hooks are present.")


def check_hook_scripts_compile() -> CheckResult:
    hook_dir = ROOT / ".codex/hooks"
    scripts = sorted(path for path in hook_dir.glob("*.py"))
    failures = []
    for script in scripts:
        try:
            compile(script.read_text(encoding="utf-8"), str(script), "exec")
        except SyntaxError as exc:
            failures.append(f"{script.relative_to(ROOT)}: {exc}")

    if failures:
        return CheckResult("hook-scripts-compile", "fail", "; ".join(failures))
    return CheckResult("hook-scripts-compile", "pass", f"{len(scripts)} hook scripts compile in memory.")


def check_skills_frontmatter() -> CheckResult:
    skill_paths = sorted((ROOT / ".agents/skills").glob("*/SKILL.md"))
    if not skill_paths:
        return CheckResult("skills-frontmatter", "fail", "No skills found under .agents/skills.")

    failures = []
    for path in skill_paths:
        frontmatter = read_frontmatter(path)
        if not frontmatter:
            failures.append(f"{path.parent.name}: missing YAML frontmatter")
            continue
        for field in ("name", "description"):
            if not frontmatter.get(field):
                failures.append(f"{path.parent.name}: missing {field}")
        if frontmatter.get("name") and frontmatter["name"] != path.parent.name:
            failures.append(f"{path.parent.name}: name does not match folder")

    if failures:
        return CheckResult("skills-frontmatter", "fail", "; ".join(failures))
    return CheckResult("skills-frontmatter", "pass", f"{len(skill_paths)} skills have basic metadata.")


def check_rag_index_freshness() -> CheckResult:
    try:
        from tools.rag_mcp.config import load_config
        from tools.rag_mcp.index import iter_source_files
    except Exception as exc:
        return CheckResult("rag-index", "warn", f"Could not import RAG modules: {exc}")

    try:
        config = load_config(ROOT / "config/rag_sources.json")
    except Exception as exc:
        return CheckResult("rag-index", "fail", f"Could not load RAG config: {exc}")

    if not config.index_path.exists():
        return CheckResult("rag-index", "warn", "Index missing; run `python3 -m tools.rag_mcp.cli build`.")

    index_mtime = config.index_path.stat().st_mtime
    newest_source: Path | None = None
    newest_mtime = 0.0
    for source in config.sources:
        for path in iter_source_files(source, config.root):
            mtime = path.stat().st_mtime
            if mtime > newest_mtime:
                newest_mtime = mtime
                newest_source = path

    if newest_source and newest_mtime > index_mtime:
        display = newest_source.relative_to(ROOT) if newest_source.is_relative_to(ROOT) else newest_source
        return CheckResult("rag-index", "warn", f"Index may be stale; newer source: {display}.")
    return CheckResult("rag-index", "pass", f"Index exists at {config.index_path.relative_to(ROOT)}.")


def strip_jsonc_comments(text: str) -> str:
    output = []
    in_string = False
    escape = False
    index = 0
    while index < len(text):
        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ""
        if in_string:
            output.append(char)
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            index += 1
            continue

        if char == '"':
            in_string = True
            output.append(char)
            index += 1
            continue

        if char == "/" and next_char == "/":
            index += 2
            while index < len(text) and text[index] not in "\r\n":
                index += 1
            continue

        output.append(char)
        index += 1
    return "".join(output)


def read_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            values[match.group(1)] = match.group(2).strip().strip('"')
    return values


def print_results(results: list[CheckResult]) -> None:
    for result in results:
        icon = {"pass": "PASS", "warn": "WARN", "fail": "FAIL"}[result.status]
        print(f"{icon} {result.name}: {result.detail}")


if __name__ == "__main__":
    main()
