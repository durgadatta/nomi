# Flow & Collections

> Normal form: Flow.  Values passed through calls, functions, collection
> transforms, or query plans.  Pipeline is the canonical spelling.
>
> Deep research: [table_and_flow_systems_deep_dive.md](../research/table_and_flow_systems_deep_dive.md)
> (8-system survey: SQL, LINQ, dplyr, Polars, DuckDB, Nushell, pandas, K/Q),
> [array_languages_deep_dive.md](../research/array_languages_deep_dive.md),
> [scientific_languages_r_matlab_julia.md](../research/scientific_languages_r_matlab_julia.md),
> [modern_language_feature_survey.md](../research/modern_language_feature_survey.md),
> [csharp_java_dart_modern_features.md](../research/csharp_java_dart_modern_features.md),
> [beam_languages_erlang_elixir_gleam.md](../research/beam_languages_erlang_elixir_gleam.md),
> [standard_library_design_comparative.md](../research/standard_library_design_comparative.md),
> [structured_collections_query_language.md](../features/structured_collections_query_language.md).
>
> Interaction map: [interaction_map.md](interaction_map.md) connects flow to
> function holes, pattern filters, result collection, decode, and explanation.
>
> Primary surface: collections are unavoidable. Most programs move through
> lists, maps, sets, ranges, slices, rows, decoded records, and result lists
> before they ever reach specialized query systems.

## Design Pressure

Collection design is a daily-use surface, not a data-engine feature first.
Users need to:

- build, index, slice, destructure, and combine ordinary collections;
- transform values with readable `where`/`select`/`map`/`fold`-like operations;
- move between eager values, lazy streams, and materialized results without
  changing the meaning of their code;
- collect absence and result values without inventing ad hoc loops;
- inspect larger flows when they become plans, diagnostics, or performance
  concerns.

The universal bar is strict. Syntax belongs here only if it improves ordinary
programs across domains. Table schemas, columnar layout, query planners,
broadcast rank, parallel execution, and SQL-like blocks are important, but they
are secondary layers unless they reduce to the same collection and flow normal
forms.

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

Collection transforms are library functions over typed values. The primary
surface must work for ordinary lists, sets, maps, iterables, generators, and
decoded records before it specializes into table/query planning.

The cross-language center is wider than SQL-style tables: Python
comprehensions/`itertools`, JavaScript arrays, Rust iterators, Kotlin/Swift
collections, C# LINQ, Java streams, Clojure seqs, Elixir `Enum`/`Stream`,
Haskell lists, R/tidyverse, Polars, DuckDB, pandas, K/Q, and array languages.
The shared user need is left-to-right value transformation with visible
functions and predictable materialization.

### Primary Collection Surface

This is the universal everyday layer. Names may have aliases while the language
settles, but each operation should have one canonical meaning and one reduction
shape.

| Verb/helper | Meaning | Universal pressure | Initial layer |
|------|---------|--------------------|---------------|
| `where` / `filter` | Keep elements matching a predicate. | Python, JS, Rust, LINQ, SQL, dplyr, Elixir | library-first canonical verb |
| `select` / `map` | Transform each element. | Python, JS, Rust, LINQ, Haskell, Elixir | library-first canonical verb |
| `flat_map` | Map each element to zero or more outputs and flatten one level. | Rust, Scala, Kotlin, JS, FP libraries | library-first |
| `fold` / `reduce` | Combine values into one. | FP fold/reduce, Python, JS, Rust, LINQ | library-first |
| `scan` | Keep intermediate fold states. | Haskell, Rust, Kotlin, array languages | library-first |
| `sort` | Order values by key. | Python, JS, SQL, LINQ, dplyr | library-first |
| `take` / `drop` | Limit or skip values. | Rust, LINQ, itertools, streams | library-first |
| `any` / `all` | Test whether predicates hold. | Python, JS, Rust, SQL | library-first |
| `find` | Return the first matching element, usually as absence/result. | Python idioms, JS, Rust, LINQ | library-first |
| `zip` / `enumerate` | Combine parallel collections or attach positions. | Python, Rust, Swift, Kotlin | library-first |
| `chunk` / `windowed` | Process fixed-size groups or sliding windows. | Kotlin, Rust, itertools, data streams | library-first |
| `group_by` | Partition elements by a key. | LINQ, Kotlin, Python libraries, SQL/dplyr | library-first; table specialization later |
| `collect` | Materialize lazy values or plans. | Rust, streams, LINQ, Polars | library-first |
| `collect_results` | Turn `list[Result[T,E]]` into `Result[list[T], E]`. | Rust `collect`, FP traverse, validation | prototype-ready as library |
| `tap` / `tee` | Inspect an intermediate pipeline value. | Ruby, Unix, Rx/data pipelines | library + explanation hook |

`where`/`select` remain attractive Nomi names because they can span ordinary
collections and future table plans. `filter`/`map` are globally familiar names.
If both spellings survive, aliases must desugar to the canonical operation and
diagnostics should explain one vocabulary.

### Table And Query Secondary Layer

Structured tables are important enough to design, but they are not the first
collections story. They should extend the primary verbs with schema, row scope,
planning, and inspection.

| Table verb | Meaning | Source precedent | Status |
|------|---------|------------------|--------|
| `where` | Keep rows matching a predicate. | SQL WHERE, dplyr `filter()`, Polars `.filter()` | shares primary verb |
| `select` | Project or rename columns. | SQL SELECT, dplyr `select()`, Polars `.select()` | shares primary verb |
| `derive` | Add computed columns. | dplyr `mutate()`, Polars `.with_columns()` | design-needed |
| `group_by` | Add grouping metadata for later verbs. | dplyr `group_by()`, SQL GROUP BY, Polars `.group_by()` | library-first/design-needed |
| `summarize` | Aggregate groups into one row each. | dplyr `summarize()`, SQL aggregate functions | design-needed |
| `join` | Combine two tables on key columns. | SQL JOIN, dplyr joins, Polars `.join()` | design-needed |
| `window` | Apply window functions over partitions. | SQL OVER, Polars `.over()` | secondary |
| `distinct` | Remove duplicate rows. | SQL DISTINCT, dplyr `distinct()` | library-first |
| `explain` | Show a plan without executing. | SQL EXPLAIN, Polars `.explain()`, DuckDB EXPLAIN | explanation layer |

### Design Principles

These are direction-level decisions, not a license to hardcode a data engine
into the language core.

**One verb, one way.** One canonical verb per operation. Convenience aliases
(e.g., `filter` for `where`, `mutate` for `derive`) must desugar to the
canonical verb. No `inplace=True` — verbs always return new values.

**Collections are ordinary values.** Lists, maps, sets, iterables, streams,
tables, and plans must remain values that can be passed, returned, named,
patterned, explained, and tested. Avoid collection features that only work as
statement islands.

**Tables are specialized collection values.** Table literals, query results,
and file loads may converge on a `Table` value family. Table operations can
preserve schema and grouping metadata, but that metadata is a specialization of
collection flow, not a new evaluation model.

**`group_by()` is context, not a separate verb set.** Grouping adds metadata
to a table; subsequent verbs (`summarize`, `window`, `derive`) automatically
respect grouping context. No separate "grouped verbs" vocabulary.

**Structural expressions are optional power, not the base callback story.**
Ordinary collection verbs accept ordinary functions:

```nomi
active = users |> where(_.active) |> select(_.name)
```

Table/query verbs may additionally accept structural expressions for
inspection and optimization:

```nomi
# Expression captures structure for explain/optimize
active = users |> where(.active) |> select(.name, .email)

# Equivalent to: filter by column, project named columns
```

The `.field` syntax needs a separate spec packet for row scope, ambiguity,
diagnostics, and fallback to explicit lambdas (`x => x.field`). It should not
become magic member access for ordinary collections by accident.

**Lazy/eager should preserve meaning.** A lazy source can build a stream or
query plan; an eager source can execute immediately. The same verb should mean
the same transformation in both cases, but materialization rules need explicit
diagnostics and examples:

```nomi
# Eager: executes immediately
in_memory_table |> where(.score > 50)

# Lazy: builds plan, executes on materialization
csv_file |> where(.score > 50) |> collect()
```

Materialization triggers: `collect()`, iteration, `explain()`, writing to disk.

**`explain()` is first-class when a flow becomes inspectable.** Ordinary
pipelines can explain expansion and intermediate types; query plans can explain
estimated rows, column schema, operations, and optimization opportunities:

```nomi
plan = csv_file |> where(.score > 50) |> group_by(.region) |> summarize(avg_score = .score.mean())
plan.explain()
# Shows: estimated rows, column schema, operations, optimization opportunities
```

**Schema belongs to table values and data boundaries.** Table verbs should
preserve and augment column-level schema when available. Schema errors should
be caught as early as possible for lazy sources. Ordinary list transforms should
not pay the conceptual cost of table schemas.

**Storage layout is a backend concern.** Columnar layout and Apache Arrow
interop are promising implementation targets, not language syntax. They belong
behind capability tables and backend plans unless user-visible behavior depends
on them.

### Query Syntax (Future)

SQL-like query blocks are deferred. The architectural invariant is:

> Query syntax, if added later, MUST lower to the same verb vocabulary as
> pipeline expressions.

This is the LINQ lesson: query expressions and method chains are two surfaces
over the same operators (`IQueryable`). Nomi preserves this option by building
the verb vocabulary first and treating query syntax as syntactic sugar over it.

**Status:** primary collection verbs are library-first; table/query verbs are a
secondary design packet that must lower to the same flow vocabulary.

### Collection Gaps To Research

Close these gaps before promoting more collection features:

- canonical naming: whether Nomi teaches `where`/`select`, `filter`/`map`, or
  one pair with documented aliases;
- materialization: exact difference between list, stream, iterator, table, and
  plan values;
- result collection: `collect_results`, validation accumulation, and failure
  diagnostics in pipelines;
- selector scope: whether `.field` is only row/record shorthand, and how it
  interacts with ordinary member access;
- flow explanation: what `explain` shows for ordinary pipelines versus query
  plans;
- collection patterns: how destructuring, rest captures, and pattern filters
  compose with flow.

Helpers should not become syntax until diagnostics, laziness, or plan
inspection require a stronger surface. See [interaction_map.md](interaction_map.md)
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
| K/Q table operations | Secondary table layer; see §2 Collection Verbs above |
| Each/over/scan adverbs | Partial; `map`/`reduce` exist; `scan` is library-first |

For deep analysis, see [array_languages_deep_dive.md](../research/array_languages_deep_dive.md).

## 8. Rejected or Deferred

| Idea | Decision |
|------|----------|
| Implicit elementwise list arithmetic | Rejected; conflicts with Python list semantics |
| Dense APL/J/K rank notation | Future layer; start with named shape/rank functions |
| SQL-like query blocks | Secondary/future; must lower to same verb vocabulary as `|>` pipelines |
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
| Primary collection vocabulary (`where`/`select`, `fold`, `sort`, `take`, `zip`, etc.) | library-first/design-needed for canonical naming |
| Table/query vocabulary (`derive`, `group_by`, `summarize`, `join`, `window`, `distinct`) | secondary design packet |
| `explain()` for ordinary flows and query plans | design-needed in Explanation layer |
| Lazy/eager materialization rules | design-needed |
| Lazy collection adapters | library-first |
| Explicit broadcasting | design-needed |

## 10. Research Coverage And Universal Bar

The collection surface has enough research to avoid copying any one ecosystem:

- Python gives the baseline for lists, dicts, sets, slices, comprehensions, and
  explicit iterator helpers;
- JavaScript/TypeScript, Swift, Kotlin, Java streams, and C# LINQ show the
  mainstream map/filter/reduce and fluent-chain pressure;
- Rust iterators show explicit laziness, `collect`, `Result` collection, and
  type-directed diagnostics;
- Elixir and Clojure show sequence libraries that keep data transformation
  regular across collection types;
- SQL, dplyr, Polars, DuckDB, pandas, Nushell, and K/Q show why table flows need
  schema, planning, and explainability;
- APL, J, K, BQN, Uiua, R, MATLAB, and Julia show the power and risk of
  elementwise and rank-based collection notation.

The Nomi rule is: promote syntax only when it helps the majority of programmers
write ordinary collection code. Specialized table, array, parallel, and lazy
planning features should compose from primary flow, functions, patterns,
absence/result, data boundaries, and explanation before they receive their own
surface.

## 11. Design Context

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
