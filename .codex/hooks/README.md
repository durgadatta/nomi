# Agent Hooks For Nomi

These hooks are intentionally small and conservative. They are here to make
Codex and Claude Code remember Nomi's existing agent workflow, not to replace
`AGENTS.md`, skills, tests, or direct file reading.

Codex discovers repo-local hooks from `.codex/hooks.json` when the project
`.codex/` layer is trusted. Claude Code discovers hooks from
`.claude/settings.json`. In either CLI, use `/hooks` to review and trust the
commands before they run.

The scripts live under `.codex/hooks/` for now because Codex requires its hook
config beside the project `.codex/` layer. Claude calls the same scripts through
`$CLAUDE_PROJECT_DIR/.codex/hooks/...` so the behavior stays consistent.

## Hooks

- `session_start.py` adds a compact startup reminder: read `AGENTS.md`, choose
  relevant `.agents/skills/*/SKILL.md`, use RAG/MCP as source discovery, and
  keep parser/interpreter/docs/tests aligned.
- `user_prompt_submit.py` maps prompt wording to likely Nomi skills and returns
  model-visible context. It is advisory only.
- `pre_tool_use_policy.py` blocks a few obviously destructive shell commands and
  adds reminders for snapshot regeneration and broad pytest runs.

## Design Notes

- Keep hooks deterministic and fast. They run inside the agent loop.
- Prefer advisory `additionalContext` over blocking unless the command is
  clearly unsafe.
- Keep hook policy project-specific. General coding style belongs in
  `AGENTS.md`; task workflows belong in `.agents/skills/`.
- If a hook becomes noisy, remove or narrow it. Hooks should feel like a
  seatbelt, not a second driver.

## Local Smoke Checks

```bash
printf '{"hook_event_name":"SessionStart","source":"startup","cwd":"%s"}\n' "$PWD" \
  | python3 .codex/hooks/session_start.py

printf '{"hook_event_name":"UserPromptSubmit","prompt":"add parser tests for a desugar pass","cwd":"%s"}\n' "$PWD" \
  | python3 .codex/hooks/user_prompt_submit.py

printf '{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"git reset --hard"},"cwd":"%s"}\n' "$PWD" \
  | python3 .codex/hooks/pre_tool_use_policy.py
```
