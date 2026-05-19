"""Conservative shell policy for Nomi agent sessions.

This hook only handles the shell tool. It blocks a short list of commands that
are almost never appropriate for an autonomous coding agent in this repo, and
adds reminders for commands that usually need careful final notes.
"""

from __future__ import annotations

import re

from hook_utils import deny_tool, emit_additional_context, read_event


BLOCKED_COMMANDS = (
    (
        re.compile(r"\bgit\s+reset\s+--hard\b"),
        "Do not discard repository changes with `git reset --hard` from an agent. Ask the user to run it or explicitly revise the hook policy.",
    ),
    (
        re.compile(r"\bgit\s+checkout\s+--\b"),
        "Do not revert paths with `git checkout --` from an agent. Work with user changes unless the user explicitly requests a revert.",
    ),
    (
        re.compile(r"\bgit\s+clean\s+-(?:[A-Za-z]*[fdx][A-Za-z]*)\b"),
        "Do not delete untracked files with `git clean` from an agent. Nomi keeps local scratch and generated artifacts around during exploration.",
    ),
    (
        re.compile(r"\brm\s+-(?:[A-Za-z]*r[A-Za-z]*f|[A-Za-z]*f[A-Za-z]*r)\s+(?:/|~|\$HOME|\.git\b)"),
        "Refusing a broad destructive `rm -rf` target. Narrow the command manually and ask for user confirmation.",
    ),
    (
        re.compile(r"\b(?:curl|wget)\b.*\|\s*(?:sh|bash|zsh)\b"),
        "Do not pipe downloaded scripts directly into a shell from an agent. Download, inspect, and ask for confirmation first.",
    ),
)

REMINDERS = (
    (
        re.compile(r"\bpytest\b.*--force-regen\b"),
        "Snapshot regeneration changes expected outputs. Mention regenerated snapshot files and semantic reason in the final answer.",
    ),
    (
        re.compile(r"\bpytest\b(?!.*prototype/tests/.+)"),
        "Broad pytest runs can be useful, but for parser/interpreter work prefer a focused failing test before the full suite.",
    ),
    (
        re.compile(r"\bpython3\s+scripts/make_web.py\b"),
        "Web manifest changes are generated artifacts; include why they changed and whether `--check` passed.",
    ),
)


def command_from_event(event: dict) -> str:
    tool_input = event.get("tool_input") or {}
    if isinstance(tool_input, dict):
        return str(tool_input.get("command") or "")
    return ""


def main() -> None:
    event = read_event()
    command = command_from_event(event)
    if not command:
        return

    for pattern, reason in BLOCKED_COMMANDS:
        if pattern.search(command):
            deny_tool("PreToolUse", reason)
            return

    reminders = [message for pattern, message in REMINDERS if pattern.search(command)]
    if reminders:
        emit_additional_context("PreToolUse", "\n".join(f"- {message}" for message in reminders))


if __name__ == "__main__":
    main()
