# Symbolic, Lazy, And Structural Computation

> Status: active integration plan plus source note for future design review.
>
> Purpose: explore a Nomi layer where computations can be described,
> inspected, transformed, optimized, and executed by pluggable backends instead
> of being treated only as opaque runtime function calls. This doc also charts
> how symbolic manipulation and laziness can fit Nomi without making ordinary
> code surprising.

## Core Idea

In ordinary Python-like programming, a function is mostly a black box:

```python
func average(xs):
    return sum(xs) / len(xs)
```

The caller can execute `average([1, 2, 3])`, but the language does not normally
let the caller ask:

```text
What computation does average describe?
Does it contain sum?
Does it contain len?
Can this be lowered to SQL?
Can this be run by a dataframe engine?
Can this be optimized into a single backend operation?
Can this be explained without executing on real input?
```

The deeper idea is to separate:

```text
description of computation
from
execution of computation
```

Once separated, the same computation description can be inspected, rewritten,
validated, optimized, visualized, compiled, interpreted, or sent to a backend.

## Why This Matters

This opens a powerful middle space between normal programming and symbolic
systems:

- A function is no longer only executable behavior; it can also expose
  structure.
- Computation can be described using placeholder inputs rather than concrete
  values.
- Backends can choose how to execute the same description: interpreter, SQL,
  dataframe engine, vector engine, GPU, distributed task graph, symbolic
  simplifier, test checker, or diagnostic explainer.
- Optimization becomes a transformation of a computation value rather than an
  invisible runtime accident.
- Examples, traces, constraints, and diagnostics can inspect intent before
  executing large or expensive work.

This mixes several traditions:

- symbolic programming: code and expressions as inspectable values;
- lazy programming: build a suspended computation and run it later;
- dataflow graphs: represent dependencies explicitly;
- query planning: build a logical plan before choosing a physical plan;
- combinators: build computation from small composable operators;
- point-free style: describe composition without naming every intermediate;
- compiler IR: lower high-level structure into backend-specific form.

## Integration Thesis

Symbolic and lazy evaluation are powerful because they let a program talk about
computation before, instead of only after, execution. They become confusing when
that power is ambient.

Nomi's path should be:

```text
ordinary code is eager
structural computation is explicit
lazy execution is explicit
rewrites are scoped and explainable
plans can be inspected before materialization
```

Do not make Nomi a Mathematica clone, an R clone, or a Haskell clone. Preserve
the user need from each tradition:

| Tradition | What to keep | What to refuse |
| --- | --- | --- |
| Wolfram/Mathematica | Symbolic expressions, rules, repeated rewrites, algebraic manipulation. | Global rule magic where ordinary values can silently transform by distant definitions. |
| R | Deferred arguments and quoted expressions carrying environments. | Non-standard evaluation that forces function authors to learn a second scoping model. |
| Haskell | Composable pure functions, infinite/streaming structures, demand-driven modularity. | Lazy-by-default execution order, space-leak debugging as an everyday skill. |
| Polars/query engines | Lazy logical plans, optimizer freedom, `collect()`, `explain()`. | Planner opacity or a separate query language that drifts from ordinary functions. |

The Nomi synthesis is a small family of explicit boundary values, not one
global evaluation mode:

| Boundary | User intent | Evaluates now? | Captures structure? | Primary normal forms |
| --- | --- | --- | --- | --- |
| ordinary expression | Compute a value now. | yes | no, except trace events | Binding, function, pattern, flow |
| `quote:` | Capture syntax as data. | no | syntax tree with spans | Explanation, future reflection |
| `describe` | Capture a computation description. | no for described body | Core/computation IR | Function, flow, explanation |
| `lazy` | Delay a value computation. | when forced | maybe, as a thunk record | Binding, flow, explanation |
| table/query plan | Build logical dataflow. | on `collect`, write, or iteration | logical plan/schema | Flow, data boundary, explanation |
| rewrite rule | Transform a quoted/computation value. | transforms structure, not runtime values | match + replacement trace | Pattern, function, explanation |

## Source Scan For This Integration

- Wolfram Language exposes symbolic transformation rules over expressions and
  supports single and repeated replacement. Source:
  <https://reference.wolfram.com/language/tutorial/TransformationRulesAndDefinitions.html>.
- R's `delayedAssign` documents promise creation, first-access forcing,
  evaluation environment, and fixed value after forcing. Source:
  <https://search.r-project.org/R/refmans/base/html/delayedAssign.html>.
- The Haskell 2010 report describes Haskell as a purely functional language
  with non-strict semantics. Source:
  <https://www.haskell.org/definition/haskell2010.pdf>.
- Polars' lazy API builds queries before execution, lets the optimizer perform
  predicate/projection pushdown, executes with `collect`, and exposes
  `explain` for the planned query. Source:
  <https://docs.pola.rs/user-guide/concepts/lazy-api/>.

These systems point at the same abstraction from different directions:

```text
capture structure -> transform or optimize it -> explain it -> execute it
```

They disagree on how ambient the abstraction should be. Nomi should keep the
abstraction and make the boundary visible.

## Prior Art And Reference Systems

### Wolfram Language: Everything As Symbolic Expression

Wolfram Language treats numbers, formulas, arrays, graphs, images, interfaces,
and code as symbolic expressions with a common structural representation.
Evaluation proceeds by applying definitions and transformations to expressions.

Nomi lesson:

- A uniform expression structure makes inspection and rewrite powerful.
- Symbolic power should be explicit enough that ordinary code does not become
  magical.
- The underlying structure should be visible through tools such as `show`,
  `trace`, or `explain`.

Sources:

- [Wolfram symbolic expressions](https://www.wolfram.com/language/fast-introduction-for-programmers/en/symbolic-expressions/)
- [Wolfram evaluation of expressions](https://reference.wolfram.com/language/tutorial/EvaluationOfExpressions.html)

### Dask: Lazy Task Graphs From Python-Like Calls

Dask `delayed` lets users wrap Python functions so calls build a task graph
instead of executing immediately. Later, `.compute()` executes the graph using a
scheduler.

Nomi lesson:

- Ordinary function-call shape can build deferred computation.
- The graph can be visualized before execution.
- There must be boundaries: some operations, especially mutation and control
  flow over delayed values, are difficult or unsupported.

Sources:

- [Dask Delayed](https://docs.dask.org/en/stable/delayed.html)
- [Dask Task Graphs](https://docs.dask.org/en/stable/graphs.html)

### TensorFlow And JAX: Trace Python Into Smaller Computation Forms

TensorFlow can switch from eager execution to graph execution using
`tf.function`. JAX traces Python functions into `jaxpr`, an explicitly typed,
functional intermediate representation that can then be interpreted by
transformations such as JIT compilation or differentiation.

Nomi lesson:

- A familiar surface language can be traced into a smaller, more analyzable
  computation language.
- Not all host-language behavior can be captured; dynamic Python control and
  side effects need restrictions or special forms.
- The inspectable form is valuable even when the user writes normal-looking
  functions.

Sources:

- [TensorFlow graphs and tf.function](https://www.tensorflow.org/guide/intro_to_graphs)
- [JAX jaxpr language](https://docs.jax.dev/en/latest/jaxpr.html)
- [JAX tracing](https://docs.jax.dev/en/latest/tracing.html)
- [jax.make_jaxpr](https://docs.jax.dev/en/latest/_autosummary/jax.make_jaxpr.html)

### SQLAlchemy And Spark: Expressions Before Execution Plans

SQLAlchemy Core builds SQL expressions as Python objects. Spark SQL can explain
parsed logical plans, analyzed plans, optimized plans, and physical plans.

Nomi lesson:

- A backend-neutral expression can still expose backend-specific capabilities.
- A logical plan and physical plan should be separate.
- `explain` is part of the programming model, not a debugging afterthought.

Sources:

- [SQLAlchemy SQL Expression Language](https://docs.sqlalchemy.org/20/core/expression_api.html)
- [Spark SQL EXPLAIN](https://downloads.apache.org/spark/docs/3.5.3/sql-ref-syntax-qry-explain.html)

### Halide And MLIR: Separate Algorithm From Schedule And Lowering

Halide is especially relevant because it separates what is computed from how it
is scheduled. MLIR is relevant because it represents computations at multiple
levels of abstraction so they can be analyzed, transformed, and lowered toward
different targets.

Nomi lesson:

- "What to compute" and "how to execute it" are distinct design objects.
- Different backends may need different schedules without changing the
  algorithm.
- A human-readable intermediate form helps debugging and transformation.

Sources:

- [Halide introduction](https://halide-lang.org/)
- [Halide schedule documentation](https://halide-lang.org/docs/_schedule_8h.html)
- [MLIR language reference](https://mlir.llvm.org/docs/LangRef/)
- [MLIR overview](https://mlir.llvm.org/)

## A Nomi Mental Model

Nomi can treat this as a layered model:

```text
Source code
  -> ordinary runtime value
  -> computation description
  -> logical plan
  -> optimized plan
  -> backend plan
  -> execution result
  -> trace and diagnostic
```

The key new user-facing concept is:

```text
Computation
```

A `Computation` is not the result of running code. It is an inspectable value
that describes how to compute a result.

Possible fields:

```text
inputs       symbolic inputs or placeholders
nodes        operations, calls, constants, and bindings
edges        data dependencies
constraints  type, shape, value, purity, and backend requirements
effects      declared effects, if any
source       source spans for diagnostics
result       result type, shape, schema, or unknown
```

## Example: Average Without Concrete Input

Ordinary function:

```python
func average(xs):
    return sum(xs) / len(xs)
```

Symbolic input:

```python
xs = input "xs": List[Number]
plan = describe average(xs)
```

Inspectable structure:

```text
Computation average:
  input xs: List[Number]
  s = sum(xs)
  n = len(xs)
  result = s / n
```

Queries over the computation:

```python
plan.contains_call(sum)       # true
plan.contains_call(len)       # true
plan.inputs                   # [xs]
plan.result                   # Number
plan.explain()
```

Possible rewrites:

```python
plan.rewrite(mean_rule)
plan.lower(sql_backend)
plan.lower(dataframe_backend)
plan.lower(distributed_backend)
```

The important shift:

```text
average(xs) can mean "run now"
describe average(xs) can mean "build the computation structure"
```

## Possible Nomi Syntax

### 1. Explicit `describe`

The safest syntax is explicit:

```python
plan = describe average(xs)
```

This says: do not run this call as ordinary execution. Build a computation
description.

Advantages:

- Easy to teach.
- Clear boundary between value execution and symbolic construction.
- Good fit for diagnostics.

Risk:

- Some host-language behavior may still execute during description unless
  carefully controlled.

### 2. Symbolic Inputs

Symbolic inputs let users describe computation without real data:

```python
xs = symbolic "xs": List[Number]
rows = symbolic "orders": Table[Order]
```

Then:

```python
plan = describe average(xs)
```

A symbolic input is a placeholder with constraints. It is not a fake runtime
value; it is a named input to a computation description.

### 3. Function Transparency Markers

Some functions may be safe to inspect, inline, or lower:

```python
transparent func average(xs:List[Number]):
    return sum(xs) / len(xs)
```

or:

```python
func average(xs:List[Number]) transparent:
    return sum(xs) / len(xs)
```

Meaning:

```text
The body may be represented as computation structure when called in describe
mode.
```

This is not the same as pure, but the concepts are related. A transparent
function should probably be pure or effect-declared.

### 4. Backend Blocks

Execution can be selected by a backend:

```python
using dataframe_backend:
    result = execute plan
```

or:

```python
result = plan.run(with=dataframe_backend)
```

Backends can reject unsupported plans:

```text
BackendError: sql_backend cannot lower len(xs) for unknown collection xs
  operation: len(xs)
  source: stats.nomi:3
  suggestion: use count(xs) or provide a table schema
```

### 5. Explainable Plans

Plans should be explainable:

```python
explain plan
```

Possible output:

```text
Logical plan:
  xs: List[Number]
  s = sum(xs)
  n = len(xs)
  result = divide(s, n)

Backend candidates:
  interpreter: supported
  dataframe: supported as mean(xs)
  sql: requires table column, not bare list
  gpu: requires numeric array shape
```

## The Function Is No Longer A Total Black Box

This does not mean every function body should always be inspectable. Instead,
Nomi can distinguish kinds of functions:

```text
opaque function       callable, but body not available for symbolic lowering
transparent function  callable and inspectable in describe mode
primitive function    backend-known operation such as sum, len, map, filter
external function     calls host/library code, maybe with declared behavior
macro/rewrite rule    transforms computation descriptions
```

For `average`, the backend can only see `sum` and `len` if:

- `average` is transparent;
- `sum` and `len` have symbolic meanings;
- `xs` is a symbolic input or computation value;
- the description mode records the function body rather than executing it
  opaquely.

## Point-Free And Combinator Style

Once computation is structural, users can describe transformations without
always naming intermediate values.

Pointful style:

```python
func normalize(xs):
    m = average(xs)
    return xs |> map(x => x - m)
```

Combinator style:

```python
normalize = center_by(average)
```

Pipeline style:

```python
normalize = _ |> center_by(average)
```

Composition style:

```python
clean_average = clean >> average
```

Nomi should be careful here. Point-free style can be elegant when the
composition is simple, but it can become unreadable when the data path is not
obvious. The design rule should be:

```text
Combinators are welcome when explain can render the named dataflow clearly.
```

## Lazy Evaluation As A Boundary, Not A Default Fog

Lazy computation is useful because it lets the program build a plan before
choosing how to execute it.

Possible forms:

```python
lazy total = expensive_sum(xs)
```

```python
plan = lazy:
    clean(raw)
    |> filter(valid)
    |> average
```

But laziness should be visible. If ordinary code silently becomes lazy, users
lose a basic expectation: "this line ran before the next line."

Nomi rule:

```text
Default ordinary execution stays eager.
Description, lazy, and backend-planned execution require explicit boundaries.
```

### The Three Kinds Of Delayed Work

Nomi should keep these distinct even though source languages often blur them:

| Kind | Example spelling | Meaning | Force/materialize operation |
| --- | --- | --- | --- |
| Promise/thunk | `lazy total = expensive_sum(xs)` | A delayed value computation. | `force(total)` or first explicit demand. |
| Computation description | `plan = describe average(xs)` | A structured representation of a call/body. | `plan.run(...)`, backend lowering, or interpreter execution. |
| Query/data plan | `orders |> where(.paid) |> summarize(...)` from a lazy source | A logical dataflow with schema and backend choices. | `collect()`, write, iteration, or explicit `run`. |

The difference matters:

- A lazy value may close over ordinary runtime values.
- A computation description should reject or mark effects.
- A query plan should expose schema, column scope, optimizer rewrites, and
  backend capability diagnostics.

Do not teach all of these as "lazy." Teach them as:

```text
delay a value
describe a computation
plan a dataflow
```

### Force And Capture Policy

R shows the sharp edge: a delayed expression can run later in an environment
whose bindings have changed. Nomi should not make late binding the silent
default.

First-pass rule:

```text
`lazy` captures the lexical binding identities at the boundary and records the
capture policy in `explain`.
```

For immutable values this behaves like a value snapshot from the user's point
of view. For mutable or external values, the lazy record should name the
captured reference and its effect risk:

```text
lazy total = expensive_sum(buffer)

explain total
  lazy value: not forced
  captures:
    buffer: mutable reference captured at stats.nomi:12
  effects:
    reads memory
  force policy:
    memoized once
```

If a user wants late lookup, make it explicit later, for example with a
reference/capability form, not by accident.

### Effects And Laziness

Lazy-by-default languages work best when effects are sequenced by the type or
runtime model. Nomi should instead keep ordinary effects eager and make
effectful delayed work visible:

```python
lazy pure total = sum(xs)
lazy io text = read(path)      # visibly delayed IO
```

Possible effect grades:

| Grade | Meaning | First status |
| --- | --- | --- |
| `pure` | No IO, mutation, time, randomness, or host calls. | allowed first |
| `read` | Reads stable data or captured immutable inputs. | allowed with explanation |
| `io` | Files, network, console, clock, random, subprocess. | design-needed |
| `mutate` | Mutates captured or external state. | reject in first slice |

The first lazy feature should probably support only `pure` and a narrow
read-only grade. That keeps debugging humane.

### Debugging Contract

Every delayed value or plan needs the same basic inspection contract:

```text
explain x:
  status: pending | forced | failed | cached
  source: file:line:col
  captured names
  effect grade
  force count
  cached value or redacted summary
  failure, if forcing failed
```

For query/data plans, explanation should also include schema, row/group scope,
rewrites, predicate/projection pushdown, and unsupported backend operations.

For symbolic rewrites, explanation should include matched pattern, rule name,
constraints required, before/after expression, and rewrite budget consumed.

## Backend Interface Sketch

A backend receives a computation description and returns either:

- an execution result;
- a lowered plan;
- an unsupported-operation diagnostic;
- a transformed plan plus trace.

Sketch:

```python
backend DataFrame:
    supports sum(xs) when xs is Column[Number]
    supports len(xs) when xs is Column
    rewrite sum(xs) / len(xs) => mean(xs)
    execute plan:
        ...
```

Or more structurally:

```text
Backend:
  can_lower(node, context) -> yes/no/diagnostic
  lower(node, context) -> backend_node
  optimize(plan) -> plan
  execute(plan, inputs) -> result
  explain(plan) -> diagnostic tree
```

## Rewrites And Rules

Symbolic computation enables rules:

```python
rule mean_rule:
    sum(xs) / len(xs) => mean(xs)
```

```python
rule map_filter_fusion:
    map(f, filter(p, xs)) => filter_map(p, f, xs)
```

Rules need strict boundaries:

- Rules apply to computation descriptions, not arbitrary runtime objects.
- Rules must preserve meaning under stated constraints.
- Rule application should be traceable.
- Ambiguous or looping rewrites need safeguards.

Possible trace:

```text
Rewrite trace:
  matched sum(xs) / len(xs)
  applied mean_rule
  result mean(xs)
  required xs: finite collection
```

### Scoped Rewrite Sets

Mathematica's rule language is compelling because the rewrite operation is
small and general. The danger for a general-purpose language is that rules can
become ambient semantic weather.

Nomi rule:

```text
Rewrite rules apply only to quoted/computation values and only through an
explicit rule set.
```

Example:

```python
rules algebra:
    x + 0 => x
    x * 1 => x
    x * (y + z) => x*y + x*z

expr = quote:
    a * (b + 0)

simple = expr.rewrite(with=algebra, limit=10)
explain simple
```

Rejected for the first layer:

- global rewrite tables that affect ordinary evaluation;
- rules that silently run during every function call;
- repeated replacement without a visible termination/budget policy;
- rewrites over effectful expressions unless the effects are represented as
  explicit nodes and the rule proves it preserves order.

### Symbolic Values Versus Syntax Values

`quote:` and `symbolic` should not mean the same thing:

```python
expr = quote:
    x + 1

x = symbolic "x": Number
term = x + 1
```

`quote:` captures source syntax. It is useful for macros, examples, structural
inspection, source-aware transformations, and teaching.

`symbolic` creates a placeholder value in a computation domain. It is useful
for algebra, query expressions, solver inputs, and backend plans.

The two can interoperate, but the user should know which side they are on:

```text
syntax value -> parse/source tree with spans
symbolic term -> computation node with constraints and domain meaning
```

This distinction keeps expression-oriented programming readable: most
expressions still compute values; only explicit boundaries produce syntax or
symbolic terms.

## Fit With Expression-Oriented And Functional Programming

Symbolic and lazy features fit best when they are values, not hidden control
effects.

Expression-oriented style:

```python
report =
    orders
    |> where(.status == "paid")
    |> group_by(.customer)
    |> summarize(total=sum(.amount))
```

If `orders` is eager, this computes through the pipeline. If `orders` is a lazy
source, the same expression builds a plan. The boundary belongs to the source
and the final materialization point:

```python
plan = scan_csv("orders.csv") |> where(.status == "paid")
rows = plan.collect()
```

Functional style:

```python
transparent func average(xs):
    return sum(xs) / len(xs)

xs = symbolic "xs": Column[Number]
plan = describe average(xs)
```

This works because function bodies are expressions over inputs. The boundary
`describe` changes "call this now" into "represent this call/body." A
transparent function is still an ordinary function when called normally.

The integration rule:

```text
function application remains function application;
only the surrounding boundary chooses value execution vs structural capture.
```

That keeps higher-order functions, pipelines, equations, `where`, and
pattern-matching aligned with the rest of Nomi.

### Where It Gets Subtle

| Interaction | Failure mode | Nomi resolution |
| --- | --- | --- |
| Lazy + side effects | Print/file/time happens later or never. | Effectful laziness is explicit and inspectable; default ordinary effects stay eager. |
| Lazy + exceptions | Error appears far from source. | Lazy records store source spans and report both construction and force sites. |
| Lazy + mutation | Captured state changes before force. | Capture policy is shown; mutation-heavy laziness is rejected first. |
| Symbolic + ordinary `if` | Branch condition is unknown. | `describe` lowers to a symbolic conditional or rejects with a diagnostic. |
| Symbolic + function calls | User expects backend to inspect opaque code. | Only transparent or primitive functions expose bodies/meanings. |
| Rewrite + nontermination | Rules bounce forever. | Rewrites require budget, strategy, and trace. |
| Query plan + row scope | Column names hide local variables. | Row/column scope exists only inside table-verb argument boundaries. |
| Backend lowering + semantics drift | SQL/Polars/Python disagree on nulls, order, strings, floats. | Backend diagnostics name unsupported or changed semantics before execution. |

### User-Facing Vocabulary

The words should teach the mental model:

| Word | Teaching line |
| --- | --- |
| `quote` | "Treat this source as syntax data." |
| `symbolic` | "Create a named placeholder term." |
| `describe` | "Build a computation description instead of running this call." |
| `lazy` | "Delay this value computation until forced." |
| `force` | "Run a lazy value now and cache or report the result." |
| `collect` | "Materialize a data/query plan." |
| `explain` | "Show what will happen or what transformation happened." |
| `transparent` | "This function body may be inspected in description mode." |

## What Must Be Representable

For this layer to work, Nomi needs structured representations for:

- constants;
- symbolic inputs;
- variable bindings;
- function calls;
- primitive operations;
- blocks and yielded blocks, if supported;
- patterns and constraints;
- collection transforms;
- effects or purity claims;
- source spans;
- backend requirements;
- diagnostics and traces.

Not every Python-like construct should enter this layer immediately. Start with
simple expressions and collection transforms.

## Good First Slice

A minimal prototype could support:

```text
symbolic inputs
transparent expression-only functions
primitive calls: sum, len, count, mean, map, filter
pipelines
plan.inspect
plan.explain
one rewrite: sum(xs) / len(xs) -> mean(xs)
two backends: interpreter and SQL-like/string-rendering backend
```

Example:

```python
transparent func average(xs):
    return sum(xs) / len(xs)

xs = symbolic "xs": Column[Number]
plan = describe average(xs)

explain plan
explain plan.rewrite(mean_rule)
sql = plan.lower(sql_backend)
```

Expected explanation:

```text
average(xs)
  expands to sum(xs) / len(xs)
  rewrites to mean(xs)
  lowers to AVG(xs)
```

This is small but profound: it proves that Nomi can inspect computation rather
than only execute it.

## Hard Problems

### Side Effects

If a function prints, mutates state, reads time, reads files, or performs
network calls, description mode must not pretend it is a pure expression.

Possible rule:

```text
Only pure or effect-declared functions can be transparent.
```

### Dynamic Control Flow

Control flow based on symbolic values is not ordinary control flow:

```python
if x > 0:
    ...
```

If `x` is symbolic, the host interpreter cannot know which branch to take.
Nomi needs either:

- symbolic `if` nodes;
- restrictions;
- branch tracing with concrete examples;
- explicit backend control forms.

### Mutation And Identity

Symbolic descriptions prefer values and dependencies. Mutation introduces time,
identity, aliasing, and order.

First slice rule:

```text
No mutation inside transparent computation descriptions.
```

### Exceptions

Should `1 / x` describe a possible divide-by-zero diagnostic, a runtime
exception, a backend error, or a constraint requirement?

Nomi should connect this to constraints:

```python
func inverse(x:(Number, x != 0)) transparent:
    return 1 / x
```

### Python Interop

Calling arbitrary Python from a computation plan should be treated as an opaque
external operation unless an adapter gives it symbolic meaning.

### Backend Drift

Different backends may not agree exactly on missing values, floating point,
integer division, string collation, time zones, nulls, or ordering.

Plans need backend capability diagnostics, not silent semantic drift.

## Relation To Existing Nomi Concepts

This layer should not replace the current foundation. It should extend it.

```text
Value        -> includes Computation values
Binding      -> can bind symbolic inputs and plans
Constraint   -> describes allowed values and backend requirements
Function     -> may be opaque, transparent, primitive, or external
Call         -> may execute or build a computation node depending on boundary
Collection   -> can be eager, lazy, stream, table, or symbolic collection
Block        -> later, can describe control or policy as structure
Example      -> can check a computation description against sample inputs
Trace        -> records expansion, rewrite, lowering, and execution
Diagnostic   -> explains unsupported operations and semantic mismatches
Module       -> exports functions plus symbolic/backend metadata
```

Possible new concepts:

```text
Computation
SymbolicInput
Primitive
RewriteRule
Backend
Lowering
Plan
Schedule
```

## Design Principles

1. Ordinary code remains ordinary unless the user enters `describe`, `lazy`, or
   another explicit structural boundary.
2. Computation descriptions are values that can be inspected and transformed.
3. A function is transparent only when the language can safely expose its body
   as structure.
4. Backends should reject unsupported plans with source-aware diagnostics.
5. Rewrites should be traceable and constrained.
6. Point-free and combinator styles are acceptable only when `explain` can
   recover the dataflow.
7. Description and execution should be separate, but connected by a clear
   lowering story.
8. The first version should support a small expression/dataflow subset, not the
   whole language.
9. `quote`, `symbolic`, `describe`, `lazy`, and query plans remain distinct
   because they answer different user questions.
10. Any delayed or symbolic feature must have an `explain` story before it has
    a clever syntax story.

## Candidate Syntax Summary

```python
transparent func average(xs):
    return sum(xs) / len(xs)

xs = symbolic "xs": Column[Number]

plan = describe average(xs)
explain plan

optimized = plan.rewrite(mean_rule)
result = optimized.run(with=dataframe_backend, input=data)
```

Alternative:

```python
plan = quote:
    average(xs)
```

or:

```python
lazy report =
    orders
    |> where(.status == "paid")
    |> group_by(.customer_id)
    |> summarize(total=sum(.amount))
```

The exact spelling is less important than the semantic boundary:

```text
run this now
vs
describe this computation
vs
optimize/lower/execute this plan
```

## Open Questions

- Should Nomi use `describe`, `quote`, `lazy`, or separate constructs for
  expression structure, delayed execution, and syntax values?
- How much of a function body can be transparent in the first version?
- Are constraints enough to express backend preconditions?
- Should backend selection be lexical (`using backend:`) or attached to plan
  execution (`plan.run(with=backend)`)?
- What is the smallest useful `Computation` IR?
- How does this interact with block calls?
- Should symbolic inputs require explicit types, schemas, shapes, or examples?
- Can examples automatically test that two plans are equivalent on sample data?
- Should `lazy` be memoized by default, like call-by-need, or should one-shot
  delayed actions be a separate type?
- Should capture policy be value snapshot, binding-cell capture, or explicit
  reference capture? Which policy can users predict in the presence of mutable
  values?
- Should effect grades be syntax (`lazy pure`) or metadata inferred from
  transparent function bodies?

## Recommended Next Step

Do not start with a general symbolic system or a global lazy mode. Start with
one concrete path:

```text
transparent expression function
symbolic collection input
describe call
inspect calls
rewrite average to mean
lower to one backend
explain the whole path
```

Then add a separate lazy-value prototype only for pure/read-only expressions:

```text
lazy value
force value
explain pending/forced value
capture/effect metadata
```

That path would make the idea visible without requiring Nomi to solve macros,
effects, full laziness, symbolic algebra, or compiler optimization all at once.

## Staged Integration Path

### Stage 0: Keep Eager Ordinary Semantics

- Document that ordinary Nomi expressions evaluate eagerly.
- Keep table/query laziness tied to lazy data sources and materialization.
- Do not add ambient symbolic variables.

Exit gate: users can predict statement order in ordinary code.

### Stage 1: Computation/Plan Values For Flow

- Treat flow/table pipelines as the first practical plan values.
- Reuse `explain` for plan structure, schema, source spans, and optimizer
  rewrites.
- Keep query syntax deferred; pipeline verbs remain the canonical lowering.

Exit gate: a lazy data source can show a logical plan before `collect()`.

### Stage 2: `quote:` And Syntax Values

- Add a fenced syntax value with source spans.
- No execution, no global macro expansion, no rule application by default.
- Use it for examples, checks, future macros, and structural inspection.

Exit gate: a quoted expression can be printed, inspected, and round-tripped.

### Stage 3: `describe` And Transparent Pure Functions

- Add transparent expression-only functions.
- Allow `describe f(symbolic_input)` to produce computation IR.
- Reject mutation, uncontrolled IO, and unsupported dynamic control with
  source-aware diagnostics.

Exit gate: `average(xs)` can run normally, while `describe average(xs)` shows
`sum(xs) / len(xs)`.

### Stage 4: Scoped Rewrite Rules

- Apply rules to quote/computation values only.
- Require rule sets, constraints, source spans, strategy, budget, and trace.
- Start with algebraic and query-plan rewrites, not arbitrary program rewrites.

Exit gate: `sum(xs) / len(xs)` can rewrite to `mean(xs)` with an explanation.

### Stage 5: Explicit Lazy Values

- Add `lazy` for pure/read-only expressions.
- Define force, memoization, failure caching, capture policy, and effect
  diagnostics.
- Keep effectful delayed actions research-only until capability/effect docs
  mature.

Exit gate: `lazy total = expensive_sum(xs)` can be explained before and after
force.

### Stage 6: Backend Lowering And Compiler IR

- Lower computation descriptions into Core IR, MLIR, SQL, dataframe engines, or
  interpreter plans as appropriate.
- Backends must report unsupported operations instead of silently changing
  semantics.

Exit gate: one computation has matching interpreter result, optimized plan, and
backend explanation.
