# AI Collaboration

> Status: current contributor and agent workflow.

AI tools help discover mechanisms, compare alternatives, implement bounded tasks,
review changes and maintain tests. Their output is a proposal; current design,
independent evidence and the user's intent determine acceptance. The prototype
is a laboratory, not a frozen language specification.

## Current Agent Assets

- [AGENTS.md](../../AGENTS.md) maps authority, setup, tests and repository areas.
- `.agents/skills/` owns shared domain workflows; tool-specific shims point there.
- `.codex/` owns advisory context/packet hooks, focused prompts and reviewer roles;
  `.claude/` reuses those contracts. `opencode.json` configures OpenCode.
- [Design packets](../../config/design_passes.json) route a topic to research,
  design, target and current implementation bridge.
- The [packet workflow](design_pass_workflow.md) defines current record and
  conformance requirements.
- [Local RAG/MCP](rag_mcp.md) discovers configured source files and books. Read
  returned files directly; retrieval cannot override source authority or grant
  capabilities. Installed tools need explicit owned configuration.

If a native skill inventory omits a repo-local skill, use the repository fallback:
read its `.agents/skills/<name>/SKILL.md` directly and state which skill guides
the work. Native discovery is a convenience; the local skill is canonical.

## Work Loop

1. Read the working map, relevant skill and canonical owner.
2. State the concrete outcome and affected files; use a short plan for broad work.
3. Reproduce the failure or prepare independent expected behavior before changing it.
4. Make a small reversible change, review it and run relevant checks.
5. Update current support, gaps and exact next actions in place.
6. Commit coherent changes when authorized and keep generated reports out of Git.

Current records must explain what runs, what is accepted, what is proposed and
what remains unknown. Do not append conversation summaries, old commit trails,
chronological receipts or AI-session narratives. Necessary project evolution is
short and isolated in [HISTORY.md](../../HISTORY.md); Git retains detailed old
versions. Primary-source dates, host versions and source/run identities remain
with the evidence they qualify.

## Independent Review And Evidence

Use a separate bounded reviewer when explicitly requested or directed by an
applicable workflow. Otherwise review against the independent oracle and report
its limits. Never substitute test totals, parser acceptance or fluent explanation
for semantic correctness, cleanup, authority, human understanding or host support.

The [feedback-cycle prompt](../../.codex/prompts/feedback-cycle.md) describes the
owned change/review/repair loop. Capture actual checks with explicit argv:

```bash
python3 -m tools.check_receipt --timeout 120 -- python3 -m tools.design_passes check
python3 -m tools.check_receipt -- python3 -m pytest -o addopts= prototype/tests/unit/tools/test_check_receipt.py
```

The command stores actual outcomes and logs in unique ignored `reports/checks/`
directories. It performs no shell expansion, test selection or commits. A passed
command establishes only that command's scope; an omitted dependency or untested
host remains an open gate. Do not copy raw logs into maintained prose.

## Context And Continuity

Prefer existing contracts and bridges over extra task notes. If a long task needs
continuity, record the goal, completed work, exact next step, open questions and
checks in a temporary note. Remove it after integrating durable facts into their
owners. Do not grow AGENTS.md, hooks or skills for one-off observations.

Rebuild the ignored retrieval index after source/document changes:

```bash
python3 -m tools.rag_mcp.cli build
python3 .codex/scripts/agent_doctor.py
```

Hooks, registries and tests should enforce deterministic invariants. Skills own
variable reasoning. Current docs own present meaning and support. HISTORY.md
alone owns the compact project chronology.
