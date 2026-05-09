# Symbolic And Structural Computation

> Status: speculative source note for Nomi design review.
>
> Purpose: explore a Nomi layer where computations can be described,
> inspected, transformed, optimized, and executed by pluggable backends instead
> of being treated only as opaque runtime function calls.

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

## Recommended Next Step

Do not start with a general symbolic system. Start with one concrete path:

```text
transparent expression function
symbolic collection input
describe call
inspect calls
rewrite average to mean
lower to one backend
explain the whole path
```

That path would make the idea visible without requiring Nomi to solve macros,
effects, full laziness, symbolic algebra, or compiler optimization all at once.
