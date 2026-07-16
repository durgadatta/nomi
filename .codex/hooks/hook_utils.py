"""Shared helpers for Nomi's repo-local agent hooks.

Hooks receive one JSON object on stdin and return either JSON or no output.
Keep this module dependency-free: Codex may run hooks before a virtualenv or
editable install exists, and Claude Code uses the same scripts.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


def read_event() -> dict[str, Any]:
    """Read the Codex hook event object from stdin.

    Codex and Claude Code send exactly one JSON object. Returning an empty dict
    for empty input makes local smoke tests and accidental direct runs harmless.
    """

    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    return json.loads(raw)


def repo_root(event: dict[str, Any]) -> Path:
    """Resolve the repository root for context text and path checks.

    Hook commands are launched with the session cwd, but agents may be started
    from a subdirectory. The hook command itself resolves from the project root,
    and this function keeps direct local runs similarly stable.
    """

    cwd = Path(event.get("cwd") or ".").resolve()
    for path in (cwd, *cwd.parents):
        if (path / ".git").exists():
            return path
    return cwd


def emit_additional_context(event_name: str, context: str) -> None:
    """Emit model-visible context without blocking the current action."""

    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": event_name,
                    "additionalContext": context,
                }
            }
        )
    )


def deny_tool(event_name: str, reason: str) -> None:
    """Deny a supported tool call with Codex's current hook shape."""

    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": event_name,
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )


def skill_line(name: str, reason: str) -> str:
    """Format a compact skill reminder for hook-injected context."""

    return f"- `{name}`: {reason}"


def load_design_passes(root: Path) -> list[dict[str, Any]]:
    """Load registered design passes, failing quiet in advisory hooks."""

    try:
        payload = json.loads(
            (root / "config/design_passes.json").read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(payload, dict):
        return []
    passes = payload.get("passes", [])
    if not isinstance(passes, list):
        return []
    return [item for item in passes if isinstance(item, dict)]


def open_design_passes(root: Path) -> list[dict[str, Any]]:
    """Return passes whose design or implementation work remains open."""

    return [
        item
        for item in load_design_passes(root)
        if item.get("status") not in {"validated", "rejected"}
    ]


def matching_design_passes(root: Path, prompt: str) -> list[dict[str, Any]]:
    """Find registry entries whose explicit keywords occur in a prompt."""

    folded = prompt.casefold()
    matches = []
    for item in load_design_passes(root):
        keywords = item.get("keywords", [])
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
            matches.append(item)
    return matches


def design_pass_lines(design_pass: dict[str, Any]) -> list[str]:
    """Format one compact pass packet for model-visible hook context."""

    artifacts = design_pass.get("artifacts", {})
    if not isinstance(artifacts, dict):
        artifacts = {}
    lines = [
        f"- `{design_pass.get('id', 'unknown')}` [{design_pass.get('status', 'unknown')}]: "
        f"{design_pass.get('topic', 'Untitled pass')}"
    ]
    for kind in ("research", "design", "target", "bridge"):
        path = artifacts.get(kind)
        if isinstance(path, str):
            lines.append(f"  - {kind}: `{path}`")
    return lines
