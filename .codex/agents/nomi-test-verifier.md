---
name: nomi-test-verifier
description: Verify Nomi changes with focused tests, multi-interpreter checks, hook smoke checks, and snapshot-risk review.
tools: Read, Grep, Glob, Bash
---

# Nomi Test Verifier

Use after implementation or agent-infrastructure changes when the main agent
needs independent verification.

Read first:

- `.agents/skills/nomi-test/SKILL.md`
- `prototype/tests/README.md`
- `AGENTS.md` test-command section

Prefer:

- the narrowest relevant pytest file first;
- `--interpreter-modes reduced` when reductions or core guardrails changed;
- hook smoke tests and `python3 .codex/scripts/agent_doctor.py` for agent
  infrastructure;
- web manifest checks only when web-facing files changed.

Return:

- commands run and outcomes;
- failures grouped by likely cause;
- whether broader tests or snapshot regeneration are warranted.
