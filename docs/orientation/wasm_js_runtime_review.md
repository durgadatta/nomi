# WASM-JS Runtime Architecture Review

> Status: implementation review notes from 2026-05-24.
>
> Scope: the browser path that parses Nomi with the Rust/WASM parser, lowers
> Rust AST JSON in JavaScript, and evaluates Core IR in
> `prototype/runtime/js/core_runtime.js`.

## Summary

The implementation is a strong proof that the web playground no longer needs
Pyodide on the hot path. `node prototype/runtime/js/test_pipeline.js` parses all
current `samples/*.nomi`, lowers `demo_terse.nomi` and
`comprehensive.nomi` without diagnostics, and evaluates both successfully.

The main risk is not speed. The main risk is semantic drift:

```text
Lark/Python path:
source -> Lark -> Python AST -> Core IR -> runtime

Browser path:
source -> Rust/WASM AST JSON -> JS raw-expression lowerer -> Core IR -> runtime
```

Those paths share `core_runtime.js`, but they do not yet share a single
authoritative Surface/Core lowering contract. The browser can therefore become
fast while accidentally defining a different Nomi.

## Review Findings

### 1. Stale Runtime Paths Broke Python-Side JS Runtime Tests

`prototype/tests/unit/runtime/test_js_core_runtime_backend.py` still executed
`web/core_runtime.js`, but the active runtime lives at
`prototype/runtime/js/core_runtime.js`. The focused suite had seven failures
from this missing file before the test path was corrected.

Improvement:

- Keep one exported constant for the JS runtime path in tests or reuse
  `prototype.runtime.backends.js_core.JS_RUNTIME_PATH`.
- Add the Node pipeline smoke command to a pytest wrapper so CI catches browser
  pipeline moves without requiring a manual `node` command.

### 2. Browser Default Conflicts With Parser Capability Metadata

`rust-fast-ast` is marked `selectable_for_execution=False` in
`ParserFrontendSpec`, which is correct for the Python runtime facade. The
browser now uses the Rust/WASM parser as its default execution parser anyway.
That makes the capability table truthful in one host and misleading in another.

Improvement:

- Split parser capabilities into host-neutral capabilities and host-specific
  promotion gates, for example `selectable_for_python_execution` and
  `selectable_for_browser_experiment`.
- Add an inspection stage that shows the active browser pipeline:
  `rust-fast-ast-wasm -> js-lowerer -> js-core-runtime`.

### 3. Rust AST JSON Is Not Yet A Stable Contract

The Rust payload is partly typed and partly textual. Many statements and
expressions still carry strings such as suite heads, assignment targets, raw
expressions, guards, function heads, and patterns. The JS lowerer then
re-parses those strings with hand-written scans and regex ordering.

Risk:

- Rust `Display` formatting changes can break JS lowering.
- Adding syntax can require parallel changes in Rust formatting, Python AST
  adapters, and JS raw-expression parsing.
- Source spans and structured diagnostics are hard to preserve through text.

Improvement:

- Version the Rust AST JSON schema separately from Core IR JSON.
- Replace string heads with typed payloads for function heads, patterns,
  assignment targets, slices, calls, and suite clauses.
- Treat `Expr::Raw(String)` as an explicit fallback with source span and
  diagnostic, not as the normal extension mechanism.

### 4. The JS Lowerer Is Becoming A Second Parser

`prototype/runtime/js/lower_to_core_ir.js` now contains precedence logic,
top-level delimiter scans, call parsing, pipeline rules, match parsing, try
expression lowering, section handling, nullish/safe navigation, slicing, and
pattern parsing. This is real language lowering work, but it has no verifier
equivalent to the Python Core IR path before execution.

Improvement:

- Move repeated delimiter/quote scanning into one tested utility.
- Add golden tests that compare Core IR JSON from the Python session pipeline
  and the Rust/WASM+JS lowerer for the same snippets.
- For every Raw fallback accepted in the browser, add a fixture that proves the
  same source has the same stdout/bindings as the Python path.

### 5. Core Runtime Parity Is Better Than Pipeline Parity

The JS Core Runtime itself is relatively well-guarded: it dispatches registered
CoreNode types and has Python/JS parity tests for data, mappings, spread,
match, errors, yield-to-block, demo stdout, and backend selection. The new
browser pipeline bypasses that stronger Python lowering path and relies on
`lower_to_core_ir.js`.

Improvement:

- Add an end-to-end browser-pipeline fixture ladder:
  source -> Rust parser -> JS lowerer -> JS runtime.
- Compare against:
  source -> Lark -> Python AST -> Python/Core runtime.
- Track accepted differences as named capability gaps, not generic
  diagnostics.

### 6. Host Capabilities Are Still Ambient

`core_runtime.js` embeds default host calls such as `print`, `range`, `list`,
`map`, `filter`, `int`, `float`, and string/list/mapping methods. This is fine
for a playground, but it is not yet a portable runtime contract.

Improvement:

- Extract a host capability manifest shared by Python direct runtime and JS.
- Record name, arity, purity, browser availability, whether it prints, and
  whether it can raise an error value.
- Keep browser filesystem, network, time, random, and future package access
  behind explicit host capabilities.

### 7. Diagnostics Are Too Coarse For A Default User Path

The worker reports parse errors, lowering diagnostics, and eval errors as
plain strings. `lower_to_core_ir.js` exposes only a diagnostic count to the
worker in the blocking path, so the user often cannot see which construct is
unsupported or where it came from.

Improvement:

- Return structured diagnostics from the JS lowerer:
  `phase`, `message`, `span`, `source_excerpt`, `node_type`, `capability`.
- Display the first diagnostic in the cell output and keep the full list in
  the result payload for tests.
- Preserve Rust parser spans through the AST JSON and Core IR nodes.

### 8. Runtime Result Shape Drops Useful Values

`CoreRuntime.evaluate(..., { displayLastExpr: true })` can return a last
expression value, but `runWithWasmJs()` only returns stdout and bindings to the
UI. A cell whose final expression has a value but prints nothing still appears
as no output.

Improvement:

- Include `value` and `has_value` in the worker result.
- Teach the UI to display the value when stdout is empty and `has_value` is
  true.
- Add a browser pipeline test for expression-only cells.

### 9. Worker Operational Controls Need Promotion Gates

The worker model is good for isolating the UI from runtime work, but long or
infinite loops still occupy the worker until the user restarts it. There is no
per-run timeout or cancellation protocol beyond terminating the whole worker.

Improvement:

- Add a run timeout option for browser execution.
- Add a cancellation command that terminates and replaces the worker while
  rejecting pending requests cleanly.
- Include request ids in user-facing errors when a stale worker replies after
  restart.

### 10. Build And Deployment Boundaries Are Blurry

`scripts/launch_web.py` builds WASM by default, then regenerates the web
manifest and starts `http.server`. That is convenient locally, but static
deployment depends on committed/generated WASM artifacts already being present.

Improvement:

- Add `scripts/build_wasm.sh --check` or a small metadata file recording the
  Rust parser source hash used for `prototype/runtime/js/pkg/*`.
- Make `launch_web.py` print a clearer remediation when `wasm-bindgen` or the
  wasm target is missing.
- Decide whether `prototype/runtime/js/pkg/` is committed release output or a
  local generated artifact, then document that policy in `docs/orientation`.

## Priority Follow-Ups

1. Keep the corrected JS runtime path tests green and add a pytest wrapper for
   `node prototype/runtime/js/test_pipeline.js`.
2. Add cross-pipeline golden fixtures for the browser path versus the
   Lark/Python path, starting with expression-only cells, `demo_terse.nomi`,
   `samples/demo.nomi`, block calls, patterns, and errors.
3. Replace the most fragile `Expr::Raw(String)` cases with typed Rust AST JSON:
   calls, slices, function heads, pattern heads, safe navigation, and pipelines.
4. Return structured diagnostics and last-expression values from the worker.
5. Extract host capabilities into a shared manifest before adding more browser
   builtins.
6. Keep web/runtime docs aligned with the current default path so future
   reviews do not chase the old Pyodide/query-param model.
