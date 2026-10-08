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
  [target suite](docs/design/targets/README.md) and
  [overall program](docs/design/targets/overall.nomi).
- **Current prototype:** runnable syntax implemented through Python/Lark and a
  browser Rust/WASM-to-JavaScript path. Runnable examples live in `samples/`
  and are covered by regression and web checks.

Do not assume target-only syntax runs today. Do not assume implemented syntax
will remain in the target.

## Target Shape

The current design direction favors:

```text
direct scripts and inferred local code
checked public contracts, inferred or declared
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

Use Python 3.12 or newer; CI is configured to test Python 3.14. The bootstrap
interpreter needs `ast.TypeAlias`, which Python 3.11 does not provide.

Install the current Python-hosted prototype in editable mode:

```bash
python3 -m pip install -e .
nomi samples/demo.nomi
```

Run without installation:

```bash
python3 scripts/cli.py samples/demo.nomi
```

For program-only output, add `--output program`; `--output json` returns
diagnostics and inspected binding strings separately from stdout. The legacy
debug output remains the default. Try `samples/data_pipeline.nomi` for ordered
`fold`/seeded `scan`, or `samples/text_pipeline.nomi.nb` for delimited-text
exploration. These are runnable prototype library operations, not a static
callback checker, strict CSV decoder or data/ML engine.

The current runtime parses source with Lark, lowers through Python AST and
Nomi-owned artifacts, and evaluates it with layered interpreters. Python is a
bootstrap substrate, not the future language definition.

For a distributable wheel, run `python3 -m pip wheel --no-deps .`. The package
includes grammars, host capability data, JavaScript/WASM runtime assets, and
the default demo. Running `nomi` without arguments uses that packaged demo,
independent of the current directory. Node.js is only needed for the optional
`js-core-runtime` backend. Repository development tools (Rust spikes, browser
launching, and RAG indexing) still need their checkout/configuration.

See [Implementation Layers](docs/orientation/implementation_layers.md) for
the readable orchestration and replaceable engine boundaries.

## Web Playground

The live playground uses Monaco, a Rust/WASM parser, and a JavaScript Core
runtime. Its sample list is generated from runnable files under `samples/`.
The optional Pyodide path loads required Python modules and explicitly registered
runtime data from the same manifest. Add `--legacy-pyodide` to the browser gate
to check that slower network-bootstrap path too.

The JS prototype rejects integers outside +/-9007199254740991 rather than
rounding them; Python supports wider integers. Target scalar semantics and
typed callbacks remain design work.

Browser text length, iteration, indexing and slicing count Unicode code points,
not grapheme clusters; normalization is not implicit. Invalid indices and
missing mapping keys fail rather than becoming `None`. The text notebook also
shows negative indices and bounded/reverse slices. Inspection distinguishes
unavailable bindings or timings from captured empty results or observed zero.

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

The launcher opens the browser only after its HTTP server accepts connections
and reaps the server on interruption or failed startup. Ports must be 1-65535;
if a port is busy it selects another unless `--strict-port` is set.

Notebook-style cells use `# %%`. `Shift+Enter` runs the current cell in a
persistent browser session; `Run All` restarts and evaluates top to bottom.

Check the actual browser experience (optional local dependencies):

```bash
python3 -m pip install -e '.[web-test]'
python3 -m playwright install chromium
python3 scripts/check_web_browser.py
python3 scripts/check_web_browser.py --legacy-pyodide
```

The check starts and stops its own local server and exercises the quick tour,
data/text examples, notebook export, source-linked diagnostics and repair,
worker cancellation, delayed replies, local draft recovery, keyboard controls
and desktop/mobile layouts.
It uses the committed WASM files and the same CDN assets as the live site.
Screenshots, a Playwright trace, and browser logs go to ignored
`reports/web-browser/`. Add `--headed` to watch it run, or
`--url https://durgadatta.github.io/nomi/web/` to check the published site.
Browser installation and CDN loading require network access.

The workbench opens local UTF-8 source without running it and downloads current
source, preserving notebook titles and framing. Edited results are visibly
marked as previous-source results. Drafts use browser-local storage; storage
failures are reported, and downloads do not depend on that storage. Stopping a
worker resets it; this is not the target language's resource-cleanup guarantee.

See [Unreleased Changes](CHANGELOG.md) and the
[delivery roadmap](docs/orientation/project_roadmap.md). This is an experimental
preview, not a stable or target-conforming release.

`.github/workflows/playground-ci.yml` runs the full Python suite, fast smoke
tests, the web/runtime gate, and Chromium checks on pull requests and pushes
to `main`. A separate Python 3.12 job verifies installed-wheel/CLI behavior;
the full regression corpus runs on Python 3.14. Browser
evidence is uploaded as the `playground-browser` artifact. This workflow checks
the checkout; publishing to GitHub Pages remains a separate step.
CI uses Python 3.14 and Node.js 24. Python 3.11 cannot import the current
interpreter because it lacks `ast.TypeAlias`.

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

This is a local development image, not a hardened service. The host launcher
binds localhost, generates a token for each new container, and redacts its own
credential-bearing output. Use `--token` or `NOMI_JUPYTER_TOKEN` to configure one;
blank tokens are rejected. Reuse checks the image tag, localhost port binding
and credential; incompatible containers require an explicit restart. For
`--no-browser`, retrieve the token with `docker exec nomi-jupyter jupyter server list`.
Jupyter's own logs still contain credentials; never expose this image publicly.

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
python3 -m tools.design_passes check
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
- `config/design_passes.json`: linked research/design/target/bridge pass registry.
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
[AI Collaboration](docs/orientation/ai_collaboration.md). Cross-cutting
language work uses the linked packet and retrospective contract in the
[Design Pass Workflow](docs/orientation/design_pass_workflow.md); inspect the
current passes with `python3 -m tools.design_passes list`.

## Project Posture

Nomi is early, ambitious, and explicitly unstable. There is no current source
compatibility promise. The near-term goal is not feature count: it is one
coherent target, a small trustworthy implementation, a good first hour, and
tooling that tells the truth across CLI, notebook, browser, and future native
backends.
