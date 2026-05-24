# Technical Implementation Improvement Notes

> Status: full implementation scan from 2026-05-24.
>
> Scope: parser frontend boundaries, Rust/WASM browser path, JavaScript Core
> Runtime, runtime facade, host capabilities, generated artifacts, launch
> scripts, tests, and docs that affect implementation flexibility.

## Scan Summary

The implementation has moved in the right direction: parser frontends, eval
backends, feature metadata, host capabilities, Core IR JSON, WASM build
metadata, web manifest freshness, and contract tests now exist. That is a
useful foundation for an exploratory language project.

The main remaining risk is not missing infrastructure. The risk is that the
new infrastructure becomes only partially truthful:

```text
source -> Lark/Python AST -> Core IR -> Python/core/js backend
source -> Rust/WASM AST JSON -> JS lowerer -> JS Core Runtime
```

Those paths are fast and increasingly tested, but they still do not share a
single authoritative source-to-meaning contract. The highest-value work is to
make every implementation path declare what it accepts, what it lowers to, what
capabilities it needs, what diagnostics it emits, and which parity oracle it
uses.

## Highest-Impact Improvements

### 1. Make The Browser Source-To-Core Path A Contract, Not A Smoke Test

The browser path now has contract smoke coverage and a small Core IR parity
slice. The fragile part is still `prototype/runtime/js/lower_to_core_ir.js`.
It lowers typed Rust nodes where available, but it also re-parses many raw
strings for function heads, assignment targets, guards, patterns, slices,
pipelines, calls, `try`, `match`, `?.`, `??`, ranges, and sections.

Why this matters:

- the JS lowerer can accidentally become a second parser;
- Rust AST formatting changes can silently change browser semantics;
- source spans and structured diagnostics cannot survive string reparsing;
- the web default can drift from the Lark/Python session path while still
  producing plausible output.

First moves:

- Expand `prototype/tests/contracts/test_wasm_js_core_parity_contract.py` from
  four snippets to a feature-owned matrix: expressions, calls, block calls,
  functions with defaults, patterns, data declarations, safe navigation,
  pipelines, ranges, errors, and representative samples.
- Add expected-difference fixtures for unsupported browser constructs. A
  difference should have a named capability gap, not just "diagnostic count".
- Version the Rust AST JSON payload independently from `nomi.core-ir`.
- Replace the raw-string forms in the Rust AST payload one cluster at a time,
  starting with calls, function heads, assignment targets, patterns, and
  slices.

Acceptance gate:

```text
same source -> Python session Core IR JSON
same source -> Rust/WASM + JS Core IR JSON
normalized Core IR either matches or declares a named capability gap
```

### 2. Promote Structured Diagnostics Before Adding More Syntax

The Python runtime facade has `ExecutionResult`, passive diagnostics, events,
timings, stdout, stderr, and final-expression values. The browser worker still
mostly returns `{ error: string }` for parse, lower, and eval failures, with
only a diagnostic count from the JS lowerer.

Why this matters:

- users cannot tell which construct failed or where;
- tests cannot assert diagnostic phase/span/capability;
- web, CLI, notebook, and runtime API will drift;
- future AI tools will treat strings as the diagnostic contract.

First moves:

- Define a shared JSON diagnostic record:
  `phase`, `severity`, `message`, `span`, `source_excerpt`, `node_type`,
  `capability`, `frontend`, and `backend`.
- Change `lower_to_core_ir.js` diagnostics from a count to a list of records.
- Change `worker.js` to return the same result envelope as the Python facade
  where possible: `ok`, `bindings`, `value`, `has_value`, `stdout`, `stderr`,
  `diagnostics`, `timings`, `pipeline`.
- Add one contract test that checks a browser unsupported construct produces a
  structured lowering diagnostic.

Acceptance gate:

```text
all user-facing execution surfaces can display the same diagnostic record
without parsing exception strings
```

### 3. Split Promotion Capabilities By Host And Pipeline

`ParserFrontendCapabilities.selectable_for_execution` is truthful for the
Python runtime facade, but incomplete for the browser. The browser default uses
Rust/WASM parsing plus JS lowering even while `rust-fast-ast` remains not
selectable for normal Python-session execution.

Why this matters:

- capability tables can look contradictory;
- agents may promote a frontend too broadly;
- "runs in browser" and "safe default parser" are different claims;
- backend promotion cannot be reasoned about without host context.

First moves:

- Split parser capability flags into host-neutral facts and promotion gates:
  `parse_current_grammar`, `lower_to_python_ast`, `emit_core_json`,
  `source_spans`, `selectable_for_session_execution`,
  `selectable_for_browser_experiment`, `default_for_browser_playground`.
- Do the same for eval backends:
  `selectable_for_session_execution`, `selectable_for_browser_execution`,
  `default_for_cli`, `default_for_web`, and `requires_host_capabilities`.
- Add an inspection stage for resolved pipelines, for example:
  `python-session-default`, `browser-playground-default`, `node-core-test`.

Acceptance gate:

```text
inspection can answer "what runs here?" without reading web/app.js,
runtime/session.py, and frontend.py together
```

### 4. Make Host Capabilities Drive Runtime Wiring

`prototype/runtime/host_capabilities.json` is a good declaration point, and
tests now check that Python and JS direct runtime builtin names are declared.
The manifest does not yet drive implementation. The actual behavior still
lives in `CoreRuntimeEvaluator._default_host_calls()` and
`CoreRuntime.defaultHostCalls()`.

Why this matters:

- docs and code can agree on names while disagreeing on arity or behavior;
- adding browser/server-only capabilities will be risky;
- sandboxing, filesystem, network, randomness, time, and package access need a
  capability model before they appear;
- the manifest cannot yet generate tests or diagnostics.

First moves:

- Add manifest fields for argument shape, return shape, value-boxing mode,
  error kind, determinism, side effects, and minimum host.
- Generate host-call declaration tests from the manifest rather than checking
  only names.
- Make runtime builtin constructors register against the manifest, even if the
  call implementations stay hand-written.
- Treat JS-only `slice` as an explicit temporary backend helper and require a
  capability gap entry while it remains JS-only.

Acceptance gate:

```text
adding a host builtin requires one manifest entry and one implementation,
and tests fail if arity/effect/error metadata is missing
```

### 5. Replace Stringly Cache And Version Identity With Stable Inputs

Parser and runtime cache keys are typed, which is good. Some fields are still
placeholders, and raw tree caching uses Python's process-local `hash(code)`.
This is acceptable inside one process today, but it is not a stable identity
model for feature profiles, docs-only parsing, target-tour parsing, or
cross-process artifacts.

Why this matters:

- future feature profiles could reuse stale parsers or ASTs;
- performance wins can hide invalidation bugs;
- cache behavior is hard to inspect;
- raw tree cache keys cannot be compared across processes.

First moves:

- Replace `hash(code)` in `RawTreeCacheKey` with a deterministic digest such as
  SHA-256 or a short BLAKE2 digest.
- Feed real feature profile IDs into `ParserCacheKey` and `RuntimeCacheKey`.
- Include grammar layer content/version metadata, not only layer names.
- Add a tiny inspection helper that prints cache key inputs for a source file.

Acceptance gate:

```text
changing feature profile, grammar content, parser frontend, source text,
span mode, or eval backend cannot reuse a stale parse/lower artifact
```

### 6. Keep Generated Artifacts Declarative And Checkable

`web/manifest.json` and WASM parser outputs now have freshness checks. The
policy still lives partly in human habit: `launch_web.py` regenerates/builds
locally, while static deployment depends on committed artifacts being fresh.

Why this matters:

- web deployment can be stale even if local launch works;
- generated diffs are easy to commit without understanding why;
- the manifest is a file list, not yet a runtime bundle contract;
- no CI workflow currently enforces these checks.

First moves:

- Add a repo-level check command or script that runs:
  `python3 scripts/make_web.py --check`,
  `scripts/build_wasm.sh --check`, focused contract tests, and agent doctor.
- Add bundle metadata beside `web/manifest.json`: schema, version, generated
  by, runtime profile, sample count, file count, and maybe source digest.
- Make `launch_web.py` fail with remediation instructions when `wasm-bindgen`,
  the wasm target, or Node is missing, instead of surfacing raw subprocess
  failures.
- Keep generated artifact changes in separate commits or final-summary notes
  that explain why they changed and which `--check` passed.

Acceptance gate:

```text
fresh checkout + one check command proves web runtime artifacts are current
without launching the playground
```

### 7. Move Surface/Core Authority Upstream Of Python AST

Core IR, Core JSON, and direct runtimes are useful now, but the main session
Core path still lowers from Python AST. Python AST is a compatibility backend,
not the language definition. This is especially risky for binding, data,
match, block calls, and diagnostics.

Why this matters:

- Python AST can erase Nomi concepts before Core IR sees them;
- diagnostics inherit Python-shaped errors;
- direct runtimes can only be as Nomi-native as the Core IR they receive;
- Surface IR cannot explain features that lower directly to Python AST.

First moves:

- Introduce authoritative Surface -> Core lowering for one tiny vertical slice:
  literals, load, bind, binary op, call, function, return.
- Keep Python AST as a backend projection for that slice.
- Move `DataDecl`, `MatchExpr`, `BindingTarget`, and block-call metadata onto
  Surface nodes before adding more target syntax.
- Add inspection that can show `source -> Surface -> Core -> Python AST` for
  the supported slice.

Acceptance gate:

```text
at least one feature's meaning is inspectable without using Python AST as the
semantic source of truth
```

### 8. Give Runtime Events A Real First Producer

`RuntimeEventCollector` exists, but most parse/lower/runtime paths do not emit
semantic events yet. Without event production, explanation remains a future
promise rather than an implementation pressure.

Why this matters:

- diagnostics and explain views cannot be developed incrementally;
- feature manifests cannot prove explainability;
- AI tools lack artifact-level evidence for behavior;
- runtime tests stay locked to stdout/bindings.

First moves:

- Pick one normal form, preferably binding, and emit passive events:
  `binding.started`, `binding.constraint_checked`, `binding.committed`,
  `binding.failed`.
- Keep events off by default or collect them only when an `event_collector` is
  supplied.
- Add a contract test that events are present and stable for one binding
  example.

Acceptance gate:

```text
one implemented feature can produce a stable semantic trace without changing
user-visible behavior
```

### 9. Add Operational Controls To The Browser Worker

The worker isolates UI work from runtime work, but one long or infinite run can
still occupy the worker until restart. There is a reset path and a restart path
in the UI, but no per-run cancellation or timeout protocol.

Why this matters:

- the playground is now the fast default path and should survive experiments;
- infinite loops are common during language exploration;
- stale worker replies can confuse UI state;
- cancellation policy will matter for future notebook and REPL surfaces.

First moves:

- Add per-run request state with a timeout option.
- Add a `cancel` command that terminates and replaces the worker, rejects the
  specific pending request, and marks old replies stale.
- Include request IDs in structured error diagnostics.
- Add a browser-worker contract test using a deliberately long loop once a
  deterministic timeout hook exists.

Acceptance gate:

```text
a stuck run can be cancelled without losing the whole page state or leaving
pending promises unresolved
```

### 10. Make Feature Coverage Explicit Rather Than Derived

`SyntaxFeature` is now central enough to be valuable. Its capability matrix is
still partly inferred from status, docs, tests, and implementation fields. That
is fine for orientation, but too weak as a promotion gate.

Why this matters:

- a feature can look "run=yes" while web/notebook/reduced/diagnostic support is
  unknown;
- target-only examples can drift into runnable samples;
- agents cannot tell which tests are mandatory for a feature change;
- docs and tests can diverge from manifest status.

First moves:

- Add explicit per-feature coverage fields for parse, lower, core, run,
  reduce, diagnostics, regression, web, notebook, docs, samples, and status.
- Add a feature coverage contract test that checks declared test paths exist.
- Add a rule that runnable samples must be referenced by a feature or scenario
  manifest.
- Render the feature coverage table in docs or inspection without inferring
  unknown axes as success.

Acceptance gate:

```text
feature status can be audited from metadata, and missing coverage is visible
as unknown or no, never silently inferred as yes
```

## Suggested Pass Order

1. **Result and diagnostic schema:** define the shared record, wire browser
   worker results to it, add one unsupported-construct diagnostic test.
2. **Cross-pipeline parity matrix:** grow the source-to-Core contract tests and
   classify all current browser gaps.
3. **Rust AST payload versioning:** add schema/version metadata and replace
   raw-string forms for calls, assignment targets, function heads, and slices.
4. **Host/pipeline promotion fields:** split capability flags and add resolved
   pipeline inspection.
5. **Generated artifact check command:** add one local/release check script for
   manifest, WASM metadata, browser pipeline, and focused contracts.
6. **Surface -> Core vertical slice:** make one tiny Nomi-owned path the
   semantic source, with Python AST as backend projection.
7. **Feature coverage manifest:** move coverage status out of inference and
   into explicit per-feature data.

## Do Not Do Yet

- Do not promote `rust-fast-ast` as a general execution frontend just because
  the browser path is fast.
- Do not add more browser-only syntax support by extending raw regex lowering
  without typed payload work or parity fixtures.
- Do not make `host_capabilities.json` a large stdlib wishlist before it can
  enforce implementation metadata.
- Do not rewrite package layout before the facade/result/pipeline contracts are
  stronger.
- Do not optimize parser/runtime caches further until identity and profile
  invalidation are stable.

## Quick Check Commands

Use these after the next implementation pass:

```bash
python3 scripts/check_web_runtime.py
python3 scripts/make_web.py --check
scripts/build_wasm.sh --check
pytest prototype/tests/contracts/test_wasm_js_core_parity_contract.py
pytest prototype/tests/contracts/test_wasm_js_pipeline_contract.py
pytest prototype/tests/contracts/test_host_capabilities_contract.py
pytest prototype/tests/unit/runtime/test_js_core_runtime_backend.py
python3 .codex/scripts/agent_doctor.py
```
