# Nomi

Nomi is an experimental general-purpose programming language exploring a
simple question: can a language keep Python's cognitive ease while making
types, data boundaries, failure, effects, concurrency, diagnostics, and
packages coherent enough for large systems?

The project is intentionally willing to break everything before stability.
Current implementations are laboratories; the target language is defined in
[docs/design](docs/design/README.md).

> **Try the current prototype:**
> [durgadatta.github.io/nomi/web/](https://durgadatta.github.io/nomi/web/)

## Two Truths

Nomi distinguishes:

- **Target design:** the language being designed, independent of current
  parser/runtime limitations. Start with [Syntax](docs/design/syntax.md),
  [Semantics](docs/design/semantics.md), and the aspirational
  [target program](docs/design/target.nomi).
- **Current prototype:** runnable syntax implemented through Python/Lark and a
  browser Rust/WASM-to-JavaScript path. Runnable examples live in `samples/`
  and are covered by regression and web checks.

Do not assume target-only syntax runs today. Do not assume implemented syntax
will remain in the target.

## Target Shape

The current design direction favors:

```text
direct scripts and inferred local code
explicit typed public APIs
immutable names and data by default
nominal data with explicit external decode
one named function form and one match form
Option, Result, and panic as separate failure stories
visible mutation, effects, resources, and suspension
structured concurrency
shared structured diagnostics
reproducible, content-addressed packages and builds
```

The full rationale and action sequence are in the
[2026-07-16 language-design review](docs/review/2026-07-16.md).

## Quick Start

Install the current Python-hosted prototype in editable mode:

```bash
python3 -m pip install -e .
nomi samples/demo.nomi
```

Run without installation:

```bash
python3 scripts/cli.py samples/demo.nomi
```

The current runtime parses source with Lark, lowers through Python AST and
Nomi-owned artifacts, and evaluates it with layered interpreters. Python is a
bootstrap substrate, not the future language definition.

## Web Playground

The live playground uses Monaco, a Rust/WASM parser, and a JavaScript Core
runtime. Its sample list is generated from runnable files under `samples/`.

Run it locally:

```bash
python3 scripts/launch_web.py
```

Useful variants:

```bash
python3 scripts/launch_web.py --no-browser
python3 scripts/launch_web.py --port 8090
python3 scripts/make_web.py --check
scripts/build_wasm.sh --check
python3 scripts/check_web_runtime.py
```

Notebook-style cells use `# %%`. `Shift+Enter` runs the current cell in a
persistent browser session; `Run All` restarts and evaluates top to bottom.

## Jupyter

Install and launch the current Nomi kernel:

```bash
python3 tools/jupyter/launch_nomi_notebook.py
```

The kernel preserves definitions between cells and supports `%run`, `%who`,
`%reset`, and `%ast`. Start with
[notebooks/nomi_syntax_tour.ipynb](notebooks/nomi_syntax_tour.ipynb).

For the Dockerized notebook path:

```bash
python3 scripts/run_nomi_docker.py
```

See [tools/jupyter/README.md](tools/jupyter/README.md) for details.

## VS Code

The local extension provides `.nomi` registration, syntax highlighting,
snippets, run commands, symbols, hover information, and first-pass navigation.

```bash
python3 tools/vscode/nomi/scripts/nomi-vscode.py enable-local
```

For extension development:

```bash
python3 tools/vscode/nomi/scripts/nomi-vscode.py dev
```

See [VS Code Extension](docs/orientation/vscode_extension.md).

## Tests

Install development dependencies and run the full suite:

```bash
python3 -m pip install -e '.[dev]'
pytest
```

Useful focused checks:

```bash
pytest --interpreter-modes reduced
python3 scripts/check_web_runtime.py
python3 -m tools.jupyter.check_nomi_kernel
python3 .codex/scripts/agent_doctor.py
```

The default pytest configuration uses parallel workers. Runnable sample files
participate in regression tests; changing them may require snapshot
regeneration.

## Repository Map

- `docs/design/`: canonical target language.
- `docs/research/`: consolidated evidence and bounded open questions.
- `docs/orientation/`: current implementation and collaboration maps.
- `docs/review/`: dated evidence and decisions awaiting promotion.
- `prototype/grammar/`: current Lark grammars.
- `prototype/parser/`: parser and lowering experiments.
- `prototype/interpreter/`: Python-compatible, Nomi, and reduced interpreters.
- `prototype/syntax/`: feature metadata, Surface artifacts, and Core IR.
- `prototype/runtime/`: runtime sessions, result contracts, and backend APIs.
- `prototype/tests/`: unit, regression, e2e, and conformance-oriented tests.
- `samples/`: runnable user-facing programs used by regression and web checks.
- `web/`: browser playground and JavaScript runtime.
- `tools/jupyter/`: notebook kernel.
- `tools/vscode/nomi/`: editor extension.
- `tools/rag_mcp/`: local retrieval/indexing tools.
- `.agents/skills/`: repository-local agent workflows.

See [Artifacts And Usage](docs/orientation/artifacts_and_usage.md) for the
current pipeline and [AGENTS.md](AGENTS.md) for engineering guidance.

## Research And AI Collaboration

The design research compares everyday, functional, typed, systems,
concurrent, data, scientific, pedagogical, security, and deployment traditions.
It is now consolidated under [docs/research](docs/research/README.md); the old
deep-dive corpus remains available in Git history at `08f2aad`.

AI systems are used for exploration, critique, synthesis, implementation, and
validation. Their output is design material, not authority. Repository code,
tests, target decisions, and human judgment remain the checks. See
[AI Collaboration](docs/orientation/ai_collaboration.md).

## Project Posture

Nomi is early, ambitious, and explicitly unstable. There is no current source
compatibility promise. The near-term goal is not feature count: it is one
coherent target, a small trustworthy implementation, a good first hour, and
tooling that tells the truth across CLI, notebook, browser, and future native
backends.
