# AI Collaboration

> Status: active process note.

Nomi is intentionally an AI-assisted language project. AI is not treated as an
authority, oracle, or replacement for design judgment. It is treated as a
high-throughput collaborator for exploration, critique, synthesis, refactoring,
test generation, and documentation pressure.

The durable source of truth remains the repository: code, tests, design notes,
and executable examples.

## Why AI Belongs In The Repo

Nomi's README frames AI and programming languages as complementary forces:

- AI broadens the search frontier by proposing, recombining, and critiquing.
- A language compresses intention into stable, inspectable, executable form.

That distinction should shape the workflow. AI can generate many candidate
forms quickly, but Nomi should accept only the forms that survive reduction into
clear semantics, tests, examples, and documentation.

## Existing AI-Influenced Artifacts

- `AGENTS.md`: project-level operating manual for AI coding agents.
- `.codex/config.toml`: tracked Codex defaults for model, reasoning effort,
  sandbox, approval policy, and reusable profiles.
- `documentation/Implementation_guideline.md`: records the early use of
  ChatGPT, Grok, DeepSeek, Gemini, and Claude for parser/evaluator
  infrastructure and syntax-layer exploration.
- `documentation/design_review_archive/ai-codex_project_overview_vision.md`:
  Codex-generated project overview preserved as an AI-assisted summary, not a
  canonical specification.
- `documentation/design_review/`: active synthesis layer where AI-generated and
  human-written ideas must be reconciled into one coherent direction.
- `documentation/artifacts_and_usage.md`: artifact map, now including the AI
  agent entrypoint.

## Collaboration Roles

Use AI for:

- summarizing scattered notes into design pressure;
- comparing Nomi against Python, Lisp, ALGOL-family languages, ML/Haskell,
  Julia, Rust, Mathematica, R, APL, and other reference systems;
- turning vague design pressure into explicit feature specs;
- producing implementation plans before parser/interpreter edits;
- generating focused tests for intended semantics;
- reviewing diffs for regressions, missing tests, and conceptual drift;
- maintaining handoff notes during long work.

Do not use AI output as:

- a final language specification without reconciliation;
- a substitute for executable tests;
- an excuse to add syntax that does not reduce to a small semantic primitive;
- a way to overwrite active design direction with a polished but incompatible
  proposal.

## Long-Running Agent Workflow

For substantial work, prefer a loop that leaves durable traces:

1. Read `AGENTS.md` and the relevant active design notes.
2. State the concrete goal and expected files.
3. Create a short plan.
4. Implement one coherent increment.
5. Run focused checks.
6. Checkpoint what changed, what passed, and what remains.
7. Continue from the checkpoint instead of relying on chat memory.

This is especially useful for parser, interpreter, constraint, and
yield-to-block changes, where a half-remembered intent can easily become a
semantic regression.

## Checkpoint Note Shape

Use a temporary task note when a task spans multiple sessions or agents:

```markdown
# Task: <short name>

## Goal

## Current Plan

## Completed

## Next Step

## Open Questions

## Tests
```

Keep task notes short. They are continuity tools, not narrative journals.

## Acceptance Rule For AI Suggestions

An AI-generated idea is ready to move from proposal to implementation only when
it can answer these questions:

- What primitive or small set of primitives does it reduce to?
- What user-facing pattern becomes clearer?
- What Python behavior, if any, must remain compatible?
- Which parser, AST, interpreter, and test surfaces are affected?
- What example demonstrates the behavior?
- What failure or diagnostic should exist when the idea is misused?

If those answers are not clear, keep the idea in notes or design review rather
than making it runtime behavior.

## Practical Defaults

- Keep `AGENTS.md` concise and operational.
- Put broader AI process notes here.
- Put canonical language direction in `documentation/design_review/`.
- Put historical or superseded AI synthesis in
  `documentation/design_review_archive/`.
- Mention AI provenance when a document is primarily AI-generated or
  AI-synthesized.
