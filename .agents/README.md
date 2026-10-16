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

Native skill inventories are convenience surfaces, not the source of truth. If
Codex, Claude, OpenCode, or another tool fails to expose a repo-local skill in
its current session but the skill exists here, read the canonical
`.agents/skills/<name>/SKILL.md` directly and use it as the repository fallback.
This especially matters for `nomi-ai-native`, because it is the skill that
audits skill discovery, hooks, MCP/RAG, subagents, and agent workflow drift.

Current skills:

- `caveman`: ultra-concise output for low-context or terse models.
- `nomi-interp`: interpreter runtime changes.
- `nomi-ai-native`: AI-agent setup, hooks, MCP/RAG, skills, subagents, and workflow audits.
- `nomi-language-design`: broad language/interaction discovery, synthesis and semantic admission.
- `nomi-parse`: parser, grammar, and AST lowering changes.
- `nomi-reduce`: syntactic reduction/desugar work.
- `nomi-rust-parser`: Rust/Wasm parser frontends, payload contracts, and parity.
- `nomi-test`: test authoring and multi-interpreter test patterns.
- `nomi-web`: web playground and Monaco editor work.

## Registered Design Passes

Local retrieval and the `nomi_design_passes` MCP tool expose this navigation
without running declared commands. Build/export/check with
`python3 -m tools.rag_mcp.setup`; use `docs/orientation/rag_mcp.md` for client
wiring, selected source boundaries and current limitations.

`config/design_passes.json` routes a bounded language topic to one linked
research document, canonical focused design, target fixture, implementation
bridge, validation list, and exact next actions. The process contract is
`docs/orientation/design_pass_workflow.md`; the registry is navigation, not a
language specification.

The guiding purpose is `docs/design/vision.md`. Discovery can precede a bounded
packet and can revise the taxonomy; source/semantic promotion still needs its
owned contract and evidence. The active whole-language fixture is
`docs/design/targets/overall.nomi`.

Inspect it with:

```bash
python3 -m tools.design_passes list
python3 -m tools.design_passes show pattern-matching
python3 -m tools.design_passes check
```

Codex/Claude hooks inject open or prompt-matched packets. Other agents should
check the registry before creating another design note. Every pass ends with a
current bridge that promotes repeated reasoning into skills/prompts and
deterministic invariants into checks, while avoiding instruction growth from
one-off observations.

## Subagents

Project subagent prompts are canonical under `.codex/agents/*.md`. Claude Code
native shims under `.claude/agents/*.md` point back to those prompts.

## Prompt Templates

Reusable prompt templates, including the registered design-pass loop, are
canonical under `.codex/prompts/*.md`. Claude
Code command shims under `.claude/commands/*.md` point back to those templates.

Use `.codex/prompts/feedback-cycle.md` for the implementation loop: independent
oracle, owned change, review, repair, checks, current bridge and next exact task.
`python3 -m tools.check_receipt -- COMMAND [ARG ...]` retains actual command
outcomes and logs in unique ignored `reports/checks/` directories. It runs only
explicit argv and performs no shell expansion, test selection or commits. See
`docs/orientation/ai_collaboration.md` for evidence limits and usage.
