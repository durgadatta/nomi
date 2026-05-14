# Architecture Refactoring Plan

> Status: planning note for high-level refactoring.
>
> Scope: architecture boundaries, package ownership, execution pipeline shape,
> host/tool adapters, and staged migration. This is not an implementation
> patch list and should not be used to justify large rewrites without tests.

## Purpose

Nomi is ready for more syntax and semantic experiments, but the prototype still
has several broad architectural shortcuts:

- each interpreter mode has its own `usage.py` entry point;
- CLI, tests, notebook, and web bridge reach into different parts of the
  parser/runtime stack;
- the runner returns raw global bindings instead of a structured execution
  result;
- parse, lower, desugar, execute, inspect, and explain are not first-class
  pipeline stages;
- Python AST is both semantic IR and backend;
- Pyodide packaging follows the current file tree instead of a runtime bundle
  contract;
- tools learn implementation details instead of calling one stable API.

The goal of this refactor line is not to make the code "enterprise shaped."
The goal is to make the language lab faster: experiments should plug into a
declared pipeline, tools should share one execution API, and Python-hosted
bootstrap code should become one backend rather than the whole architecture.

## Architecture Target

Desired long-term shape:

```text
source input
  -> Frontend adapter: CLI, tests, notebook, web, VS Code
  -> PipelineSpec: language mode, feature profile, host target, inspection
  -> Parse stage: grammar/profile selected, raw tree, transformed tree
  -> Surface stage: Nomi-owned nodes with SourceSpan
  -> Core stage: normal forms for binding, call, block, flow, match, data
  -> Backend stage: Python AST backend today, later direct core interpreter
  -> Runtime stage: session, environment, semantic events, diagnostics
  -> ExecutionResult: values, stdout/stderr, diagnostics, trace, timings
```

The key shift is from "call a mode-specific `run_eval_loop`" to "construct a
pipeline and ask for a result."

## Refactor TODO Index

Stable IDs for broad architecture work use `NOMI-ARCH-*`. They are deliberately
larger than `NOMI-SUBSTRATE-*`, which points to syntax/lowering seams.

| ID | Theme | Current shape | Target shape | First safe move |
| --- | --- | --- | --- | --- |
| NOMI-ARCH-001 | Pipeline object | `make_runner()` wires parser, optional desugar, interpreter, and error wrapping. | A `PipelineSpec` plus `PipelineResult` names each stage and artifact. | Add passive dataclasses around current runner output without changing behavior. |
| NOMI-ARCH-002 | Mode registry | `helpers.py` lazily imports `python`, `nomi`, and `reduced` usage modules. | One registry declares parser, lowering pipeline, interpreter, feature profile, and host support. | Replace hardcoded helper registry with metadata that still returns today's callables. |
| NOMI-ARCH-003 | Frontend adapters | CLI, tests, notebook, and web bridge call parser/runtime internals differently. | All frontends depend on one public runtime API. | Introduce `prototype/runtime/api.py` as a thin adapter over current functions. |
| NOMI-ARCH-004 | Structured results | Runners return bindings or raise wrapped exceptions. | `ExecutionResult` carries bindings, printed output, diagnostics, events, timings, and optional exception. | Add result object behind an opt-in API; keep old `run_eval_loop` compatibility. |
| NOMI-ARCH-005 | Runtime session | Web cells, notebook cells, and CLI file execution each manage state differently. | `RuntimeSession` owns parser cache, environment, feature profile, cell history, reset, and cancellation policy. | Wrap web/notebook persistent execution in a shared session facade. |
| NOMI-ARCH-006 | Host boundary | Python host, Pyodide host, CLI, Docker, and notebook each know file/package details. | Host adapters expose capabilities: filesystem, stdout, timing, package loading, cancellation, and artifact fetch. | Define a host interface document before moving code. |
| NOMI-ARCH-007 | Package layering | `prototype/parser`, `prototype/grammar`, and `prototype/interpreter` are organized by implementation era. | Packages separate syntax, core semantics, backends, runtime API, and frontends. | Add new packages only as facades; migrate one feature at a time. |
| NOMI-ARCH-008 | Artifact bundle | Web manifest mirrors source files individually. | Buildable runtime artifact bundles declare version, files, samples, grammar, and feature profiles. | Add bundle metadata beside `manifest.json`; keep current file fetch path. |
| NOMI-ARCH-009 | Diagnostics and events | Parse/runtime errors are strings, Python exceptions, or test snapshots. | Shared diagnostic/event records flow through parser, lowering, runtime, web, notebook, and tests. | Define record schemas and add no-op collection hooks. |
| NOMI-ARCH-010 | Testing contract | Tests call internals directly depending on level. | Contract tests cover public runtime API, pipeline stages, feature profiles, and frontend adapters. | Add tests for the adapter while old tests continue to use internals. |
| NOMI-ARCH-011 | Compatibility layer retirement | Old imports such as `prototype.interpreter.nomi.usage` are part of the public habit. | Compatibility shims remain temporarily and emit migration comments in docs. | Keep old modules as wrappers over the new runtime API once it exists. |
| NOMI-ARCH-012 | Performance measurement | Web and tests measure some local hotspots, but pipeline timings are not shared. | Every stage can optionally report timings under the same result schema. | Add timing fields to future `ExecutionResult`; do not optimize before measuring. |

## Proposed Package Direction

This is a target map, not a rename plan.

```text
prototype/
  syntax/
    features/          # feature manifests, grammar refs, surface nodes
    surface.py         # SourceSpan and surface-node base classes
    core.py            # normal-form nodes
    lowering/          # surface -> core and core -> backend passes
  backends/
    python_ast/        # Python AST backend and compatibility lowering
    python_runtime/    # current Python-hosted interpreter facade
  runtime/
    api.py             # public execute/inspect/session API
    pipeline.py        # PipelineSpec, PipelineResult, stage orchestration
    session.py         # RuntimeSession for cells, notebook, web
    diagnostics.py     # diagnostic and semantic event records
    modes.py           # python, nomi, reduced, lab profiles
  frontends/
    cli.py             # thin wrapper for scripts/cli.py later
    web.py             # bridge shape for web/nomi_web.py later
    notebook.py        # bridge shape for tools/jupyter later
```

Existing packages should not be moved wholesale. The safer path is facade
first, migration second, cleanup last.

## Staged Refactor Sequence

### Stage 1: Public Runtime API Facade

Create a small API over current behavior:

```python
execute(source=None, filename=None, mode="nomi", profile="default") -> ExecutionResult
inspect(source=None, filename=None, mode="nomi", stage="python_ast") -> InspectionResult
create_session(mode="nomi", profile="default") -> RuntimeSession
```

Rules:

- no behavior changes;
- old `run_eval_loop` functions keep working;
- CLI, tests, notebook, and web can migrate one at a time.

### Stage 2: Pipeline Metadata

Introduce passive metadata for:

- parser function;
- parse-tree transforms;
- surface/core lowering path;
- Python AST backend path;
- interpreter class;
- desugar pipeline;
- feature profile;
- host support.

This stage should make the current three modes visible as data, not yet make
them dynamically pluggable.

### Stage 3: Structured Results And Diagnostics

Add result objects with:

- `bindings`;
- `stdout` and `stderr`, even if initially empty;
- `diagnostics`;
- `events`;
- `timings`;
- `exception`, only when the caller asks not to raise.

This should unlock cleaner web output, notebook display, and e2e tests without
changing language semantics.

### Stage 4: Session Unification

Unify:

- web file execution;
- web cell execution;
- notebook cell execution;
- future REPL execution.

The shared session should know how to reset, run one cell, run all cells,
preserve or discard environment, and eventually cancel or restart work.

### Stage 5: Syntax/Core/Backend Split

After the runtime API is stable, start migrating syntax features behind the
new substrate:

1. `BlockCall` surface node;
2. binding target and constraint nodes;
3. pipeline and placeholder lowering;
4. match expression lowering;
5. data/decode syntax.

Each migration should keep the Python AST backend working until a direct core
interpreter is real.

### Stage 6: Host And Artifact Boundary

Make web, notebook, Docker, and CLI load the same declared runtime artifact:

- source file list;
- grammar reference;
- samples;
- feature profiles;
- runtime version;
- generated bundle hash or timestamp.

The current manifest can remain the first implementation of this contract.

## Cross-Cutting Rules

- Prefer facade adapters before moving files.
- Keep compatibility imports until tests and tools migrate.
- Do not combine package moves with semantic changes.
- Every architecture refactor should have a focused contract test.
- The web playground and notebook are first-class frontends, not afterthoughts.
- Preserve Python parity tests during any backend split.
- Measure before optimizing, especially in Pyodide.
- Keep docs and skills aligned when public APIs change.

## First Three Work Packages

### Package A: Runtime API Facade

Deliver:

- `prototype/runtime/api.py`;
- `ExecutionResult` with bindings and exception fields only;
- wrappers over existing `python`, `nomi`, and `reduced` runners;
- one contract test for `execute(..., mode=...)`;
- no frontend migration yet.

Why first:

It gives every tool a stable target without disturbing internals.

Progress:

- Done in `e251351`: added `prototype.runtime.execute()` and
  `ExecutionResult` as an opt-in facade over current runners.
- Done after `e27c03c`: added read-only `prototype.runtime.inspect()` for the
  current `python_ast` artifact.
- Done after inspection facade: added `PipelineSpec` metadata shared by
  execution and inspection.
- Done after `PipelineSpec`: added coarse `total` timings to execution and
  inspection results.
- Still pending: stdout/stderr capture, diagnostics, events, detailed stage
  timings, richer inspection stages, and frontend migration.

### Package B: Mode Registry Metadata

Deliver:

- `prototype/runtime/modes.py`;
- metadata for parser, desugar path, interpreter class, status, and host notes;
- `get_run_eval_loop()` backed by this registry;
- existing tests unchanged.

Why second:

It turns "which language am I running?" into data, which later feature profiles
and inspection tools can share.

Progress:

- Done in `e27c03c`: added `prototype.runtime.modes.ModeSpec` and backed the
  legacy `get_run_eval_loop()` helper with mode metadata.
- Still pending: feature profiles, host support metadata, pipeline stage
  objects, and mode/profile selection from CLI, web, and notebook.

### Package C: Session Facade For Web And Notebook

Deliver:

- `RuntimeSession`;
- reset/run-cell/run-file methods;
- adapter use in `web/nomi_web.py` and `tools/jupyter/nomi_kernel.py`;
- timing fields for parse, lower, execute;
- focused web/notebook e2e checks.

Why third:

The most user-visible surfaces are where ad hoc state management hurts most.

Progress:

- Done after coarse timings: added `RuntimeSession` and `create_session()` as
  a persistent interpreter facade with reset/run methods and parse/lower/eval
  timings.
- Done after session facade: added opt-in AST caching to `RuntimeSession` so
  the web migration can preserve repeated-cell performance.
- Done after AST caching: moved `tools/jupyter/nomi_kernel.py` to own a
  `RuntimeSession` facade while preserving its existing notebook display logic.
- Still pending: migrate notebook execution itself through `RuntimeSession.run`
  once expression-result display has a shared result field; migrate
  `web/nomi_web.py`; then add cancellation/restart policy.

Notes from implementation:

- The first session facade intentionally mirrors current Nomi behavior:
  parse with the selected mode parser, apply a mode-declared session lowerer
  when needed, then evaluate against one persistent interpreter.
- Mode metadata now needs to distinguish human-readable lowering descriptions
  from callable lowerers used by sessions.
- Web currently adds AST caching and millisecond timing locally. The shared
  session now has optional AST caching, but web migration should preserve the
  existing millisecond timing shape until the UI consumes structured results.
- Jupyter has an IPython trait named `session`, so frontend adapters should
  avoid assuming `session` is always a safe attribute name. The kernel uses
  `runtime_session`.

Next safe extension:

- Add an optional expression-result field to `ExecutionResult` so notebook
  display-last-expression behavior can move behind `RuntimeSession.run`.

## Open Questions

1. Should `ExecutionResult` raise by default, or should all frontends receive
   structured failures and decide how to render them?
2. Should `RuntimeSession` own parser caches, or should parser caches remain
   module-level and keyed by feature profile?
3. Should `python` mode be a true language mode forever, or mainly a parity
   backend used by tests?
4. How much of `scripts/cli.py` should move into `prototype/frontends/cli.py`
   versus staying as a thin console script?
5. Should web bundles be generated as many files, one JSON payload, or a
   compressed archive?
6. When should package renames happen: after the facade exists, after one
   feature migrates, or only before a larger release?

## Non-Goals For The First Pass

- Do not rewrite the interpreter.
- Do not move the whole tree into the target package map.
- Do not replace Lark.
- Do not replace Pyodide packaging before a runtime API exists.
- Do not make dynamic external plugins.
- Do not change Nomi syntax or semantics.

## Success Criteria

This architecture refactor is working when:

- CLI, tests, notebook, and web can all call one runtime API;
- old runner imports still work as compatibility wrappers;
- each execution can optionally produce structured diagnostics and timings;
- feature profiles are declared data rather than hidden import choices;
- a syntax experiment can be parsed, inspected, and run or rejected through the
  same pipeline;
- Python AST remains a backend, not the only place where Nomi meaning exists.
