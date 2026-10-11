# AI Collaboration

> Status: active process note.

Nomi is intentionally an AI-assisted language project. AI is not treated as an
authority, oracle, or replacement for design judgment. It is treated as a
high-throughput collaborator for exploration, critique, synthesis, refactoring,
test generation, and documentation pressure.

For installed RAG/MCP developer tools, use an explicit owned configuration as
described in [RAG setup](rag_mcp.md#configuration). Checkout defaults are not
wheel assets; startup errors explain that boundary without writing messages
to MCP stdout. This configuration requirement does not change document authority.

The durable source of evidence remains the repository: code, tests, design
notes, and executable examples. But because Nomi is exploratory, the repository
is not a frozen product contract. Current artifacts may lag the intended
language, preserve bootstrap compromises, or disagree with newer design
direction.

Nomi is an early exploratory language-design initiative. AI tools should
optimize for flexible, reversible implementation: declare intent in metadata,
keep reductions inspectable, and avoid turning the current prototype substrate
into the de facto language specification. See
[`exploratory_implementation_doctrine.md`](exploratory_implementation_doctrine.md).
Focused language work follows the linked packet and retrospective contract in
[`design_pass_workflow.md`](design_pass_workflow.md).

## Vision Over Snapshot

The [guiding vision](../design/vision.md) covers the language and whole activity.
Discovery may begin outside the current targets, packet taxonomy or release
profile. A mature source/semantic change still needs a coherent owned contract;
an exploratory question does not need to satisfy that admission packet first.
Use the [active target suite](../design/targets/README.md), including
`targets/overall.nomi`; the older `target.nomi` is superseded.

Every tool invocation should carry this bias:

```text
current repo state -> design pressure -> intended Nomi direction -> smallest
reversible update
```

Not:

```text
current repo state -> rigid alignment -> accidental language definition
```

AI collaborators should read existing files carefully, but they should not
overfit to them. If a doc, test, parser behavior, or skill instruction appears
stale, the correct move is to name the drift and update the relevant artifact
or status label. Do not silently force new work to match stale mechanics merely
because they are currently implemented.

## Why AI Belongs In The Repo

Nomi's README frames AI and programming languages as complementary forces:

- AI broadens the search frontier by proposing, recombining, and critiquing.
- A language compresses intention into stable, inspectable, executable form.

That distinction should shape the workflow. AI can generate many candidate
forms quickly, but Nomi should accept only the forms that survive reduction into
clear semantics, tests, examples, and documentation.

## Existing AI-Influenced Artifacts

- `.github/copilot-instructions.md` and `.github/instructions/`: GitHub/VS Code
  entrypoints that route to `AGENTS.md`, canonical skills, and playground
  checks. `.github/workflows/playground-ci.yml` executes the runtime and browser
  checks; `.vscode/tasks.json` exposes the same commands locally. See the
  [VS Code task map](vscode_extension.md#vs-code-tasks).
- `opencode.json`: project-level OpenCode config (model, LSP, formatter,
  permissions, instructions, watcher, compaction, enabled local RAG/MCP, and
  commented-out templates for providers, agents, commands and plugins).
- `.mcp.json`: portable project-root RAG/MCP wiring for Claude Code. Personal
  approvals and absolute machine-specific command snippets stay outside git;
  [setup and client checks](rag_mcp.md#start-here) explain the distinction.
- `.agents/skills/`: generic AI-assistant skill definitions shared by Codex,
  OpenCode, deepseek-tui, Claude Code, and other agents that can read a
  `SKILL.md`. Available skills:
  | Skill | Purpose |
  |---|---|
  | `caveman` | Ultra-concise output — no explanations, just code |
  | `nomi-reduce` | Add a syntactic reduction (desugarer + interpreter override + tests) |
  | `nomi-parse` | Modify parser/grammar/AST lowering |
  | `nomi-interp` | Modify interpreter runtime behavior |
  | `nomi-test` | Write tests with multi-interpreter patterns |
  | `nomi-web` | Work with the web playground and Monaco editor |
  | `nomi-rust-parser` | Maintain Rust/Wasm parser frontends, structural payload contracts, and parity |
  | `nomi-language-design` | Broad language/interaction discovery, whole-activity synthesis and semantic admission |
  | `nomi-ai-native` | Improve AI-agent setup: skills, hooks, MCP/RAG, subagents, commands, context hygiene, and workflow audits |
  If an agent has a skill loader, load the matching skill from this directory.
  If it does not, or if the loader's current session inventory omits a
  repo-local skill that exists under `.agents/skills/`, read the relevant
  `SKILL.md` directly before working and state that you are using the repository
  fallback. The
  `caveman` skill is recommended for deepseek models to keep output minimal.
- `.claude/skills/`: Claude Code native skill shims. These should stay tiny and
  point back to `.agents/skills/`, which remains the canonical shared skill
  directory.
- `.codex/agents/`: canonical project subagent prompts for review,
  language-design critique, test verification, and docs/RAG synthesis.
- `.claude/agents/`: Claude Code native subagent shims that point back to the
  `.codex/agents/` prompts.
- `.codex/prompts/`: canonical reusable prompt templates for task start,
  registered design passes, feedback cycles, checkpoints, review, and snapshot
  regeneration.
- `.claude/commands/`: Claude Code command shims that point back to
  `.codex/prompts/`.
- `AGENTS.md`: project-level operating manual for AI coding agents.
- `.codex/config.toml`: tracked Codex defaults for model, reasoning effort,
  sandbox, approval policy, and reusable profiles.
- `.codex/hooks.json` and `.codex/hooks/`: repo-local Codex lifecycle hooks
  that inject compact Nomi context, suggest relevant skills from prompt text,
  route registered design-pass packets, and block a few obviously destructive
  shell commands. Review them with
  `/hooks` in Codex before trusting changed hook scripts.
- `.claude/settings.json`: tracked Claude Code defaults, permissions, and
  project hooks. Claude calls the same hook scripts under `.codex/hooks/` so
  Codex and Claude share Nomi's lightweight context and safety policy.
- `implementation_guideline.md`: records the early use of
  ChatGPT, Grok, DeepSeek, Gemini, and Claude for parser/evaluator
  infrastructure and syntax-layer exploration.
- `../design/`: canonical target decisions where AI-generated and human-written
  ideas must be reconciled into one language.
- `../research/`: consolidated evidence and bounded open experiments, not a
  second specification.
- `../../config/design_passes.json`, `design_pass_workflow.md`, and
  `../../tools/design_passes.py`: declarative topic routing, packet lifecycle,
  deterministic cross-link checks, validations, and retrospectives.
- `artifacts_and_usage.md`: artifact map, now including the AI
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
- a shortcut around declarative feature metadata, capability gates, or
  inspection artifacts;
- a way to overwrite active design direction with a polished but incompatible
  proposal.
- a way to preserve stale current behavior after the intended direction has
  become clearer.

## Long-Running Agent Workflow

For substantial work, prefer a loop that leaves durable traces:

1. Read `AGENTS.md` and the relevant active design notes.
2. State the concrete goal and expected files.
3. Create a short plan.
4. Establish independent expected judgments/traces, then implement one coherent
   increment with a named support boundary.
5. Review against the oracle, repair findings and run focused checks. Add a
   regression for each substantive behavior finding; widen checks as warranted.
6. Checkpoint what changed, failed, passed and remains. Promote observed friction
   into the smallest durable improvement, or state why none is justified.
7. Continue from the checkpoint instead of relying on chat memory.

For language design, first check `config/design_passes.json`. Resume a matching
packet rather than creating parallel notes. The packet preserves a more useful
trace than chat alone:

```text
research -> canonical design -> focused target -> implementation bridge
-> registered checks -> retrospective -> next exact action
```

Run `python3 -m tools.design_passes check` whenever packet artifacts change.

This is especially useful for parser, interpreter, constraint, and
yield-to-block changes, where a half-remembered intent can easily become a
semantic regression.

### Retaining Actual Check Evidence

The reusable [feedback-cycle prompt](../../.codex/prompts/feedback-cycle.md)
connects the loop to the existing checkpoint and design-pass retrospective.
Capture actual checks with explicit argv:

```bash
python3 -m tools.check_receipt --timeout 120 -- python3 -m tools.design_passes check
python3 -m tools.check_receipt -- python3 -m pytest -o addopts= prototype/tests/unit/tools/test_check_receipt.py
```

Each invocation creates a unique ignored `reports/checks/check-*/` directory.
`receipt.json` records a versioned local result: command argv, working directory,
UTC start/end times, elapsed seconds, optional timeout, child return code, runner
exit code, and Git HEAD/status before and after. Status includes staged,
unstaged and untracked paths as Git porcelain v1 NUL-separated records stored
in a JSON list; rename records retain Git's following original-path record.
`output.log` captures combined stdout/stderr while streaming it to the console.
Output goes directly to disk with bounded reads for console streaming; logs are
not size-limited. The command runs from the caller's directory, with inherited
environment and no stdin, without a shell. Do not put secrets in command argv
or output that should not be retained locally.

Successful commands have `status=passed` and `returncode=0`. Failures remain in
their own directories when a later check succeeds. The runner returns the child
exit code (128 + signal for signal termination), 124 on timeout, 128 + signal
when interrupted, 127 on launch failure, and 1 on an internal runner error.
Timeout and interruption stay distinct even if termination makes the child exit
zero. On POSIX the runner stops its command's process group; elsewhere it stops
the direct child. It is not a sandbox for detached processes. Abrupt termination
that prevents finalization can leave a `running` receipt, which is incomplete
evidence and never success.

A receipt is editable local evidence, not attestation or a freshness certificate.
The receipt also fingerprints the index and nonignored tracked/untracked files
before and after execution. Symlink contents are not followed. A missing
fingerprint is unknown evidence, and `worktree_changed` flags content changes
even when HEAD and dirty filenames match. This is not a transactional snapshot
or a fingerprint of dependencies, ignored inputs or external state.
Git status alone captures paths and status, not file contents; identical status can
hide intervening edits. Read the log, compare the command, cwd, times and Git
state, and rerun affected checks after changes. Missing Git metadata is reported
as unknown. The runner does not automatically execute registry commands, choose
an oracle, change validation policy, approve a design or commit. Summarize the
results and remaining obligations in the existing tracked bridge/checkpoint;
leave raw receipts and logs ignored. Remove or consolidate process guidance
when a smaller durable check captures the same lesson.

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
- Which current artifacts are authoritative for this decision, and which might
  be stale bootstrap residue?
- What declarative owner records the feature: manifest, schema, registry,
  capability table, or profile?
- What user-facing pattern becomes clearer?
- What Python behavior, if any, must remain compatible?
- Which parser, AST, interpreter, and test surfaces are affected?
- What example demonstrates the behavior?
- What failure or diagnostic should exist when the idea is misused?
- What future design choice would this implementation make harder?
- How does this move the current snapshot toward Nomi's intended direction?
- If this is registered design work, what did the previous retrospective say
  and which packet validation proves the new state?

If those answers are not clear, keep the idea in notes or design review rather
than making it runtime behavior.

## Practical Defaults

- Keep `AGENTS.md` concise and operational.
- Keep `opencode.json` in sync with the project toolchain (model, LSP,
  formatter) and uncomment sections as the project adopts new tooling.
- Put broader AI process notes here.
- Put canonical language direction in `../design/`.
- Use the design-pass registry for durable cross-cutting feature packets; keep
  status, checks, next actions, and retrospective current.
- Keep temporary synthesis in the active task or Git history. Add a repository
  document only when it owns a durable information type that the consolidated
  docs cannot hold cleanly.
- Mention AI provenance when a document is primarily AI-generated or
  AI-synthesized.
