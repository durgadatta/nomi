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

Nomi is still an early exploratory language-design initiative. Implementation
work should preserve optionality: prefer declarative/spec-driven metadata,
registries, schemas, capability tables, and inspectable reductions over
hardcoded wiring. Treat current substrates (Python AST, Lark, Rust/WASM, JS,
Pyodide, Core IR) as replaceable laboratory tools, not as the language
definition.

## Canonical Reading Order

Start with these files before broad design or implementation changes:

- `README.md`: user-facing project vision, usage, current status, and examples.
- `docs/orientation/artifacts_and_usage.md`: current runtime pipeline and artifact
  map.
- `docs/orientation/implementation_guideline.md`: implementation posture and AI
  tool history.
- `docs/orientation/ai_collaboration.md`: AI collaboration doctrine, accepted use
  cases, and checkpoint workflow.
- `docs/orientation/exploratory_implementation_doctrine.md`: doctrine for
  flexible, declarative, reversible implementation while Nomi is exploratory.
- `docs/README.md`: docs map and current design spine.
- `docs/language/language_foundation.md`: canonical foundation for the next
  design pass.
- `docs/language/language_spec.md`: draft concrete language specification.
- `docs/language/language_design_dimensions.md`: design-space analysis — the
  irreducible axes of variation and where languages converge.
- `docs/language/language_degrees_of_freedom.md`: core/sugar/library/scoped
  freedom framework.
- `docs/language/adversarial_exploratory_implementation_critique.md`:
  skeptical critique of implementation choices that could prematurely freeze
  the language design.
- `docs/language/implementation_todos.md`: staged design and
  implementation tasks.
- `docs/features/binding_constraints_feature.md`: constrained
  binding feature pillar.
- `docs/features/block_calls_feature.md`: yield-to-block and
  block-call control design.
- `docs/language/delta_on_python.md`: rationale for Nomi changes relative to
  Python.
- `docs/features/block_calls_feature.md`: resumable-control and block-call design.
- `docs/convenience/design_lessons_and_integration.md`: design synthesis, systemic patterns, and integration critique.
- `docs/convenience/absence_and_result.md`: absence, result, and error handling design.
- `docs/research/language_family_coverage_map.md`: index of the full research
  corpus — 23 deep dives across 16 language families and 8 cross-cutting
  dimensions. Start here before doing new cross-language research.
- `docs/research/cross_language_synthesis_master.md`: capstone synthesis —
  8 convergences, 8 design forks, 7 hidden incompatibilities, Nomi resolution
  per normal form.
- `docs/research/research_notes_synthesis.md`: earlier synthesis with
  progressive-reification spine and design tensions.
- `docs/orientation/vscode_extension.md` and `tools/jupyter/README.md`: tooling
  surfaces.

The research corpus under `docs/research/` is design evidence, not active
specification. Stable decisions from deep dives should migrate to
`docs/convenience/` and `docs/language/`. The `.agents/skills/` directory
contains agent skill definitions — read the relevant skill before working
in a domain.

## Setup Commands

- Install the package locally: `python3 -m pip install -e .`
- Install development extras: `python3 -m pip install -e '.[dev]'`
- Rust parser spikes use the root `rust-toolchain.toml` (stable + `rustfmt`).
  With `rustup` installed, Cargo commands will use that project toolchain.
- Build the browser WASM parser: `scripts/build_wasm.sh`
- Check browser WASM parser freshness: `scripts/build_wasm.sh --check`
- Run the CLI: `nomi scripts/demo.nomi`
- Run without installation: `python3 scripts/cli.py scripts/demo.nomi`
- Build/run the Dockerized notebook: `python3 scripts/run_nomi_docker.py`
- Start the notebook tooling: `python3 tools/jupyter/launch_nomi_notebook.py`
- Enable the local VS Code extension:
  `python3 tools/vscode/nomi/scripts/nomi-vscode.py enable-local`

## Test Commands

- Run the full Python test suite: `pytest`
- Run a focused test file: `pytest prototype/tests/path/to/test_file.py`
- Run tests on a specific interpreter only:
  `pytest --interpreter-modes reduced`
  `NOMI_INTERPRETER_MODE=reduced pytest`
- Available interpreter modes: `python`, `nomi`, `reduced`, `all`
  (default: all three). The `--interpreter-modes` flag and
  `NOMI_INTERPRETER_MODE` env var are defined in
  `prototype/tests/conftest.py`.
- Tests that use `interpreter_mode` fixture are auto-parametrized.
  Tests that hardcode a specific interpreter import are unaffected.
- Regenerate regression snapshots after semantic changes:
  `pytest --force-regen prototype/tests/regression/test_interpreter.py`
- Generate HTML reports: `python3 scripts/test_report.py --no-open`
- Check the Nomi Jupyter kernel:
  `python3 -m tools.jupyter.check_nomi_kernel`
- Build local RAG context: `python3 -m tools.rag_mcp.cli build`
- Search local RAG context: `python3 -m tools.rag_mcp.cli search "binding constraints"`
- Regenerate web manifest: `python3 scripts/make_web.py`
- Check web manifest freshness: `python3 scripts/make_web.py --check`
- Run web playground locally: `python3 scripts/launch_web.py`
- Run web playground without opening a browser:
  `python3 scripts/launch_web.py --no-browser`

The project config currently sets pytest addopts to `-n auto`, so tests may run
in parallel. For parser/interpreter work, prefer a focused failing test first,
then the broader relevant suite.

### Test Layout

- `prototype/tests/unit/` — isolated unit tests (parser desugar passes, utilities).
- `prototype/tests/functional/` — retired compatibility bucket; do not add new
  tests here.
- `prototype/tests/regression/` — snapshot-based regression tests.
  - `test_interpreter.py` runs every ``.nomi`` / ``.py`` file in
    `data/sample_sources/interpreter/` **and** every ``.nomi`` / ``.nomi.nb``
    file in `samples/` through all three interpreter modes. Sample-file
    snapshots are namespaced with a ``sample-`` prefix (e.g.
    ``test_eval_loop_nomi_sample-demo_nomi_.txt``).
  - After a semantic change that alters output, regenerate snapshots:
    `pytest --force-regen prototype/tests/regression/test_interpreter.py`
- `prototype/tests/e2e/` — end-to-end scenarios exercising the CLI, Pyodide
  bridge behaviour, and the full runtime pipeline.
- `prototype/tests/data/sample_sources/` — fixture ``.nomi`` and ``.py`` files
  consumed by regression and functional tests.
- `samples/` — user-facing sample files (demo, block, constraint, etc.).
  These are **always** part of the regression suite; adding or renaming a
  file here requires regenerating snapshots.

## Repository Map

- `prototype/grammar/`: Lark grammar definitions.
- `prototype/parser/python/`: Python-compatible parsing and AST lowering.
- `prototype/parser/nomi/`: Nomi-specific syntax handling.
- `prototype/parser/nomi/desugar/`: AST desugaring package. Each module
  implements one reduction pass. The `pipeline.py` chains them in order.
  To add a reduction: (1) create a module with a ``BaseDesugarer`` subclass,
  (2) add it to the pipeline, (3) add the corresponding ``eval_*`` override
  in the reduced interpreter, (4) add tests under
  ``prototype/tests/unit/parser/desugar/``.
- `prototype/interpreter/python/`: Python-compatible custom interpreter layers.
- `prototype/interpreter/nomi/`: Nomi-specific runtime behavior.
- `prototype/interpreter/reduced/`: minimal-semantics interpreter; inherits from
  Nomi interpreter. Each reduction commit removes `eval_*` methods from this
  interpreter as the corresponding syntactic form is desugared at parse time.
- `prototype/interpreter/helpers.py`: dispatch helper for selecting an interpreter
  at test time via `interpreter_mode` fixture.
- `prototype/tests/`: unit, functional, regression, and end-to-end tests.
- `prototype/tests/conftest.py`: shared fixtures (`interpreter_mode`) and
  `--interpreter-modes` CLI flag for multi-interpreter testing.
- `prototype/tests/data/sample_sources/`: executable language examples and
  regression samples.
- `opencode.json`: project-level OpenCode config (model, LSP, formatter,
  permissions, instructions, etc.).
- `scripts/`: CLI, demo program, and report generation.
- `tools/jupyter/`: Nomi notebook kernel and helpers.
- `tools/docker/`: Docker container entrypoint for the notebook image.
- `tools/vscode/nomi/`: local VS Code extension scaffold.
- `tools/rag_mcp/`: local RAG index and MCP server scaffold for codebase plus
  programming-book context.
- `config/rag_sources.json`: tracked RAG source map. It points at this repo and
  a placeholder `Local_Programming_Books` folder that can later be replaced by
  the real programming-books path.
- `.agents/skills/`: generic AI assistant skill definitions shared by Codex,
  OpenCode, deepseek-tui, Claude Code, and other agents that can read a
  `SKILL.md`. See `docs/orientation/ai_collaboration.md` for the full list and
  usage.
- `docs/language/`, `docs/features/`, and `docs/research/`: active language
  design workspace grouped by concreteness.
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
- Prefer declarative/spec-driven extension points. A new syntax or runtime
  feature should name its owner, status, normal form, layer, reduction/core
  target, diagnostics, tests, and inspection surface before the implementation
  becomes hard to unwind.
- Use metadata/config/registries to drive grammar, lowering, desugar, runtime
  capabilities, host capabilities, diagnostics, tests, and generated artifacts
  whenever practical. Manual wiring is acceptable for a fenced spike, but name
  the intended extraction point.
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

When local RAG/MCP context is available, use it as a source-discovery layer for
questions about Nomi and nearby programming-language references. Prefer
`rag_search` results that cite repository paths or configured book paths, then
reconcile those results with the active docs and code before changing behavior.
Run the MCP server with:

```bash
python3 -m tools.rag_mcp.mcp_server
```

For longer Codex sessions, use this loop:

1. Read this file, `opencode.json`, and the most relevant design docs.
2. Restate the concrete goal and identify the files likely to change.
3. Make a short implementation plan before editing.
4. Work in focused increments: implement, test, checkpoint, continue.
5. For broad changes, state how the change preserves or reduces future design
   optionality.
6. Leave a concise note in the final answer describing changed files, checks
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
