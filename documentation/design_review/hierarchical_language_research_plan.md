# Hierarchical Language Research Plan

> Status: active research and implementation roadmap.
>
> This document turns the first-principles model into a concrete design and
> implementation ladder. The rule is: primitive ideas first, progressively more
> sophisticated features later, and every higher layer must reduce back down to
> the smaller core beneath it.

## Purpose

Nomi should be researched and implemented as a hierarchy, not as a flat feature
wishlist.

Each layer should answer:

- what primitive cognitive act it supports,
- what semantic core it adds,
- which lower layers it depends on,
- which concrete syntax ideas are worth exploring,
- what variations and tradeoffs need study,
- what small prototype would prove the idea,
- how the layer reduces back to the core.

The shape is:

```text
L0  source, context, spans
L1  values
L2  bindings and scope
L3  constraints, judgement, diagnostics
L4  functions, calls, transformation
L5  data and shape
L6  patterns and choice
L7  collections, tables, repetition
L8  blocks, yield, time-shaped control
L9  effects, worlds, capabilities
L10 examples, traces, explanation
L11 quote, rewrite, notation
```

This is both a research ladder and an implementation ladder. A later feature
may be prototyped early, but its design is not complete until it reduces to the
layers below it.

## Research Method

The companion [Research Notes Synthesis](research_notes_synthesis.md) maps the
raw research anchors into this hierarchy. Use it as the intake layer before
promoting scattered notes into focused feature specs.

For each layer:

1. Start from the first-principles need.
2. Define the semantic role in Nomi's small core.
3. Study references from other languages only as possible answers.
4. Compare syntax variations.
5. Choose one preferred direction and name rejected alternatives.
6. Write a focused feature spec.
7. Add target examples, including not-yet-implemented syntax when useful.
8. Implement the smallest useful operational slice.
9. Add diagnostics and explanation hooks early.
10. Revisit the layer once higher layers stress it.

Every focused feature spec should include this header:

```text
First-principles act:
Core primitives:
Depends on:
Enables:
Reduction:
Open tradeoffs:
```

## L0: Source, Context, And Spans

First-principles act:

```text
make thought inspectable
```

Core primitives:

```text
Source
Span
Context
Module
Diagnostic
```

Why it comes first:

Before values or syntax become meaningful, the language needs a durable notion
of source location, lexical context, module boundary, and diagnostic attachment.
Without this, later explanation features become retrofits.

Concrete ideas:

- source spans attached to every parsed node,
- a module object as an executable namespace,
- a context stack for lexical scopes and dynamic policy scopes,
- comments and doc blocks that can attach to declarations,
- stable internal representation independent of Python AST where needed.

Variations to research:

- lower directly to Python AST versus introduce a Nomi IR first,
- keep indentation exactly Python-like versus define Nomi-specific layout rules,
- make comments inert text versus attach doc/comment values to syntax nodes,
- file-as-module versus explicit `module name:` declaration.

Reduction:

```text
source text -> parsed forms with spans -> Nomi IR -> evaluation in Context
```

Small prototype:

- parse a file into Nomi-owned nodes with spans,
- report a diagnostic with exact source location,
- preserve module-level bindings in a `Context`.

Focused spec to write:

```text
source_context_spans_feature.md
```

## L1: Values

First-principles act:

```text
Distinguish
```

Core primitives:

```text
Value
Identity
Equality
Display
```

Concrete ideas:

- literals: number, string, bool, none/absence,
- structured literal values: list, tuple, dict, set,
- value identity versus equality,
- display/repr rules for diagnostics,
- eventual exact numeric tower: int, float, decimal, rational, complex,
- symbolic values only behind explicit `quote`.

Variations to research:

- Python-compatible literals versus cleaned-up Nomi literal grammar,
- one absence value (`None`) versus option-style `Some/None`,
- decimal/rational exactness as syntax versus library values,
- mutable collections by default versus persistent values for selected data.

Reduction:

```text
literal syntax -> Value
collection literal -> Value containing Values
display -> Value rendered with context
```

Small prototype:

- define a Nomi `Value` protocol or IR-level value representation,
- keep Python-hosted values where useful but wrap diagnostics around them,
- add value display tests independent of Python's default `repr` where needed.

Focused spec to write:

```text
values_and_literals_feature.md
```

## L2: Bindings And Scope

First-principles act:

```text
Name
```

Core primitives:

```text
Binding
Context
Scope
Name
```

Concrete ideas:

- simple binding: `name = value`,
- lexical scope and shadowing,
- module scope,
- block-local names versus caller-visible names,
- destructuring as binding to a shape,
- imports as bindings,
- explicit constant/non-rebindable bindings,
- possible `let` or `scope` form for local contexts.

Variations to research:

- Python assignment semantics versus more explicit rebinding rules,
- block-created names escape versus stay local,
- `const name = value` versus `name const = value` versus binding policy,
- imports as ordinary bindings versus special module operation,
- dynamic binding as an advanced explicit feature.

Reduction:

```text
name = value -> bind name to Value in Context
parameter -> bind argument Value in call Context
import -> bind module/member Value in Context
destructuring -> pattern-shaped binding
```

Small prototype:

- write an explicit `BindingTarget` model for names and destructuring,
- make assignment and function parameters use the same binding path,
- add tests for shadowing, deletion, globals, nonlocals, and block scope.

Focused spec to write:

```text
bindings_and_scope_feature.md
```

## L3: Constraints, Judgement, And Diagnostics

First-principles act:

```text
Judge
Explain
```

Core primitives:

```text
Constraint
Judgement
Diagnostic
Trace
```

Concrete ideas:

- type/class constraints,
- predicate constraints,
- expression constraints in tentative binding context,
- human messages with `else`,
- structured `BindingError`,
- constraints on assignment, parameters, block parameters, patterns, and shape
  fields,
- examples/tests as later judgement forms.

Variations to research:

- constraints as runtime checks versus optional static analysis,
- accumulating constraints versus re-annotation replaces constraints,
- `x:int, x > 0` versus `x: int where x > 0`,
- failure raises immediately versus returns structured `Result`,
- message syntax: `else "..."` versus `because "..."`.

Reduction:

```text
constraint syntax -> Constraint value
constrained binding -> tentative Binding + Constraint checks + Diagnostic
```

Small prototype:

- replace bare predicates with `Constraint` objects,
- add `BindingError` with source span and failed constraint,
- route assignment and parameters through the same judgement path.

Focused spec already started:

```text
binding_constraints_feature.md
```

Next focused spec:

```text
constraints_and_diagnostics_feature.md
```

## L4: Functions, Calls, And Transformation

First-principles act:

```text
Transform
```

Core primitives:

```text
Function
Call
ArgumentMap
Return
```

Concrete ideas:

- named functions with `func`,
- arrow functions,
- expression-bodied and block-bodied functions,
- parameter binding through the shared binding engine,
- return constraints,
- final-expression return for expression-oriented blocks,
- pipelines and composition as call structure,
- partial application and placeholder `_` as later features.

Variations to research:

- `func f(...):` versus `f = func(...):`,
- arrow syntax `(x) => expr` versus `fn(x) -> expr`,
- final expression return everywhere versus only in selected forms,
- pipeline placeholder `_` required versus optional single-argument shorthand,
- composition operator `>>` versus named `compose`.

Reduction:

```text
func definition -> bind name to Function
arrow expression -> Function value
call -> evaluate callee + map arguments to parameter bindings + execute body
pipeline -> nested or sequenced calls
composition -> Function value that performs calls in order
```

Small prototype:

- make argument mapping produce binding operations,
- add a focused pipeline parser experiment,
- trace call and return values for diagnostics.

Focused specs to write:

```text
functions_and_calls_feature.md
pipelines_and_composition_feature.md
```

## L5: Data And Shape

First-principles act:

```text
Group
Judge
```

Core primitives:

```text
Data
Shape
Field
Constructor
```

Concrete ideas:

- `data` for owned program values,
- product data: `data User(id:UserId, email:str)`,
- sum data: variants such as `Ok(value)` and `Err(error)`,
- `shape` for external structural data,
- optional fields and defaulted fields,
- constructor constraints,
- shape-to-data transformation.

Variations to research:

- `data User(...)` single-line form versus block form,
- product-only first versus sum types from the beginning,
- structural shape versus nominal shape,
- optional marker `?` versus `Option[T]`,
- default values in shape declarations versus separate normalization step.

Reduction:

```text
data declaration -> constructors + field bindings + pattern shape
shape declaration -> named Constraint over external structure
field -> binding plus optional constraint/default
```

Small prototype:

- implement a minimal `data` declaration as constructor plus fields,
- implement `shape` over dictionaries,
- allow shape binding with structured diagnostics.

Focused specs to write:

```text
data_declarations_feature.md
shape_binding_feature.md
```

## L6: Patterns And Choice

First-principles act:

```text
Choose
Name
```

Core primitives:

```text
Pattern
Match
Guard
BindingTarget
```

Concrete ideas:

- destructuring assignment,
- `match` statements and expressions,
- pattern guards,
- constraint patterns,
- data variant patterns,
- shape patterns,
- or-patterns and wildcard patterns,
- exhaustiveness diagnostics later.

Variations to research:

- Python-like `match/case` versus expression-first `match value: ...`,
- constraint in pattern `age:(int, age >= 13)` versus guard `if age >= 13`,
- match failure as error versus non-match depending on context,
- structural matching before nominal matching versus nominal-first.

Reduction:

```text
pattern -> structural test + tentative bindings
case -> pattern + optional guard + body
destructuring assignment -> pattern binding that raises on failure
match expression -> ordered cases that produce a value
```

Small prototype:

- reuse `BindingTarget` for destructuring and match captures,
- define direct pattern-binding failure,
- add trace explaining why cases failed.

Focused spec to write:

```text
patterns_and_match_feature.md
```

## L7: Collections, Tables, And Repetition

First-principles act:

```text
Repeat And Accumulate
Transform
```

Core primitives:

```text
Collection
Iterator
Transform
Fold
Table
```

Concrete ideas:

- readable whole-collection transforms,
- `map`, `where`, `select`, `group`, `join`, `sort`, `fold`,
- comprehensions as syntax over transforms,
- table rows as shape-bound records,
- array rank and shape concepts inspired by APL,
- streaming transforms and lazy collections.

Variations to research:

- method style `users.where(...)` versus pipeline `users |> where(...)`,
- block transforms `where(users) -> user: ...` versus arrow predicates,
- SQL-like query block versus function pipeline,
- APL-like rank operators versus named rank-aware functions,
- eager versus lazy default.

Reduction:

```text
map/filter/query -> repeated calls with binding of each element
table row -> shape-bound value
group/fold -> accumulation over collection values
rank operation -> transform parameterized by shape metadata
```

Small prototype:

- implement a tiny transform library using existing functions,
- add pipeline syntax only after call semantics are stable,
- add trace of collection stages.

Focused specs to write:

```text
collection_transforms_feature.md
tables_and_queries_feature.md
rank_and_shape_feature.md
```

## L8: Blocks, Yield, And Time-Shaped Control

First-principles act:

```text
Sequence In Time
Touch The World
Explain
```

Core primitives:

```text
Block
Yield
Policy
ContinuationPoint
```

Concrete ideas:

- block calls,
- yielded block parameters,
- retry, timeout, using, transaction, trace, test,
- block result semantics,
- exception propagation through yield,
- block-local versus caller-visible scope,
- structured concurrency later.

Variations to research:

- block call syntax `call(args):` versus `with call(args):`,
- yielded parameter arrow `-> x` versus block parameter inside body,
- block result owned by callee versus last expression of block,
- full continuations versus practical resumable yield,
- async blocks integrated now versus later.

Reduction:

```text
block call -> call + attached Block value
yield -> invoke attached Block at continuation point
policy -> function that controls when/how block is invoked
```

Small prototype:

- use `block_calls_feature.md`,
- replace ad hoc block keyword with explicit block representation,
- route block parameters through binding engine,
- add yield diagnostics.

Focused spec already started:

```text
block_calls_feature.md
```

Next focused specs:

```text
block_scope_and_control_flow_feature.md
structured_concurrency_feature.md
```

## L9: Effects, Worlds, And Capabilities

First-principles act:

```text
Touch The World
Judge
Explain
```

Core primitives:

```text
Effect
World
Capability
Policy
Audit
```

Concrete ideas:

- capability values for filesystem, network, time, randomness, subprocess,
  environment, database,
- `world(...)` scopes,
- transactions as effect policies,
- simulation and replay worlds,
- effect traces,
- explicit permission boundaries.

Variations to research:

- Haskell-like effect types versus runtime capability scopes,
- ambient standard library access versus explicit imported capabilities,
- `with world(...) as w:` versus `world(...) -> w:`,
- effect tracking as diagnostics only versus enforced restrictions,
- single world object versus separate capability objects.

Reduction:

```text
capability -> Value granting operations
world scope -> block policy that binds capabilities
effectful operation -> call through capability value + trace event
transaction -> block policy over effect log/commit/rollback
```

Small prototype:

- introduce a simple `World` object for file/time/network stubs,
- run examples against fake worlds,
- record effect trace events.

Focused spec to write:

```text
effects_worlds_capabilities_feature.md
```

## L10: Examples, Traces, And Explanation

First-principles act:

```text
Explain
Judge
```

Core primitives:

```text
Example
Trace
Diagnostic
Expectation
```

Concrete ideas:

- `examples:` blocks inside functions and declarations,
- examples as tests and documentation,
- `explain(value_or_expr)`,
- trace for binding, calls, patterns, blocks, effects, pipelines, rewrites,
- counterexamples from failed constraints or properties,
- diagnostics written in feature vocabulary.

Variations to research:

- examples embedded in functions versus separate declarations,
- examples as compile-time tests versus runtime metadata,
- trace always available versus opt-in tracing,
- proof/property syntax now versus examples first,
- human messages attached to constraints versus generated explanation.

Reduction:

```text
example -> executable judgement over calls/values
trace -> structured record of core semantic events
diagnostic -> rendered explanation from trace + span + judgement
```

Small prototype:

- add trace records for binding constraint failures,
- add examples as ordinary test data attached to a function object,
- render one high-quality diagnostic.

Focused spec to write:

```text
examples_traces_explanation_feature.md
```

## L11: Quote, Rewrite, And Notation

First-principles act:

```text
Reflect And Rewrite
Transform
```

Core primitives:

```text
Quote
SyntaxValue
RewriteRule
Expansion
UseScope
```

Concrete ideas:

- `quote:` block for code-shaped values,
- rewrite rules over quoted expressions,
- explicit evaluation boundary,
- scoped macros or transforms,
- `use` scopes for domain notation,
- inspectable expansion.

Variations to research:

- `quote:` blocks versus prefix quote syntax,
- Mathematica-like `/.` versus named `rewrite(expr, rule)`,
- rewrite rules as values versus declaration forms,
- macros as compile-time functions versus runtime syntax transforms,
- notation definitions allowed globally versus only inside `use` scopes.

Reduction:

```text
quote -> SyntaxValue
rewrite rule -> Pattern over SyntaxValue + replacement SyntaxValue
macro/notation -> scoped rewrite over syntax before evaluation
expansion -> traceable transformation from syntax to lower syntax
```

Small prototype:

- define a tiny Nomi expression AST,
- quote a subset of expressions into syntax values,
- apply one rewrite rule with trace output.

Focused specs to write:

```text
quote_and_syntax_values_feature.md
rewrite_rules_feature.md
scoped_notation_feature.md
```


## First Implementation Spine

The first operational implementation path should be:

```text
Nomi IR with spans
  -> Value and Context model
  -> BindingTarget and lexical scope
  -> Constraint and BindingError
  -> Function call argument binding
  -> Data/Shape declarations
  -> Pattern binding and match
  -> Pipeline lowering to calls
  -> Explicit Block representation and yield
  -> Trace records and diagnostics
```

This path deliberately postpones advanced symbolic rewrite and capabilities
until the lower semantic events are traceable.

## Research Guardrails

- Do not add syntax before naming the primitive cognitive act.
- Do not add a feature that bypasses the lower layers it should reduce to.
- Do not copy a language's surface spelling until the semantic role is clear.
- Do not treat diagnostics as a later UI concern.
- Do not let current implementation convenience decide the long-term model.
- Do not flatten the roadmap into independent features; preserve dependency.
