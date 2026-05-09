# AGENTS.md

This is the agent entrypoint for Nomi. Treat it as a working map, not a
language specification. User prompts override this file; more specific
instructions in a nested `AGENTS.md`, if one is added later, override this file
for that subtree.

## Project Overview

Nomi is an experimental programming language built around a small, coherent
core: values, bindings, functions, calls, blocks, constraints, and controlled
evaluation. The current implementation is a Python-hosted prototype, using
Lark for parsing, Python AST as a transitional semantic substrate, and custom
interpreter layers for Python-compatible and Nomi-specific behavior.

The important design pressure is not feature accumulation. Nomi should grow by
making small semantic primitives combine into richer forms while preserving
local reasoning, readable syntax, and inspectable reduction.

## Canonical Reading Order

Start with these files before broad design or implementation changes:

- `README.md`: user-facing project vision, usage, current status, and examples.
- `docs/orientation/artifacts_and_usage.md`: current runtime pipeline and artifact
  map.
- `docs/orientation/implementation_guideline.md`: implementation posture and AI
  tool history.
- `docs/orientation/ai_collaboration.md`: AI collaboration doctrine, accepted use
  cases, and checkpoint workflow.
- `docs/README.md`: docs map and current design spine.
- `docs/language/language_foundation.md`: canonical foundation for the next
  design pass.
- `docs/language/language_spec.md`: draft concrete language specification.
- `docs/language/implementation_todos.md`: staged design and
  implementation tasks.
- `docs/features/binding_constraints_feature.md`: constrained
  binding feature pillar.
- `docs/features/block_calls_feature.md`: yield-to-block and
  block-call control design.
- `docs/language/delta_on_python.md`: rationale for Nomi changes relative to
  Python.
- `docs/features/yield_to_block.md`: delicate resumable-control notes.
- `docs/orientation/vscode_extension.md` and `tools/jupyter/README.md`: tooling
  surfaces.

Archived design notes under `docs/archive/design_review/` are source
material, not active specification. Use them to recover history, then reconcile
work with the active docs in `docs/language/` and `docs/features/`.

## Setup Commands

- Install the package locally: `python3 -m pip install -e .`
- Install development extras: `python3 -m pip install -e '.[dev]'`
- Run the CLI: `nomi scripts/demo.nomi`
- Run without installation: `python3 scripts/cli.py scripts/demo.nomi`
- Build/run the Dockerized notebook: `python3 scripts/run_nomi_docker.py`
- Start the notebook tooling: `python3 tools/jupyter/launch_nomi_notebook.py`
- Enable the local VS Code extension:
  `python3 tools/vscode/nomi/scripts/nomi-vscode.py enable-local`

## Test Commands

- Run the full Python test suite: `pytest`
- Run a focused test file: `pytest prototype/tests/path/to/test_file.py`
- Generate HTML reports: `python3 scripts/test_report.py --no-open`
- Check the Nomi Jupyter kernel:
  `python3 -m tools.jupyter.check_nomi_kernel`

The project config currently sets pytest addopts to `-n auto`, so tests may run
in parallel. For parser/interpreter work, prefer a focused failing test first,
then the broader relevant suite.

## Repository Map

- `prototype/grammar/`: Lark grammar definitions.
- `prototype/parser/python/`: Python-compatible parsing and AST lowering.
- `prototype/parser/nomi/`: Nomi-specific syntax handling.
- `prototype/interpreter/python/`: Python-compatible custom interpreter layers.
- `prototype/interpreter/nomi/`: Nomi-specific runtime behavior.
- `prototype/tests/`: unit, functional, regression, and end-to-end tests.
- `prototype/tests/data/sample_sources/`: executable language examples and
  regression samples.
- `scripts/`: CLI, demo program, and report generation.
- `tools/jupyter/`: Nomi notebook kernel and helpers.
- `tools/docker/`: Docker container entrypoint for the notebook image.
- `tools/vscode/nomi/`: local VS Code extension scaffold.
- `docs/language/`, `docs/features/`, and `docs/research/`: active language
  design workspace grouped by concreteness.
- `docs/archive/design_review/`: preserved AI-assisted and exploratory
  design material.
- `docs/orientation/ai_collaboration.md`: process note for AI-assisted design,
  implementation, critique, and checkpointing.
- `local/` and `PLAY/`: scratch/reference material; do not treat as canonical
  unless the user points there directly.

## Development Posture

- Preserve Python parity where Nomi intentionally follows Python; make
  deliberate semantic departures explicit in tests and docs.
- Keep parser, lowering, and interpreter changes aligned. A syntax change often
  needs grammar coverage, AST lowering, runtime behavior, and regression tests.
- Treat binding, constraints, and resumable control as high-risk areas. Read the
  active design docs before changing them.
- Prefer small, reversible implementation steps over broad rewrites.
- Do not collapse Nomi's design ambition down to the current prototype
  mechanics. The prototype is a laboratory for the language, not the final
  boundary of the language.
- Update documentation when behavior, commands, or design direction changes.
- Avoid committing generated caches, reports, local notebooks, or VS Code
  extension build artifacts unless the task is specifically about those
  artifacts.

## AI Collaboration Workflow

Nomi has already used ChatGPT, Grok, DeepSeek, Gemini, Claude, and Codex for
design critique, synthesis, and infrastructure work. Treat AI output as design
material that must be reconciled with the repo, tests, and the user's current
intent.

For longer Codex sessions, use this loop:

1. Read this file and the most relevant design docs.
2. Restate the concrete goal and identify the files likely to change.
3. Make a short implementation plan before editing.
4. Work in focused increments: implement, test, checkpoint, continue.
5. Leave a concise note in the final answer describing changed files, checks
   run, and any unresolved risk.

When a task is large enough to span multiple prompts, create or update a
temporary task note only if it adds real continuity. A good task note captures:

- Goal.
- Current plan.
- Completed steps.
- Next exact step.
- Open questions.
- Test status.

Prefer repo-root task notes only for active handoff work requested by the user;
otherwise keep continuity in the conversation and final summary.

## Style Notes

- Python code should follow the surrounding file style and stay readable over
  clever.
- Keep comments sparse and useful, especially around parser/interpreter control
  flow.
- Tests should name the intended semantic behavior, not merely the current
  implementation detail.
- Documentation should distinguish implemented behavior, active design, and
  speculative direction.

## External References

This artifact follows the public `AGENTS.md` convention described at
https://agents.md/: a predictable Markdown file for build steps, tests,
conventions, and agent-specific context.

It also incorporates practical long-running Codex workflow patterns discussed
in the r/codex thread at
https://www.reddit.com/r/codex/comments/1t0v2da/how_are_people_getting_codex_to_work_for_longer/:
keep an agent entrypoint, write plans for large work, checkpoint progress, use
repo docs as source of truth, and break work into executable chunks instead of
depending on chat memory alone.
