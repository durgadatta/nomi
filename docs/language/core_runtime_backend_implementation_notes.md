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
- `prototype/syntax/core.py` has 17 CoreNode types plus `verify_core(strict=True)`.
  This is enough to give a future backend a stable node contract even before
  Surface -> Core lowering is authoritative for the full language.
- `RuntimeSession` already has an opt-in Core IR execution path through
  `NOMI_USE_CORE_IR=1` or a non-`python-ast` `PipelineSpec.eval_backend`.
- `core-runtime` is now registered as an unselectable prototype backend and can
  be selected explicitly for the current Core subset through
  `execute(..., eval_backend="core-runtime")`,
  `create_session(..., eval_backend="core-runtime")`, or
  `NOMI_EVAL_BACKEND=core-runtime`.

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
- Dispatch table covers all 17 CoreNode classes, even if unsupported nodes
  produce explicit diagnostics or `NotImplementedError` at first.
- Initial implemented nodes: `Module`, `Literal`, `Load`, `Bind`, `Function`,
  `Call`, `Return`, `Branch`.

Tests:
- Registry table includes `core-runtime`, but it remains unselectable.
- Parity with `python_ast` for the implemented subset.
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
- **G4**: supports all 17 CoreNode classes either semantically or through
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

## Next Implementation Slice

Broaden Core IR coverage for expressions that ordinary programs need before the
backend can run sample files: binary operations, comparisons, unary operations,
boolean operations, and assignment-like mutation. These should land as Core IR
nodes or explicit lowering rules before `core-runtime` claims full-language
support.
