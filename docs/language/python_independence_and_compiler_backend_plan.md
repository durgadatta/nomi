# Python Independence And Compiler Backend Plan

> Status: active architecture plan.
>
> Scope: staged path from the Python-hosted prototype toward a Python-independent
> Nomi implementation using modern compiler infrastructure. This is not a
> rewrite request and not an immediate LLVM implementation plan.

## Purpose

Nomi currently uses Python as a productive bootstrap substrate:

```text
Nomi source -> Lark parse tree -> Python AST -> Python-hosted interpreter
```

That is the right laboratory for fast language design. It should not become
the permanent boundary of the language.

The long-term target is:

```text
Nomi source
-> CST / parse tree
-> Nomi Surface IR
-> Nomi Core IR
-> multiple backends:
   - Python AST / Python runtime backend, for bootstrap and interop
   - direct Nomi interpreter / bytecode backend, for semantic independence
   - MLIR dialects, for staged optimization and tooling
   - LLVM IR, for native code and JIT where appropriate
   - WebAssembly/WASI, for portable sandboxed execution
```

## Source Scan

This note treats "ILR" as the likely family of IR technologies around
intermediate representations, especially MLIR and LLVM IR.

Parser independence is now tracked separately in
[Parser Frontend Decoupling Plan](parser_frontend_decoupling_plan.md). The
important boundary is that future parser frontends emit Nomi-owned CST/Surface
IR before any Python AST backend lowering.

Primary-source observations:

- The LLVM project describes itself as modular, reusable compiler/toolchain
  infrastructure with source- and target-independent optimizer/codegen
  libraries built around LLVM IR. Source: <https://llvm.org/>.
- LLVM explicitly positions itself as easy to use as an optimizer and code
  generator for new languages. Source: <https://llvm.org/>.
- MLIR is an LLVM subproject for reusable and extensible compiler
  infrastructure. It is designed to reduce compiler fragmentation, connect
  compilers, and support heterogeneous/high-level lowering. Source:
  <https://mlir.llvm.org/>.
- MLIR's language reference describes an extensible operation-based IR with
  operations, values, blocks, regions, traits, interfaces, passes, textual
  form, in-memory form, and serialized form. Source:
  <https://mlir.llvm.org/docs/LangRef/>.
- MLIR's own overview says it is not a low-level machine-code generation
  layer; that remains a better fit for LLVM. Source:
  <https://mlir.llvm.org/>.
- LLVM ORC JIT is the modern LLVM JIT API family and supports JITing LLVM IR,
  including eager and lazy compilation layers. Source:
  <https://llvm.org/docs/ORCv2.html>.
- WASI 0.2 and the WebAssembly Component Model are aimed at cross-language
  component interoperability through WIT-defined interfaces, while WASI 0.1 is
  still more widely deployed. Source: <https://wasi.dev/interfaces>.

Implication for Nomi:

```text
MLIR is the likely middle compiler layer.
LLVM IR is the low-level optimizer/codegen layer.
Wasm/WASI is the portable sandbox/runtime layer.
Python remains the bootstrap and interop layer until Nomi Core IR is real.
```

## Should Nomi Use LLVM And MLIR?

Yes, but not as the next immediate substrate.

LLVM and MLIR are valuable for Nomi if Nomi first defines its own core
semantics. Without Nomi Core IR, an LLVM backend would only encode today's
Python-shaped accidents in a lower-level form.

### Benefits

| Technology | Benefit for Nomi | Best use |
| --- | --- | --- |
| MLIR | Extensible dialects, verifier, textual dumps, pass infrastructure, staged lowering. | Represent Nomi normal forms and gradually lower them. |
| LLVM IR | Mature optimizer, native code generation, ORC JIT, many target CPUs. | Lower already-typed/settled core code to native/JIT. |
| WebAssembly | Portable low-level code format with sandboxing and browser/server runtimes. | Run Nomi outside Python and in the web without Pyodide as the core path. |
| WASI / Component Model | Typed host interfaces, capability-like system APIs, cross-language components. | Model files, clocks, HTTP, CLI, and package boundaries portably. |

### Costs And Risks

| Risk | Why it matters | Mitigation |
| --- | --- | --- |
| LLVM/MLIR complexity | Compiler infrastructure can dominate language design time. | Delay until Nomi Core IR and runtime events are stable. |
| Dynamic semantics | Closures, blocks, constraints, exceptions, dynamic dispatch, and data boundaries need a runtime model. | Build a Nomi runtime/ABI before native codegen. |
| Debuggability | Lowered native code can lose source-level explanation. | Keep source spans, event schema, and IR dumps at every stage. |
| Compile time | LLVM and MLIR can be heavy for small scripts. | Keep interpreter/bytecode mode for fast startup; compile hot modules later. |
| Python interop | Nomi's first ecosystem bridge depends on Python. | Keep Python as one backend/FFI layer, not the only implementation. |
| Web portability | LLVM native and Wasm/WASI have different host assumptions. | Define host capabilities and WIT-like interfaces early. |

## Architecture Direction

Nomi should not jump directly from Python AST to LLVM IR. The layers should be:

```text
Surface IR:
    what the user wrote, with SourceSpan

Core IR:
    Nomi normal forms: Binding, Function, Call, PatternMatch, Flow, Block,
    Data, DecodeBoundary, Result, Trace/Event

Runtime IR / Bytecode:
    executable, Python-independent semantics for dynamic language behavior

MLIR Dialects:
    optional compiler representation for optimization/lowering

LLVM IR / Wasm:
    low-level executable targets
```

### Why MLIR Before LLVM IR

LLVM IR is too low-level to represent Nomi's important user concepts directly.
Nomi needs to preserve:

- binding and constraint failures;
- decode provenance;
- pattern match shape failures;
- block policy events;
- flow stages;
- result/absence distinctions;
- source-spanned diagnostics.

MLIR can host a custom `nomi` dialect first, then lower pieces into existing
MLIR dialects and finally to LLVM IR. This keeps explanation and verification
closer to Nomi semantics.

## Proposed Backend Stack

| Layer | Initial implementation | Later implementation |
| --- | --- | --- |
| Parser/CST | `ParserFrontendSpec` with Lark + NomiPostLexer as the implemented frontend | Add Tree-sitter for editor CST/incremental parsing; possibly a Rust native parser later. |
| Surface IR | Python dataclasses in `prototype/syntax/surface.py` | Language-neutral schema, serializable text/JSON/debug dump. |
| Core IR | Python dataclasses in `prototype/syntax/core.py` | Stable Nomi Core IR with verifier and textual format. |
| Interpreter | Current Python AST interpreter | Direct Core IR interpreter or bytecode VM. |
| Compiler middle end | None | MLIR `nomi` dialect + lowering passes. |
| Native backend | None | MLIR -> LLVM dialect -> LLVM IR -> object/JIT. |
| Portable backend | Pyodide for web | Core IR interpreter in Wasm or MLIR/LLVM -> Wasm + WASI/component model. |
| Python interop | Native because host is Python | FFI/backend module that calls Python explicitly. |

## Staged Migration Plan

### Stage 0: Keep Python Productive

Goal: preserve today's tests, samples, web playground, notebook, and Python
interop while exposing architecture seams.

Work:

- keep Python AST backend working;
- keep `RuntimeSession` and `ExecutionResult` as public facade targets;
- maintain performance budgets for current path;
- avoid large rewrites before Core IR exists.

Exit gate:

- Current demo and regression suite still run.

### Stage 1: Nomi Surface IR Everywhere

Goal: stop losing user syntax too early.

Work:

- migrate `DataDecl`, `MatchExpr`, `BindingTarget`, `PipeExpr`, and syntax
  islands to `SurfaceNode`;
- preserve `SourceSpan` for these nodes;
- expose raw tree, transformed tree, surface IR, and Python AST via inspection;
- add snapshot tests for surface IR.

Exit gate:

- A target syntax feature can parse and inspect without executing.

### Stage 2: Nomi Core IR And Verifier

Goal: define Python-independent semantics.

Work:

- create `prototype/syntax/core.py`;
- define core nodes for binding, call, function, match, block, data, decode,
  flow, result, and trace;
- add a verifier for binding scopes, block ownership, pattern structure, and
  source-span presence;
- lower surface IR to core IR before Python AST backend lowering.

Exit gate:

- `demo_target.nomi` can be partially lowered into Core IR in docs-only or lab
  profile, even if it cannot run.

### Stage 3: Direct Core Interpreter Or Bytecode VM

Goal: prove Nomi can run without Python AST.

Design: [`core_runtime_backend_design.md`](core_runtime_backend_design.md) —
detailed reference architecture with Nomi-owned Value system, scoped Frame
environments, explicit ControlFlow signals, fenced host interop, and a 7-slice
implementation sequence.

Work:

- implement a small direct interpreter over Core IR for a subset:
  literals, bindings, calls, functions, simple data, `match`, `Result`, and
  pipelines;
- define Nomi runtime values independent of Python objects;
- keep Python FFI as explicit host interop;
- add cross-backend tests comparing Python AST backend and Core interpreter.

Exit gate:

- A small runnable subset executes without Python AST.

### Stage 4: MLIR Exploration Spike

Goal: test whether MLIR is the right compiler middle layer without committing
the whole language to it.

Work:

- define a minimal `nomi` MLIR dialect for pure functions, primitive values,
  data construction, calls, and simple control;
- generate textual MLIR from Core IR;
- add an MLIR verifier pass for a tiny subset;
- lower only pure numeric/string-free examples first;
- keep this behind a lab profile.

Exit gate:

- A tiny pure Nomi function can round-trip through Core IR -> textual MLIR ->
  verification/lowering experiment.

### Stage 5: LLVM / ORC JIT Backend For A Subset

Goal: use LLVM where it is strongest: optimized native code for settled,
typed, low-level-enough code.

Work:

- lower MLIR subset to LLVM-compatible IR;
- define runtime calls for allocation, strings, data, errors, and tracing;
- experiment with ORC JIT for REPL or hot functions;
- add native backend tests for pure functions and loops.

Exit gate:

- A pure subset can run through LLVM/native or JIT and match Core interpreter
  results.

### Stage 6: WebAssembly/WASI Backend

Goal: make Nomi portable and independent of Pyodide for web/server execution.

Work:

- compile the Core interpreter or compiled subset to Wasm;
- define host capabilities using a WIT-like interface model;
- target WASI 0.2/component model where supported, while recognizing WASI 0.1
  remains more widely deployed;
- keep web playground support but gradually replace Pyodide as the required
  runtime.

Exit gate:

- A Nomi module runs in a Wasm runtime with explicit host capabilities.

### Stage 7: Python Becomes One Backend

Goal: fully decouple language semantics from Python.

Work:

- keep Python backend for interop, bootstrapping, and ecosystem calls;
- make Core IR interpreter/VM the reference semantics;
- make MLIR/LLVM/Wasm backends optional performance/deployment targets;
- retire Python AST as the canonical IR.

Exit gate:

- The spec, tests, and diagnostics define Nomi behavior without referencing
  Python AST.

## Runtime And ABI Questions

Before native codegen, Nomi needs answers for:

- value representation: tagged values, boxed objects, unboxed primitives;
- strings: Unicode, grapheme/display width, memory ownership;
- data values: layout, equality, display, redaction;
- functions and closures: environment representation;
- blocks/yield: continuation or callback representation;
- errors: `Result`, exceptions, stack traces, diagnostics;
- memory management: reference counting, tracing GC, arena, or hybrid;
- host capabilities: files, time, network, random, subprocess;
- Python interop: conversion, ownership, exceptions, GIL concerns;
- debugging: source maps, trace events, IR dumps.

These questions should be answered in Core IR/runtime docs before LLVM work
goes beyond experiments.

## Recommended Near-Term Work

Do not start with LLVM codegen. Start with Nomi's own semantic substrate:

1. Add `NOMI-ARCH-018`: Python independence backend roadmap.
2. Add `NOMI-SUBSTRATE-034`: Nomi Core IR textual/debug format.
3. Add `NOMI-ARCH-019`: Nomi Core IR and verifier.
4. Add `NOMI-ARCH-020`: MLIR feasibility spike.
5. Add `NOMI-ARCH-021`: LLVM/native backend boundary.
6. Add `NOMI-ARCH-022`: Nomi runtime value/ABI plan.
7. Migrate `DataDecl`, `MatchExpr`, and `BindingTarget` to surface nodes.
8. Add cross-backend test harness shape: Python AST backend vs future Core IR
   backend.
9. Keep performance budgets on the Python path so the lab stays fast.

## Decision

Nomi should plan for MLIR/LLVM, but it should not depend on them for language
definition.

The canonical sequence is:

```text
Nomi semantics first.
Core IR second.
Direct interpreter/VM third.
MLIR/LLVM/Wasm after semantics are inspectable and tested.
```

This gives Nomi a credible path away from Python without throwing away the
current productive prototype.

## TODO Anchors

- `NOMI-ARCH-018`: keep the Python-independence roadmap visible in architecture
  planning and public runtime APIs.
- `NOMI-ARCH-019`: build a Nomi Core IR and verifier before native backend
  implementation.
- `NOMI-ARCH-020`: run an MLIR feasibility spike only after Core IR can emit a
  tiny pure subset.
- `NOMI-ARCH-021`: treat LLVM/ORC/native codegen as an optional backend for
  settled subsets, not the reference semantics.
- `NOMI-ARCH-022`: define runtime values, ABI, memory, host capabilities, and
  Python interop before compiling dynamic features.
