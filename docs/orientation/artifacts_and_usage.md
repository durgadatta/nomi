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
The target artifact separation is defined in
[Industrial Model](../design/industrial.md):

```text
lossless CST
Surface AST
typed Surface
Core IR
module interfaces
diagnostics/events
package/build graph
```

The immediate implementation pressure is semantic separation: target
conveniences should reduce before backend evaluation, core forms should lower
to backend-independent operations, and Python AST should remain one bootstrap
backend.

For command/policy/adapter/engine ownership and incremental replacement gates,
see [Implementation Layers](implementation_layers.md).
Project-wide enhancement priorities and delivery dependencies live in the
[Project Enhancement Roadmap](project_roadmap.md).

Parsing and evaluation can now be modified with substantial granularity. The
implemented resumable-control subsystem remains delicate and tested, but the
target language no longer treats yield-to-block as its universal control or
concurrency model.

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

The CLI and Jupyter now use this facade for supported execution/session
operations; Jupyter AST/completeness and most `tools.syntax.inspect` stages use
runtime inspection too. Raw/transformed parser trees and Surface debug views
remain deliberately parser-specific inspection adapters. The inspection CLI's
`passes` and `expansions` continue to show the full reduction inventory; runtime
`inspect(mode="nomi", stage="passes")` still shows the default Nomi profile.

## Current Pipeline Artifacts

### Bounded Prototype Library And Numeric Contracts

These are current operational contracts, not target typing/effect admission.
The [generic-operation research](../research/generic_operations.md) motivates
ordinary calls rather than additional grammar or Core nodes.

| Operation | Current contract |
| --- | --- |
| `fold(items, seed, combine)` | Strict ordered left traversal; `combine(state, item)` once per visited item; empty input returns the seed; first callback failure stops traversal. |
| `scan(items, seed, combine)` | Same traversal; materialized list includes the seed, then every successive state. Empty input returns `[seed]`. States are references, not implicit deep-copy snapshots. |

Owner/layer: collections, library experiment; normal form: ordinary `Call`.
The Nomi/reduced interpreter prelude and Python/JavaScript Core host adapters
expose these names. The plain Python compatibility interpreter is unchanged.
The existing host-capability manifest records callbacks as potentially
effectful/fallible; it is inventory, not an effect checker or authority grant.
Inspect using `--stage host-capabilities` and `--stage core-json`.
Coverage includes empty/non-associative reductions, callback order/failure,
seeded history, Python reference aliasing and backend/sample comparisons.
Replace or remove the experiment when D1 closes the typed callback contract;
no syntax, parser feature, universal method or parallel-merge law is admitted.

The JavaScript prototype represents integers only in
`-9007199254740991..9007199254740991`. Unsupported literals are rejected before
program effects; arithmetic, conversion and summation overflow fail at the
operation with `NOMI-NUMERIC-RANGE`. Internal BigInt arithmetic prevents 32-bit
bitwise truncation and inaccurate integer division, but BigInt is not exposed
as a language value or JSON transport. Floats must be finite; they are not
exact arithmetic. Python retains its wider integer range. This fence repairs
silent loss without choosing the unresolved target numeric tower. The bound
follows [ECMAScript's safe-integer definition](https://tc39.es/ecma262/multipage/numbers-and-dates.html#sec-number.max_safe_integer).

Browser text length, iteration, indexing and slicing now use Unicode code
points, not UTF-16 units or grapheme clusters. No normalization is implicit:
an astral character occupies one element; a combining mark remains a separate
element. Sequence/text indexing accepts prototype integer (including Bool)
indices, resolves negatives relative to length, and rejects wrong types or
out-of-range access. Missing mapping keys fail; a present `None` remains a value.
These are compatibility repairs at Core `GetItem`, not target absence policy.

Browser slices retain the existing temporary `Call(slice, ...)` lowering.
Half-open bounds clip to length; omitted reverse bounds differ from explicit
negative bounds; zero strides and noninteger bounds fail. Sequence copies are
shallow and retain tagged values/callables; text copies preserve code points.
The host-capability record describes this fenced helper and its removal gate.
Python-AST-to-Core slice lowering is still unsupported; the Python interpreter
and structured Rust/WASM browser path are covered. Target Text/Bytes validity,
normalization, grapheme APIs, portable maps and source coordinates remain D3.

Failed facade/session execution now carries a fallback `NOMI-PARSE` or
`NOMI-RUNTIME` diagnostic while retaining the original exception and captured
output. Known binding errors keep their specific record. Source locations are
reported only when known; Lark columns are Unicode code-point positions,
browser Rust byte offsets are converted to Monaco's UTF-16 positions. Runtime
source mapping and a complete versioned result transport remain future work.

The generated browser manifest includes Python/Lark source plus explicitly
registered runtime data (`make_web.py:RUNTIME_ASSET_PATHS`), including host
capability JSON required by Pyodide initialization. Missing registered assets
fail generation; unrelated JSON is not broadly collected. An isolated-manifest
runtime test and the opt-in `check_web_browser.py --legacy-pyodide` gate cover
that boundary. The legacy adapter forwards actual pipeline metadata, captured
output and shared diagnostic records, without exposing internal tracebacks as
the user-facing error. It does not yet export arbitrary Python bindings as
portable browser values. Pyodide gets a bounded 60-second bootstrap/reset
request budget; the default WASM worker retains five seconds.

CLI `--output program` separates program output from the legacy debug dump;
`--output json` emits a `nomi.cli-inspection` v1 record with diagnostic records
and **repr strings** for bindings, not a value codec. The default stays `debug`
for existing tooling. Execution errors exit 1 without an internal traceback.
Missing-file and invalid frontend/backend setup failures also exit 1;
program/JSON modes carry `NOMI-CLI`, with a null pipeline when none resolved.
The legacy debug missing-file message remains unchanged. Argparse usage errors
retain their standard exit-2/text contract rather than an inspection envelope.


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
    Python-lowering artifacts such as `BlockCall`.
-   **Target Pattern Surface:** `prototype/syntax/pattern_surface.py` and
    `docs/design/schemas/pattern_surface.schema.json` define the target-only,
    frontend-neutral fragment artifact. Its Lark and Rust producers are
    capability-registered but do not feed normal execution.
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

See `prototype/tests/README.md` for the current layout.

## Implementation Direction

### Target Direction Inspection

The feature registry now records `target_direction` separately from prototype
`status` and execution capabilities:

```bash
python3 -m tools.syntax.inspect --stage target-alignment
```

The shared runtime facade also accepts `inspect(stage="target_alignment")`.
Both render the same registry metadata without parsing or executing supplied
source. `retain` keeps a target concept, `rework` changes its current mechanism
or surface, `retire` removes its source form from the target, and `open` leaves
its representation undecided. Missing metadata renders as `unreviewed`, never
as accepted. Each reviewed direction links its canonical contract, target
normal form and rationale.

Directions do **not** select or disable grammar, lowering, desugar passes,
runtime hooks, or samples. An implemented equation/placeholder form can still
run while its target direction is `retire`. `retain` does not imply conformance:
the retained Pattern Surface fragment still has no full-match execution.
This is migration inspection, not a target compiler or a browser UI feature.
Future direction changes belong in the existing registry, reviewed against
the linked design owner; do not add a competing feature list.

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

The playground has two execution modes. `Run` and `Ctrl+Enter` evaluate the
current program from a clean runtime session. `# %%` comments split a file into lightweight cells;
`Ctrl+Enter` evaluates the active cell against the browser session,
`Shift+Enter` evaluates and advances, and `Run all` restarts that session before
evaluating the cells in order. Each notebook cell keeps its own result record.

Notebook framing preserves column-zero marker titles, preamble comments,
whitespace and each cell's LF/CRLF convention rather than synthesizing `Cell n`
headings on load. Executable preamble text becomes a cell. This is a lightweight
marker-framed document, not a lossless language CST or a Jupyter file codec.
Uniform LF and CRLF are supported; Monaco may normalize mixed line endings.
Open/download controls use local UTF-8 source (import limit 256 KiB), never
automatically executing imported code. Models are disposed when cells are
removed; tab navigation and pane resizing support keyboard input.

Run epochs and document generations fence late results. `Run all` captures
the cells' source at its start, while individual cells share only their current
document's session. Source edits mark retained results stale and clear source
markers; known parse locations navigate to the editor only for current source.
Worker stop/timeout replaces the worker and loses its session, not a proof of
language cancellation/cleanup. Initialization failures stop rather than retry
indefinitely; Retry/restart is explicit. Samples come only from the generated
manifest; missing deployment assets cannot be hidden by embedded fallback code.

The browser workbench exposes the runtime result record directly. Each run has
`Output`, `Bindings`, `Diagnostics`, and `Pipeline` views; the last view names
the parser/lowerer/backend/host path and reports parse, lower, and evaluation
timings. Samples are searchable, editor/result and sample panes are resizable,
and the sidebar becomes a dismissible drawer on narrow screens.

Inspection displays supplied evidence, not inferred pipeline defaults. Missing
stage metadata or timings show `Unavailable`, distinct from measured zero;
missing bindings show `Bindings unavailable`, distinct from a captured empty
map. The legacy Pyodide bridge does not export arbitrary Python bindings.
Failed JS runs likewise do not claim a captured binding map. Elapsed UI time
can still be reported without pretending it is a measured engine phase.

Edits are kept as browser-local drafts per sample. `New scratch` creates a
local-only Nomi file, while the revert action returns a tracked sample to its
manifest source. These drafts are convenience state, not repository artifacts
or a persistence API.

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

`make_web.py` includes prototype `.py`/`.lark` runtime files, registered runtime
data and `samples/*.nomi`/`*.nomi.nb`. When `samples/demo.nomi`, `samples/demo_terse.nomi`,
`samples/notebook_intro.nomi.nb`, or another focused sample changes, rerun the
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
architecture review and promotion risks, and the
[`2026-07-16 design review`](../review/2026-07-16.md) for the current
project-wide follow-up plan.

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
  target source semantics are defined in `docs/design/semantics.md`.
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

Before any Docker/Homebrew setup, the launcher rejects ports outside 1-65535
and nonpositive wait/Colima resource values. Tokens are URL-encoded as a single
query value, including when they contain `&`, `#`, `+` or spaces. Launcher-owned
command logs redact token/password arguments without changing execution, and
printed URLs omit authentication query values. The browser receives the real
authenticated URL; `--no-browser` users enter their configured token at login.
This does not sanitize Jupyter's own logs or change container reuse policy. The
fixed `nomi` development token remains; this is not a publicly deployable service.

The Docker context is bounded by `.dockerignore`, which excludes local scratch
files, generated reports, installed JavaScript dependencies, Python caches, and
distribution artifacts. It also excludes `.nomi`, agent configuration trees,
`.env` files and common private-key extensions. Source, notebooks and
documentation remain in the image. These filename exclusions are a guard,
not a secret scanner or proof that the context contains no sensitive material.
Credential filename patterns use Docker's recursive `**` matching, including
nested files; see the [Docker context reference](https://docs.docker.com/build/concepts/context/#matching).

The container entrypoint lives at `tools/docker/serve_nomi_notebook.py`.


## Building A New Substrate Beneath A Familiar Surface

While Python serves as Nomi’s conceptual and semantic baseline, almost all infrastructure beyond the standard AST layer has been built from the ground up. The parser is hand-rolled with Lark; the evaluator, environment model, and resumable-control mechanisms are entirely new. Python’s built-in `ast.parse` and `exec` are used only for reference tests—ensuring that, where Nomi intentionally follows Python, alignment is exact.

The implementation still uses Python’s concrete data structures (dicts, lists, objects) and function-calling mechanism, but only through thin, explicit abstraction layers. These layers are intentionally designed to be peeled away as the implementation matures—making room for a VM-based interpreter, custom bytecode, or a stack-machine execution model.

Python is thus the host, the semantic reference, and the bootstrap backend, but
not the destination. The next implementation work should turn that intention
into concrete artifacts: layer metadata, Core IR skeleton, verifier, staged
inspection, and opt-in core eval for a small subset.
