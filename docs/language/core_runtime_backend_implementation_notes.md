# Core Runtime Backend Implementation Notes

> Status: active implementation notes for the non-Python eval backend.
>
> Parent design: [`core_runtime_backend_design.md`](core_runtime_backend_design.md).
> Tracking list: [`implementation_todos.md`](implementation_todos.md#track-0d-core-runtime-backend-python-independent-reference).

## Goal

Build a reference evaluator that consumes Core IR directly and does not depend
on Python AST, Python stack unwinding, or raw Python values as language
semantics. The implementation can be written in Python, but its public runtime
model must be portable to Rust, Wasm, LLVM, or another backend.

This backend is not the fast path. It is the reusable semantic shape:

```text
Core IR Module
-> backend registry target
-> Nomi-owned Value / Frame / ControlFlow runtime
-> EvalBackendResult
```

## Current Baseline

- `prototype/runtime/backends/python_ast.py` is the implemented execution
  backend. It lowers Core IR back to Python AST and calls the existing
  interpreter.
- `prototype/runtime/backends/core_direct.py` proves direct CoreNode dispatch,
  but it is intentionally not reusable as a native design because it uses raw
  Python dictionaries, callables, exceptions, and values.
- `prototype/syntax/core.py` has registered CoreNode dataclasses plus
  `verify_core(strict=True)`. This is enough to give a future backend a stable
  node contract even before Surface -> Core lowering is authoritative for the
  full language.
- `RuntimeSession` already has an opt-in Core IR execution path through
  `NOMI_USE_CORE_IR=1` or a non-`python-ast` `PipelineSpec.eval_backend`.
- `core-runtime` is now registered as an unselectable prototype backend and can
  be selected explicitly for the current Core subset through
  `execute(..., eval_backend="core-runtime")`,
  `create_session(..., eval_backend="core-runtime")`, or
  `NOMI_EVAL_BACKEND=core-runtime`.
- `samples/demo.nomi` now runs through the direct `core-runtime` backend as a
  smoke target. This proves executable independence from Python AST for the
  demo path, but it is not yet a default-backend promotion.
- `prototype/syntax/core_json.py` serializes verified Core IR as a
  backend-neutral JSON payload (`schema: "nomi.core-ir"`, `version: 1`).
  Inspect it with `python3 -m tools.syntax.inspect FILE --stage core-json`.
- `prototype/runtime/js/core_runtime.js` is the first non-Python evaluator. It consumes the Core
  IR JSON payload directly, dispatches every currently registered CoreNode, and
  is tested against the Python `core-runtime` for fixtures covering bindings,
  functions, calls, operations, sequences, mappings, data fields, match/rest
  patterns, error handling, for-each, yield-to-block, and stdout.
- The browser worker now has a no-Pyodide default path: Rust/WASM parser,
  `prototype/runtime/js/lower_to_core_ir.js`, then
  `prototype/runtime/js/core_runtime.js`. This is fast enough for the web
  playground, but it is a separate source-to-Core pipeline from the Python
  session path and needs cross-pipeline parity tests before default-promotion
  claims move beyond the playground.
- `js-core-runtime` is also registered in the Python eval backend registry via
  `prototype/runtime/backends/js_core.py`, which shells to Node using the same
  serialized Core IR JSON boundary.
- `prototype/tests/backend_fixtures/` is the first shared fixture ladder,
  compared across `python-ast`, `core-runtime`, and `js-core-runtime`.

## Reusable Backend Boundary

Every backend should be shaped around the same four pieces:

1. **Spec and capabilities**
   - `EvalBackendSpec` declares the backend name, IR contract, status, and
     capability flags.
   - Capability flags are promotion gates, not marketing copy. A backend should
     start unselectable until focused parity tests cover the subset it claims.

2. **Runtime values**
   - Values are backend-owned tagged data, not host primitives at semantic
     boundaries.
   - The Python reference uses dataclasses; a Rust backend can map them to an
     enum with the same variants.

3. **Environment model**
   - Evaluation happens in linked frames with explicit lookup, assignment, and
     child-frame extension.
   - Function calls extend a captured closure frame instead of mutating one flat
     global dictionary.

4. **Control-flow model**
   - Return, break, continue, yield, and expected runtime errors are explicit
     signal/value objects.
   - Python exceptions may still be used for backend bugs, but not as the
     language-level control-flow protocol.

## Slice Plan

### Slice A: Shared Runtime Kernel

Files:
- `prototype/runtime/backends/values.py`
- `prototype/runtime/backends/environment.py`
- `prototype/runtime/backends/control_flow.py`

Deliverables:
- `Value` variants for primitive values, nil, function, native host calls, data,
  and eventually runtime errors.
- `box_value()` and `unbox_value()` helpers, with unboxing treated as an API
  boundary for compatibility with current Python tests.
- `Frame` with `lookup()`, `bind()`, `assign()`, `extend()`, and a read-only
  `export_bindings()` helper for backend results.
- Explicit `ControlFlow` variants.

Tests:
- Value boxing/unboxing contract tests.
- Frame lookup, shadowing, assignment, extension, and export tests.

### Slice B: `core-runtime` Backend Registration

Files:
- `prototype/runtime/backends/core_runtime.py`
- `prototype/runtime/backends/__init__.py` only if the registry needs a
  stronger backend protocol.

Deliverables:
- `CORE_RUNTIME_SPEC` registered as `core-runtime`.
- `CoreRuntimeEvaluator.evaluate()` verifies Core IR strictly.
- Dispatch table covers every registered CoreNode class, even if unsupported nodes
  produce explicit diagnostics or `NotImplementedError` at first.
- Initial implemented nodes: `Module`, `Literal`, `Load`, `Bind`, `Function`,
  `Call`, `Return`, `Branch`.

Tests:
- Registry table includes `core-runtime`, but it remains unselectable.
- Parity with `python-ast` for the implemented subset.
- Unsupported executable nodes fail clearly instead of silently returning nil.

### Slice C: Data, Fields, and Sequences

Files:
- `core_runtime.py`
- `values.py`

Deliverables:
- `DataValue` for `ConstructData`.
- `GetField` access against `DataValue.fields`.
- `Sequence` as a first portable collection value. If list semantics are not
  settled, keep it as `SequenceValue` and unbox to Python `list`.

Tests:
- Constructed data can be bound and inspected through fields.
- Sequence unboxing matches current public result expectations.

### Slice D: Portable Control Flow

Files:
- `core_runtime.py`
- `control_flow.py`

Deliverables:
- `Loop` with `BreakSignal` and `ContinueSignal`.
- Module-level control-flow rejection.
- Function-level `ReturnSignal` handling without Python exceptions.

Tests:
- Branch and function tests prove signals do not leak into bindings.
- Loop smoke tests once Core IR can represent break/continue, or explicit
  unsupported tests until those nodes exist.

### Slice E: Pattern and Error Semantics

Files:
- `core_runtime.py`
- `values.py`

Deliverables:
- Minimal `Match` / `PatternTest` dispatch, starting with literal and wildcard
  patterns before destructuring.
- `ErrorValue`, `Raise`, and `Handle` as runtime data/control values, not host
  exceptions.

Tests:
- Literal-pattern match parity.
- Raise/handle behavior for simple error values.

### Slice F: Host Interop Fence

Files:
- `core_runtime.py`
- optional `host.py` if the interop table grows.

Deliverables:
- `NativeValue` host-call registry.
- Default host calls can include only the small functions needed by tests, such
  as `print` or `len`.
- `supports_python_interop` stays false until the fence is intentional enough
  for web/notebook use.

Tests:
- Native calls are unavailable unless supplied in the host table.
- Host-call diagnostics name the missing capability.

## Promotion Gates

The backend can graduate in these steps:

- **G1**: registered, inspectable, unselectable.
- **G2**: implements Slice A and B; parity tests pass for basic Core IR.
- **G3**: can be selected explicitly in `RuntimeSession` or a test-only
  pipeline but is still not a default backend.
- **G4**: supports every registered CoreNode class either semantically or through
  deliberate, tested rejection.
- **G5**: passes a cross-backend acceptance file set alongside `python-ast`.
- **G6**: `selectable_for_execution=True`.

## Non-Goals For The First Pass

- Do not rewrite the existing Python interpreter.
- Do not make Core IR the default execution path.
- Do not claim full language support while Core IR still contains diagnostics
  for common Python AST nodes such as binary operations and comparisons.
- Do not add Rust/Wasm codegen until the Python reference backend has a small,
  clear value/environment/control-flow contract.

## Current Direct Runtime Coverage

Implemented enough for the demo smoke path:

- default fenced host calls for `abs`, `bool`, `filter`, `float`, `int`, `len`,
  `list`, `map`, `print`, `range`, `str`, and `sum`;
- data constructors as `DataConstructorValue` producing `DataValue`;
- native host errors fenced into `ErrorValue`;
- `Handle` matching by error kind;
- block calls represented on Core `Call`;
- yield-to-block dispatch for simple caller blocks and yielded values;
- `ForEach` Core IR for `for item in sequence`.
- serialized Core IR JSON export/import for backend-neutral fixture exchange.
- JavaScript Core Runtime dispatch for every currently registered CoreNode,
  including simple yield-to-block and raise/handle semantics.
- `Defer` CoreNode with LIFO finalizer stacks in both `core-runtime` and
  `js-core-runtime`, matching `python-ast` defer ordering.
- `samples/demo.nomi` produces identical stdout across all three backends.
- `create_session(mode="nomi", eval_backend="js-core-runtime")` runs through
  the first-class backend registry and captures backend stdout/stderr into
  `ExecutionResult`.

Known parity risks before default promotion:

- annotated/constrained bindings are projected to plain `Bind`, so constraint
  metadata is not yet preserved in Core IR;
- host capabilities are a useful default table, but not yet a declared portable
  capability manifest;
- `DataValue` API unboxing is still compatibility-shaped for Python tests rather
  than a final user display/value protocol;
- block/yield support is enough for the demo but not a full resumable generator
  model.

## JS Core Runtime Operational Completion Plan

This section is the working checklist for making `js-core-runtime` maximally
functional. "Fully run `samples/demo.nomi`" means more than process success:
the JavaScript backend should execute the session-lowered Core IR, produce the
same user-facing behavior as the intended Nomi runtime, and expose any
remaining backend differences as explicit, tested decisions.

### Current Demo Audit

Command used for this audit:

```bash
python3 - <<'PY'
from pathlib import Path
from prototype.runtime import create_session

path = Path("samples/demo.nomi")
for backend in ["python-ast", "core-runtime", "js-core-runtime"]:
    result = create_session(mode="nomi", eval_backend=backend).run(
        filename=path,
        capture_output=True,
        raise_on_error=False,
    )
    print(backend, result.ok, len(result.stdout.splitlines()))
PY
```

Current status:

- `python-ast`, `core-runtime`, and `js-core-runtime` all execute
  `samples/demo.nomi` without exceptions.
- **All three backends now produce identical stdout** for
  `samples/demo.nomi`. The `Defer` CoreNode (added 2026-05-23) preserves
  LIFO defer semantics across all runtimes.
- `js-core-runtime` matches `core-runtime` for all demo bindings, including
  `count == 2`, `collected == [2, 4, 6]`, `total == 6`, `parsed == 0`, and
  `result == 49`.
- Core IR JSON preserves numeric literal kind so JS can display float-looking
  values like `5.0`, `12.0`, and `Point(x=3.0, y=5.0)` consistently with the
  Python reference runtime.
- Type aliases are not a Core concept yet. `python-ast` leaves `UserId` and
  `JsonStr` as Python classes; `core-runtime` leaks host functions for them;
  `js-core-runtime` currently omits them from exported bindings. This is a
  semantic-core gap, not only a JS gap.
- Python-shaped values such as `filter`/`map` iterators and Python class
  objects should not be treated as direct-runtime parity targets. The direct
  runtime target is Nomi-owned values and display, with `python-ast` retained
  as a compatibility oracle until Nomi display/value policy is settled.

### Completion Definition

`js-core-runtime` can be called maximally functional for the current prototype
when these gates are true:

1. `create_session(mode="nomi", eval_backend="js-core-runtime")` runs
   `samples/demo.nomi` and the backend fixture ladder without exception.
2. User-facing stdout for `samples/demo.nomi` matches the chosen direct-runtime
   oracle exactly. Until Core-owned defer/display policy lands, the temporary
   oracle is `core-runtime` plus a tracked list of intentional display gaps.
3. All currently registered CoreNode types either execute semantically in JS or
   reject with a named diagnostic that matches Python `core-runtime`.
4. Host calls used by the demo and fixture ladder are declared as capabilities,
   not ambient JS globals.
5. Browser execution through the WASM parser + JS lowerer path produces the
   same Core JSON semantics and result shape as Node tests for the supported
   subset.
6. The backend fixture ladder contains at least one fixture for each roadmap
   rung already represented in Core IR: operations, calls/recursion,
   collections/data, loops, patterns, errors, host calls, block/yield calls,
   and demo smoke.
7. Promotion remains blocked until source spans/diagnostics, constraint
   metadata, and host capability policy are explicit enough for user-facing
   default execution.

### Workstream A: Exact Demo Semantics

Goal: turn "demo executes" into "demo behavior is intentionally identical."

1. ✅ **DONE** (2026-05-23): Added `test_all_backends_demo_stdout_parity` that
   compares full stdout across `python-ast`, `core-runtime`, and
   `js-core-runtime`.
2. ✅ **DONE**: Short-term stdout oracle is `python-ast`. All three backends
   now produce identical stdout for `samples/demo.nomi`.
3. ✅ **DONE**: Fixed defer ordering by adding a `Defer` CoreNode with
   LIFO finalizer stacks in both `core-runtime` and `js-core-runtime`.
   The `lower_python_ast_to_core` path now wraps `_nomi_defer`-tagged
   statements in `Defer` nodes.
4. ✅ **DONE**: Direct-runtime display helpers already converged:
   booleans use `True`/`False`, nil uses `None`, floats preserve `.0`,
   data uses `Point(x=3.0, y=5.0)` display.
5. ✅ **DONE**: Full stdout parity tests exist across all three backends.
   The backend fixture ladder includes a defer-specific fixture
   (`06_defer_lifo.nomi`).

### Workstream B: Core IR Contract Completeness

Goal: make JS behavior follow the same Core IR contract a future JVM/C/Wasm
backend would implement.

1. Keep the static "every registered CoreNode has JS dispatch" test.
2. Add negative tests for unsupported/misplaced nodes:
   `Spread` outside `Sequence`, `PatternTest` outside `Match`/`Handle`,
   module-level `Return`, module-level `Break`, module-level `Yield`, and
   unexecutable `Diagnostic`.
3. Add a Core IR JSON schema snapshot for a compact fixture. The schema should
   document `schema`, `version`, `root`, `type`, tuple-as-array encoding, and
   literal-value limits.
4. Move Python `core-runtime` and JS display/value decisions into shared
   fixture expectations instead of ad hoc assertions inside backend tests.
5. Extend `EvalBackendResult` parity checks to include stdout, stderr,
   diagnostics, value, and `has_value`, not only selected bindings.

### Workstream C: Host Capability Manifest

Goal: make host behavior portable and inspectable.

1. Extract default host calls into a declared table for Python and JS direct
   runtimes. Minimum fields:
   `name`, `arity`, `expects_values`, `pure`, `may_print`, `may_throw`,
   `available_in_browser`, and notes.
2. Add an inspection stage or backend table column for host capabilities only
   after the table exists; avoid inventing a separate doc first.
3. Add fixture cases for `range`, `list`, `sum`, `map`, `filter`, `str`, `int`,
   `float`, `bool`, `abs`, and `len`.
4. Ensure host exceptions become `ErrorValue`/JS error values with stable
   `kind`, `message`, and optional payload fields.
5. Decide whether type aliases (`type UserId = int`) lower to metadata,
   constructor aliases, or erased declarations; then make both direct runtimes
   export or intentionally hide them consistently.

### Workstream D: Browser Operational Readiness

Goal: make the browser path prove the same runtime as Node tests.

1. Add a browser/worker contract test for the current WASM parser + JS lowerer
   + JS runtime path, not just `core_json_for_nomi()`.
2. Verify `web/manifest.json` remains fresh for the legacy Pyodide bridge while
   the JS/WASM path remains the default; run
   `python3 scripts/make_web.py --check` in every web backend commit.
3. Do not claim language-wide browser independence until the Rust/WASM parser
   and JS lowerer have cross-pipeline parity against the Lark/Python path.
4. Add a manual smoke note for local launch:
   `python3 scripts/launch_web.py --no-browser`, then open `/web/` and run
   `samples/demo.nomi`.

### Workstream E: Promotion Gates

Goal: make promotion boring and evidence-based.

`js-core-runtime` remains explicitly runnable but not promoted as default until:

- full backend fixture ladder passes against selected direct-runtime oracles;
- `samples/demo.nomi` exact stdout parity is tested or every remaining diff is
  documented as an intentional direct-runtime policy;
- host capabilities are declared and covered;
- error/diagnostic shape is stable enough for users;
- browser worker tests cover JS execution mode;
- performance is measured for demo and fixture ladder startup/eval time;
- docs consistently distinguish:
  - Python-hosted parsing/lowering,
  - Python `core-runtime` reference execution,
  - JavaScript Core Runtime execution,
  - future parser-independent browser execution.

## Next Implementation Slice

Workstream A (defer ordering + demo stdout parity) is complete. The next
slice is Workstream B (Core IR contract completeness) or Workstream C (host
capability manifest):

1. Add negative tests for unsupported/misplaced nodes (Spread outside
   Sequence, PatternTest outside Match/Handle, module-level Return/Break/
   Yield, unexecutable Diagnostic).
2. Extract default host calls into a declared capability table shared by
   Python and JS runtimes.
3. Add a Core IR JSON schema snapshot for compact fixture exchange.
4. Extend `EvalBackendResult` parity checks to include stdout, stderr,
   diagnostics, value, and `has_value`, not only selected bindings.
