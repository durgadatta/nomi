# Agent Assets

Shared AI-agent assets live here so they are not tied to one tool.

All agents should treat Nomi as an early exploratory language-design project.
Before hardening implementation behavior, prefer declarative/spec-driven
artifacts: feature metadata, schemas, registries, capability tables, profiles,
inspection output, and focused tests. See
`docs/orientation/exploratory_implementation_doctrine.md`.

## Skills

`skills/*/SKILL.md` files are plain Markdown with YAML frontmatter. Agents with
native skill loading can load them directly; other agents can read the relevant
`SKILL.md` before working.

The canonical skill bodies live here. Tool-specific shims should be thin:
Claude Code shims under `.claude/skills/*/SKILL.md` only point back to these
files so the shared skill text does not drift.

Current skills:

- `caveman`: ultra-concise output for low-context or terse models.
- `nomi-interp`: interpreter runtime changes.
- `nomi-ai-native`: AI-agent setup, hooks, MCP/RAG, skills, subagents, and workflow audits.
- `nomi-language-design`: language design synthesis and syntax critique.
- `nomi-parse`: parser, grammar, and AST lowering changes.
- `nomi-reduce`: syntactic reduction/desugar work.
- `nomi-test`: test authoring and multi-interpreter test patterns.
- `nomi-web`: web playground and Monaco editor work.

## Subagents

Project subagent prompts are canonical under `.codex/agents/*.md`. Claude Code
native shims under `.claude/agents/*.md` point back to those prompts.

## Prompt Templates

Reusable prompt templates are canonical under `.codex/prompts/*.md`. Claude
Code command shims under `.claude/commands/*.md` point back to those templates.
