# Flow & Collections

> Normal form: Flow.  Values passed through calls, functions, collection
> transforms, or query plans.  Pipeline is the canonical spelling.
>
> Deep research: [table_and_flow_systems_deep_dive.md](../research/table_and_flow_systems_deep_dive.md)
> (8-system survey: SQL, LINQ, dplyr, Polars, DuckDB, Nushell, pandas, K/Q),
> [array_languages_deep_dive.md](../research/array_languages_deep_dive.md),
> [scientific_languages_r_matlab_julia.md](../research/scientific_languages_r_matlab_julia.md),
> [structured_collections_query_language.md](../features/structured_collections_query_language.md).
>
> Interaction map: [interaction_map.md](interaction_map.md) connects flow to
> function holes, pattern filters, result collection, decode, and explanation.

## 1. Pipeline

Pipeline is the main value-flow operator:

```nomi
active_names =
    users
    |> where(_.active)
    |> select(_.name)
    |> sort
```

Reduction: `x |> f` → `f(x)`, `x |> f(_, y)` → `f(x, y)`.

Pipeline applies a value now. Function composition (`>>>`/`<<<`) builds a
function for later. Keep these separate. See
[functions.md](functions.md) for composition.

**Source reference:** F# `|>`, Elixir `|>`, Gleam `|>`, Julia `|>`,
R `%>%`, Nushell `|`.
**Status:** implemented.

## 2. Collection Verbs

Collection transforms are library functions over typed values. The verb
vocabulary is drawn from cross-language synthesis (SQL, LINQ, dplyr, Polars,
DuckDB, Nushell, pandas, K/Q) — the full synthesis is in
[table_and_flow_systems_deep_dive.md](../research/table_and_flow_systems_deep_dive.md).

### Core Verbs

| Verb | Meaning | Source precedent |
|------|---------|-----------------|
| `where` | Keep rows matching a predicate | SQL WHERE, dplyr `filter()`, Polars `.filter()` |
| `select` | Project or rename columns | SQL SELECT, dplyr `select()`, Polars `.select()` |
| `derive` | Add computed columns | dplyr `mutate()`, Polars `.with_columns()`, SQL SELECT |
| `group` / `group_by` | Add grouping metadata for subsequent verbs | dplyr `group_by()`, SQL GROUP BY, Polars `.group_by()` |
| `summarize` | Aggregate groups into one row each | dplyr `summarize()`, SQL aggregate functions |
| `join` | Combine two tables on key columns | SQL JOIN, dplyr `*_join()`, Polars `.join()` |
| `sort` | Order rows by key | SQL ORDER BY, dplyr `arrange()` |
| `window` | Apply window functions over partitions | SQL OVER, Polars `.over()` |
| `fold` / `reduce` | Combine values into one | FP fold/reduce, Polars `.fold()` |
| `take` | Limit rows | SQL LIMIT, dplyr `slice()` |
| `distinct` | Remove duplicate rows | SQL DISTINCT, dplyr `distinct()` |
| `explain` | Show the query plan without executing | SQL EXPLAIN, Polars `.explain()`, DuckDB EXPLAIN |

### Design Principles

These are settled design decisions (from cross-language synthesis):

**One verb, one way.** One canonical verb per operation. Convenience aliases
(e.g., `filter` for `where`, `mutate` for `derive`) must desugar to the
canonical verb. No `inplace=True` — verbs always return new values.

**Tables are ordinary values.** Table literals, query results, and file loads
all produce the same `Table` type. Every verb takes a table and returns a
table. No separate index axis — keys are column metadata.

**`group_by()` is context, not a separate verb set.** Grouping adds metadata
to a table; subsequent verbs (`summarize`, `window`, `derive`) automatically
respect grouping context. No separate "grouped verbs" vocabulary.

**Expressions are structural, not opaque callbacks.** Verb arguments are
composable expression values, not anonymous functions:

```nomi
# Expression captures structure for explain/optimize
active = users |> where(.active) |> select(.name, .email)

# Equivalent to: filter by column, project named columns
```

The `.field` syntax provides column-name scoping within verb expressions.
Explicit lambdas (`x => x.field`) are available when needed but are opaque
to the query planner.

**Lazy/eager with identical API.** A lazy data source (CSV file, database
table) builds a query plan; an eager data source (in-memory table) executes
immediately. Both use the same verb API:

```nomi
# Eager: executes immediately
in_memory_table |> where(.score > 50)

# Lazy: builds plan, executes on materialization
csv_file |> where(.score > 50) |> collect()
```

Materialization triggers: `collect()`, iteration, `explain()`, writing to disk.

**`explain()` is first-class.** Every verb plan supports `explain()` for
inspection without execution:

```nomi
plan = csv_file |> where(.score > 50) |> group_by(.region) |> summarize(avg_score = .score.mean())
plan.explain()
# Shows: estimated rows, column schema, operations, optimization opportunities
```

**Schema maintained across all operations.** Every verb preserves and augments
column-level schema (name, type, constraints). Schema errors are caught at plan
construction time for lazy sources.

**Columnar layout.** Nomi tables use struct-of-arrays (columnar) memory layout,
compatible with Apache Arrow. This enables zero-copy interop with Polars,
DuckDB, and other columnar systems.

### Query Syntax (Future)

SQL-like query blocks are deferred. The architectural invariant is:

> Query syntax, if added later, MUST lower to the same verb vocabulary as
> pipeline expressions.

This is the LINQ lesson: query expressions and method chains are two surfaces
over the same operators (`IQueryable`). Nomi preserves this option by building
the verb vocabulary first and treating query syntax as syntactic sugar over it.

**Status:** library-first for core verbs; table/query plan verbs are
design-settled (vocabulary and semantics decided, implementation deferred).

### Verb Gaps To Research

The current verb vocabulary covers the table/query core, but everyday
collection work also needs small list/stream helpers. Start library-first:

| Verb/helper | User need | Initial status |
| --- | --- | --- |
| `scan` | Keep intermediate fold states. | library-first |
| `chunk` / `windowed` | Process fixed-size groups or sliding windows. | library-first |
| `partition` | Split values by predicate. | library-first |
| `partition_map` | Split and transform matched/result values in one pass. | library-first |
| `zip` / `enumerate` | Combine positions or parallel collections. | library-first |
| `flat_map` | Map each item to zero or more outputs. | library-first |
| `collect_results` | Turn `list[Result[T,E]]` into `Result[list[T], E]`. | prototype-ready as library |
| `tap` / `tee` | Inspect an intermediate pipeline value. | prototype-ready as library + explanation hook |

These helpers should not become syntax until diagnostics, laziness, and query
plans require a stronger surface. See [interaction_map.md](interaction_map.md)
for the function/pattern/result interactions behind them.

### Explicit Broadcasting (Future)

Julia-style explicit broadcasting (`f.(x)`) is a future concern. Start with
named shape/rank functions. Implicit broadcasting is rejected for the first
layer (conflicts with Python scalar semantics).

## 3. Ranges

```nomi
1..10        # inclusive; → range(1, 11)
1..<10       # exclusive; → range(1, 10)
1..10 by 2   # step;     → range(1, 11, 2)
```

The `by` keyword avoids overloading `//` (floor division).

**Source reference:** Rust `..`/`..=`, Swift `..<`/`...`, Kotlin `..`/`until`,
Ruby `..`/`...`, Pascal `1..10`, PowerShell `1..10`.
**Status:** implemented.

## 4. Spread & Destructuring

Python-compatible spread and destructuring:

```nomi
combined = [*a, *b]
merged = {**defaults, **overrides}
first, *rest = items
```

Reuses the same binding and pattern semantics used elsewhere.

**Status:** partial (Python-compatible paths working).

## 5. Slices

```nomi
items[1:5]
items[:5]
items[1:]
items[::-1]
```

**Status:** Python-compatible, stable.

## 6. Comprehensions

Python-compatible list, set, dict, and generator expressions. Future lazy
adapters should be library-first unless diagnostics or plan inspection
require syntax.

## 7. Array-Language Patterns (Research)

Array languages (APL, J, K, BQN, Uiua) offer patterns that Nomi may
selectively adopt:

| Pattern | Nomi assessment |
|---------|----------------|
| Implicit broadcasting (APL rank) | Rejected for first layer; conflicts with Python scalar semantics |
| Explicit broadcasting (Julia `.`) | Design-needed; opt-in with visible marker |
| Function trains (J forks/hooks) | Partial; `_` holes cover the 80% case |
| Rank polymorphism | Research-only; future layer |
| K/Q table operations | Design-settled; see §2 Collection Verbs above |
| Each/over/scan adverbs | Partial; `map`/`reduce` exist; `scan` is library-first |

For deep analysis, see [array_languages_deep_dive.md](../research/array_languages_deep_dive.md).

## 8. Rejected or Deferred

| Idea | Decision |
|------|----------|
| Implicit elementwise list arithmetic | Rejected; conflicts with Python list semantics |
| Dense APL/J/K rank notation | Future layer; start with named shape/rank functions |
| SQL-like query blocks | Design-settled; must lower to same verb vocabulary as `|>` pipelines |
| Multiple pipeline spellings | Rejected; keep `|>` as the single flow operator |
| Implicit broadcasting | Rejected for first layer |

## 9. Implementation Status

| Feature | Status |
|---------|--------|
| `|>` pipeline | implemented |
| `1..10` inclusive range | implemented |
| `1..<10` exclusive range | implemented |
| `1..10 by 2` range step | implemented |
| Spread in literals | partial |
| Slices | Python-compatible |
| Collection verbs (map/filter/reduce) | implemented as library functions |
| Core verb vocabulary (where/select/derive/group/join/sort/window/fold/take/distinct) | design-settled |
| `explain()` for query plans | design-settled |
| Lazy/eager with identical API | design-settled |
| Lazy collection adapters | library-first |
| Explicit broadcasting | design-needed |

## 10. Design Context

This doc covers Nomi's **Flow** normal form. For the broader picture:

- [Language Foundation §Coherence Contract](../language/language_foundation.md) —
  the One Function And Call Story, and the rule that pipelines and collection
  transforms must reduce to ordinary calls.
- [Language Specification §8.1, §12](../language/language_spec.md) — operators,
  pipeline reduction, collection transforms, comprehensions, and future
  table/query plans.
- [Language Degrees Of Freedom §Library-First Freedom](../language/language_degrees_of_freedom.md) —
  why collection verbs start as library conventions before becoming syntax.
- [Implementation Learnings](../convenience/implementation_learnings.md) —
  `eval_List`/`eval_Tuple` `Starred` spreading fix.
