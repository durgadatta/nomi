# Core Layer Separation Plan

> Status: active architecture and implementation plan.
>
> Scope: separate Nomi's implementation core, semantic core, surface forms,
> syntax sugar, library conventions, scoped extensions, and backend targets.
> The immediate priority is eval separation, with parser, grammar, lowering,
> tests, and docs following the same layer model.

## Purpose

Nomi needs a stronger boundary between what the language *is* and the many
ways users may write it pleasantly.

The current prototype is productive, but the layers still blur:

```text
Lark grammar
-> Nomi/Python AST lowering
-> AST desugar passes
-> Python/Nomi/reduced interpreters
```

That path proves features quickly, but it lets surface syntax, Python AST
encoding, runtime behavior, and future backend assumptions leak into one
another.

The target is a layered language where:

- the lowest implementation core can be evaluated, inspected, verified, and
  eventually compiled or bound to other runtimes;
- the semantic core is what users learn first and what docs explain;
- special forms and syntax sugars reduce to named semantic concepts;
- scoped extensions are fenced and inspectable;
- Python AST becomes one backend, not the definition of Nomi.

This plan complements:

- [Language Foundation](language_foundation.md), which names Nomi's normal
  forms;
- [Language Degrees Of Freedom](language_degrees_of_freedom.md), which
  separates fixed core, sugar, libraries, scoped extension, and advanced
  layers;
- [Flexible Syntax Substrate Plan](flexible_syntax_substrate_plan.md), which
  plans parser/lowering mechanics;
- [Architecture Refactoring Plan](architecture_refactoring_plan.md), which
  plans runtime API, pipeline, sessions, and frontend adapters;
- [Python Independence And Compiler Backend Plan](python_independence_and_compiler_backend_plan.md),
  which plans Python-independent backends.

## Layer Vocabulary

Use these layer names in code, tests, docs, and commits. The exact boundary can
evolve, but each feature should declare which layer owns it.

| Layer | Name | Audience | Purpose | Examples |
| --- | --- | --- | --- | --- |
| L0 | Runtime substrate | implementers/backends | Minimal machine-facing execution objects. | value cells, environments, frames, continuations, host capabilities, diagnostics. |
| L1 | Implementation core IR | implementers/tools | Small executable IR independent of Python AST. | bind, call, branch, block invoke, pattern test, construct value, raise diagnostic. |
| L2 | Semantic core | users/spec/tools | Concepts users learn first and docs explain. | binding, function, call, constraint, data, pattern, match, block, diagnostic. |
| L3 | Canonical surface | everyday users | Primary syntax for semantic core. | `func`, constrained bindings, `data`, `match`, block calls. |
| L4 | Sugar reductions | everyday users/tools | Pleasant spelling with boring expansion. | equations, holes, sections, pipelines, `where`, `unless`, try-expr, ranges. |
| L5 | Library conventions | library authors/users | Ordinary functions and values that should not be syntax yet. | collection verbs, result helpers, config merge, trace policies. |
| L6 | Scoped extensions | domain users | Fenced notation with explicit expansion. | symbolic `quote`, units, query DSLs, templates. |
| L7 | Backend targets | implementers/integrators | Runtime or compiler output contracts. | Python AST, direct core interpreter, Python bindings, JS/Wasm, MLIR, LLVM. |

The main distinction:

```text
L1 is what the evaluator can execute.
L2 is what the language means.
L3/L4/L5/L6 are ways to write or package that meaning.
L7 is where executable artifacts go.
```

## First Boundary To Enforce: Eval

Eval should stop being the place where every surface construct has a privileged
runtime hook.

The desired direction:

```text
surface syntax
  -> surface nodes with spans
  -> semantic-core nodes
  -> implementation-core IR
  -> eval core / backend
```

The evaluator should eventually dispatch on L1 operations, not on every Nomi
surface form.

Current useful stepping stones already exist:

- `prototype.runtime.execute()` and `RuntimeSession` provide a public facade.
- `prototype.runtime.modes.ModeSpec` names parser/lowering/interpreter choices.
- `prototype.syntax.features.SyntaxFeature` centralizes syntax/lowering/desugar
  registrations.
- `prototype.syntax.surface.BlockCall` is an early Nomi-owned surface node.
- `prototype.interpreter.reduced.Interpreter` already guards against syntax
  that should have reduced away.

The gap: these are still centered on Python AST. The next separation is to add
Nomi-owned core artifacts and make reduced/eval checks talk about those
artifacts directly.

## Layer Contracts

### L0 Runtime Substrate

L0 is not user-facing language design. It is the portable execution substrate.

It should eventually contain:

- value representation;
- environment and lexical frame ownership;
- call frames;
- block/yield frames;
- continuation or resumable-control records;
- diagnostic/event sinks;
- host capabilities such as stdout, filesystem, time, network, imports;
- runtime errors and structured failure values;
- backend ABI notes for Python, Wasm, native, and foreign-language bindings.

L0 should not know about:

- `where`;
- equations;
- hole syntax;
- `unless`;
- operator sections;
- scoped symbolic notation;
- source spelling choices.

### L1 Implementation Core IR

L1 is the lowest executable Nomi IR. It should be small enough to evaluate
directly and structured enough for tools and future backends.

Initial candidate operations:

```text
Module
Literal
Load
Bind
AssignExisting
Function
Call
Return
Branch
Loop
PatternTest
Match
ConstructData
GetField
BlockValue
InvokeBlock
Raise
Handle
Diagnostic
HostCall
```

This list is intentionally implementation-facing. It may be more primitive
than the concepts users learn.

Rules:

- every L1 node carries source span/provenance, even if synthesized;
- every node declares whether it is pure, may branch, may bind, may call, may
  touch the host, or may suspend/resume;
- the L1 verifier rejects surface-only nodes;
- future backends target L1 or a verified subset of L1.

### L2 Semantic Core

L2 is the stable user-facing core. It is allowed to be larger and friendlier
than L1 because users need concepts, not opcodes.

Initial semantic core:

```text
Source
Value
Binding
Constraint
Function
Call
Data
Pattern
Match
Collection
Block
Example
Trace
Diagnostic
Module
```

L2 features can lower to multiple L1 operations. For example, a constrained
binding may lower to evaluate, type/predicate checks, diagnostic branch, and
commit. It remains one semantic concept for docs and teaching.

### L3 Canonical Surface

L3 is syntax that directly teaches L2 concepts.

Candidates:

- `name = value`;
- `name: Type, predicate = value`;
- `func name(params): body`;
- `data Name: fields`;
- `match value: case pattern: body`;
- `callee(args): block`;
- modules/imports once settled.

These forms are not "mere sugar" from a teaching perspective. They are how a
new user learns Nomi's semantic core. Implementation may still lower them to
L1.

### L4 Sugar Reductions

L4 is admitted convenience syntax. It must reduce to L2/L3 with boring,
inspectable expansions.

Examples:

- `f(x) = expr` -> canonical function plus match/return;
- `_ + 1`, `$1 + $2` -> function values;
- `x |> f` -> call;
- `(+)`, `(+ 1)`, `(1 +)` -> function values;
- `expr where: ...` -> local bindings plus expression/function rewrite;
- `return x if cond` -> branch plus return;
- `unless cond:` -> branch with inverted condition;
- ranges and spread -> calls or collection constructors, if semantics stay
  ordinary.

Rules:

- no L4 construct should require an eval method in the final model;
- every L4 feature has a reduction test;
- inspection can show pre-reduction and post-reduction forms;
- diagnostics point back to source spelling.

### L5 Library Conventions

L5 is where useful patterns grow before becoming syntax.

Candidates:

- collection/table verbs;
- result combinators;
- config merge helpers;
- testing policies;
- trace/report helpers;
- resource policies built on blocks.

Library conventions may become L4 only when examples prove that function
spelling is too cumbersome and syntax improves diagnostics.

### L6 Scoped Extensions

L6 is for notation that is genuinely not ordinary evaluation.

Candidates:

- symbolic/lazy/structural computation;
- units;
- templates;
- domain query notation;
- advanced array/rank notation;
- future effect/proof/rewrite experiments.

Rules:

- extension scope is explicit in source;
- ordinary Nomi outside the scope is unchanged;
- expansion is inspectable;
- diagnostics explain both source notation and expanded form;
- no global syntax mutation.

### L7 Backend Targets

L7 consumes L1 or a verified subset.

Early targets:

- Python AST backend, preserving current behavior;
- direct Python-hosted core interpreter;
- textual/debug core dumps;
- Python foreign-function binding surface.

Later targets:

- Wasm/WASI host adapter;
- MLIR dialect experiment;
- LLVM/native subset;
- bindings for other languages.

Backends must declare capabilities:

```text
supports_dynamic_values
supports_blocks
supports_host_calls
supports_exceptions
supports_resume
supports_python_interop
supports_source_maps
```

## Feature Classification Rules

Every feature manifest should eventually include:

```text
layer
semantic_forms
reduces_to
runtime_hooks_allowed
backend_requirements
inspection_stages
docs
tests
status
```

Decision rules:

1. If the feature changes executable meaning, classify it at L2 or below.
2. If the feature is a spelling for existing meaning, classify it at L4.
3. If ordinary functions are enough, keep it at L5.
4. If it changes notation rules or evaluation discipline locally, classify it
   at L6 and require a fence.
5. If it only affects artifact generation, classify it at L7.
6. If it needs a new eval hook, it is not allowed to pretend to be sugar.
7. If users must learn it in the first hour, it belongs in L2/L3 even if its
   implementation lowers away.

## Current Feature Classification Draft

| Feature/form | Proposed layer | Current implementation shape | Target |
| --- | --- | --- | --- |
| binding assignment | L2/L3 | Python AST assignment plus Nomi env constraints | L2 binding lowers to L1 bind/check/commit. |
| parameter constraints | L2/L3 | Python AST annotations plus Nomi function binding | unified binding semantics for params/fields/patterns. |
| function call | L2/L3 | Python AST call eval | L1 call frame with explicit argument binding. |
| data declarations | L2/L3 | lowering to Python `ClassDef` | semantic data node lowering to L1 construct/value ops. |
| match | L2/L3 | Python AST match eval | pattern engine plus L1 match/pattern-test ops. |
| block calls/yield | L2/L3 | surface `BlockCall` then Python-AST-ish block kwarg | core block value and invoke-block op. |
| equations/piecewise | L4 | desugar pass | canonical function/match reduction. |
| holes/underscore lambdas | L4 | desugar pass | canonical function literal reduction. |
| operator sections/composition | L4 | lowering/desugar | canonical function/call reduction. |
| `where` | L4 or L2-local-binding if promoted | custom attr plus desugar | explicit local binding expression/core block reduction. |
| `unless`/postfix flow | L4 | parser/lowering/runtime path | branch reduction; no eval hook. |
| try expression/null sugar | L4 over L2 failure model | IIFE/runtime helpers | absence/result core once settled. |
| collection verbs | L5 | syntax experiments/tests | standard library functions first. |
| symbolic `quote`/rewrite | L6 | design note only | fenced scoped extension with expansion. |
| Python AST backend | L7 | primary IR today | backend target behind core. |
| reduced interpreter | L1/L2 guardrail | Python AST node stubs | core verifier plus backend parity guard. |

## Implementation Strategy

Do not rewrite the interpreter wholesale. Build the boundary first, then move
one form at a time.

## Operational Orientation Notes

Before touching parser, grammar, lowering, or eval for this effort, do a small
orientation pass:

1. Identify the feature's layer: L0-L7.
2. Identify whether the change is:
   - metadata only;
   - inspection only;
   - reduction/lowering only;
   - evaluator semantics;
   - backend compatibility;
   - frontend/tool presentation.
3. Name the current artifact path and the target artifact path:

```text
current: Lark tree -> Python AST -> interpreter eval_*
target: surface -> semantic core -> implementation core -> backend/eval
```

4. Pick one guardrail test before editing:
   - feature metadata contract;
   - reduction target test;
   - verifier rejection test;
   - `inspect()` stage test;
   - reduced-mode invariant;
   - backend parity test.
5. Keep the Python AST backend green while adding the new artifact.

### Current Code Anchors

Use these files as the starting map:

| Area | Current file | Near-term role |
| --- | --- | --- |
| Feature registry | `prototype/syntax/features.py` | Add layer metadata and reduction targets. |
| Surface nodes | `prototype/syntax/surface.py` | Keep user-spelled shape and spans before backend lowering. |
| Core IR | `prototype/syntax/core.py` or `prototype/core/ir.py` | New passive L1 dataclasses and verifier. |
| Parser API | `prototype/parser/nomi/usage.py` | Expose more inspection stages without changing default execution. |
| Runtime facade | `prototype/runtime/api.py` | Route `inspect()` and future opt-in core execution. |
| Pipeline metadata | `prototype/runtime/pipeline.py` | Record stages, profiles, layers, and backend target. |
| Mode metadata | `prototype/runtime/modes.py` | Keep current mode behavior visible as data. |
| Reduced guard | `prototype/interpreter/reduced/interpreter.py` | Continue catching unreduced forms; later delegate to Core IR verifier. |
| Syntax inspector | `tools/syntax/inspect.py` | Make artifact boundaries visible from the command line. |

### Preparatory Commit Shape

Prefer this order:

```text
commit 1: docs/skills/orientation updates
commit 2: passive feature metadata fields + tests
commit 3: fill metadata for builtin features
commit 4: passive CoreNode skeleton + verifier tests
commit 5: inspection stage for feature/layer table or core stub
commit 6: first sugar reduction invariant
commit 7: first semantic-core subset
```

If a commit needs both metadata and behavior changes, split it unless the
behavior is impossible to test without the metadata.

### Do Not Start With

- package-wide moves;
- deleting Python AST backend paths;
- adding MLIR/LLVM/Wasm code;
- rewriting the interpreter dispatch loop;
- moving all grammar files into new directories;
- converting multiple features at once.

Those become safer after feature metadata, passive Core IR, verifier, and
inspection stages exist.

### Phase 0: Name The Layers

Deliver:

- this plan;
- docs index links;
- terms used consistently in future TODOs and commits.

Gate:

- no behavior change;
- team can classify new features without inventing new vocabulary.

### Phase 1: Add Passive Layer Metadata

Deliver:

- extend `SyntaxFeature` with layer metadata:
  - `layer`;
  - `semantic_forms`;
  - `reduces_to`;
  - `runtime_hooks_allowed`;
  - `backend_requirements`;
- extend `ModeSpec` or add `FeatureProfile` metadata for active layers;
- add contract tests that all builtin features declare a layer.

Gate:

- no parser or eval behavior changes;
- current tests pass;
- `python`, `nomi`, and `reduced` modes still work.

### Phase 2: Define Core IR Skeleton

Deliver:

- `prototype/syntax/core.py` or `prototype/core/ir.py`;
- dataclasses for the smallest useful L1 nodes;
- `SourceSpan`/provenance support shared with surface nodes;
- text/dump printer;
- verifier that rejects unknown/surface/sugar nodes;
- read-only inspection stage: `inspect(stage="core_stub")` or
  `inspect(stage="core")` for a tiny subset.

Initial subset:

```text
literal
load
bind
call
function
return
branch
diagnostic
module
```

Gate:

- no execution depends on the new IR yet;
- fixtures can snapshot core dumps for simple programs;
- verifier exists before evaluator work starts.

### Phase 3: Add Core Evaluation Skeleton

Deliver:

- `prototype/core/eval.py` with a tiny direct evaluator for the Phase 2 subset;
- `CoreExecutionResult`;
- environment/call-frame records separate from Python interpreter env;
- contract tests comparing core eval with existing Python-backed eval for pure
  examples.

Gate:

- core eval is opt-in only;
- existing runtime remains default;
- no L4 sugar reaches core eval unless reduced first.

### Phase 4: Make Reduced Mode About Core, Not Only Python AST

Deliver:

- a core verifier equivalent to the current reduced-interpreter guard;
- tests that L4 constructs are absent after reduction;
- error messages name the unreduced feature and expected reduction path;
- keep current Python AST reduced interpreter as the backend guard until core
  eval takes over.

Gate:

- reduced mode still passes full language feature tests;
- every L4 feature has a declared reduction target.

### Phase 5: Parse/Lower Pipeline Stages Become First-Class

Deliver inspection stages:

```text
raw_tree
transformed_tree
surface
semantic_core
implementation_core
python_ast
```

Deliver pipeline metadata:

- stage names;
- active feature profile;
- layer boundaries;
- reduction pass list;
- backend target.

Gate:

- `prototype.runtime.inspect()` can inspect more than Python AST;
- contract tests cover stage availability and invalid-stage diagnostics.

### Phase 6: Migrate One Semantic Core Feature End To End

First candidate: constrained binding.

Why:

- it is central to Nomi;
- it already has runtime tests;
- it crosses assignment, parameter binding, data fields, patterns, and
  diagnostics;
- it clarifies the difference between user-facing semantic core and
  implementation core ops.

Deliver:

- L2 binding node or semantic record;
- L1 bind/check/commit lowering;
- direct core-eval support for simple binding constraints;
- Python AST backend compatibility;
- feature tests that compare old and core-backed paths.

Gate:

- one semantic core concept can be inspected at surface, semantic core,
  implementation core, Python AST, and eval result stages.

### Phase 7: Migrate One Sugar Feature End To End

First candidate: `unless` or postfix conditional return.

Why:

- it should not need eval semantics;
- it is easy to verify as branch reduction;
- it demonstrates the L4 rule clearly.

Deliver:

- feature metadata: L4, reduces to branch;
- core/surface inspection before and after reduction;
- tests proving no `unless` node reaches L1 eval;
- diagnostics/provenance still point to `unless` source.

Current state:

- `unless` and postfix conditional flow are declared as L4 features with
  branch reduction targets in `prototype/syntax/features.py`;
- their existing parser lowering already emits ordinary `ast.If` branch shape;
- remaining work is to make the before/after expansion inspectable through
  surface/core stages with source provenance.

Gate:

- a sugar feature is fully separated from eval.

### Phase 8: Migrate Block Calls As A Control Core Feature

Block calls should probably stay L2/L3, not L4, because they introduce the
one block story: caller-side code attached to a call, callee invokes with
`yield`.

Deliver:

- core block value;
- invoke-block operation;
- block frame/continuation record;
- Python backend compatibility path;
- direct eval tests for simple block invocation;
- eventual reduced guard that treats block call as core, not sugar.

Gate:

- block semantics no longer depend on a Python-AST-shaped keyword convention.

### Phase 9: Backend Capability Boundary

Deliver:

- backend target metadata;
- capability flags;
- `python_ast` backend contract tests;
- core debug backend;
- a small foreign-binding note for how other languages could call L1/L2
  artifacts.

Gate:

- a backend can say "I support this verified subset" without claiming full
  language support.

### Phase 10: Scoped Extension Framework

Deliver:

- parse/profile support for fenced scoped extensions;
- `extension` metadata in feature manifests;
- inspection view that shows source form and expansion;
- a stub or prototype for `quote`/symbolic structure, kept out of default
  everyday Nomi.

Gate:

- advanced notation has a home without contaminating core eval or everyday
  syntax.

## Eval Refactor Rules

Use these rules before adding or keeping any `eval_*` behavior.

1. If the form is L4 sugar, do not add a final eval hook. Lower it first.
2. If the form is L2 semantic core, the eval hook belongs to core eval, not a
   surface spelling.
3. If the form is L6 scoped extension, eval sees only its declared expansion or
   a fenced extension node.
4. If a backend needs special handling, put it in L7 backend code, not the
   language evaluator.
5. If Python AST needs a workaround, document it as backend compatibility, not
   semantics.
6. A new eval hook must name its layer and its removal/migration path if it is
   temporary.

## Parser And Grammar Rules

Grammar should reflect layer ownership.

Recommended organization over time:

```text
prototype/grammar/
  core/              # canonical L3 forms needed for semantic core
  sugar/             # L4 spelling layers
  extensions/        # L6 fenced notation, inactive by default
  python_compat/     # Python compatibility surface, if retained as profile
```

Do not move files all at once. First add metadata:

- grammar fragment layer;
- owning feature;
- default profile;
- inspection name;
- reduction target.

Then move one grammar cluster when tests and feature metadata already name the
target.

## Test Strategy

New tests should follow the new layers:

```text
unit/core/                # L1 node verifier/evaluator tests
unit/syntax/              # feature metadata, manifests, grammar profile tests
features/<feature>/       # L2/L3/L4 behavior by feature
contracts/                # runtime inspect/execute/profile/backends
regression/               # snapshots for parse/core/backend/output drift
e2e/                      # actual user surfaces
```

Required tests by feature layer:

| Layer | Required tests |
| --- | --- |
| L2/L3 semantic core | parse/surface, semantic core, implementation core, eval, diagnostics. |
| L4 sugar | parse/surface, reduction target, no unreduced node reaches core eval, runtime behavior. |
| L5 library | ordinary unit/feature tests, no grammar changes. |
| L6 scoped extension | profile/fence tests, expansion inspection, no effect outside scope. |
| L7 backend | capability contract, artifact inspection, parity tests for supported subset. |

## First Implementation Slice

The first code phase should be deliberately boring.

Suggested commit sequence:

1. Extend `SyntaxFeature` metadata with layer fields and fill them for current
   features.
2. Add tests that every feature declares a layer and that L4 features declare a
   reduction target.
3. Add a passive `CoreNode` skeleton and verifier with no runtime integration.
4. Add `inspect(stage="features")` or a tiny CLI/debug helper to print the
   active feature/layer table.
5. Only then start a small core eval subset.

This gives us a stable map before touching semantics.

## Open Questions

- Is `where` L4 sugar over local binding, or does Nomi want a first-class L2
  local-binding expression concept?
- Are exceptions part of L1, or should expected failure become an L2 result
  story that lowers to multiple backend mechanisms?
- How much Python compatibility remains in default Nomi versus a
  `python-compat` profile?
- Should `match` be L2 semantic core immediately, or should the first L1
  evaluator support only lower-level branch/pattern-test operations?
- Which subset must be backend-portable first: pure functions/data/calls, or
  scripts with host calls?
- How visible should implementation core be to everyday users versus tools and
  advanced docs?

## Success Criteria

This separation is working when:

- a new feature can answer "what layer owns me?" in one line;
- sugar cannot accidentally acquire permanent eval semantics;
- reduced mode and core verification catch unreduced forms early;
- parser inspection can show source, surface, semantic core, implementation
  core, and backend artifacts;
- backend work can target a verified subset without reinterpreting surface
  syntax;
- docs teach L2/L3 first while implementers can work on L0/L1 without changing
  user concepts.
