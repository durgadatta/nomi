# Collection, Table, And Rank Integration Feature

> Status: active integration feature packet; design direction settled,
> implementation mostly pending.
>
> Normal forms: flow, binding, data boundary, pattern, absence/result,
> explanation.
>
> Canonical homes: this file owns the shared integration contract for ordinary
> collection flow, table values, row/group context, lazy plans, materialization,
> shape/rank-aware operations, and query syntax admission. Detailed local
> syntax remains in [Flow And Collections](../convenience/flow_and_collections.md)
> and source design evidence remains in
> [Structured Collections And Query Language](structured_collections_query_language.md),
> [Symbolic, Lazy, And Structural Computation](symbolic_structural_computation.md),
> [Table And Flow Systems](../research/table_and_flow_systems_deep_dive.md),
> [Array Languages](../research/array_languages_deep_dive.md), and
> [Scientific Languages](../research/scientific_languages_r_matlab_julia.md).

## One Sentence

Nomi collection power should grow from ordinary value flow into table plans and
shape-aware computation without changing the user's mental model.

```text
value -> flow step -> collection/table value -> optional plan
-> materialize or explain
```

This packet exists because data languages split a single user need across many
traditions:

- Python lists, iterators, comprehensions, and pandas;
- Julia arrays and explicit broadcasting;
- R/dplyr table verbs and data masks;
- SQL relations, grouping, joins, and optimizers;
- Polars/DuckDB lazy plans and `explain`;
- K/Q first-class tables;
- APL/J/BQN rank, shape, reduce, scan, and whole-array thought;
- notebooks that demand inspectable intermediate values.

Nomi should keep their durable strengths while refusing the hidden contexts and
dense secondary languages that make data code hard to reason about.

## Design Position

The primitive is flow:

```text
take a value, apply a named step, produce the next value
```

Pipeline is the canonical surface:

```nomi
active_names =
    users
    |> where(_.active)
    |> select(_.name)
    |> sort
```

Everything more powerful must preserve that structure:

| Layer | User question | Boundary |
| --- | --- | --- |
| List/iterator | How do I transform these values? | ordinary function call |
| Result list | How do failures move through the flow? | absence/result collection |
| Record/table | How do I transform named fields or columns? | row context |
| Grouped table | How do I compute by key? | group context |
| Lazy source | When does work execute? | plan/materialization |
| Backend | Where can this plan run? | capability table |
| Array/rank | Which cells or axes does this operation touch? | shape/rank context |
| Query block | Can this read like a table grammar? | sugar over flow verbs |
| Explain | What happened or will happen? | semantic events + plan view |

The source language lesson is not "copy SQL" or "copy dplyr." The lesson is
that data work needs a small verb vocabulary, explicit context, delayed plans
when useful, and trustworthy explanation.

## Competitive Source Anchors

This packet is grounded in the local research corpus and in current official
documentation for the major source systems:

- dplyr presents data manipulation as a consistent verb grammar:
  <https://dplyr.tidyverse.org/index.html>.
- Polars documents eager versus lazy execution, `collect`, optimization, and
  `explain`: <https://docs.pola.rs/user-guide/concepts/lazy-api/>.
- Julia documents explicit dot broadcasting and array shape behavior:
  <https://docs.julialang.org/en/v1/manual/arrays/#Broadcasting>.

The Nomi synthesis keeps the verb grammar, lazy-plan boundary, and explicit
elementwise marker while rejecting hidden dataframe scoping and implicit
rank/broadcast rules in the everyday layer.

## Shared Model

### `FlowStep`

A flow step is a named transformation with explicit input and output behavior.

Minimum fields:

| Field | Meaning |
| --- | --- |
| `verb` | `where`, `select`, `derive`, `group`, `summarize`, `join`, `sort`, `window`, `fold`, `collect`, `explain` |
| `input_kind` | list, stream, table, group, plan, array, result list |
| `expression` | ordinary function, structural selector, aggregate, or policy |
| `context` | element, row, group, window, rank, backend |
| `materialization` | eager, lazy, streaming, forced |
| `schema_effect` | preserved, projected, derived, aggregated, joined, reshaped |
| `failure_policy` | propagate, collect, accumulate, skip, diagnose |
| `span` | source location when available |

Pipeline syntax should reduce to ordinary calls, but serious data flows need
metadata beside the call so `explain`, backends, and notebooks can inspect the
computation.

### `CollectionPlan`

A plan is a value that describes a flow before materialization.

Minimum fields:

| Field | Meaning |
| --- | --- |
| `source` | table, file, stream, query, notebook cell, database, in-memory value |
| `steps` | ordered `FlowStep` records |
| `schema` | known columns/fields/types, if available |
| `shape` | array dimensions, axes, rank, if available |
| `capabilities` | backend operations that are supported or denied |
| `provenance` | source paths, rows, cells, query ids |
| `diagnostics` | schema, shape, capability, or expression errors |

Plan values are ordinary values: they can be named, passed, returned, explained,
tested, collected, or rejected by a backend.

### Contexts

Nomi must distinguish contexts explicitly:

| Context | Example | Rule |
| --- | --- | --- |
| Element | `where(_ > 0)` | `_` is the current element. |
| Row | `where(.status == "paid")` | `.status` is a field/column of the current row. |
| Group | `summarize(total = sum(.amount))` | `.amount` is the column within each group. |
| Window | `window(by=.customer_id, order=.date)` | window expressions see partition/order/frame. |
| Shape/rank | `sin.(angles)` | dot marks elementwise application. |
| Query block | `query orders:` | bare names may refer to row columns only inside the query context. |
| Backend | `collect(plan, backend=duckdb)` | unsupported steps diagnose before or during collection. |

Hidden context is the danger. If a name can mean a local binding, row field,
group field, column expression, or outer variable, the syntax must reveal the
boundary or `explain` must show the lookup path.

## Canonical Verb Vocabulary

The starting vocabulary should be small and regular:

| Verb | Everyday meaning | Table/plan meaning | Status |
| --- | --- | --- | --- |
| `where` | keep values matching predicate | keep rows/groups matching predicate | canonical |
| `select` | transform each value | project columns or expressions | canonical |
| `derive` | add named computed value | add/replace columns | design-needed |
| `group` | partition by key | group table by keys | design-needed |
| `summarize` | reduce partitions | aggregate each group | design-needed |
| `join` | combine related collections | relational join by key/predicate | design-needed |
| `sort` | order values | order rows | canonical |
| `take` | bounded prefix | limit rows | canonical |
| `fold` | reduce with accumulator | reduce collection/group | canonical |
| `scan` | intermediate fold states | running/window-like states | library-first |
| `window` | sliding/chunked view | partition/order/frame context | secondary |
| `pivot`/`unpivot` | reshape values | wide/long table reshape | secondary |
| `collect` | materialize lazy values | execute plan | canonical |
| `collect_results` | turn many `Result`s into one | collect decode/row failures | library-first |
| `explain` | inspect flow | inspect plan/schema/backend | required |

Aliases may exist for familiarity (`filter` for `where`, `map` for `select`),
but diagnostics, docs, and generated plans should prefer one canonical
vocabulary.

## Syntax Variations And Decisions

### Ordinary Collection Flow

Canonical:

```nomi
total =
    orders
    |> where(_.status == "paid")
    |> select(_.amount)
    |> fold(0, (sum, amount) => sum + amount)
```

Compact with row shorthand:

```nomi
total =
    orders
    |> where(.status == "paid")
    |> select(.amount)
    |> sum
```

Decision:

- Keep `|>` as the only pipeline operator.
- Keep ordinary functions as the base callback story.
- Admit `.field` only as a scoped row/record selector, with ambiguity
  diagnostics.

### Table Pipeline

Target:

```nomi
customer_totals =
    orders
    |> where(.status == "paid")
    |> derive(line_total = .quantity * .price)
    |> group(.customer_id)
    |> summarize(
        total = sum(.line_total),
        orders = count(),
    )
    |> sort(.total desc)
    |> take(20)
```

Decision:

- `group` changes context; it does not create a parallel grouped-verb universe.
- `summarize` aggregates group context into a new table.
- `where` keeps the same name before and after grouping, but `explain` should
  show whether it ran in row or group context.

### Query Block Sugar

Future sugar:

```nomi
customer_totals = query orders:
    where status == "paid"
    derive line_total = quantity * price
    group by customer_id
    summarize:
        total = sum(line_total)
        orders = count()
    sort total desc
    take 20
```

Equivalent canonical form:

```nomi
customer_totals =
    orders
    |> where(.status == "paid")
    |> derive(line_total = .quantity * .price)
    |> group(.customer_id)
    |> summarize(total=sum(.line_total), orders=count())
    |> sort(.total desc)
    |> take(20)
```

Decision:

- Query blocks are future L4 sugar.
- They must lower to the same verb calls and `CollectionPlan`.
- Pipeline is the canonical form for explanation, lowering, and first
  implementation.
- Bare column names are allowed only inside the explicit query block context.

### Lazy Plan And Materialization

```nomi
plan =
    scan_csv(path)
    |> where(.status == "paid")
    |> select(.customer_id, .amount)

explain(plan)
rows = collect(plan)
```

Decision:

- Eager sources may execute each step immediately.
- Lazy sources build a `CollectionPlan`.
- `collect`, iteration, write sinks, and selected display operations are
  materialization triggers.
- `explain` must work before materialization.
- Backend pushdown and optimization are plan rewrites with trace evidence.

### Explicit Broadcasting And Shape

Preferred first shape-aware spelling:

```nomi
angles_rad = degrees .* (pi / 180)
waves = sin.(angles_rad)
```

Library-first alternatives:

```nomi
waves = broadcast(sin, angles_rad)
scaled = broadcast(*, values, factor)
```

Deferred rank layer:

```nomi
row_means = rank(mean, axis=rows)(matrix)
```

Decision:

- Adopt explicit Julia-style dot broadcasting as the likely future compact
  spelling.
- Keep `broadcast(...)`, `shape(...)`, `axes(...)`, and named helpers as the
  first library surface.
- Refuse implicit vector recycling and implicit rank polymorphism in everyday
  code.
- Dense APL/J/BQN glyphs remain future scoped notation at most.

## Integration Boundaries

### Row Boundary

Row context begins only in a table-aware verb or explicit query block:

```nomi
orders |> where(.amount > threshold)
```

Rules:

- `.amount` reads the current row field.
- `threshold` reads the lexical binding.
- ambiguous names diagnose.
- `explain` can show row-field and lexical lookups separately.

### Group Boundary

Grouping is metadata on a table/plan:

```nomi
orders |> group(.customer_id) |> summarize(total=sum(.amount))
```

Rules:

- group keys become part of the result schema;
- aggregate functions consume group columns;
- non-aggregate column reads in `summarize` diagnose unless explicitly
  allowed;
- `where` after `group` must state whether it filters groups or rows in the
  plan trace.

### Plan Boundary

Lazy sources create plans:

```text
lazy source -> verb chain -> CollectionPlan -> collect/write/iterate
```

Rules:

- schema errors diagnose as early as possible;
- unsupported backend nodes diagnose before execution when possible;
- optimizer rewrites preserve source spans and original verb chain;
- `explain` shows user-level verbs, not only backend internals.

### Shape And Rank Boundary

Shape-aware operations must name which level they touch:

```text
scalar -> element -> row/cell -> axis -> whole array
```

Rules:

- ordinary arithmetic stays scalar/ordinary unless dot-marked;
- dot operations are elementwise and may fuse later;
- rank/axis helpers are library-first until examples prove syntax pressure;
- shape mismatch diagnostics show input shapes, expected agreement, and the
  operation that required them.

### Backend Boundary

Backends are capability providers, not language authorities.

Minimum backend capability questions:

| Capability | Example |
| --- | --- |
| source | CSV, parquet, SQL table, in-memory table |
| verbs | `where`, `select`, `derive`, `group`, `join`, `window` |
| expressions | arithmetic, string operations, custom functions |
| shape | arrays, tensors, column vectors |
| missing/result | null, missing, `none`, `Err` mapping |
| materialization | collect, stream, write, preview |
| explain | logical plan, optimized plan, actual row counts/timing |

If a backend cannot support a step, Nomi should report the unsupported node and
offer a fallback path if one exists.

## Failure And Result Semantics

Collection flow should not erase failure vocabulary:

| Case | Default |
| --- | --- |
| `where` predicate error | produce structured diagnostic; exact propagation depends on eager/lazy context |
| `select` returns `Err` values | values remain `Result` unless `collect_results` is requested |
| `collect_results` sees failures | returns `Err` with accumulated errors |
| decode inside flow fails | row/field errors retain source path and row number |
| missing column | schema diagnostic |
| ambiguous column name | context diagnostic |
| shape mismatch | shape/rank diagnostic |
| backend cannot lower step | capability diagnostic |

Example:

```nomi
people =
    read_csv(path)
    |> select(Person.decode)
    |> collect_results
```

This should preserve row numbers, field paths, decode rules, and redaction
policy rather than throwing a generic loop error.

## Explanation Events

Every serious flow should be explainable through shared semantic events:

| Producer | Event pressure |
| --- | --- |
| Pipeline | stage entered, value summarized, result kind |
| Table verb | input schema, output schema, row/group context |
| Plan | logical steps, optimized steps, backend capability |
| Materialization | trigger, rows read/written, timings |
| Shape/rank | input shapes, operation rank, mismatch |
| Result collection | successes, failures, accumulation path |

Example:

```text
plan: customer_totals
  source: orders.csv
  stage 1: where .status == "paid"
    context: row
    schema: [customer_id, status, quantity, price]
  stage 2: derive line_total = .quantity * .price
    output: +line_total
  stage 3: group by .customer_id
    output: grouped table keyed by customer_id
  stage 4: summarize total=sum(.line_total), orders=count()
    output schema: [customer_id, total, orders]
```

The user sees Nomi verbs. Backend-specific plans can be attached, but they
should not replace the source-level explanation.

## Target Examples

### Boring Python-Competitive Script

```nomi
totals =
    read_csv("orders.csv")
    |> select(Order.decode)
    |> collect_results
    |> where(_.status == "paid")
    |> group(_.customer_id)
    |> summarize(total=sum(_.amount))
```

This proves that files, decode, result collection, filtering, grouping, and
aggregation compose without a second language.

### Scientific Shape Work

```nomi
z = (x .- mean(x)) ./ std(x)
signal = sin.(time .* frequency)
```

This proves explicit elementwise operations are readable enough for everyday
math without implicit broadcasting.

### Plan Before Execution

```nomi
plan =
    scan_csv("orders.csv")
    |> where(.status == "paid")
    |> group(.customer_id)
    |> summarize(total=sum(.amount))

explain(plan)
rows = collect(plan)
```

This proves a Polars/DuckDB-like optimizer boundary while keeping Nomi syntax.

### Future Query Block

```nomi
top_customers = query scan_csv("orders.csv"):
    where status == "paid"
    group by customer_id
    summarize total = sum(amount)
    sort total desc
    take 20
```

This should stay target-only until the pipeline form, row context, group
context, plan value, and explain output are implemented.

## Rejected Alternatives

| Alternative | Why not |
| --- | --- |
| SQL strings as the primary query surface | Loses source spans, injection safety, host-language checks, and shared flow semantics. |
| Hidden dataframe data masks in ordinary pipeline code | Makes local names and column names compete invisibly. |
| Query block before verb vocabulary | Creates a second language before the normal form is stable. |
| Implicit vector recycling | Silent length bugs; R shows the danger. |
| Implicit broadcasting/rank everywhere | Conflicts with Python-like scalar/list expectations and hides shape mistakes. |
| pandas-style hidden index semantics | Makes alignment a secret axis of meaning. |
| `inplace=True` or mutation flags | One verb should not have two semantic modes. |
| Opaque callbacks as the only query representation | Prevents schema checking, backend lowering, and explanation. |
| Dense glyph notation in the everyday layer | Raises the first-hour cost and fractures readability. |

## Implementation Slices

1. Declare canonical collection verbs and aliases in prelude/stdlib docs.
2. Add passive `FlowStep` metadata for pipeline inspection without changing
   runtime semantics.
3. Define `Table`, `Schema`, `Column`, `Group`, and `CollectionPlan` value
   shapes at the docs/spec level before runtime hardening.
4. Implement library-first `where`, `select`, `fold`, `scan`, `sort`, `take`,
   `collect`, and `collect_results` contracts over ordinary collections.
5. Add row-selector syntax or helper values only after ambiguity diagnostics
   are specified.
6. Add table-aware verbs: `derive`, `group`, `summarize`, `join`, `distinct`.
7. Add plan-producing lazy sources such as `scan_csv`, with `collect` and
   `explain` before query-block syntax.
8. Add shape helpers: `shape`, `axes`, `broadcast`, and shape diagnostics.
9. Prototype explicit dot broadcasting only after parser/reducer ownership and
   formatter behavior are clear.
10. Add query block syntax as L4 sugar only after it lowers to the same
    `FlowStep`/`CollectionPlan` representation.

## Test And Sample Gates

Before this packet is promoted beyond active design, the project should have:

- library tests for canonical collection verbs and aliases;
- parser/reduction tests for `|>` preserving ordinary call semantics;
- flow inspection snapshots that show ordered `FlowStep` metadata;
- table fixtures for filter, project, derive, group, summarize, join, sort,
  limit, and result collection;
- decode-in-flow fixtures with row paths and accumulated errors;
- lazy plan fixtures for `scan_csv -> where -> group -> summarize -> explain`;
- shape diagnostics for explicit broadcast success and mismatch;
- refusal fixtures or docs-only labels for query blocks, dense rank syntax, and
  implicit broadcasting;
- capability matrix rows for collection verbs, table plans, explain, web, and
  notebook exposure.

## Promotion Rule

This packet becomes spec-ready only when Nomi can show the same verb chain as
an eager collection flow, a lazy table plan, and an `explain` trace. Query block
syntax and rank notation must wait until that shared plan representation is
visible.
