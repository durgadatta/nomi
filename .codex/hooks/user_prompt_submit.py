"""Prompt-time skill hints for Nomi agent sessions.

This hook maps the user's prompt to likely local skills and docs. It does not
block prompts; it only adds context that helps the model pick the right workflow
without rereading every skill on every turn.
"""

from __future__ import annotations

import re

from hook_utils import emit_additional_context, read_event, skill_line


SKILL_HINTS = (
    (
        "nomi-language-design",
        re.compile(r"\b(design|syntax|language|spec|research|convenience|normal form|feature admission)\b", re.I),
        "read active language docs and reduce ideas to Nomi normal forms before implementation",
    ),
    (
        "nomi-ai-native",
        re.compile(
            r"\b(ai[- ]?native|agent[- ]?native|agent setup|codex|claude|opencode|hooks?|skills?|subagents?|mcp|rag|prompt templates?|context hygiene)\b",
            re.I,
        ),
        "audit the agent environment and choose between docs, skills, hooks, MCP, subagents, commands, and tests",
    ),
    (
        "nomi-parse",
        re.compile(r"\b(parser|parse|grammar|lark|ast|lowering|desugar|surface syntax)\b", re.I),
        "keep grammar, lowering, desugar, feature metadata, and parser tests aligned",
    ),
    (
        "nomi-rust-parser",
        re.compile(r"\b(rust parser|wasm parser|tree[- ]?sitter|parser frontend|core json|parse acceptance|parser spike)\b", re.I),
        "keep Rust/WASM parser frontends, payload contracts, and parse-acceptance parity aligned",
    ),
    (
        "nomi-interp",
        re.compile(r"\b(interpreter|runtime|eval|environment|binding|constraint|yield|block call|control flow)\b", re.I),
        "keep Python-compatible behavior separate from deliberate Nomi runtime departures",
    ),
    (
        "nomi-reduce",
        re.compile(r"\b(reduce|reduction|desugar pass|reduced interpreter|normal form)\b", re.I),
        "add inspectable desugar behavior and reduced-mode guardrails together",
    ),
    (
        "nomi-test",
        re.compile(r"\b(test|pytest|snapshot|regression|fixture|coverage|interpreter modes?)\b", re.I),
        "prefer focused tests first, then broader multi-interpreter checks when risk grows",
    ),
    (
        "nomi-web",
        re.compile(r"\b(web|playground|monaco|pyodide|manifest|browser|frontend)\b", re.I),
        "keep browser-facing runtime, manifest, samples, and UI checks in sync",
    ),
    (
        "caveman",
        re.compile(r"\b(caveman|terse|ultra[- ]?concise|minimal output)\b", re.I),
        "switch to minimal wording when the user explicitly asks for terse work",
    ),
)


DOC_HINTS = (
    (
        re.compile(r"\b(mcp|rag|retrieval|context search|source discovery)\b", re.I),
        "For RAG/MCP questions, read `docs/orientation/rag_mcp.md` and `tools/rag_mcp/` before changing behavior.",
    ),
    (
        re.compile(r"\b(vscode|extension|textmate|syntax highlighting)\b", re.I),
        "For VS Code work, read `docs/orientation/vscode_extension.md` and `tools/vscode/nomi/README.md`.",
    ),
    (
        re.compile(r"\b(jupyter|notebook|kernel)\b", re.I),
        "For notebook work, read `tools/jupyter/README.md` and run the focused kernel check when relevant.",
    ),
)


def main() -> None:
    event = read_event()
    prompt = event.get("prompt") or ""

    skill_matches = [
        skill_line(name, reason)
        for name, pattern, reason in SKILL_HINTS
        if pattern.search(prompt)
    ]
    doc_matches = [hint for pattern, hint in DOC_HINTS if pattern.search(prompt)]

    if not skill_matches and not doc_matches:
        return

    sections = []
    if skill_matches:
        sections.append("Likely Nomi skills for this prompt:\n" + "\n".join(skill_matches))
    if doc_matches:
        sections.append("Relevant Nomi docs/tooling notes:\n" + "\n".join(f"- {hint}" for hint in doc_matches))

    sections.append(
        "These are hints only. User instructions and local code context still decide the actual workflow."
    )
    emit_additional_context("UserPromptSubmit", "\n\n".join(sections))


if __name__ == "__main__":
    main()
