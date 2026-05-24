# Backend Independence Roadmap

> Status: concrete path sketch for making Nomi independent of Python as the
> semantic host.
>
> Related:
> [`python_independence_and_compiler_backend_plan.md`](python_independence_and_compiler_backend_plan.md),
> [`core_runtime_backend_design.md`](core_runtime_backend_design.md), and
> [`core_runtime_backend_implementation_notes.md`](core_runtime_backend_implementation_notes.md).

## North Star

Python remains a bootstrap backend and interop target, not the language
definition. All non-Python backends should consume the same verified Core IR
contract and implement the same runtime vocabulary:

```text
Core IR
-> Value model
-> Frame / environment model
-> explicit ControlFlow
-> fenced HostCapabilities
-> diagnostics / traces / result
```

The first portable target is not LLVM or a native compiler. It is the reference
Core Runtime becoming precise enough that another host can implement it without
reading Python AST or the Python interpreter.

## Shared Backend Contract

Every backend must implement these pieces before it can claim semantic parity:

- **Core IR reader:** accepts the registered CoreNode schema or a serialized
  equivalent.
- **Verifier:** rejects unsupported node shapes before execution.
- **Value model:** primitives, nil, sequence, mapping, data, function/native,
  and error values.
- **Frame model:** lexical scopes, closure capture, assignment, and export.
- **Control flow:** return, break, continue, yield/block, and errors as tagged
  signals/values.
- **Host capabilities:** print, clock, filesystem, network, packages, and
  browser/CLI IO are explicit imports, not ambient globals.
- **Result contract:** bindings, optional value, diagnostics, events, stdout,
  stderr, and backend metadata.

The Python implementation in `prototype/runtime/backends/core_runtime.py` is the
executable reference for this contract.

## Target 1: JavaScript / Web

Purpose: replace Pyodide as the long-term browser runtime while preserving the
current web playground workflow.

Concrete path:

1. Emit serialized Core IR JSON from Python tooling and load it in the browser.
   The first schema boundary now lives in `prototype/syntax/core_json.py` and
   can be inspected with `python3 -m tools.syntax.inspect FILE --stage core-json`.
2. Implement a TypeScript/JavaScript `CoreRuntime` with the same value/frame/control-flow
   variants as the Python reference.
   The first non-Python evaluator is `prototype/runtime/js/core_runtime.js`; it consumes the
   serialized Core IR payload directly, dispatches every currently registered
   CoreNode, and runs `samples/demo.nomi` after Python/Pyodide parsing and
   lowering.
3. Add browser `HostCapabilities`: stdout buffer, stdin prompt later, clock,
   cancellation, and safe module loading from the web manifest.
4. Add cross-backend tests that run small Core IR fixtures in Python
   `core-runtime` and the JavaScript runtime and compare `ExecutionResult` JSON.
   The first fixture ladder lives under `prototype/tests/backend_fixtures/`
   and is exercised against `python-ast`, `core-runtime`, and
   `js-core-runtime`.
5. Move `web/nomi_web.py` from "run Python through Pyodide" to "parse/lower
   through a bundled artifact, then execute Core IR in JS" in stages.
   A query-param opt-in now exists for the worker path:
   `web/?backend=js-core-runtime`.

Near-term compromise:

- Keep Pyodide for parsing/lowering until the Rust or JS parser can emit Core IR.
- Execute Core IR in JS for accepted fixtures first.
- Eventually ship parser + Core Runtime without Pyodide.

## Target 2: JVM Runtime

Purpose: server-side runtime, Java/Kotlin interop, and stable deployment.

Concrete path:

1. Define a JVM package around the same Core IR JSON/schema.
2. Implement a tree-walking interpreter first: sealed `Value`, `Frame`, and
   `ControlFlow` classes in Kotlin or Java.
3. Add host capabilities for stdout, files, environment, and Java interop.
4. Add a later bytecode backend only for a verified pure subset; keep dynamic
   blocks/errors in the interpreter until their ABI is settled.
5. Use Java exceptions only at backend boundaries; Core return/break/yield/error
   remain tagged runtime results.

Best first JVM milestone:

- Run arithmetic, functions, data, pattern match, loops, and host `print` from
  serialized Core IR with parity against Python `core-runtime`.

## Target 3: C Runtime / Embeddable VM

Purpose: small embeddable runtime, CLI portability, and a stable ABI for native
hosts.

Concrete path:

1. Define a C ABI around opaque `NomiValue`, `NomiFrame`, `NomiModule`, and
   `NomiResult` handles.
2. Implement a bytecode or compact Core IR interpreter in C after the Python
   reference runtime stabilizes.
3. Keep memory ownership explicit: reference counting or arena allocation first,
   tracing GC only if language semantics demand it.
4. Expose host capabilities as function-pointer tables.
5. Treat strings, sequences, mappings, data, and errors as owned runtime values,
   not borrowed host pointers.

Best first C milestone:

- Run pure Core IR fixtures with integers, strings, functions, sequence/mapping,
  and explicit errors; no parser, no package system, no foreign object model.

## Target 4: Wasm / WASI

Purpose: portable sandboxed runtime for browser/server, with a clearer boundary
than native host APIs.

Concrete path:

1. Prefer compiling the C or Rust Core Runtime to Wasm once the runtime ABI is
   stable.
2. Model host IO through WASI/component-style interfaces rather than ambient
   process globals.
3. Keep browser JS as the first host for Wasm runtime loading.
4. Use the same Core IR fixtures used by JS/JVM/C backends.

Best first Wasm milestone:

- Run the same pure Core IR fixture corpus as the C runtime in a browser worker
  and in a WASI CLI harness.

## Target 5: MLIR / LLVM / Native

Purpose: optimization and native execution for settled, typed, mostly pure
subsets.

Concrete path:

1. Do not lower full dynamic Nomi directly to LLVM.
2. Add a `nomi` MLIR dialect for pure functions, primitive ops, data
   construction, and simple control.
3. Lower gradually from verified Core IR to MLIR only when types/effects are
   known enough.
4. Call into the shared runtime ABI for allocation, strings, errors, tracing,
   dynamic calls, and host capabilities.
5. Add JIT/AOT only after interpreter parity exists for the same fixture.

Best first compiler milestone:

- Compile a pure numeric/string-free function from Core IR through MLIR/LLVM,
  then compare against `core-runtime`.

## Fixture Ladder

Backends should graduate through the same fixture ladder:

1. literals, bindings, arithmetic, comparisons;
2. functions, calls, closures, recursion;
3. sequences, mappings, data constructors, field/item access;
4. branches, loops, for-each;
5. patterns, guards, rest patterns, mapping patterns;
6. expected errors and handler matching;
7. host capabilities through a declared table;
8. block/yield calls and resume semantics;
9. constrained binding metadata and diagnostics;
10. sample programs such as `samples/demo.nomi`.

## Near-Term Repo Markers

- Keep `core-runtime` and `js-core-runtime` unpromoted as default-capable
  backends until cross-backend parity, host capability policy, and diagnostics
  tests cover the fixture ladder.
- Keep serialized Core IR inspection aligned with the executable session
  lowering path.
- Grow the first JavaScript Core Runtime (`prototype/runtime/js/core_runtime.js`) from
  current CoreNode parity toward default web playground use.
- Expand the `prototype/tests/backend_fixtures/` corpus so parity tests are not
  tied to Python AST regression fixtures or only `samples/demo.nomi`.
- Keep Pyodide web execution working while introducing a JS Core Runtime path.
- Preserve Python AST backend as the compatibility oracle until each feature has
  a Core IR fixture and direct runtime coverage.
