# Global Consistency Audit

> Status: high-impact follow-up notes from 2026-05-24.
>
> Scope: repo-wide inconsistencies exposed by the Rust/WASM browser runner,
> JavaScript Core Runtime, parser frontend registry, runtime backend registry,
> tests, docs, and generated artifacts.

## Why This Matters

Nomi now has multiple serious implementation paths:

```text
CLI/session path:
source -> Lark or rust-fast-ast -> Python AST -> Core IR -> backend

Browser default path:
source -> Rust/WASM AST JSON -> JS lowerer -> JS Core Runtime

Legacy browser bridge:
source -> Pyodide/Python modules -> Lark/Python AST interpreter
```

That is good progress, but it also means "works" can now mean several different
things. The highest-value consistency work is to make parser promotion, backend
promotion, browser defaults, diagnostics, host capabilities, and generated
artifacts use the same vocabulary and gates.

## High-Impact Findings

### 1. Promotion Vocabulary Is Overloaded

`selectable_for_execution=False` currently means "not promoted as a normal
Python/runtime frontend," but the browser default can still use the same Rust
parser technology for execution. That is defensible, but the wording makes
registry tables look contradictory.

Improvement:

- Split capability fields by host/promotion level:
  `selectable_for_session_execution`, `selectable_for_browser_experiment`,
  `default_for_browser_playground`, and eventually `default_for_cli`.
- Add one inspection table for resolved pipelines, not just parser and eval
  registries in isolation.

### 2. Source-To-Core Parity Is Now More Important Than Runtime Parity

`js-core-runtime` has decent CoreNode parity tests. The weaker point is the
browser-specific source-to-Core path in `lower_to_core_ir.js`. If the JS lowerer
produces different Core IR from the Python session path, the runtime can be
correct and still run a different language.

Improvement:

- Add golden tests comparing Core IR JSON for:
  Lark/Python session lowering versus Rust/WASM parser + JS lowering.
- Start with expression-only cells, `demo_terse.nomi`, `samples/demo.nomi`,
  block calls, patterns, errors, safe navigation, pipelines, and ranges.
- Store intentional differences as named capability gaps with diagnostics.

### 3. The Test Taxonomy Needs Enforcement

The important Rust parser execution proof now lives under
`prototype/tests/contracts/test_rust_fast_ast_execution_contract.py`, and the
Node browser-pipeline smoke has pytest coverage. The remaining risk is
regression: new tests can still drift back into retired buckets or manual-only
commands unless the docs and checks stay aligned.

Improvement:

- Keep `prototype/tests/functional/` empty of tracked tests.
- Prefer contract tests for adapter/frontend/backend promises and feature tests
  for language behavior.
- Define a dedicated `browser_pipeline` contract bucket for:
  source -> Rust/WASM parser -> JS lowerer -> JS runtime.

### 4. Generated Artifact Policy Is Split

`web/manifest.json` is generated and checked by `scripts/make_web.py --check`.
The WASM parser package under `prototype/runtime/js/pkg/` is also generated in
practice. It now has `scripts/build_wasm.sh --check` and
`prototype/runtime/js/pkg/nomi_parser_build.json`, which records the Rust
parser source hash and expected outputs. The remaining risk is policy clarity:
CI and release docs should consistently run the check and explain when generated
outputs are committed.

Improvement:

- Run `scripts/build_wasm.sh --check` in web/runtime CI or release checks.
- Document whether `prototype/runtime/js/pkg/` is committed release output or
  local build output.
- Keep `python3 scripts/make_web.py --check` as the manifest gate; no manifest
  update should be committed unless the check explains why the generated file
  changed.

### 5. Result And Diagnostic Shapes Diverge Across Hosts

`ExecutionResult` carries structured fields such as `stdout`, `stderr`,
`diagnostics`, `value`, `has_value`, `timings`, and `pipeline`. The browser
worker result currently returns a smaller ad hoc object and collapses parse,
lowering, and eval failures into strings.

Improvement:

- Define a browser `ExecutionResult` JSON shape that mirrors the Python facade
  where possible.
- Include `value` and `has_value` so expression-only cells display useful
  output.
- Use structured diagnostics with `phase`, `message`, `span`, `source_excerpt`,
  `node_type`, and `capability`.

### 6. Host Capabilities Are Ambient

Direct runtimes expose useful builtins, but the host boundary is still an
implementation table rather than a declared capability model. This matters more
now that browser, Node, Python, and future Wasm/WASI hosts can differ.

Improvement:

- Extract host capabilities into a shared manifest or generated table.
- Record availability, arity, purity, output behavior, error behavior, and
  browser/server differences.
- Make host capabilities visible through `tools.syntax.inspect` or a runtime
  inspection stage after the table exists.

### 7. Documentation Entry Points Were Out Of Sync

The top-level README and web orientation docs still described Pyodide as the
primary web runtime. Those have been refreshed, but other historical notes
still mention the old path. That is fine when explicitly marked historical, but
bad when shown as the current path.

Improvement:

- Keep `README.md`, `AGENTS.md`, `docs/orientation/artifacts_and_usage.md`,
  `.agents/skills/nomi-web/SKILL.md`, and
  `.agents/skills/nomi-interp/SKILL.md` as the small set of current-entry docs.
- Allow historical notes elsewhere, but add a short status banner when the
  file's main body describes an older Pyodide path.

## Suggested Next Commit Sequence

1. Add pytest coverage for the Node browser-pipeline smoke test.
2. Add the first cross-pipeline Core IR JSON parity fixture.
3. Introduce host-aware parser/backend promotion fields without changing
   default behavior.
