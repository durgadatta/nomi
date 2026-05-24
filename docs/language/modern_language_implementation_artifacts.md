# Modern Language Implementation Artifacts

> Status: active implementation research note.
>
> Scope: concrete tools, artifacts, and operating lessons from real language
> implementations. This is not a language feature proposal and not an immediate
> LLVM plan. It exists to help Nomi iterate quickly while keeping future
> implementation choices reversible.

## Purpose

Language design and implementation cannot be fully separated. A beautiful
surface becomes hard to evolve if the implementation loses source structure too
early, hides semantic decisions in one backend, or gives tools only final
strings instead of inspectable artifacts.

The practical lesson from modern language projects is not "use LLVM" or "use
Tree-sitter." It is:

```text
keep a chain of durable artifacts,
make each artifact inspectable,
verify each lowering,
share the same artifacts with tools,
and graduate backends through the same fixture ladder.
```

For Nomi, infrastructure quality matters because the language is exploratory.
Good infrastructure should make design changes cheaper: parse target-only
syntax, inspect reductions, compare backends, surface diagnostics, run examples
in the browser, and let agents/tools reason from the same pipeline instead of
private conventions.

## Source Grounding

This note is grounded in primary project documentation and implementation
artifacts, not general vibes:

- LLVM's Kaleidoscope tutorial demonstrates an iterative language frontend,
  first AST, then LLVM IR generation, optimization, JIT, control flow, mutable
  variables, and object code. Source:
  <https://llvm.org/docs/tutorial/MyFirstLanguageFrontend/>.
- LLVM positions itself as reusable compiler and toolchain infrastructure for
  optimizers, code generators, JITs, and specialized compilers. Source:
  <https://llvm.org/docs/>.
- MLIR provides extensible operation-based IR, dialects, traits, interfaces,
  regions, passes, verifiers, textual form, and dialect conversion. Sources:
  <https://mlir.llvm.org/docs/LangRef/>,
  <https://mlir.llvm.org/docs/Dialects/>,
  <https://mlir.llvm.org/docs/Passes/>.
- Rust's compiler development guide documents layered IR such as HIR and MIR;
  MIR is constructed from HIR and is manipulated by dedicated build, transform,
  and dataflow components. Sources:
  <https://rustc-dev-guide.rust-lang.org/hir.html>,
  <https://rustc-dev-guide.rust-lang.org/mir/index.html>.
- Swift documents a compiler pipeline where parsing produces an AST, semantic
  analysis/type checking follows, SIL represents Swift semantics, and IRGen
  lowers SIL to LLVM IR. Source:
  <https://www.swift.org/documentation/swift-compiler/>.
- GHC exposes many dump flags for parsed AST, typechecker output, Core, STG,
  Cmm, LLVM, timings, and pass traces. Source:
  <https://ghc.gitlab.haskell.org/ghc/doc/users_guide/ghc.html>.
- Tree-sitter is an incremental parsing library and parser generator designed
  to build concrete syntax trees, update them during edits, remain robust under
  syntax errors, and embed in editors. Source:
  <https://tree-sitter.github.io/>.
- LSP standardizes JSON-RPC communication between editors and language servers
  for completion, definition, references, diagnostics, hover, and related
  language intelligence. Source:
  <https://microsoft.github.io/language-server-protocol/>.
- WebAssembly specifies a portable low-level core with validation,
  instantiation, execution, binary format, and text format; embeddings live in
  separate specifications. Source:
  <https://webassembly.github.io/spec/core/>.
- The WebAssembly Component Model and WIT define language-agnostic component
  interfaces and worlds; WIT defines contracts, not behavior. Source:
  <https://component-model.bytecodealliance.org/design/wit.html>.
- Cranelift is a fast compiler backend used by Wasmtime for JIT and AOT
  compilation, designed to be embedded behind a frontend-produced IR. Source:
  <https://cranelift.dev/>.
- Roslyn exposes compiler stages as APIs: syntax trees, declaration/symbol
  tables, semantic analysis, diagnostics, analyzers, and IL emit. Source:
  <https://learn.microsoft.com/en-us/dotnet/csharp/roslyn-sdk/compiler-api-model>.
- TypeScript exposes `Program`, `CompilerHost`, and `TypeChecker` APIs that
  tools use to query semantic information and emit artifacts. Source:
  <https://github.com/microsoft/TypeScript/wiki/Using-the-Compiler-API>.

## What Mature Language Implementations Actually Keep

The recurring artifact set is remarkably consistent.

| Artifact | What it preserves | Real examples | Nomi meaning |
| --- | --- | --- | --- |
| Lossless or tolerant CST | Source shape, trivia, incomplete code, editor recovery. | Tree-sitter CST; Roslyn syntax trees. | Keep parser-frontends producing Nomi-owned CST/Surface artifacts; do not make Python AST the first durable shape. |
| Surface AST / HIR | User concepts after parsing but before low-level lowering. | Rust HIR; Swift AST; Roslyn symbols and bound trees. | `SurfaceNode` should cover `BindingTarget`, `DataDecl`, `MatchExpr`, `PipeExpr`, block calls, and future syntax islands. |
| Semantic IR | Meaning after name resolution, typing/checking, and desugaring. | Rust MIR; Swift SIL; GHC Core/STG. | Nomi Core IR should own binding, function, call, pattern, flow, block, data, result, and explanation normal forms. |
| Verifier | Rejection of impossible or unsupported lowered forms. | MLIR verifiers; Wasm validation; Core/STG lint-style dumps. | `verify_core(strict=True)` should become promotion-critical, not just inspection. |
| Pass pipeline | Named lowering, optimization, canonicalization, and cleanup steps. | MLIR pass infrastructure; LLVM pass managers; GHC pass dumps. | Desugar and lowering passes should remain feature-owned and inspectable. |
| Text/debug dumps | Human-readable intermediate artifacts. | GHC `-ddump-*`; MLIR textual IR; LLVM IR; Tree-sitter parse output. | `tools.syntax.inspect` is central, not auxiliary. Every new feature should add inspection evidence. |
| Queryable semantic model | Tool APIs for type/symbol/diagnostic/refactor queries. | TypeScript `TypeChecker`; Roslyn semantic model; LSP servers. | Nomi tooling should query one pipeline rather than duplicate compiler logic in web, notebook, or editor code. |
| Runtime result shape | Values, output, diagnostics, events, timings, exceptions. | Language services, test runners, notebook kernels, browser playgrounds. | `ExecutionResult` should be the shared output/error/event contract. |
| Cross-backend fixtures | Same programs through multiple implementations. | Rust/LLVM/Cranelift experiments; Wasmtime test suites; compiler regression corpora. | `prototype/tests/backend_fixtures/` should become the backend graduation ladder. |
| Host/interface model | Explicit imports, capabilities, IO, component boundaries. | WASI/WIT; Wasmtime host imports; Swift/Rust FFI boundaries. | Files, network, clock, stdout, packages, and secrets should be host capabilities, not ambient globals. |

## Tool Lessons

### LLVM

LLVM is excellent when the language has already reached a low-level, typed, and
settled representation. It gives Nomi eventual native code generation, ORC JIT,
object emission, mature optimization, and many CPU targets.

What it does not give Nomi:

- a source language design;
- high-level data-boundary semantics;
- string/path/URL/security policy;
- binding diagnostics;
- pattern failure explanation;
- browser/editor tooling by itself.

Nomi should treat LLVM as a backend for settled Core/MLIR subsets, not as the
semantic center.

### MLIR

MLIR is the strongest fit for Nomi's future compiler middle layer because it
lets a project define dialects that retain higher-level meaning and then lower
gradually. That matches Nomi's need for inspectable reductions:

```text
Nomi Surface
-> Nomi Core
-> optional nomi MLIR dialect
-> lower to standard/LLVM/Wasm-facing dialects
-> LLVM IR or other backend
```

The risk is complexity. A `nomi` dialect should wait until Core IR and the
runtime fixture ladder are stable enough that MLIR is representing Nomi, not
today's Python-AST residue.

### Cranelift

Cranelift is attractive for a faster, simpler codegen path than LLVM in some
JIT/AOT contexts, especially around WebAssembly and embedders. It is not a
replacement for a semantic IR. Like LLVM, it wants a frontend-produced IR and
clear runtime ABI.

Nomi should keep it as a later backend candidate for a compact VM/JIT path,
especially if Wasm/server embedding becomes important.

### WebAssembly, WASI, And WIT

Wasm is a portable execution target and sandbox boundary. WIT is a practical
model for host contracts: interfaces and worlds define what a component may
import or export.

For Nomi this suggests:

- model host capabilities early: stdout, files, clock, network, packages,
  cancellation, environment, secrets;
- keep browser and CLI behavior behind the same capability vocabulary;
- prefer Core IR runtime-in-Wasm before compiling all dynamic Nomi directly to
  Wasm instructions.

### Tree-Sitter

Tree-sitter is most valuable for editor-grade parsing: incremental updates,
tolerant trees, useful structure under syntax errors, and small embeddable
runtime. It should not silently become the language definition.

Nomi's existing parser-frontend acceptance and Python-AST equivalence rules are
the right posture. Tree-sitter can be an editor CST frontend first, and an
execution parser only after it matches the accepted source and lowering
contracts.

### LSP, Roslyn, TypeScript, SourceKit-Style Tooling

Modern language experience depends on exposing compiler knowledge through
stable APIs:

- diagnostics with ranges and codes;
- hover and signature help;
- go-to-definition and references;
- semantic tokens;
- code actions;
- formatter and organize-import behavior;
- "show expansion" or "show lowering" actions for sugar.

The important artifact is the analysis service, not only the editor extension.
Nomi should have one analysis/runtime pipeline that CLI, web, notebook, VS Code,
agents, and tests can query.

### GHC-Style Dumps And Rust/Swift IR Layers

GHC's dump flags and Rust/Swift's named IR layers show an important cultural
practice: implementation internals become user/developer artifacts. This makes
language evolution less mystical. People can see what parsing, type checking,
desugaring, simplification, and code generation did.

Nomi already has the beginning of this in `tools.syntax.inspect`. The next
quality bar is to make every promoted feature explain its artifacts at each
stage.

## Nomi Tooling Stack Direction

The practical stack should be:

```text
source text
-> parser frontend registry
-> lossless/tolerant CST where available
-> Nomi Surface IR with SourceSpan
-> Nomi Core IR with verifier
-> serialized Core IR / debug text / source map
-> execution backend:
     python-ast compatibility
     core-runtime reference
     js-core-runtime browser path
     future wasm/vm/native backend
-> ExecutionResult:
     value, bindings, stdout, stderr, diagnostics, events, timings, artifacts
-> shared consumers:
     CLI, web, notebook, tests, VS Code/LSP, agents
```

The stack should be boringly explicit. Each arrow should eventually be a named
pipeline stage with an inspection command, a verifier or contract test, and
feature capability metadata.

## Artifact Checklist For New Implementation Work

Any serious feature or implementation tool should ask which of these artifacts
it affects:

| Artifact | Question |
| --- | --- |
| Grammar/CST | Does source parse in the default profile, lab profile, target-tour profile, or docs-only profile? |
| Surface IR | Is the user syntax preserved with source spans before backend lowering? |
| Core IR | Which normal forms represent the feature? What is unsupported? |
| Verifier | What invalid states are rejected before runtime? |
| Backend lowering | Does Python AST remain only a backend view? |
| Runtime values | Are values Nomi-owned rather than host-object leaks? |
| Control flow | Are return, break, continue, yield, errors, and absence explicit signals/values? |
| Host boundary | Which capabilities are imported? Which are unavailable in browser/notebook/native? |
| Diagnostics/events | What semantic event records explain success or failure? |
| Inspection | Which `tools.syntax.inspect` stages show the feature? |
| Tests | Which parser, lowering, reduced-mode, runtime, backend, frontend, and sample fixtures prove the claim? |
| Tooling | What will LSP/web/notebook/agents see? |
| Reversibility | If the syntax changes later, which artifacts stay stable? |

## Recommended Nomi Adoption Slices

### Slice 1: Make Existing Artifacts More Truthful

- Promote capability axes from derived optimism to explicit feature fields:
  parse, lower, run, reduced, explain, docs, samples, web, notebook, backend.
- Add feature-owned test templates that point to parse snapshots, lowering
  snapshots, runtime checks, backend fixtures, docs, and frontend exposure.
- Require every new syntax feature to have an inspection story before runtime
  promotion.

### Slice 2: Finish The Surface/Core Boundary For High-Leverage Forms

- Add passive `BindingTarget`, `DataDecl`, `MatchExpr`, and `PipeExpr` surface
  nodes.
- Preserve `SourceSpan` through those nodes.
- Keep Python AST behavior working, but stop letting it be the only artifact
  that remembers the feature.

### Slice 3: Treat Core IR JSON As A Product Artifact

- Version the serialized Core IR payload.
- Add source maps or span tables beside Core JSON.
- Add a human-readable Core text form for review diffs.
- Grow backend fixtures against the serialized payload, not only Python objects.

### Slice 4: Turn Semantic Events Into The Explanation Backbone

- Define event records for binding, call, match, data decode, pipeline, block,
  host call, and backend fallback.
- Route parser/lowering/runtime through a no-op-to-real collector.
- Surface the same event records in CLI, web, notebook, tests, and future LSP.

### Slice 5: Build Editor Tooling From The Pipeline

- Keep Tree-sitter as editor CST/tolerant parse work first.
- Build LSP around pipeline artifacts: diagnostics, hover, go-to-definition,
  semantic tokens, code actions, and "show lowering."
- Avoid a separate editor-only parser or analyzer that knows different facts
  from the runtime pipeline.

### Slice 6: Use Compiler Infrastructure Only After Nomi Semantics Are Owned

- MLIR spike: only for a tiny pure subset after Core IR verifier and fixture
  parity exist.
- LLVM/ORC spike: only after MLIR or direct Core lowering proves stable
  low-level semantics.
- Cranelift spike: only if a fast embeddable JIT/backend helps a measured use
  case.
- Wasm/WASI: prefer compiling or porting the Core Runtime first, then compile
  pure subsets later.

## Anti-Patterns To Avoid

- Lowering a new feature directly to Python AST and calling it designed.
- Adding LLVM/MLIR before source spans, diagnostics, and Core IR are stable.
- Letting the web playground invent a separate runtime result format.
- Treating Tree-sitter acceptance as semantic acceptance.
- Building an LSP that reparses and reinterprets Nomi differently from CLI/tests.
- Creating backend demos without cross-backend fixture parity.
- Using package moves to create the appearance of architecture.
- Optimizing away dumps, source maps, spans, or event traces before the design
  has settled.

## Ground Rule

Modern implementation infrastructure should make Nomi more experimental, not
less. The goal is not to become compiler-heavy for its own sake. The goal is to
let the project change its mind cheaply while giving users a more coherent
experience:

```text
pleasant surface
-> visible reduction
-> good diagnostics
-> shared tooling
-> portable execution
-> reversible evolution
```

That is the infrastructure story that best serves Nomi's language story.
