"""Session-start context for AI agents in the Nomi repository.

This hook is deliberately advisory. It gives Codex and Claude Code a short,
stable reminder of the repo's collaboration rules and skill layout every time a
trusted local session starts or resumes.
"""

from __future__ import annotations

from hook_utils import (
    design_pass_lines,
    emit_additional_context,
    open_design_passes,
    read_event,
    repo_root,
)


def main() -> None:
    event = read_event()
    root = repo_root(event)

    context = f"""Nomi project context loaded from {root}.

Before broad design or implementation work, use `AGENTS.md` as the working map.
Choose relevant skills from `.agents/skills/` before editing:
- `nomi-language-design` for syntax/design decisions and research synthesis.
- `nomi-parse` for grammar, AST lowering, and desugar pipeline changes.
- `nomi-rust-parser` for Rust/WASM parser frontends and parser-spike parity.
- `nomi-interp` for runtime, evaluation, environment, and control-flow changes.
- `nomi-reduce` for syntactic reductions that need desugar + reduced-mode tests.
- `nomi-test` for tests, snapshots, and multi-interpreter coverage.
- `nomi-web` for the web playground, Monaco, Pyodide, and manifest work.
- `nomi-ai-native` for improving agent setup, hooks, MCP/RAG, skills, and
  workflow repeatability.
- `caveman` only when the user explicitly wants ultra-concise output.

Use local RAG/MCP only as source discovery; read returned files directly before
editing. Keep parser, lowering, interpreter, docs, and focused tests aligned."""

    design_passes = open_design_passes(root)
    if design_passes:
        lines = [
            "Open registered design passes (routing indexes, not specifications):"
        ]
        visible_passes = design_passes[:5]
        for design_pass in visible_passes:
            lines.extend(design_pass_lines(design_pass))
        if len(design_passes) > len(visible_passes):
            lines.append(
                f"- {len(design_passes) - len(visible_passes)} more; run "
                "`python3 -m tools.design_passes list`."
            )
        lines.append(
            "Read `docs/orientation/design_pass_workflow.md` and the matching "
            "packet before creating another design note."
        )
        context += "\n\n" + "\n".join(lines)

    emit_additional_context("SessionStart", context)


if __name__ == "__main__":
    main()
