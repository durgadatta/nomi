# Artifacts And Usage

> Status: orientation map for the current prototype.
>
> Scope: runtime artifacts, execution entry points, inspection commands,
> frontend/tool surfaces, and the implementation direction from Python-hosted
> bootstrap toward Nomi-owned core layers.

Nomi is currently executed through a Python-hosted prototype. Parsing is
performed by Lark, Nomi syntax is lowered through a mix of Nomi-owned surface
nodes and Python AST, and execution is handled by layered Python-hosted
interpreters.

Python is the host and bootstrap backend, not the intended semantic boundary.
For the current layer plan, read
[`core_layer_separation_plan.md`](../language/core_layer_separation_plan.md).
That plan defines:

```text
L0 runtime substrate
L1 implementation core IR
L2 semantic core
L3 canonical surface
L4 sugar reductions
L5 library conventions
L6 scoped extensions
L7 backend targets
```

The immediate implementation pressure is eval separation: L4 sugar should
reduce before evaluation, L2/L3 semantic core should lower toward L1
operations, and Python AST should become one L7 backend.

Parsing and evaluation can now be modified with substantial granularity, though the resumable-control subsystem (generator/coroutine–based) remains one of the more delicate components—functional, tested, but documented with caveats.

## Current Execution Entry Points

The installed command runs a Nomi source file:

``` bash
nomi samples/demo.nomi
```

Without installation, use the Python CLI script:

```bash
python3 scripts/cli.py samples/demo.nomi
```

The public runtime facade is available from Python:

```python
from prototype.runtime import execute, inspect, create_session

result = execute(source="x = 2\nx + 3\n", mode="nomi")
session = create_session(mode="nomi", cache_size=32)
```

Compatibility entry points such as `prototype.interpreter.*.usage.run_eval_loop`
still exist, but new frontend/tool work should prefer `prototype.runtime`.

## Current Pipeline Artifacts

The current default pipeline is:

```text
.nomi source
-> Lark parser with NomiPostLexer
-> raw Lark tree
-> transformed Lark tree
-> NomiToPythonAST transformer
-> optional SurfaceNode islands
-> Python AST backend artifact
-> optional desugar pipeline for reduced mode
-> Python-hosted interpreter
-> bindings / ExecutionResult
```

With opt-in Core IR path (`NOMI_USE_CORE_IR=1`) or an explicit eval backend
(`NOMI_EVAL_BACKEND=core-runtime`, `NOMI_EVAL_BACKEND=js-core-runtime`,
`execute(..., eval_backend="core-runtime")`, or
`create_session(..., eval_backend="js-core-runtime")`):

```text
.nomi source
-> ... Python AST artifact
-> lower_python_ast_to_core() -> Core IR (L1 nodes)
-> verify_core(strict=True)
-> eval backend dispatch (python-ast, core-direct, core-runtime, or js-core-runtime)
-> bindings / ExecutionResult
```

Core IR can also be emitted as a backend-neutral JSON payload:

```bash
python3 -m tools.syntax.inspect samples/demo.nomi --stage core-json
```

The JSON schema helpers live in `prototype/syntax/core_json.py`. The first
non-Python consumer is `prototype/runtime/js/core_runtime.js`, a JavaScript Core Runtime that
dispatches every currently registered CoreNode and can run session-lowered
`samples/demo.nomi`. The browser playground now uses the Rust/WASM parser plus
the JS lowerer by default, while the Python-side `js-core-runtime` backend
still exercises the same runtime over session-lowered Core IR through Node.

The eval backend registry is at `prototype/runtime/backends/`. Current
backends:
`python-ast` (wraps the existing interpreter behind Core IR),
`core-direct` (minimal direct CoreNode dispatch proof),
`core-runtime` (portable reference runtime with Nomi-owned values, frames, and
explicit control-flow signals), and `js-core-runtime` (Node/browser JavaScript
runtime over serialized Core IR JSON). `samples/demo.nomi` runs through both
direct runtime backends as opt-in smoke targets, and
`prototype/tests/backend_fixtures/` is the first shared cross-backend fixture
ladder. `python-ast` is the only promoted/default-selectable backend; direct
runtime backends are explicitly runnable by name but remain unpromoted as
defaults until host capability policy and broader fixture parity are settled.
Enable verification without changing the eval path with `NOMI_VERIFY_CORE=1`.

Useful files:

-   **Grammar and Parsing:** Lark is used to define the grammar and
    perform parsing. Grammars live under `prototype/grammar/`, and
    parsing logic resides under `prototype/parser/`.
-   **Feature manifests:** `prototype/syntax/features.py` is the current
    registry for grammar layers, parse transforms, lowering mixins, and
    desugar passes.
-   **Surface nodes:** `prototype/syntax/surface.py` contains early Nomi-owned
    surface artifacts such as `BlockCall`.
-   **Eval backends:** `prototype/runtime/backends/` — eval backend registry
    (`EvalBackendSpec`, `EvalBackendCapabilities`), Python AST backend adapter,
    Core IR direct evaluator, portable Core Runtime reference backend, and
    JavaScript Core Runtime wrapper.
-   **Runtime API:** `prototype/runtime/api.py`, `modes.py`, `pipeline.py`, and
    `session.py` provide the public facade and mode metadata.
-   **Execution:** Execution is handled by a layered interpreter located
    in `prototype/interpreter/`.

Additional Python and Nomi source examples live under:

```text
prototype/tests/data/sample_sources/parser/
prototype/tests/data/sample_sources/interpreter/
samples/
```

## Inspection Commands

Use these before and after grammar/lowering changes:

```bash
python3 -m tools.syntax.inspect samples/demo.nomi --stage raw-tree
python3 -m tools.syntax.inspect samples/demo.nomi --stage transformed-tree
python3 -m tools.syntax.inspect samples/demo.nomi --stage surface-ast
python3 -m tools.syntax.inspect samples/demo.nomi --stage python-ast
python3 -m tools.syntax.inspect samples/demo.nomi --stage core
python3 -m tools.syntax.inspect samples/demo.nomi --stage core-verify
python3 -m tools.syntax.inspect samples/demo.nomi --stage core-to-python
python3 -m tools.syntax.inspect samples/demo.nomi --stage backend-lowered
python3 -m tools.syntax.inspect samples/demo.nomi --stage runtime-cache-key
python3 -m tools.syntax.inspect --stage parser-frontends
python3 -m tools.syntax.inspect --stage eval-backends
python3 -m tools.syntax.inspect --stage host-capabilities
python3 -m tools.syntax.inspect --stage resolved-pipelines
python3 -m tools.syntax.inspect --stage features
python3 -m tools.syntax.inspect --stage capabilities
python3 -m tools.syntax.inspect --stage passes
python3 -m tools.syntax.inspect samples/demo.nomi --stage expansions
```

Use the runtime inspection facade:

```python
from prototype.runtime import inspect

artifact = inspect(source="x = 1\n", mode="nomi", stage="python_ast")
frontends = inspect(mode="nomi", stage="parser_frontends")
backends  = inspect(mode="nomi", stage="eval_backends")
hosts     = inspect(mode="nomi", stage="host_capabilities")
pipelines = inspect(mode="nomi", stage="resolved_pipelines")
core_ok   = inspect(source="x = 1\n", mode="python", stage="core_verify")
print(artifact.output)
```

Current stages:

```text
raw_tree, transformed_tree, surface-ast, python-ast, core
core-verify, core-to-python, backend-lowered
runtime-cache-key
features, capabilities, parser-frontends, eval-backends
host-capabilities, resolved-pipelines
passes, expansions
```

## Test Suite

The test suite is located under:

```text
prototype/tests/
```

Current buckets:

- `unit/` — parser, desugar, interpreter, runtime, and tool internals;
- `features/` — feature-owned language packets;
- `contracts/` — public runtime/tool adapter contracts;
- `regression/` — snapshot and broad-output drift checks;
- `e2e/` — user-facing CLI, notebook, report, and scenario surfaces;
- `smoke/` — tiny checkout-alive checks.

See `prototype/tests/README.md` and
[`test_suite_restructure_plan.md`](../language/test_suite_restructure_plan.md).

## Implementation Direction

Semantic extensions such as constrained binding and yield-to-block are
currently implemented through Python AST encodings, desugar passes, interpreter
overrides, and controlled runtime deviations.

Going forward, implementation work should make those layers explicit:

1. record feature layer metadata in `SyntaxFeature`;
2. preserve source spans in surface artifacts;
3. ~~define passive Core IR nodes and a verifier before changing eval~~ done —
   `prototype/syntax/core.py` (registered CoreNode dataclasses, `verify_core()`, `core_to_python_ast()`,
   `lower_python_ast_to_core()`);
4. ~~expose inspection stages through `prototype.runtime.inspect()`~~ done —
   `core`, `core-verify`, `core-to-python`, `backend-lowered`, `eval-backends`,
   host-capabilities, resolved-pipelines, plus parser-frontends, features,
   capabilities, passes, expansions;
5. keep Python AST as the compatibility backend while direct core evaluation
   grows behind opt-in env vars (`NOMI_VERIFY_CORE=1`, `NOMI_USE_CORE_IR=1`).

Do not add new permanent evaluator hooks for syntax sugar. If a construct is
L4 sugar, it should reduce to L2/L3 meaning before eval.

## AI Agent Entry Point

The repository includes a root `opencode.json` config file for AI coding
agents running under OpenCode. It sets the default model, enables `pyright` LSP
and `ruff` formatting for Python files, maps instruction files, controls
permissions, and provides commented-out templates for providers, agents,
commands, and MCP servers.

The root `AGENTS.md` file serves as the project-level working map for setup
commands, test commands, repository structure, design-document reading order,
and long-running Codex-style checkpoint workflow.

The companion process note `ai_collaboration.md` explains how
Nomi uses AI for exploration, critique, implementation planning, test pressure,
and checkpointing while treating code, tests, and active design docs as durable
evidence for the intended language, not as a frozen product contract.

These artifacts follow the public AGENTS.md convention and reflect the existing
Nomi AI collaboration history documented in `implementation_guideline.md`, the
tracked `.codex/config.toml`, and the active language-design docs.

Use `AGENTS.md` as the first stop for agent work, then follow its links into
the active design documents before changing parser, interpreter,
constraint, or yield-to-block behavior.

Repo-local Codex hooks live in `.codex/hooks.json` and `.codex/hooks/`. They
are a light reminder layer over `AGENTS.md` and `.agents/skills/`: session
startup injects the core workflow, prompt submission suggests likely skills,
and shell preflight blocks a few destructive commands. They are intentionally
not a replacement for reading the relevant docs and tests. Claude Code is wired
through `.claude/settings.json` to call the same hook scripts, keeping the
project's agent behavior consistent across both tools.

Reusable agent prompts are canonical under `.codex/prompts/`, with Claude
command shims under `.claude/commands/`. Project subagent prompts are canonical
under `.codex/agents/`, with Claude shims under `.claude/agents/`.

## Web Playground

The web playground under `web/` provides a browser-based Nomi editor backed by
Monaco. Its current default execution path uses the Rust/WASM parser,
`prototype/runtime/js/lower_to_core_ir.js`, and
`prototype/runtime/js/core_runtime.js`; the older Pyodide bridge remains in the
tree for compatibility work. It is a static site: sample programs are loaded
from `samples/*.nomi`, and the legacy Python-hosted bridge loads prototype
files listed in `web/manifest.json`.

The playground has two execution modes. `Run File` and `Ctrl+Enter` evaluate
the current editor contents from a clean interpreter session. `# %%` comments
split a file into lightweight cells; `Run Cell` and `Shift+Enter` evaluate the
current cell against the browser session, while `Run All` restarts that session
and evaluates all cells in order. The `Cells` result tab keeps a compact
input/output history beside the plain output and bindings views.

Use the launcher for local testing:

```bash
python3 scripts/launch_web.py
```

The launcher builds the WASM parser unless `--no-wasm` is passed, regenerates
the manifest, picks the requested port or the next available one, starts
`python3 -m http.server`, and opens the playground. Common options:

```bash
python3 scripts/launch_web.py --no-browser
python3 scripts/launch_web.py --no-wasm
python3 scripts/launch_web.py --port 8090
python3 scripts/launch_web.py --strict-port
```

Regenerate or check the manifest directly with:

```bash
python3 scripts/make_web.py
python3 scripts/make_web.py --check
```

`make_web.py` includes prototype `.py` and `.lark` runtime files plus
`samples/*.nomi`. When `samples/demo.nomi`, `samples/demo_terse.nomi`,
`samples/notebook_intro.nomi`, or another focused sample changes, rerun the
manifest generator before testing the web editor. The generator also writes
`web/manifest_metadata.json`, a deterministic sidecar with schema/version,
runtime profile, file/sample counts, generator name, and a digest of
`web/manifest.json`.

The browser Rust/WASM parser package is generated by:

```bash
scripts/build_wasm.sh
scripts/build_wasm.sh --check
python3 scripts/check_web_runtime.py
```

`build_wasm.sh` records `prototype/runtime/js/pkg/nomi_parser_build.json`
beside the generated JS/WASM outputs. The metadata stores the Rust parser
source hash, wasm-bindgen version, target triple, and expected output files.
When `rust_fast_ast` parser sources change, rebuild the WASM package and commit
the updated metadata with the generated outputs. `check_web_runtime.py` runs
the manifest check, WASM freshness check, focused browser/runtime contracts,
and agent doctor as one local release-readiness command.

### WASM-JS Pipeline (no-Pyodide path)

The playground also supports a lighter execution path that skips Pyodide entirely:
Nomi source is parsed by a Rust WASM parser (`nomi_parser.wasm`), lowered to
Core IR by `prototype/runtime/js/lower_to_core_ir.js`, and executed by `prototype/runtime/js/core_runtime.js`.
This path is the default in the browser playground. See
[`wasm_js_runtime_review.md`](wasm_js_runtime_review.md) for the current
architecture review and promotion risks, and
[`global_consistency_audit.md`](global_consistency_audit.md) for repo-wide
follow-up notes.

```text
.nomi source
-> Rust WASM parser (pest, nomi_parser.wasm) → Rust AST JSON
-> lower_to_core_ir.js → Core IR JSON
-> core_runtime.js → stdout, bindings
```

The Rust parser does shallow structural parsing: function defs, assignments,
suite/match/try headers are proper AST nodes, but many expressions fall through
to `Expr::Raw(String)` — the parser serializes the source span via Rust's
`Display` trait and the JS lowerer re-parses it with regex-based heuristics
(~800 lines of `lowerRawExpr`). This split was a fast-path spike to get the
playground working without Pyodide's load time.

**Known tight fits (see `performance_notes.md` for the full list):**

- **Regex expression parsing:** `lowerRawExpr` tries ~20 patterns in priority
  order with no real precedence climbing. Order-sensitive; adding a new pattern
  in the wrong position breaks existing constructs.
- **Rust Display spacing:** The Rust parser adds extra spaces in serialized
  output (`int ( "bad" )`, `items2 [ 1 : ]`) that the JS side must tolerate.
  There's no contract between the two sides.
- **Depth/quote tracking duplicated ~15 times:** Every expression parser
  reimplements the same scan loop. Bugs fixed in one won't propagate.
- **Try expressions as IIFEs:** `try EXPR except T: V` is lowered as
  `(function() { try { return EXPR } except { return V } })()` because Core IR
  only has statement-level Handle nodes. This is an implementation bridge; the
  source-level doctrine is tracked in
  `docs/convenience/expression_statement_orientation.md`.
- **Pipeline arg ordering heuristic:** Uses a `hasHoleArg` flag to decide
  whether the pipe result goes first or last. Breaks for user functions with
  signatures that don't match filter/map conventions.
- **String/sequence methods hand-coded:** `evalGetField` has inline switch
  statements covering ~10 methods. Missing many common methods.
- **Dual error model:** `callNative` returns boxed `{kind: "error"}` values
  while other eval methods throw JS exceptions directly.

Known UI issues (side-by-side scrolling, Monaco layout) are tracked in
`web/web_playground_ui_challenges.md`.

## Portable Docker Notebook

The repository can be packaged into a portable Linux-based Jupyter image with:

```bash
python3 scripts/run_nomi_docker.py
```

The launcher is designed to be the single host command for first run and reuse.
It checks for Docker, can set up Docker CLI plus Colima on macOS through
Homebrew when Docker is not ready, builds the root `Dockerfile` when needed,
starts or reuses the `nomi:jupyter` container, and opens
`notebooks/nomi_syntax_tour.ipynb` in Jupyter Lab with the local `Nomi` kernel
registered inside the container.

The Docker context is bounded by `.dockerignore`, which excludes local scratch
files, generated reports, installed JavaScript dependencies, Python caches, and
distribution artifacts while keeping source, notebooks, documentation, and AI
artifacts in the image.

The container entrypoint lives at `tools/docker/serve_nomi_notebook.py`.


## Building A New Substrate Beneath A Familiar Surface

While Python serves as Nomi’s conceptual and semantic baseline, almost all infrastructure beyond the standard AST layer has been built from the ground up. The parser is hand-rolled with Lark; the evaluator, environment model, and resumable-control mechanisms are entirely new. Python’s built-in `ast.parse` and `exec` are used only for reference tests—ensuring that, where Nomi intentionally follows Python, alignment is exact.

The implementation still uses Python’s concrete data structures (dicts, lists, objects) and function-calling mechanism, but only through thin, explicit abstraction layers. These layers are intentionally designed to be peeled away as the implementation matures—making room for a VM-based interpreter, custom bytecode, or a stack-machine execution model.

Python is thus the host, the semantic reference, and the bootstrap backend, but
not the destination. The next implementation work should turn that intention
into concrete artifacts: layer metadata, Core IR skeleton, verifier, staged
inspection, and opt-in core eval for a small subset.
