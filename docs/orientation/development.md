# Developing Nomi

> Status: development guide for the current prototype.

[Documentation](../README.md) / Development

Use this page to work on the checkout, run the playground locally, set up editor
and notebook tools, and verify changes. To learn by running examples, start with
[Getting Started](../guide/getting_started.md).

For ordinary tool use and recovery, read
[Tools And Troubleshooting](../guide/tools.md). This page contains the build,
verification, and contribution details behind those instructions.

Run the commands below from the repository root. Use Python 3.12 or newer;
CI runs the full suite on Python 3.14 and checks installed-package behavior on
Python 3.12. These are prototype tools; supported syntax differs by execution path.

## Documentation Checks

Check navigation after moving a page or changing a link:

```bash
python3 scripts/check_doc_links.py
```

This dependency-free check scans the root README/changelog, `docs/`, and the
Jupyter/VS Code guides for missing local file destinations. It ignores code
examples and remote URLs. It does not validate heading anchors or remote link
availability. CI runs it in the fast smoke job. Pass Markdown filenames to
check selected pages. Executable beginner programs are checked separately by
`scripts/check_guide_examples.py`, described below.

## Python Setup And Packaging

Use a virtual environment and install the development dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e '.[dev]'
```

For a distributable wheel:

```bash
python3 -m pip wheel --no-deps .
```

The package includes grammars, host capability data, JavaScript/WASM runtime
assets and the default demo. Running `nomi` without arguments uses the packaged
demo independently of the current directory. Node.js is needed for the optional
`js-core-runtime` backend; repository development tools still need their checkout
and configuration. See [Implementation Layers](implementation_layers.md) for
orchestration, packaging and engine boundaries.

## Web Playground

The checkout's default playground uses Monaco, a Rust/WASM parser, and a JavaScript Core
runtime. Its sample list is generated from runnable files under `samples/`.
The optional Pyodide path loads required Python modules and explicitly registered
runtime data from the same manifest. Add `--legacy-pyodide` to the browser gate
to check that slower network-bootstrap path too.

The [public playground](https://durgadatta.github.io/nomi/web/) serves the current
main branch. The same browser gate checks calculation, report repair/export,
inspection, recovery and mobile layouts on the declared local or public URL.

The JS prototype rejects integers outside +/-9007199254740991 rather than
rounding them; Python supports wider integers. Target scalar semantics and
typed callbacks remain design work.

Browser text length, iteration, indexing and slicing count Unicode code points,
not grapheme clusters; normalization is not implicit. Invalid indices and
missing mapping keys fail rather than becoming `None`. The text notebook also
shows negative indices and bounded/reverse slices. Inspection distinguishes
unavailable bindings or timings from captured empty results or observed zero.

Run it locally:

The launcher normally rebuilds the browser parser. That path needs Cargo,
the Rust `wasm32-unknown-unknown` target, and the `wasm-bindgen` CLI. To serve
the committed parser assets without rebuilding, use `--no-wasm`.

```bash
python3 scripts/launch_web.py
```

Useful variants:

```bash
python3 scripts/launch_web.py --no-browser
python3 scripts/launch_web.py --no-wasm
python3 scripts/launch_web.py --port 8090
python3 scripts/make_web.py --check
scripts/build_wasm.sh --check
python3 scripts/check_web_runtime.py
python3 scripts/check_guide_examples.py
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

The check starts and stops its own local server and exercises fresh/returning
example navigation, guide discovery, the quick tour,
data/text examples, notebook export, source-linked diagnostics and repair,
worker cancellation, delayed replies, local draft recovery, keyboard controls
and desktop/mobile layouts.
It uses the committed WASM files and the same CDN assets as the live site.
Screenshots, a Playwright trace, and browser logs go to ignored
`reports/web-browser/`. Add `--headed` to watch it run, or
`--url https://durgadatta.github.io/nomi/web/` to check the published site.
Browser installation and CDN loading require network access.

`check_guide_examples.py` reads the complete programs and exact output directly
from [Language Basics](../guide/language_basics.md). It checks hosted Nomi,
reduced, and the browser's WASM/JS pipeline in Node without duplicated source
fixtures. Use `--route nomi` for a Python-only check. The full default check
requires Node and the committed WASM assets. Use `--route core-runtime` to check
the optional Python Core backend, now including the beginner text-trimming
operation. Neither selection claims whole-language parity. The default guide
check is included in the web/runtime gate.

The workbench opens local UTF-8 source without running it and downloads current
source, preserving notebook titles and framing. Edited results are visibly
marked as previous-source results. Drafts use browser-local storage; storage
failures are reported, and downloads do not depend on that storage. Stopping a
worker resets it; this is not the target language's resource-cleanup guarantee.

See [current support](../guide/status.md) and the
[delivery roadmap](project_roadmap.md). This is an experimental
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
[notebooks/nomi_calculation.ipynb](../../notebooks/nomi_calculation.ipynb).

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

See [tools/jupyter/README.md](../../tools/jupyter/README.md) for details.

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

See [VS Code Extension](vscode_extension.md).

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
- `docs/guide/`: user walkthroughs of runnable examples.
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

See [Artifacts And Usage](artifacts_and_usage.md) for the
current pipeline and [AGENTS.md](../../AGENTS.md) for engineering guidance.

## Work On A Change

Start with a concrete user task or a small failing program. Read the relevant
guide, then its target/design owner and current implementation owner. The
[roadmap](project_roadmap.md#current-support) records current support and open delivery gates. Reproduce a defect on its
actual supported path before treating it as pending.

For a documentation change, verify links, support labels, and every runnable
example you claim. For a runtime or tool change, reproduce the failure first,
repair its smallest owner, and check the affected CLI/browser/notebook/editor
path as well as the neighboring tests. Preserve a usable playground during
migration. Existing test assertions and snapshots need their repository-defined
review/authorization; see [AGENTS.md](../../AGENTS.md) and the relevant local skill.

Keep target-only programs outside `samples/`. A runnable sample change affects
regressions and the generated browser manifest; follow
[Artifacts And Usage](artifacts_and_usage.md) for its verification boundaries.
Do not commit caches, browser captures, local VSIX files, or generated reports.

In a review description, state the user-visible before/after behavior, the
changed contract, actual validation, and remaining limits. Package builds and
local browser checks are evidence for the checkout; release/deployment requires
the separate [distribution gates](project_roadmap.md#current-support).
