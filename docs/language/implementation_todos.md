# Language Feature Todos

> Status: staged backlog for the forward-looking language design.

This backlog turns [Language Foundation](language_foundation.md),
[Spec Readiness Map](spec_readiness_map.md),
[Cognitive Language Vision](../research/cognitive_language_vision.md), and
[Binding Constraints Feature](../features/binding_constraints_feature.md) into
implementation-sized work. The current prototype is a bootstrap path, not a
limit on what should be designed.

For the design-only steering layer above this backlog, see
[Language Direction And Gap Map](language_direction_and_gap_map.md). That
document names adoption, documentation, teaching, standard library, and
coherence gaps before they become implementation tasks.

For a staged execution plan with gates, caveats, risks, and recommended next
work packages, see [Forward Implementation Plan](forward_implementation_plan.md).

For a full-docs scan that names hidden bridge gaps and planning priorities, see
[Docs Eagle Eye Review](docs_eagle_eye_review.md).

For the implementation scan that ties code seams to stable TODO IDs, see
[Implementation Codebase Audit](implementation_codebase_audit.md).

For the project-wide evolvability lens that turns those seams into feature
ownership, capability honesty, frontend parity, and reversible implementation
rules, see
[Implementation Evolvability Gap Review](implementation_evolvability_gap_review.md).

For the staged path away from Python as the semantic center, see
[Python Independence And Compiler Backend Plan](python_independence_and_compiler_backend_plan.md).

For concrete lessons from modern language implementation tools and real
compiler/tooling artifacts, see
[Modern Language Implementation Artifacts](modern_language_implementation_artifacts.md).

For the implementation/core/sugar/backend layer vocabulary, eval separation
rules, and preparatory Core IR sequence, see
[Core Layer Separation Plan](core_layer_separation_plan.md).

For test-suite organization before moving files or adding markers, see
[Test Suite Restructure Plan](test_suite_restructure_plan.md).

For the promotion workflow from design material to spec-ready language sections,
see [Spec Readiness Map](spec_readiness_map.md).

## Track 0: First Principles, Vision, And Design Fixtures

- [ ] Maintain the first-principles programming model as the main spine of the
  language design.
- [ ] Use the hierarchical language research plan to order focused design
  commits from primitive layers upward.
- [ ] For each feature, identify the primitive cognitive act it supports before
  comparing language precedents.
- [ ] Maintain one canonical cognitive-language vision document and keep it
  ahead of the implementation.
- [ ] Maintain the language coherence model as a blocking design review for new
  features.
- [x] Purge `docs/archive/` after promoting its durable ideas into active docs.
  Future source-only ideas should live in `docs/research/` or `docs/drafts/`
  until promoted.
- [ ] For each promoted idea, document what Nomi keeps from the source language
  and what it deliberately refuses to copy.
- [ ] Use `design_proposal_template.md` for new syntax or feature proposals
  before promoting them into canonical docs.
- [ ] Maintain a central design decision ledger for accepted, rejected,
  deferred, and revisit-later language choices.
- [ ] Maintain a current capability/spec matrix, using
  `spec_readiness_map.md` as the consolidation home until the table needs its
  own file. It should separate parser support, lowering, runtime behavior,
  tests, samples, docs status, and target-only syntax.
- [~] Add target Nomi programs that intentionally use not-yet-implemented
  features: explicit data decoding, algebraic data, pipelines, block policies,
  symbolic rewrite, table queries, and examples.
- [ ] Keep `target_program_fixtures.md` current as the docs-only home for
  aspirational programs before runnable samples exist.
- [ ] Add executable examples for accepted surface forms only after focused
  tests pass. Update `samples/demo.nomi` with the full teaching example and
  `samples/demo_terse.nomi` with the compressed memory-refresh example. When a
  feature belongs in interpreter regression coverage, also update the relevant
  file under `prototype/tests/data/sample_sources/interpreter/`.
- [x] Add a small design-fixture file that contains desired future syntax even
  before all examples parse.
  (`docs/language/demo_target.nomi` is the compact target-only script for
  ordinary language cases. It must stay outside `samples/` until it parses and
  runs under regression tests.)
- [ ] Add a test matrix that distinguishes currently supported, planned, and
  intentionally rejected syntax.
- [ ] Add a first-hour Nomi teaching path that excludes advanced layers and
  proves the language can be learned from values, names, calls, functions,
  binding constraints, and diagnostics.
- [ ] Add a prelude and standard library plan for ordinary tasks: files, paths,
  text, JSON, CSV, HTTP, time, subprocesses, tables, tests, config, secrets,
  and Python interop.
- [ ] For each major feature spec, include the explanation contract from
  `spec_readiness_map.md`: what happened, where, what value, what rule, what
  the user can do next, and what is redacted.
- [ ] Use `implementation_evolvability_gap_review.md` as the implementation
  gate before broad syntax, runtime, backend, web, notebook, or package work:
  every promoted feature should name its owner, layer, capability axes,
  reduction, diagnostics, tests, frontend exposure, and reversibility story.
- [ ] Use `modern_language_implementation_artifacts.md` before adopting a new
  implementation tool such as Tree-sitter, MLIR, LLVM, Cranelift, Wasm/WASI,
  LSP, or a formatter/runtime bundle. The tool must map to concrete artifacts,
  tests, inspection, diagnostics, and backend/frontend contracts.

## Track 0A: Declarative Syntax And Experimentation Substrate

These tasks make large syntax and semantics changes faster without turning the
prototype into a pile of one-off grammar edits. They should advance before
major new surface forms such as `data`, decode, scoped notation, or symbolic
layers move from docs into implementation.

- [ ] Keep
  [`syntax_substrate_todo_audit.md`](syntax_substrate_todo_audit.md) as the
  central TODO index for parser, grammar, lowering, feature profile, and
  inspection work.
- [x] Add a passive `SyntaxFeature` manifest model that can name grammar
  fragments, parse-tree transforms, surface/core nodes, lowering passes,
  diagnostics, docs, tests, status, and feature owner.
  (Done in `prototype/syntax/features.py` — `BUILTIN_FEATURES` is the single
  source of truth; grammar layers, layer transforms, lowering mixins, and
  desugar passes are all derived from it.)
- [~] Add a current capability/spec matrix that separates target-only,
  parse-only, lowerable, runnable, explainable, documented, sample-covered,
  web-exposed, and notebook-exposed features.
  (`render_feature_capability_table()` and `inspect(stage="capabilities")`
  expose the first derived matrix. Remaining: make reduced-mode, samples, web,
  notebook, and docs/spec status explicit instead of derived/defaulted.)
- [~] Split `SyntaxFeature.status` into machine-readable capability axes so
  parser support, lowering, runtime, reduced-mode support, diagnostics,
  docs/spec status, samples, web, and notebook exposure cannot be collapsed
  into one optimistic lifecycle label. (`NOMI-SUBSTRATE-035`; initial derived
  axes exist in `FeatureCapabilityAxes`.)
- [ ] Add named experiment profiles such as `default`, `lab`, `target-tour`,
  and `docs-only` after the parser grows `features=[...]`.
- [x] Add `tools.syntax.inspect` so every grammar or lowering change can show
  raw tree, transformed tree, surface AST, core AST, Python AST backend, and
  normal-form expansion.
  (Done — 15 stages: `raw-tree`, `transformed-tree`, `surface-ast`, `python-ast`,
  `core`, `core-verify`, `core-to-python`, `backend-lowered`, `features`,
  `capabilities`, `parser-frontends`, `eval-backends`, `passes`, `expansions`.)
- [~] Introduce `SourceSpan` and preserve it through the earliest practical
  parser/lowering path for bindings, functions, calls, match cases, and block
  calls.
  (`SourceSpan` dataclass, `captures_span` decorator, and `SurfaceNode.span`
  field in `prototype/syntax/surface.py`. Wired through `BlockCall` via
  Lark's `visit_wrapper` mechanism. Source-position propagation is available
  with `NOMI_PARSER_SPANS=1` or `preserve_positions=True`; the default
  execution parser disables it for speed. Remaining: apply `@captures_span` to
  other surface-node-producing lowering methods.)
- [~] Add Nomi-owned surface nodes for new or awkward forms before lowering
  them to Python AST. Start with `BlockCall`, `BindingTarget`, `PipeExpr`,
  `MatchExpr`, and `DataDecl`.
  (`BlockCall` and `lower_surface_to_python` done; `BindingTarget`, `PipeExpr`,
  `MatchExpr`, `DataDecl` pending.)
- [x] Add declarative pass metadata for existing desugar passes: pass name,
  feature owner, dependencies, input nodes, removed nodes, produced nodes,
  normal forms, and inspection output.
  (`Phase` enum, `depends_on`, `input_node_types`, `removed_node_types`,
  `produced_node_types`, and `normal_forms` on `BaseDesugarer`; pipeline
  auto-derived from `BUILTIN_FEATURES`; dependencies and metadata validated at
  import time; `_check_pass_invariants` validates `removed_node_types` after
  each pass. Dead `precedence.py` removed.)
- [ ] Add feature-driven test templates that name parse snapshots, lowering
  snapshots, diagnostics, runtime behavior, reduced-interpreter invariants,
  sample regression coverage, docs references, web playground checks, and
  notebook checks.
- [x] Restructure tests according to
  [`test_suite_restructure_plan.md`](test_suite_restructure_plan.md): document
  run tiers first, add markers without changing behavior second, then split
  large functional feature clusters one migration commit at a time.
  (Done: `functional/` is drained; feature, contract, regression, smoke, and
  e2e buckets are documented in `prototype/tests/README.md`.)
- [ ] Add no-op semantic event hooks before feature-specific tracing so
  binding, call, block, match, decode, pipeline, and rewrite diagnostics do not
  each invent a private explanation format.
- [ ] Keep symbolic/lazy computation behind explicit boundaries from
  [`symbolic_structural_computation.md`](../features/symbolic_structural_computation.md):
  `quote`, `describe`, `lazy`, query plans, rewrite rules, `collect`, and
  `explain` must remain separate until a small computation IR proves they
  compose.
- [ ] Update `.agents/skills/nomi-*` whenever the substrate workflow changes,
  so agents propose feature-owned, spec-driven changes instead of scattered
  grammar/interpreter patches.
- [ ] Keep the evolvability scorecard current whenever a major substrate seam
  changes: feature metadata, capability axes, Surface/Core authority,
  runtime result contract, feature profiles, test matrix, semantic events, or
  frontend exposure.

## Track 0B: Runtime And Architecture Refactoring

These tasks prepare the larger architecture around syntax work: public runtime
APIs, execution sessions, frontend adapters, structured results, host
boundaries, and package ownership. Keep the detailed plan in
[`architecture_refactoring_plan.md`](architecture_refactoring_plan.md).

- [x] Add a thin public runtime API facade over the current `run_eval_loop`
  functions before moving internals.
- [~] Add `ExecutionResult` as an opt-in structured result with bindings,
  diagnostics, events, timings, and exception fields.
  (`ExecutionResult` exists with bindings, timings, exception, optional value,
  stdout, stderr, diagnostics, and events. `execute()` captures stdout/stderr;
  `RuntimeSession.run()` can opt into capture. Remaining: real diagnostic/event
  producers and detailed stage artifacts.)
- [x] Add mode metadata for `python`, `nomi`, and `reduced` so parser,
  lowering, interpreter class, status, and host support are declared as data.
- [ ] Keep old `prototype.interpreter.*.usage` modules as compatibility
  wrappers until CLI, tests, web, and notebook migrate.
- [x] Add `RuntimeSession` for persistent execution in web cells, notebook
  cells, future REPL work, and run-all workflows.
- [ ] Define host adapter responsibilities for filesystem access, stdout,
  timing, package loading, cancellation/restart, and artifact fetching.
- [ ] Treat the web manifest as the first runtime artifact bundle contract and
  evolve it toward declared files, samples, grammar, profiles, and version.
- [ ] Add architecture contract tests for the public runtime API before
  migrating frontend surfaces.
- [x] Move the CLI onto `prototype.runtime.execute()` after `ExecutionResult`
  owns stdout/stderr, diagnostics, structured errors, and exit behavior.
  (`NOMI-ARCH-023`)
- [~] Make web and notebook adapters consume the same structured runtime result
  contract instead of maintaining private output/error payloads.
  (`NOMI-ARCH-024`; web now consumes `RuntimeSession.run(...,
  capture_output=True)`, notebook still streams through kernel redirects.)
- [ ] Avoid package moves until a facade exists and one feature proves the
  migration path.
- [ ] Keep `NOMI-ARCH-018` current: Python AST should become one backend behind
  Nomi-owned Surface/Core IR, not the permanent language IR.
  (Partially done: `prototype/runtime/backends/` exists with `python_ast.py` as
  one backend, `core_runtime.py` as the Python reference runtime,
  `js_core.py`/`prototype/runtime/js/core_runtime.js` as the first non-Python backend, and
  `NOMI_USE_CORE_IR=1` plus explicit eval-backend selection gating the Core IR
  path.)
- [x] Add `NOMI-ARCH-019`: introduce a passive Core IR and verifier before any
  serious native or Wasm backend work.
  (Done: registered CoreNode types, `verify_core(strict=True)`, `core_to_python_ast()`,
  `lower_python_ast_to_core()`, `NOMI_VERIFY_CORE=1` gate.)
- [~] Upgrade `NOMI-ARCH-019` from passive inspection to an authoritative tiny
  Surface -> Core lowering path before runtime diagnostics or backend work rely
  on Core IR as a source of truth.
  (In progress: registered node types lower, and basic expression operations now
  have Core IR nodes. Remaining Python AST forms still produce Diagnostic
  sentinels. Direct runtime backends now consume this Core IR contract, so the
  remaining pressure is to replace Python-AST back-projection with
  Surface -> Core lowering.)
- [ ] Add `NOMI-ARCH-020`: run an MLIR spike only for a tiny pure subset after
  Core IR inspection works.
- [x] Add `NOMI-ARCH-021`: define backend capability flags and cross-backend
  tests before LLVM/ORC/native codegen.
  (Done: `EvalBackendCapabilities`, `EvalBackendSpec`, registry,
  `NOMI_USE_CORE_IR=1` gate, `render_eval_backend_table()`, and
  `prototype/tests/backend_fixtures/` parity across `python-ast`,
  `core-runtime`, and `js-core-runtime`.)
- [~] Add `NOMI-ARCH-022`: define runtime values, ABI, memory, host
  capabilities, and Python interop boundaries before compiling dynamic
  features.
  (Design written: [`core_runtime_backend_design.md`](core_runtime_backend_design.md).
  Implementation in 7 slices — see Track 0D below.)

## Track 0C: Core Layer Separation Preparation

These tasks operationalize
[`core_layer_separation_plan.md`](core_layer_separation_plan.md). They should
come before any attempt to rewrite eval, add native backends, or move grammar
directories wholesale.

- [x] Add the core-layer plan and link it from the docs entry point.
- [x] Update orientation docs and agent skills with the L0-L7 vocabulary and
  eval-separation guardrail.
- [x] Extend `prototype/syntax/features.py` so `SyntaxFeature` can declare:
  layer, semantic forms, reduction target, runtime-hook policy, backend
  requirements, docs, and tests.
- [x] Add contract tests that every builtin feature declares a layer.
- [x] Add contract tests that every L4 sugar feature declares a reduction
  target and no permanent eval requirement.
- [x] Classify existing builtin features using the first draft in
  `core_layer_separation_plan.md`.
- [x] Add a passive `prototype/syntax/core.py` or `prototype/core/ir.py`
  skeleton with L1 dataclasses for Module, Literal, Load, Bind, Function,
  Call, Return, Branch, and Diagnostic.
- [x] Add a Core IR verifier that rejects surface/sugar nodes and unknown node
  shapes before any evaluator depends on the IR.
- [x] Add a text/debug dump for Core IR so snapshots and inspection output are
  readable.
- [x] Add `inspect(stage="features")` or an equivalent tool stage that prints
  active feature/layer metadata.
- [x] Add `inspect(stage="core")` only after the passive Core IR skeleton can
  represent a tiny subset.
- [x] Keep `prototype/interpreter/reduced/interpreter.py` aligned with feature
  metadata, so reduced mode catches unreduced L4 forms by declared reduction
  target, not just Python AST node type.
- [x] Move default/reduced desugar pass selection into `SyntaxFeature`
  metadata instead of class-name filtering in the pipeline.
- [x] Make desugar phases executable: pass order is now grouped by
  `syntax`, `semantic`, and `cleanup`, with dependency validation after
  phase ordering.
- [x] Add a `passes` inspection stage that shows desugar pass order, phase,
  feature owner, profiles, dependencies, and removed node types.
- [x] Add an `expansions` inspection stage that shows pass-by-pass before/after
  AST rewrites and normal forms.
- [ ] Use constrained binding as the first L2/L3 semantic-core migration
  candidate after metadata and passive Core IR exist.
- [ ] Use `unless` or postfix conditional return as the first L4 sugar
  migration candidate after reduction-target tests exist. Started: both
  conditional-flow sugars now have L4 feature metadata and reduction targets;
  remaining work is surface/core expansion inspection and provenance.

## Track 0D: Core Runtime Backend (Python-Independent Reference)

Design: [`core_runtime_backend_design.md`](core_runtime_backend_design.md).
Implementation notes:
[`core_runtime_backend_implementation_notes.md`](core_runtime_backend_implementation_notes.md).
The Core Runtime is the reference implementation that defines Nomi-owned
abstractions (Value system, Frame environments, ControlFlow signals, fenced
host interop) that future Rust/Wasm/LLVM backends implement in their host
language. The Python implementation stays as the test oracle.

### Slice 1: Value system + basic eval (7 node types)
Files: `prototype/runtime/backends/values.py`, `core_runtime.py`
- [x] Define `Value` subtypes: `IntValue`, `FloatValue`, `BoolValue`,
  `StrValue`, `NilValue`, `FunctionValue`, `NativeValue`.
- [x] Define `ControlFlow` subtypes: `ReturnSignal`, `BreakSignal`,
  `ContinueSignal`, `YieldSignal`.
- [x] Define `Frame` with scoped bindings, parent chain, lookup, assign, extend.
- [x] Implement `CoreRuntime.eval()` dispatching on: `Literal`, `Load`, `Bind`,
  `Function`, `Call`, `Return`, `Branch`.
- [x] Implement `_unbox()` for `EvalBackendResult.bindings` compatibility.
- [x] Parity tests against `python_ast` backend for the 7-node subset.

### Slice 2: Data and fields (2 node types)
- [x] Implement `eval_ConstructData()` — evaluate fields, return `DataValue`.
- [x] Implement `eval_GetField()` — access `DataValue.fields[name]`.
- [x] Contract tests for data construction and field access.

### Slice 3: Expression operations (4 node types)
- [x] Define `UnaryOp`, `BinaryOp`, `BooleanOp`, and `CompareOp` Core IR nodes.
- [x] Lower Python AST operation nodes into portable Core IR operation nodes.
- [x] Lower Core IR operation nodes back to Python AST for `python-ast` backend compatibility.
- [x] Implement operation dispatch in `core-runtime`.
- [x] Focused syntax and runtime tests for operation nodes.

### Slice 4: Data access expressions (4 node types)
- [x] Define `ConditionalExpr`, `MappingLiteral`, `GetItem`, and `Spread` Core IR nodes.
- [x] Lower Python AST `IfExp`, `Dict`, `Subscript`, and `Starred` into Core IR.
- [x] Lower Core IR data-access nodes back to Python AST for `python-ast` backend compatibility.
- [x] Implement mapping, subscript, conditional expression, and sequence spread dispatch in `core-runtime`.
- [x] Focused syntax and runtime tests for data-access nodes.

### Slice 5: Statement control (3 node types)
- [x] Define `NoOp`, `Break`, and `Continue` Core IR nodes.
- [x] Lower Python AST `pass`, `break`, and `continue` into Core IR.
- [x] Lower Core IR statement-control nodes back to Python AST.
- [x] Implement no-op and loop-control dispatch in `core-runtime`.
- [x] Focused syntax and runtime tests for statement-control nodes.

### Slice 6: Annotated binding projection
- [x] Lower Python AST `AnnAssign` into Core IR `Bind` for executable backend reduction.
- [ ] Preserve annotation and constraint metadata in Core IR once constrained binding migrates from Python AST semantics.

### Slice 7: Yield representation
- [x] Define `Yield` Core IR node.
- [x] Lower Python AST `Yield` into Core IR and lower Core IR `Yield` back to Python AST.
- [x] Emit explicit `YieldSignal` in `core-runtime`; full resume/block semantics remain a later gate.

### Slice 8: Control flow (2 node types)
- [x] Implement `eval_Loop()` — while-style loop with `BreakSignal`/`ContinueSignal`.
- [x] Implement `eval_Sequence()` — evaluate elements, produce list.
- [x] Parity tests for loops and sequences.

### Slice 9: Pattern matching
- [x] Lower Python AST value, wildcard/capture, sequence, mapping, and rest patterns into Core IR pattern shapes.
- [x] Lower Core IR pattern shapes back to Python AST match patterns.
- [x] Implement `eval_Match()` — subject evaluation + case dispatch.
- [x] Implement `eval_PatternTest()` — pattern matching + guard + body.
- [x] Focused runtime tests for literal, capture, sequence, mapping, rest, guard/capture rollback paths.

### Slice 10: Exception handling (2 node types)
- [x] Define `ErrorValue` subtype.
- [x] Implement `eval_Raise()` — produce `ErrorValue`.
- [x] Fence native host exceptions into `ErrorValue`.
- [x] Implement `eval_Handle()` — try/catch dispatch, always eval `finalbody`.
- [x] Focused tests for native error fencing and handler matching.

### Slice 11: Host interop + unboxing
- [x] Implement `NativeValue` wrapping and host-call dispatch table.
- [x] Complete `_unbox()` for all value types.
- [x] Add default fenced host calls needed by demo: `list`, `range`, `sum`,
  `str`, `int`, `float`, `abs`, `filter`, `map`, `len`, `bool`, and `print`.
- [x] Host-interop tests for builtins and explicit supplied host functions.

### Slice 12: Blocks and resume (capability promotion)
- [x] Preserve block-call payloads on Core `Call`.
- [x] Implement simple yield-to-block support for caller blocks and yielded values.
- [ ] Add `GeneratorState` for general resumable functions.
- [ ] Promote `supports_blocks=True`, `supports_resume=True`.
- [x] Block-call focused tests.

### Slice 13: For-each loops
- [x] Define `ForEach` Core IR node.
- [x] Lower Python AST `for target in iterable` into `ForEach` for simple named targets.
- [x] Lower Core `ForEach` back to Python AST.
- [x] Implement direct `core-runtime` `ForEach` dispatch.
- [x] Focused syntax/runtime tests.

### Slice 14: Demo direct-runtime smoke
- [x] `samples/demo.nomi` passes strict Core IR verification.
- [x] `samples/demo.nomi` lowers Core IR back to Python AST.
- [x] `samples/demo.nomi` runs with `NOMI_EVAL_BACKEND=core-runtime`.
- [ ] Turn demo smoke into cross-backend semantic parity assertions.

### Slice 15: Serialized Core IR and first non-Python runtime
- [x] Define Core IR JSON payload helpers in `prototype/syntax/core_json.py`.
- [x] Add `core-json` inspection through `tools.syntax.inspect` and
  `prototype.runtime.inspect()`.
- [x] Implement `prototype/runtime/js/core_runtime.js` as a JavaScript evaluator over serialized
  Core IR JSON.
- [x] Add fixture-level parity against Python `core-runtime` for bindings,
  function calls, operations, sequences, for-each, and stdout.
- [x] Dispatch every currently registered CoreNode in the JavaScript runtime.
- [x] Add JS parity coverage for mappings, spreads, data fields, match/rest
  patterns, error handling, and simple yield-to-block.
- [x] Run `samples/demo.nomi` through session-lowered Core JSON in Node.
- [x] Add browser worker path; the current default is Rust/WASM parser -> JS
  lowerer -> JS Core Runtime.
- [x] Register `js-core-runtime` as a first-class eval backend wrapper.
- [x] Move the first fixture ladder into `prototype/tests/backend_fixtures/`
  and compare it across `python-ast`, `core-runtime`, and `js-core-runtime`.
- [~] Expand the fixture ladder with host capability, source-map, diagnostic,
  and resume edge cases.
  (Partial: `07_host_calls.nomi` covers declared host calls across
  `python-ast`, `core-runtime`, and `js-core-runtime`; source-map, diagnostic,
  and resume edge fixtures remain.)
- [ ] Execute the JS Core Runtime Operational Completion Plan in
  `core_runtime_backend_implementation_notes.md`: exact demo stdout parity,
  Core JSON contract tests, host capability manifest, browser JS execution
  contracts, and promotion evidence.
- [ ] Promote the JS runtime from opt-in browser path to default only after
  fixture corpus parity and host capability policy are settled.

## Track 1: Binding, Constraints, And Data Boundaries

- [ ] Introduce a runtime `BindingError` type with fields for name, value,
  failed constraint, source span when available, binding kind, and optional
  human message.
- [ ] Replace plain `TypeError` constraint failures with `BindingError`, while
  keeping compatibility where existing tests expect `TypeError`.
- [ ] Add a `Constraint` representation instead of storing bare predicate
  callables only. It should preserve the original expression/name and support
  diagnostics.
- [ ] Add a `BindingTarget` abstraction for name binding, tuple/list
  destructuring, mapping destructuring, and later pattern captures.
- [ ] Implement tentative binding and commit/rollback so failed constraints do
  not leak partially bound names.

### Parser And AST Shape

- [ ] Keep current assignment syntax working:
  `x:int, x > 0 = value`.
- [ ] Decide whether bare declaration syntax is accepted now:
  `x:int, x > 0`.
- [x] Parse grouped parameter constraints:
  `func f(x:(int, x > 0)): ...`.
- [ ] Parse constrained block parameters:
  `each(xs) -> x:int: ...` and `pairs(xs) -> k:str, v:int: ...`.
- [ ] Parse constrained destructuring targets:
  `(x:int, y:int) = point`.
- [ ] Parse constrained match captures:
  `case {"age": age:(int, age >= 13)}:`.
- [ ] Preserve enough source location data for useful diagnostics.

### Parameter Binding

- [ ] Route function call argument mapping through the same binding-validation
  path used by assignment.
- [x] Validate basic grouped parameter constraints in the current function
  setup path.
- [x] Validate defaulted parameters after defaults are applied.
- [x] Define first-pass `*args` and `**kwargs` behavior: constraints apply to
  the collected tuple or mapping.
- [x] Add tests for ordinary positional/keyword, keyword-only, defaults,
  varargs, and keyword arguments.
- [x] Add explicit positional-only parameter constraint tests.
- [ ] Ensure arrow functions either support constrained parameters or reject
  them with a clear parse/runtime error.

### Block Parameter Binding

- [ ] Replace one-to-one yielded-value mapping with the shared binding engine.
- [ ] Support constrained single block parameters:
  `each(xs) -> item:int: ...`.
- [ ] Support constrained multi-value block parameters:
  `pairs(xs) -> key:str, value:int: ...`.
- [ ] Define behavior when the callee yields the wrong number of values.
- [ ] Add tests that failed block-parameter constraints prevent block body
  execution.

### Pattern And Destructuring Binding

- [ ] Reuse `BindingTarget` for tuple/list destructuring assignment.
- [ ] Reuse `BindingTarget` for mapping destructuring assignment.
- [ ] Add constrained pattern captures in `match`.
- [ ] Define direct assignment failure as `BindingError`.
- [ ] Define match-case constraint failure as case non-match before body entry.
- [ ] Add tests that partial pattern bindings do not leak on failure.

### Human Diagnostics

- [x] Add `else "message"` syntax for individual assignment constraints.
- [x] Add `else "message"` syntax inside grouped parameter constraints.
- [ ] Carry messages through the future structured `Constraint` model.
- [ ] Produce diagnostics that name the binding kind: assignment, parameter,
  block parameter, destructuring target, or match capture.
- [ ] Include the failing source expression when available.
- [ ] Add regression tests for multi-constraint failures.

### Data Boundary Decoding

- [ ] Create a focused `data_decode_boundary_feature.md` spec covering
  provenance, defaults, optional fields, extra fields, redaction, source paths,
  nested decoders, and `explain`.
- [ ] Follow `language_foundation.md`: do not add a first-layer `shape`
  keyword as a peer to `data`.
- [ ] Specify explicit `Data.decode(value)` conversion for external mappings
  before considering a named structural `shape` form.
- [ ] Reuse binding constraints for each decoded field.
- [ ] Define missing-field, extra-field, default-field, and optional-field
  policy.
- [ ] Preserve source/provenance for request JSON, config, form data, CLI args,
  CSV rows, and environment variables.
- [ ] Add examples for explicit decode boundaries after tests pass.

## Track 2: Blocks As Control Values

- [ ] Use `../features/block_calls_feature.md` as the canonical focused feature
  spec.
- [ ] Specify block calls as calls with attached caller-side code and explicit
  `yield` points.
- [ ] Define block scoping: which names are read, rebound, shadowed, and
  captured.
- [ ] Implement block parameters through the shared binding engine.
- [ ] Add standard block policies: `using`, `retry`, `timeout`, `transaction`,
  `trace`, and `test`.
- [ ] Add diagnostics that show when and why a block was entered, yielded,
  resumed, retried, or cancelled.

## Track 3: Expression Flow, Pipelines, And Composition

- [ ] Promote expression/statement doctrine from
  `docs/convenience/expression_statement_orientation.md` into Core IR
  requirements: value-producing block nodes, branch value checks, and
  source-level control-transfer diagnostics.
- [ ] Specify `|>` pipeline semantics, including placeholder `_` and simple
  single-argument shorthand.
- [ ] Specify `>>` function composition separately from pipeline application.
- [ ] Add final-expression return for selected expression-oriented blocks.
- [ ] Add scoped intermediate bindings for calculational expressions.
- [ ] Add trace output for pipeline stages so the programmer can inspect value
  flow.

## Track 4: Algebraic Data, Results, And Pattern Matching

- [ ] Create a focused `failure_taxonomy_feature.md` that distinguishes
  absence, expected failure, exceptions, pattern non-match, and constraint
  failure.
- [ ] Specify `data` declarations for product and sum types.
- [ ] Define constructor, field access, equality, display, and destructuring
  behavior.
- [ ] Add `Result[T, E]` and optional-value conventions.
- [ ] Extend `match` to cover algebraic variants, guards, constraints, and
  expression results.
- [ ] Add exhaustiveness diagnostics as an eventual goal, even if runtime-only
  checking comes first.

## Track 5: Collections, Arrays, Tables, And Queries

- [ ] Specify a collection transform vocabulary: `map`, `where`, `select`,
  `group`, `join`, `sort`, `fold`, and `window`.
- [ ] Decide which operations are syntax and which remain library-led block
  calls.
- [ ] Add table/row/column structure concepts that reuse binding and
  constraints without introducing a second validation story.
- [ ] Explore APL-style rank and whole-array operations with readable spelling.
- [ ] Add examples for ordinary lists, records, dataframes, and time-indexed
  data.

## Track 6: Symbolic Expressions And Rewrite Rules

- [ ] Specify `quote:` as the explicit boundary where code-shaped syntax becomes
  data.
- [ ] Specify rewrite rules such as `expr /. pattern -> replacement`.
- [ ] Define evaluation boundaries so ordinary runtime code is not implicitly
  symbolic.
- [ ] Add a small expression AST model independent of Python's AST where needed.
- [ ] Add examples for algebra simplification, code transformation, and
  teaching/debugging tools.

## Track 7: Effects, Worlds, Capabilities, And Policies

- [ ] Create a practical `state_and_capability_model.md` focused on rebinding,
  mutation, `with:` updates, transactions, `world`, and traceable authority
  before any advanced effect typing.
- [ ] Specify capability scopes for filesystem, network, time, randomness,
  subprocesses, and environment access.
- [ ] Explore `world` values for simulation, test isolation, and replay.
- [ ] Define how block policies interact with capabilities.
- [ ] Add effect-aware diagnostics: what did this code touch, and under what
  authority?
- [ ] Keep this cognitive and inspectable rather than making it a resource
  optimization project.

## Track 8: Examples, Tests, Explanation, And Trace

- [ ] Create a focused `explanation_trace_feature.md` spec with an explanation
  contract for binding, decode, match, pipeline, block policy, examples, query
  plans, and symbolic rewrites.
- [ ] Specify `examples:` blocks inside functions and data declarations.
- [ ] Let examples serve as tests, documentation, and behavioral anchors.
- [ ] Add `explain(expr)` or equivalent runtime explanation hooks.
- [ ] Add trace objects for constraints, matches, pipelines, block control, and
  rewrites.
- [ ] Make diagnostics speak in feature terms, not interpreter internals.

## Track 9: Scoped Notation And Language Growth

- [ ] Specify `use` scopes for enabling extension syntax or domain notation.
- [ ] Require every notation extension to provide a desugaring.
- [ ] Add guardrails against global syntax mutation.
- [ ] Prototype one small notation domain, such as units or symbolic algebra.
- [ ] Ensure tooling can show the expanded form on demand.

## Track 10: Cleanups And Coherence Checks

- [ ] Before implementing a feature, answer the coherence questions from
  `language_foundation.md`, `spec_readiness_map.md`, and
  `language_direction_and_gap_map.md`.
- [ ] Reject or redesign any feature that adds a second unrelated story for
  binding, blocks, patterns, expression flow, symbolic code, effects, or
  diagnostics.
- [ ] Remove duplicate ad hoc validation paths after the shared binding engine
  covers assignment, parameters, blocks, and patterns.
- [ ] Update `delta_on_python.md` to point to the canonical
  constrained-binding spec.
- [ ] Keep `../features/block_calls_feature.md` as the only active home for
  block-call/yield decisions, including block-parameter binding once
  implemented.
- [ ] Add a conformance-style test file containing the design tests from the
  feature spec.
- [ ] For every implemented convenience feature, update `samples/demo.nomi` and
  `samples/demo_terse.nomi` in the same commit after tests pass.
- [x] Remove archived design-review docs after promoting durable material into
  the active spine.

## Codebase Scan Backlog

These items came from a fresh scan of the prototype and tooling. They are
intentionally small, file-specific hints for the next cleanup pass.

- [ ] Update [`Dockerfile`](../../Dockerfile) to a newer Python base image once
  the runtime and notebook stack are verified on that image.
- [ ] Split the macOS-specific Docker/Colima bootstrap out of
  [`scripts/run_nomi_docker.py`](../../scripts/run_nomi_docker.py) so the
  cross-platform path stays small and the Apple-specific setup is isolated.
- [ ] Add return-annotation support to equation-style (`f(x) = expr`) and
  arrow (`(x) => expr`) function forms. Both hardcode `returns=None` in
  `func_equation.py` and `func_expr.py`; the grammar rules lack `-> type`
  syntax. Standard `funcdef` already supports it.
- [ ] Clean up the generator-state comments and frame queueing in
  [`prototype/interpreter/python/generator_state.py`](../../prototype/interpreter/python/generator_state.py)
  so resumable execution has one named policy instead of several tentative
  stacks and queues.
- [ ] Revisit the generator/resumable hook-up in
  [`prototype/interpreter/python/function.py`](../../prototype/interpreter/python/function.py)
  and [`prototype/interpreter/python/control.py`](../../prototype/interpreter/python/control.py)
  so the block/yield path is easier to follow.
- [x] Remove the stale comment about the collapsed `name` field in
  [`prototype/parser/python/expressions.py`](../../prototype/parser/python/expressions.py)
  after confirming the AST shape is stable.
  (The "Precedence pass" reference on the bin_expr handler was fixed; the
  "collapsed name field" comment is a separate issue. Done: the lingering
  dotted-name comment was removed after confirming current dotted access lowers
  to standard `ast.Attribute` chains.)
- [ ] Audit `prototype/parser/nomi/desugar/` for other unregistered or dead
  modules. `precedence.py` was an unregistered Python-AST-level duplicate of
  `parse_tree_precedence.ExpressionLayer` — the same pattern may exist elsewhere.
- [ ] Move the dedicated resumable examples into
  [`prototype/tests/data/sample_sources/interpreter/resumable.py`](../../prototype/tests/data/sample_sources/interpreter/resumable.py)
  and keep related examples together instead of scattering them across older
  sample files.
- [ ] Rewrite the block-parameter handling note in
  [`prototype/tests/data/sample_sources/interpreter/blocks.nomi`](../../prototype/tests/data/sample_sources/interpreter/blocks.nomi)
  once the shared binding engine is the only supported path.
- [x] Replace the provisional `#TODO:` comments in runtime code with tracked
  backlog items or tests. Remaining (2026-05-15 scan):
  Done: loose runtime TODO comments now point to `NOMI-ARCH-014`,
  `NOMI-ARCH-016`, or `NOMI-SUBSTRATE-011` as appropriate.
- [x] Fix side-by-side editor/output scrolling in the web playground
  ([`web/index.html`](../../web/index.html)); known constraints and approaches
  documented in
  [`web/web_playground_ui_challenges.md`](../../web/web_playground_ui_challenges.md).
  Done: single-cell/plain modes now explicitly lay out Monaco against the
  split-pane grid cell and give the output pane its own scroll boundary.

## Milestone Sequence

The first milestone should still be coherent, but it should point beyond the
current prototype:

```python
func signup(age:(int, age >= 13), email:(str, contains(email, "@"))):
    return email

payload_age:int, payload_age >= 13 = 18
payload_email:str, contains(payload_email, "@") = "a@b.com"
result = signup(payload_age, payload_email)
```

Milestone 1 means:

- assignment constraints still work,
- parameter constraints work through real argument mapping,
- failures produce `BindingError`,
- tests cover success and failure,
- docs and implementation use the same vocabulary.

Milestone 2 should make product data and explicit boundary conversion real:

```python
data SignupPayload:
    email:str, contains(email, "@")
    age:int, age >= 13

payload = SignupPayload.decode(request.json)

transaction(db):
    db.users.insert(payload.email)
```

Milestone 3 should make data flow readable:

```python
names =
    users
    |> where(_.active)
    |> select(_.name)
    |> sort
```

Milestone 4 should make algebraic data and match central:

```python
data Result[T, E]:
    Ok(value:T)
    Err(error:E)

match fetch_user(id):
    case Ok(user):
        user.name
    case Err(error):
        explain(error)
```

Milestone 5 should open explicit symbolic power:

```python
expr = quote:
    x + 0

simple = expr /. a + 0 -> a
```
