---
name: nomi-ai-native
description: Improve Nomi's AI-native development setup: AGENTS.md, skills, hooks, MCP/RAG, Claude/Codex/OpenCode config, subagents, reusable commands, agent safety, context hygiene, evals, and documentation. Use when auditing or changing how AI agents work in this repository.
compatibility: codex, opencode, deepseek-tui, claude-code
---

# Nomi AI-Native Maintenance

Use this skill when the task is about making Nomi easier, safer, or more
repeatable for AI coding agents. This is a meta-skill: it improves the agent
environment, not the language runtime directly.

If a tool's native session skill list omits `nomi-ai-native` but this file is
present, treat this file as the canonical repository fallback and use it anyway.
The native list is a convenience surface; `.agents/skills/nomi-ai-native/SKILL.md`
is the durable contract for this workflow.

## Operating Principle

AI-native does not mean "more instructions everywhere." Prefer the smallest
durable artifact that changes agent behavior:

- **Docs** for human/agent orientation and design source of truth.
- **Skills** for reasoning workflows that vary by task.
- **Hooks** for deterministic checks or guardrails that must run every time.
- **MCP/RAG** for local data/tool access and cited source discovery.
- **Subagents** for bounded research, review, or verification with separate
  context.
- **Commands/templates** for repeated prompts or handoff shapes.
- **Tests/evals** for checking whether agent-facing assets still work.

For Nomi specifically, AI-native also means preserving design optionality. The
project is an exploratory language-design initiative, so agent assets should
push work toward declarative/spec-driven metadata, inspectable reductions, and
reversible slices rather than fast hardcoded implementation.

## Feature Work Contract

Nomi skills should steer feature work through explicit ownership: feature
manifest or audit entry, layer/status, normal form or backend target,
docs/spec surface, focused tests, and inspection command. If a skill teaches an
implementation path without those checkpoints, update the skill before using it
as the canonical workflow.

## Start Here

1. Read `AGENTS.md`, `.agents/README.md`, and
   `docs/orientation/ai_collaboration.md`.
   For broad implementation or agent-behavior changes, also read
   `docs/orientation/exploratory_implementation_doctrine.md`.
2. Inspect current tool config:
   - Codex: `.codex/config.toml`, `.codex/hooks.json`, `.codex/hooks/`
   - Claude: `.claude/settings.json`
   - OpenCode: `opencode.json`
   - RAG/MCP: `docs/orientation/rag_mcp.md`, `tools/rag_mcp/`
3. Check whether the request is about agent behavior, repo structure, safety,
   context retrieval, workflow repeatability, or documentation drift.
4. Make a small plan before editing; AI-infrastructure changes can get noisy
   quickly.

## Research Baseline

Recent practice converges on these points:

- Keep repository context files short and operational. Overly broad context can
  increase cost and exploration without improving success.
- Separate feature types: hooks enforce deterministic policy; skills teach
  workflows; MCP exposes tools/data; subagents preserve main-context budget.
- Treat fast, focused tests and predictable repo structure as core agent
  infrastructure.
- Make safety executable when possible. A hook that blocks an unsafe command is
  stronger than a prose instruction asking the model not to run it.
- Evaluate agent assets. Skills, hooks, and prompts should have smoke checks or
  examples that catch drift.

## Audit Checklist

Use this checklist when asked "what is missing?" or "make this more AI-native":

- **Context shape:** Is `AGENTS.md` concise enough? Are canonical docs linked
  instead of duplicated? Are outdated instructions removed?
- **Exploratory posture:** Do agent instructions preserve reversible,
  metadata-driven implementation, or do they reward hardcoded feature work?
- **Skill coverage:** Is there a skill for each recurring fragile workflow?
  Parser/interpreter/test/web/design/meta should stay separate.
- **Feature workflow:** Do Nomi skills require owner, status, normal form,
  docs, tests, and inspection decisions before implementation?
- **Tool-native discovery:** Can the target agent actually find the asset?
  Shared `.agents/skills/` may need tool-specific shims or hooks.
- **Hooks:** Are guardrails deterministic, quiet, and tested with sample JSON?
  Avoid hooks that run expensive commands on every edit.
- **MCP/RAG:** Does retrieval return cited snippets, resources, and current
  source ranking? Is the index rebuild path obvious?
- **Subagents:** Are there bounded roles worth defining, such as code review,
  language-design critique, test verification, or docs synthesis?
- **Commands/templates:** Are repeated prompts, checkpoint notes, PR summaries,
  and review requests captured as reusable templates?
- **Verification loop:** Are focused checks documented for each workflow? Are
  hook/skill smoke checks runnable without network access?
- **Security:** Are destructive shell commands, secrets, generated artifacts,
  and MCP/tool trust boundaries explicit?
- **Handoff:** Can another agent resume from notes, tests, and git status
  without relying on chat memory?

## Improvement Workflow

1. **Inventory:** List current agent assets and which tool consumes each one.
2. **Find friction:** Look for repeated user corrections, stale docs, noisy
   hooks, missing test commands, or tool-specific discovery gaps.
3. **Choose the artifact:** Decide whether the fix belongs in docs, a skill, a
   hook, MCP, a subagent, a command/template, or tests.
4. **Patch narrowly:** Update the smallest durable surface. Keep generated
   runtime state out of git.
5. **Validate:** Run JSON parsing, hook smoke events, focused tests, or CLI
   checks relevant to the touched asset.
6. **Document the contract:** Update `.agents/README.md`,
   `docs/orientation/ai_collaboration.md`, or the local hook/skill docs if the
   workflow changed.

## Project Review Workflow

Use this workflow when asked to review the whole project, do gap analysis,
consolidate docs, or update agent skills after a broad scan.

1. **Start from evidence, not vibes.** Run or read the current validation
   surfaces before writing recommendations:
   - `git status --short`
   - `python3 -m tools.syntax.inspect --stage capabilities`
   - `python3 -m tools.syntax.inspect --stage resolved-pipelines`
   - `python3 scripts/check_web_runtime.py`, when web/runtime truth matters
   - `python3 .codex/scripts/agent_doctor.py`
2. **Use existing action surfaces.** Prefer updating:
   - `docs/design/decisions.md` for target choices and bounded experiments;
   - `docs/research/open_questions.md` for unresolved research forks;
   - `docs/orientation/artifacts_and_usage.md` for current implementation truth;
   - `docs/review/` only for dated evidence, then promote durable decisions.
3. **Avoid duplicate synthesis docs.** Do not create another "whole project
   review" unless it retires an existing action surface. Fold durable findings
   into the canonical docs and leave old reviews as evidence.
4. **Name the highest-leverage gaps.** For Nomi, broad scans should check
   capability honesty, Surface/Core authority, runtime result contracts,
   semantic event producers, frontend parity, feature profiles, generated
   artifact freshness, and agent workflow drift.
5. **Commit logical slices.** Make a planning-only docs commit before broader
   implementation. Then commit review docs, skill updates, guardrails, and
   runtime/parser changes separately.
6. **Reflect between slices.** After each commit, check `git status --short`,
   verify no generated local state is staged, and ask whether the next change
   still preserves feature ownership, capability honesty, and reversibility.
7. **Refresh derived context.** After docs edits, rebuild the ignored RAG index
   with `python3 -m tools.rag_mcp.cli build` if `agent_doctor.py` reports
   staleness.

When reporting the result, include the commits made, checks run, next planned
slice, and any remaining risk. Keep the answer short enough that another agent
or human can resume from the committed docs rather than from chat memory.

## Nomi-Specific Next Candidates

Consider these as future improvements, not requirements for every task:

- Add tool-native shims for project skills where a tool cannot discover
  `.agents/skills/` directly.
- Extend canonical project subagents in `.codex/agents/` and keep
  `.claude/agents/` as thin native shims.
- Extend `python3 .codex/scripts/agent_doctor.py` as new agent infrastructure
  becomes canonical.
- Add smoke tests for hook scripts under `prototype/tests/unit/tools/`.
- Add reusable prompt templates for task start, checkpoint, review, and
  snapshot-regeneration handoff.
- Extend the RAG/MCP server with prompts or resource templates once a real
  client need appears.
- Periodically trim `AGENTS.md` and route detailed procedures into skills or
  docs to protect context budget.

## Output Shape

When reporting an AI-native audit, use:

- **Already strong:** current assets that are working.
- **Missing or weak:** gaps, ordered by leverage.
- **Recommended next patches:** small, concrete changes.
- **Validation:** checks to run after those patches.

Avoid recommending every possible agent feature. The right answer is the next
thin layer that improves reliability without adding context clutter.
