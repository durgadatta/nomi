# Browser Runtime Architecture

> Status: current architecture and promotion boundaries.

The default playground parses with Rust/WASM, lowers Rust AST JSON in
JavaScript and evaluates serialized Core IR in a worker. Pyodide is an optional
compatibility route. Neither route implements the entire target language.

```text
Browser: source -> Rust/WASM AST JSON -> JS lowerer -> JS Core runtime
Hosted:  source -> Lark/Python AST -> selected lowering/runtime backend
```

## Current Contracts

- `prototype/runtime/js/worker.js` owns browser execution results, diagnostics,
  values, bindings and timing metadata. `web/app.js` owns requests, timeouts,
  cancellation/restart and stale-result handling.
- `prototype/runtime/js/lower_to_core_ir.js` adapts Rust payloads to Core IR;
  `core_runtime.js` executes them. Shared Core shapes do not imply identical
  source coverage across frontends or hosts.
- Runtime/frontend capabilities describe supported paths. Browser support is
  checked independently from Python-facade execution promotion.
- Structured diagnostics and last-expression display are implemented. Source
  span precision and richer semantic coverage still depend on the frontend and
  lowering path; unsupported shapes must remain explicit.
- Committed WASM/JS assets carry source freshness metadata. The manifest includes
  runtime files, registered host data and runnable samples. GitHub Pages publishes
  the main-branch root, including `/web/` and its referenced runtime assets.

## Remaining Boundaries

Rust payloads still contain raw expression/head fallbacks. Their formatting and
secondary parsing couple producers to consumers. Promote one typed family at a
time with versioned shape, source identity, negative fixtures and independent
Python/browser expectations. Avoid treating a raw fallback as target semantics.

Backend parity requires source-to-result comparisons as well as Core-runtime
fixtures. Host builtin availability is a prototype contract, distinct from the
accepted effects/capability model. Worker termination provides recovery, not the
language's structured cancellation, resource cleanup or execution isolation.

## Verification

```bash
python3 scripts/check_web_runtime.py
python3 scripts/check_web_browser.py --legacy-pyodide
python3 scripts/check_web_browser.py --url https://durgadatta.github.io/nomi/web/
```

The first command checks manifest/WASM freshness and focused contracts. Browser
checks exercise actual loading, editing, calculation/report export, diagnostics
and recovery. Local compatibility checks and the published URL are separate
host observations. [Artifacts And Usage](artifacts_and_usage.md#wasm-js-pipeline-no-pyodide-path)
owns setup and asset details; the [roadmap](project_roadmap.md) owns priorities.
