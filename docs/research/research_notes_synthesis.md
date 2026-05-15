# Research Notes Synthesis

> Status: source synthesis note; not an active language spec.
>
> This document distills a large, informal collection of research notes into
> coherent design pressure for Nomi. It is not a literature review. It is a map
> from scattered anchors to language-design work that can be implemented
> hierarchically.
>
> The links and book/article names in the raw notes are treated as research
> leads. They are not all validated here. The synthesis below is based on the
> themes and observations in the notes.
>
> Consolidation note: stable decisions from this file should be folded into
> `../language/language_foundation.md`, `../language/language_spec.md`, or
> focused syntax docs. Do not add new active design commitments here.

## Central Synthesis

The notes repeatedly circle one idea:

> Programming is the controlled growth of sophistication from simple elements,
> where every layer should remain peelable, inspectable, and reducible to a
> smaller core.

This is stronger than "take good ideas from languages." It says the language
must support a discipline of construction:

```text
primitive values
  -> names and contexts
  -> judgement and constraints
  -> transformations
  -> structured data
  -> patterns and decomposition
  -> repeated/array/table transformations
  -> time-shaped control
  -> effects and worlds
  -> examples, traces, explanations
  -> symbolic reflection and rewrite
```

The raw notes contain many references, but the useful organizing principle is
not historical chronology or language family. It is the progressive reification
of thought into executable structure.

## Major Research Pressures

### 1. Rewriting, Unification, And Symbolic Reduction

Raw anchors:

- term rewriting,
- substitutions and unification,
- equational unification modulo a theory,
- e-graphs and equality saturation,
- anti-unification,
- resolution theorem proving,
- description logic,
- Mathematica rewrite rules,
- Lisp symbolic expressions,
- logic variables.

Design pressure:

Nomi needs an explicit symbolic layer where program-shaped values can be
matched, transformed, normalized, generalized, and explained.

Important distinctions:

- pattern matching is one-way shape recognition,
- unification solves for substitutions that make shapes agree,
- equational unification adds background equations,
- rewriting transforms a matched term,
- strategies control which rewrite applies,
- normal forms are values that cannot reduce further under a chosen system.

Nomi implication:

Do not make ordinary code implicitly symbolic. Add an explicit `quote` boundary
and later add rewrite/unification tools over quoted syntax values.

Layer placement:

```text
L6 patterns and choice
L10 traces and explanation
L11 quote, rewrite, notation
```

Concrete future specs:

```text
quote_and_syntax_values_feature.md
rewrite_rules_feature.md
unification_and_patterns_feature.md
normal_forms_and_rewrite_strategies_feature.md
```

Small-core reduction:

```text
quoted syntax -> SyntaxValue
pattern -> Pattern over SyntaxValue or Value
unification -> substitutions over Pattern variables
rewrite -> Pattern + replacement + strategy
normalization -> repeated rewrite with trace
```

### 2. Binding, Environment, Store, And Scope

Raw anchors:

- R. D. Tennent on binding versus updating, environment versus store, scope
  versus lifetime,
- Tennent's correspondence principle,
- ALGOL block structure,
- Dijkstra and Landin on parameterless procedures and language semantics,
- Python global/nonlocal/env implementation friction,
- R first-class environments and data masks,
- Scala `val`/`var`,
- Pascal `with`,
- Ruby block parameter passing closer to assignment.

Design pressure:

Nomi's binding story must be made precise before higher features pile up.
Several raw implementation issues are symptoms of the same missing model:

- constraints and global/nonlocal assignment can drift apart,
- function arguments and assignment are not yet one operation,
- block parameters are not yet normal bindings,
- module environments are not yet cleanly separated,
- context manager/yield control stretches the environment model.

Nomi implication:

Binding is not just assignment syntax. It is the act of introducing a name into
a context. Updating storage is separate. This should become an explicit model.

Layer placement:

```text
L0 source, context, spans
L2 bindings and scope
L3 constraints and diagnostics
L8 blocks and yield
```

Concrete future specs:

```text
source_context_spans_feature.md
bindings_and_scope_feature.md
environment_store_lifetime_feature.md
module_context_feature.md
```

Small-core reduction:

```text
definition -> Context extension
assignment -> Binding or Store update, depending on target
parameter -> Binding in call context
block parameter -> Binding in block invocation context
import -> Binding of module/member value
```

### 3. Functions, Composition, And Function Algebra

Raw anchors:

- Landin, Strachey, McCarthy, Backus, Lisp `apply`,
- combinatory logic,
- function-level programming,
- Haskell composition, Kleisli composition, monads, applicatives, functors,
- pipelines in R, Julia, Rust-like `|>`,
- Mathematica `Apply`, `Map`, `Thread`, `Through`,
- R's "everything that happens is a function call",
- Python friction around lambda, decorators, methods, and pipeline style.

Design pressure:

Nomi needs a strong account of transformation before it adds richer surface
features. Function, call, pipeline, map, thread, method call, operator, and
composition should be related, not isolated.

Important distinctions:

- ordinary composition: `A -> B -> C`,
- Kleisli/effectful composition: `A -> M[B] -> M[C]`,
- applicative combination: combine independent contextual values,
- map/lift: transform inside a context,
- flatMap/bind: transform and flatten context,
- pipeline: value-first spelling of call sequence,
- method call: receiver-first spelling of call.

Nomi implication:

Do not import monad syntax. Understand the need: sequencing transformations
that carry context, failure, nondeterminism, logging, IO, or other effects.
Expose a readable direct style first; let deeper algebra guide reduction and
diagnostics.

Layer placement:

```text
L4 functions, calls, transformation
L7 collections, tables, repetition
L8 blocks, yield, time-shaped control
L9 effects, worlds, capabilities
```

Concrete future specs:

```text
functions_and_calls_feature.md
pipelines_and_composition_feature.md
function_lifting_and_contexts_feature.md
operator_and_infix_naming_feature.md
```

Small-core reduction:

```text
function definition -> Binding of Function value
call -> argument binding + body evaluation
pipeline -> ordered calls
method call -> call with receiver binding
lift/map -> call under a context policy
flatMap/bind -> call + context flattening rule
```

### 4. Blocks, Coroutines, Resumable Control, And Effects

Raw anchors:

- Ruby blocks, procs, lambdas, fibers,
- Python generators, `yield from`, context managers, `throw`, `close`,
- PEP 340/343 and retry-context-manager friction,
- delimited continuations,
- algebraic effects and handlers,
- resumable exceptions,
- R conditions, signals, restarts, `on.exit`,
- direct-style effects,
- Koka, Eff, OCaml effects,
- function color and async.

Design pressure:

There is a recurring need to abstract time-shaped behavior without collapsing
everything into callbacks, decorators, context managers, or monads.

The core issue is inversion of control:

- a function call is caller-controlled,
- a coroutine or block policy can return control multiple times,
- a handler can resume at the point of a signal,
- a context policy can wrap, retry, suppress, or translate failure.

Nomi implication:

Block calls and `yield` are a first candidate for user-facing control policy.
Algebraic effects and resumable exceptions should be studied as deeper models,
but the daily surface should stay direct and inspectable.

Layer placement:

```text
L8 blocks, yield, time-shaped control
L9 effects, worlds, capabilities
L10 traces and explanation
```

Concrete future specs:

```text
../features/block_calls_feature.md
block_scope_and_control_flow_feature.md
signals_conditions_restarts_feature.md
effects_worlds_capabilities_feature.md
structured_concurrency_feature.md
```

Small-core reduction:

```text
block call -> Call + attached Block value
yield -> invoke attached Block at continuation point
signal/effect -> suspend with request value
handler -> policy that supplies response or resumes/aborts
context manager -> block policy with acquire/release protocol
```

### 5. Data Construction, Deconstruction, And Algebraic Modeling

Raw anchors:

- ADTs, product and sum types,
- GADTs,
- Scala case classes, companion objects, `apply`/`unapply`,
- Kotlin data classes and receiver functions,
- Pascal records, enumerations, subranges, sets,
- F-algebras, catamorphisms, anamorphisms,
- inductive and coinductive types,
- lenses as decomposition/recomposition.

Design pressure:

Programs need a unified account of construction and deconstruction.

The notes repeatedly point to a duality:

- construct data from parts,
- observe/deconstruct data into parts,
- match shapes,
- transform recursively,
- preserve invariants.

Nomi implication:

`data`, explicit decode boundaries, structural patterns, constructor calls,
pattern matching, and deconstruction should be designed together. Scala's
`apply/unapply` is useful evidence, but Nomi should choose names and syntax
that reveal construction/deconstruction directly instead of relying on
convention.

Layer placement:

```text
L5 data and external structure
L6 patterns and choice
L10 examples and explanation
```

Concrete future specs:

```text
data_declarations_feature.md
data_decode_boundaries_feature.md
constructors_and_deconstructors_feature.md
patterns_and_match_feature.md
recursive_data_and_folds_feature.md
```

Small-core reduction:

```text
data declaration -> constructors + fields + pattern shape
decode boundary -> structural validation + projection
structural pattern -> one-off recognition + projection
deconstructor -> Pattern producer
fold/catamorphism -> structured recursion over data
lens -> focus + residue + reconstruction rule
```

### 6. Array, Table, Vector, And Listable Thinking

Raw anchors:

- APL, J, K, Q, Shakti,
- Backus function-level programming,
- Mathematica `Listable`, `Thread`, `MapThread`, `Apply`, `Through`,
- R vectors, recycling, attributes, data frames, tibbles, data masks,
- Python PEP 225 and element-wise operators,
- Pandas pipe/query friction,
- collection transforms and selectors.

Design pressure:

Scalar-first languages make whole-data programming feel bolted on. Array-first
languages are powerful but can become visually dense. Nomi should support
whole-collection thought without making glyph-density the default style.

Important distinctions:

- map one function over one collection,
- thread a function over several aligned collections,
- lift scalar operations over context,
- select/project by name or position,
- preserve shape/rank metadata,
- reduce/fold/accumulate,
- query table-shaped data.

Nomi implication:

Collection behavior should be designed as a layer over functions, calls,
binding, and explicit structure. Do not add ad hoc list magic one operation at
a time.

Layer placement:

```text
L4 functions and calls
L5 data and external structure
L7 collections, tables, repetition
```

Concrete future specs:

```text
collection_transforms_feature.md
listable_and_threaded_calls_feature.md
tables_and_queries_feature.md
rank_and_shape_feature.md
selectors_and_slicing_feature.md
```

Small-core reduction:

```text
listable call -> lift scalar Function over Collection context
threaded call -> aligned element bindings + repeated Call
table query -> shape-bound row bindings + collection transform
selector -> pattern/projection over structured Value
```

### 7. Quotation, Non-Standard Evaluation, And Contextual Names

Raw anchors:

- Lisp S-expressions and M-expressions,
- Lisp `quote`, `eval`, `apply`,
- Mathematica expression heads and parts,
- R `quote`, `substitute`, quosures, data masks, tidy evaluation,
- Julia macros, quote/unquote/splice,
- Python string-based query workarounds,
- symbolic names for plotting, formulas, and data analysis.

Design pressure:

Users often need to refer to code, names, columns, formulas, or expressions as
values. Existing languages either make this too magical or too stringly.

Nomi implication:

Quotation needs a first-class, explicit model:

- syntax values know source spans,
- quoted expressions can carry environment when needed,
- unquote/splice should be explicit,
- data masks or contextual name resolution must be scoped,
- expansion must be inspectable.

Layer placement:

```text
L0 source and spans
L2 bindings and contexts
L10 traces and explanation
L11 quote, rewrite, notation
```

Concrete future specs:

```text
quote_and_syntax_values_feature.md
quasiquote_unquote_feature.md
contextual_name_resolution_feature.md
data_masks_and_formulas_feature.md
scoped_notation_feature.md
```

Small-core reduction:

```text
quote -> SyntaxValue + Span
quosure -> SyntaxValue + Context
unquote -> explicit evaluation inside quoted syntax
data mask -> scoped Context layered before lexical Context
macro/notation -> SyntaxValue -> SyntaxValue transform with expansion trace
```

### 8. Logic, Modal Reasoning, And Program Judgement

Raw anchors:

- Boole's laws of thought,
- Tarski object/meta-language,
- modal logic and Kripke semantics,
- dynamic logic,
- Hoare triples and Dijkstra weakest preconditions,
- resolution theorem proving,
- description logic,
- bounded rationality and formalism as occasional validation.

Design pressure:

Nomi should not force users to program in formal logic. But the language should
be designed so that formal reasoning can attach where it helps.

Useful first-principles distinction:

- propositional truth: isolated truth at a point,
- modal truth: truth across reachable states/worlds,
- dynamic logic: truth after program execution,
- Hoare logic: pre/post judgement around commands,
- constraints: local judgement at a binding boundary.

Nomi implication:

Start with executable constraints, examples, and traces. Later, allow stronger
reasoning over worlds, effects, and state transitions. Formalism is a tool for
resolving deep ambiguity, not a burden on daily use.

Layer placement:

```text
L3 constraints and judgement
L9 effects/worlds/capabilities
L10 examples/traces/explanation
L11 symbolic reasoning
```

Concrete future specs:

```text
examples_traces_explanation_feature.md
state_transition_judgement_feature.md
modal_worlds_and_reachability_feature.md
```

Small-core reduction:

```text
constraint -> local judgement
example -> executable judgement over call/result
trace -> observed transition sequence
world -> point of evaluation plus reachable alternatives
proof/check -> optional judgement over traces or symbolic forms
```

### 9. Historical And Human-Centered Language Design

Raw anchors:

- Boole, Leibniz, Turing, Church, Godel, Shannon,
- Babbage and Ada,
- Dijkstra, Naur, Landin, Strachey, McCarthy,
- ALGOL 60/68, Pascal, Modula, Oberon,
- Tennent, Reynolds, Hoare, Scott, Plotkin,
- Gabriel, Tomas Petricek, Jonathan Edwards, Subtext,
- Python, Ruby, R, Scala, Kotlin, Mathematica.

Design pressure:

Language design is a human activity. Formal systems matter, but natural
language, documentation, notation, examples, and the programmer's memory matter
too.

The notes point to a productive tension:

- ALGOL-like discipline and reports,
- Lisp-like minimalism and symbolic power,
- Python/Ruby/R pragmatism,
- Mathematica's expression uniformity,
- Haskell/ML's algebraic clarity,
- Dijkstra/Tennent-style semantic principles,
- AI-assisted exploration and critique.

Nomi implication:

Use formal tools when they clarify. Avoid making users carry formal machinery
for routine programming. Preserve the ability to explain every layer in natural
language.

Layer placement:

```text
all layers, especially documentation and diagnostics
```

Concrete future specs:

```text
language_report_style_guide.md
design_review_process.md
diagnostic_language_guidelines.md
```

## Cross-Cutting Theses To Carry Forward

### Thesis 1: Hierarchy Is The Main Tool Against Complexity

Strachey-style hierarchical construction and the first-principles ladder point
in the same direction. Nomi should let programmers build bigger concepts from
smaller ones, then peel the layers back when something fails.

Design consequence:

Every feature spec should include a reduction story.

### Thesis 2: Binding And Context Are More Fundamental Than Syntax

Many scattered notes about parameters, assignment, environments, modules,
R data masks, Scala implicits, `with`, and non-standard evaluation are really
about one thing:

> In which context is this name resolved, and what does binding it mean?

Design consequence:

Bindings, scope, context stacks, and source spans should be implemented before
fancier syntax spreads.

### Thesis 3: Rewriting Is Powerful Only Behind Explicit Boundaries

Term rewriting, Mathematica, Lisp, R quasiquotation, Julia macros, and
e-graphs all point to symbolic transformation. They also warn against hidden
magic.

Design consequence:

`quote`, `rewrite`, `use`, and expansion trace are required boundaries.

### Thesis 4: Effects Need Direct Style And Explanation

Monads, applicatives, algebraic effects, continuations, exceptions, context
managers, and R conditions are different answers to sequencing contextual
computation.

Design consequence:

Nomi should first offer readable direct-style block/effect constructs, while
keeping a deeper algebraic interpretation available for design and diagnostics.

### Thesis 5: Whole-Data Thinking Must Be Designed, Not Patched On

APL/J/K/Q, R, Mathematica, Pandas, and Python's rejected element-wise operator
ideas show that scalar-first design creates friction.

Design consequence:

Listable/threaded calls, collection transforms, rank/shape, and table queries
should be one layer over functions and binding.

### Thesis 6: Explanation Is A Language Feature

The notes repeatedly return to trace, diagnostics, examples, proof, and the
difficulty of reasoning about control flow. Explanation cannot wait until
tooling.

Design consequence:

Every semantic event should eventually be traceable:

```text
bind
judge
call
match
yield
effect
rewrite
example-check
```

## Mapping Notes To The Hierarchical Plan

| Layer | Raw-note themes to digest | Next design artifact |
| --- | --- | --- |
| L0 source/context/spans | Tarski object/meta-language, R srcref, source refs, diagnostics, module/env friction | `source_context_spans_feature.md` |
| L1 values | Boole things/propositions, Lisp atoms/pairs, Mathematica atoms/heads, R vectors/scalars | `values_and_literals_feature.md` |
| L2 binding/scope | Tennent binding/store, ALGOL blocks, R env/data masks, Scala val/var, Pascal with | `bindings_and_scope_feature.md` |
| L3 constraints/judgement | refinement types, description logic, modal truth, BindingError, examples/tests | `constraints_and_diagnostics_feature.md` |
| L4 functions/calls | Landin/Strachey, Lisp apply, Backus, pipelines, Kleisli, function algebra | `functions_and_calls_feature.md` |
| L5 data/external structure | ADTs, GADTs, Scala apply/unapply, Pascal records/subranges, explicit decode validation | `data_declarations_feature.md` |
| L6 patterns/choice | unapply, pattern matching, unification, conditionals, dynamic logic | `patterns_and_match_feature.md` |
| L7 collections/tables | APL/J/K/Q, R vectors/dataframes, Mathematica Listable/Thread, Pandas pipe/query | `collection_transforms_feature.md` |
| L8 blocks/yield | Ruby blocks, Python generators/context managers, coroutines, delimited continuations | `block_scope_and_control_flow_feature.md` |
| L9 effects/worlds | algebraic effects, monads, R conditions/restarts, capabilities, modal worlds | `effects_worlds_capabilities_feature.md` |
| L10 examples/traces | Boole judgement, examples as semantics, tracing, diagnostics, Hoare/Dijkstra | `examples_traces_explanation_feature.md` |
| L11 quote/rewrite | term rewriting, Lisp/R/Julia/Mathematica quotation, e-graphs, macros | `quote_and_syntax_values_feature.md` |

## Candidate Near-Term Commit Series

The raw notes suggest this bottom-up sequence:

1. Source/context/spans: establish inspectable artifacts.
2. Values/literals: clarify atoms, collections, absence, identity, display.
3. Binding/environment/store: separate naming from mutation.
4. Constraints/diagnostics: unify type, predicate, and message judgement.
5. Functions/calls: make call semantics and argument binding central.
6. Data/shape: owned data versus external structure.
7. Patterns/match/unification boundary: choice and deconstruction.
8. Pipelines/function algebra: composition, lifting, threading.
9. Collections/tables/rank: whole-data transformation.
10. Blocks/control/effects: refine block calls, then conditions/effects.
11. Examples/traces/explanation: make behavior inspectable.
12. Quote/rewrite/notation: symbolic power after lower layers are stable.

This sequence differs slightly from the previous roadmap by splitting
function algebra and collection/rank work more explicitly.

## Immediate Implementation Implications

The notes point to several implementation tasks that should support the design
without overfitting to current syntax:

- introduce Nomi-owned IR nodes with source spans,
- separate `Context`, `Binding`, and future `Store` concepts,
- make assignment, parameters, imports, block parameters, and pattern captures
  use one binding path,
- replace bare constraint predicates with structured `Constraint` values,
- introduce trace records for semantic events before building advanced
  explanations,
- lower surface forms into a smaller evaluator core,
- treat Python AST as a bootstrap tool, not the long-term semantic model,
- document every semantic feature with reduction to the first-principles core.

## Research Notes That Need Focused Follow-Up

These raw clusters are rich enough to deserve dedicated notes later:

- R evaluation model: promises, quosures, data masks, replacement forms,
  vector semantics, conditions/restarts.
- Mathematica expression model: heads, parts, attributes, Listable, Thread,
  Apply, rewrite rules.
- Scala/Kotlin object/context model: `apply`, `unapply`, extension methods,
  givens/usings, receiver functions.
- ALGOL/Pascal/Tennent/Landin line: binding, correspondence, block structure,
  semantic principles.
- Category-theory line: functors, monads, adjunctions, F-algebras, lenses,
  Lawvere theories, but only where they clarify concrete language design.
- Logic/reasoning line: modal logic, dynamic logic, Hoare triples,
  description logic, resolution, unification.
- Array-language line: APL/J/K/Q/Shakti, rank, shape, function-level style.

## Deep Dive Index (May 2026)

Cross-language comparative research added in the May 2026 expansion. Each file
focuses on synthesis across languages rather than single-language catalogues:

- [array_languages_deep_dive.md](array_languages_deep_dive.md) — APL, J, K, Q, BQN, Uiua: rank polymorphism, trains, combinators, tacit programming.
- [beam_languages_erlang_elixir_gleam.md](beam_languages_erlang_elixir_gleam.md) — Erlang/Elixir/Gleam: OTP, supervision trees, let-it-crash, pattern matching, `use` expression.
- [csharp_java_dart_modern_features.md](csharp_java_dart_modern_features.md) — C#/Java/Dart: pattern matching, records/data classes, null safety, async models, cross-language convergence analysis.
- [diagnostics_and_explanations_comparative.md](diagnostics_and_explanations_comparative.md) — 10-language diagnostic architecture comparison: structural invariants, design choices, tensions.
- [error_handling_defer_resource_cleanup_notes.md](error_handling_defer_resource_cleanup_notes.md) — 12-language error/defer/resource survey: three error stories, propagation operators, cleanup mechanisms.
- [go_design_philosophy_deep_dive.md](go_design_philosophy_deep_dive.md) — Go: simplicity thesis, structural interfaces, goroutines/CSP, `defer`, package design, adopt/refuse decisions.
- [pattern_matching_synthesis.md](pattern_matching_synthesis.md) — 10-language pattern matching synthesis: structural invariants, genuine forks, exhaustiveness, binding style.
- [standard_library_design_comparative.md](standard_library_design_comparative.md) — 10-language stdlib design: prelude philosophy, core-vs-contrib splits, deprecation policies, package organization.
- [typescript_type_system_deep_dive.md](typescript_type_system_deep_dive.md) — TypeScript: type narrowing/flow typing, structural typing, conditional types, `satisfies`, erased types.
- [cross_language_synthesis_master.md](cross_language_synthesis_master.md) — Capstone synthesis: universal convergences, genuine design forks, hidden incompatibilities, Nomi resolution framework.
- [first_hour_pedagogy_deep_dive.md](first_hour_pedagogy_deep_dive.md) — 10-system pedagogy survey: Python, Go, Dart, Racket, Scratch, Logo, BASIC, Elm, Khan Academy, Swift Playgrounds. First-hour success design, beginner error messages.
- [packaging_and_project_structure_deep_dive.md](packaging_and_project_structure_deep_dive.md) — 8-ecosystem packaging survey: Python, Cargo, Go modules, Mix, npm, NuGet, Nix flakes, Maven. Manifest design, dependency resolution, workspaces.
- [data_boundary_systems_deep_dive.md](data_boundary_systems_deep_dive.md) — 10-system data boundary survey: Pydantic, CUE, Nickel, Pkl, Dhall, Terraform, JSON Schema, TypeScript, serde, Elm decoders. Decode pipeline, merge/override, provenance.
- [table_and_flow_systems_deep_dive.md](table_and_flow_systems_deep_dive.md) — 8-system table/flow survey: SQL, LINQ, dplyr, Polars, DuckDB, Nushell, pandas, K/Q. Verb vocabulary, query lowering, explain.
- [interactive_explanation_deep_dive.md](interactive_explanation_deep_dive.md) — 10-system interactive survey: Jupyter, Pluto, Darklang, Smalltalk, Racket, Light Table, Observable, Swift Playgrounds, Bret Victor, Elm debugger. Reactive execution, trace/explain.
- [formatting_and_style_deep_dive.md](formatting_and_style_deep_dive.md) — 10-formatter style survey: gofmt, Black, Rustfmt, Prettier, elm-format, clang-format, Ormolu, dart format, zig fmt, ocamlformat. Canonical formatter doctrine.

For the updated coverage status and remaining research gaps, see
[language_family_coverage_map.md](language_family_coverage_map.md).

## Guardrail Against Rabbit Holes

The notes contain many deep trails. A trail becomes useful for Nomi only when it
can answer this:

```text
What primitive programming act does this clarify,
what layer does it belong to,
and what implementable feature does it suggest?
```

If the answer is unclear, keep it as background inspiration. Do not promote it
to active design yet.
