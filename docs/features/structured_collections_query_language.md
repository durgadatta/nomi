# Structured Collections And Query Language

> Status: speculative source note for Nomi design review.
>
> Purpose: design a clean, composable, hierarchical API and syntax model for
> collections and structured data as a first-class language feature, not a
> library-shaped afterthought.
>
> Related notes:
>
> - [Symbolic And Structural Computation](symbolic_structural_computation.md)
> - [High-Level Language Usability Syntax Notes](../research/high_level_language_usability_syntax_notes.md)
> - [Python Syntax Stretch Feature Atlas](../research/python_syntax_stretch_feature_atlas.md)

## Design Goal

Nomi should make structured collections feel as native as functions and
bindings. Lists, rows, tables, groups, joins, windows, and summaries should not
require users to switch mental models between Python loops, SQL strings,
dataframe method chains, ad hoc lambdas, and backend-specific APIs.

The goal is a language surface that is:

- clean: a small set of verbs and concepts;
- composable: every step produces a value or plan usable by the next step;
- easy to learn: the same ideas scale from lists to tables;
- easy to remember: names and clause order follow a stable grammar;
- hierarchical: simple transforms first, grouped/windowed/joined queries later;
- inspectable: queries can explain their plan, schema, and failures;
- backend-aware: the same description can run eagerly, lazily, or through a
  backend.

This is not "add SQL as a string." It is "make structured collection
transformation part of the language core."

## Reference Pressure

### SQL

SQL is the giant because it made tabular transformation declarative and
backend-optimizable. Its lasting strengths are:

- projection, filtering, grouping, joining, ordering, limiting;
- logical query descriptions separate from physical execution;
- schemas and types;
- optimizer-friendly declarative structure;
- a shared vocabulary across many systems.

But SQL also has cognitive costs:

- clause order differs from logical evaluation order;
- nested queries and common table expressions can become scaffolding-heavy;
- column aliases, grouping rules, null semantics, and window behavior are
  subtle;
- embedding SQL inside a host language creates stringly boundaries.

Nomi should learn SQL's relational core and optimizer boundary, while avoiding
stringly embedding and unnecessary ceremony for ordinary collection work.

### R, dplyr, And The Tidyverse

dplyr describes itself as a grammar of data manipulation built from consistent
verbs such as `mutate`, `select`, `filter`, `summarise`, and `arrange`, with
`group_by` composing naturally with them.

Nomi lessons:

- A small verb grammar is easier to learn than a large method catalog.
- The "current table/current row/current column" context reduces noise.
- Grouped operations should feel like the same verbs under a grouping context,
  not a separate API.
- Backends matter: the same high-level transformation should be able to target
  local data frames or remote tables.

Sources:

- [dplyr overview](https://dplyr.tidyverse.org/index.html)
- [Programming with dplyr](https://dplyr.tidyverse.org/articles/programming.html)

### pandas

pandas made labeled, mixed-type, in-memory tabular data central to Python data
work. Its major lessons include:

- indexes and labels are powerful but cognitively expensive;
- groupby is naturally understood as split, apply, combine;
- `merge`, `join`, `concat`, reshape, pivot, melt, stack, and unstack cover
  important table-shape changes;
- `.pipe` exists because users need chainable composition;
- flexible `apply` is useful, but often less predictable and less optimizable
  than explicit verbs.

Nomi lessons:

- Avoid making implicit indexes the hidden center of semantics.
- Prefer explicit keys and row identity where possible.
- Separate aggregation, transformation, and filtering instead of using one
  catch-all apply shape.
- Make reshaping part of the grammar early enough that users do not invent
  parallel conventions.

Sources:

- [pandas groupby](https://pandas.pydata.org/docs/user_guide/groupby.html)
- [pandas merge, join, concat](https://pandas.pydata.org/pandas-docs/stable/user_guide/merging.html)
- [pandas reshaping](https://pandas.pydata.org/docs/user_guide/reshaping.html)
- [pandas DataFrame.pipe](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.pipe.html)

### Polars

Polars is especially relevant to Nomi because it exposes expressions and lazy
query plans. A Polars expression is a lazy representation of a data
transformation, and lazy queries can be optimized and explained before
execution.

Nomi lessons:

- Expressions need contexts: select, derive, filter, group, aggregate.
- Lazy plans should be inspectable with `explain`.
- Schema errors can be caught before data is processed.
- Query optimization is easiest when transformations are structural, not opaque
  callbacks.

Sources:

- [Polars expressions and contexts](https://docs.pola.rs/user-guide/concepts/expressions-and-contexts/)
- [Polars lazy API](https://docs.pola.rs/user-guide/concepts/lazy-api/)
- [Polars lazy usage](https://docs.pola.rs/user-guide/lazy/using/)

### DuckDB Friendly SQL

DuckDB is useful because it keeps SQL but makes analytical work friendlier:
features such as `GROUP BY ALL`, column-aware expressions, direct file queries,
struct/list support, trailing commas, and more ergonomic query affordances.

Nomi lessons:

- SQL can be made friendlier without abandoning declarative query planning.
- Column selection, exclusion, replacement, and reusable aliases are important
  for day-to-day usability.
- Directly querying files and in-memory values should be natural.
- "Friendly SQL" features often address real friction that a new language can
  avoid from the start.

Source:

- [DuckDB Friendly SQL](https://duckdb.org/docs/stable/sql/dialect/friendly_sql)

### kdb+/q

q and kdb+ are relevant because tables are first-class data structures, not
only database entities. q tables are column-oriented and live in the same
language as functions and expressions. qSQL also has query templates and a
functional form useful for programmatically generated queries.

Nomi lessons:

- Tables should be ordinary values.
- Columnar structure matters.
- Query syntax and functional query representation should be related.
- Keys should be explicit and usable as data structure semantics, not only
  database constraints.

Sources:

- [KX q tables](https://code.kx.com/kdb-x/how_to/basics/data_structures/tables.html)
- [KX q keyed tables](https://code.kx.com/kdb-x/how_to/basics/data_structures/keyed-tables.html)
- [KX q select](https://code.kx.com/kdb-x/reference/select.html)
- [KX functional qSQL](https://code.kx.com/q/basics/funsql/)

### APL

APL is relevant less for its glyphs than for its array thought: shape, rank,
axis, reduce, scan, key/grouping, and whole-array transformations. It teaches
that many loops are really structural operations over axes and cells.

Nomi lessons:

- Shape and rank should be concepts users can name, inspect, and constrain.
- Reduce, scan, each/map, key/group, and rank-aware transforms are powerful
  primitives.
- Nomi should prefer readable names first; dense symbolic notation can remain a
  later or domain-specific layer.

Sources:

- [Dyalog arrays](https://docs.dyalog.com/20.0/programming-reference-guide/introduction/arrays/arrays/)
- [Dyalog reduce](https://docs.dyalog.com/20.0/language-reference-guide/primitive-operators/reduce/)
- [Dyalog rank](https://docs.dyalog.com/20.0/language-reference-guide/primitive-operators/rank/)
- [Dyalog operators overview](https://course.dyalog.com/Operators/)

## Core Collection Model

Nomi should distinguish these levels clearly:

```text
Scalar       one value
Record       named fields, one entity
List         ordered values
Set          unique unordered values
Map          key -> value
Table        rows with named columns and schema
Group        table partitioned by keys
Window       ordered neighborhood over rows
Array        shaped homogeneous or typed collection
Stream       possibly unbounded sequence
Query        structured computation over collection values
Plan         inspectable, optimizable query description
```

The same small operations should recur:

```text
bind       name fields, rows, columns, groups
where      keep values matching a predicate
select     choose fields or columns
derive     add or replace computed fields/columns
summarize  reduce many values to fewer values
group      create grouped collection context
join       combine collections by related keys
order      impose ordering
limit      take a bounded subset
reshape    pivot, unpivot, nest, unnest, explode
window     compute over ordered neighborhoods
fold       reduce arbitrary collections
scan       fold with intermediate results
explain    show schema, plan, and diagnostics
```

The names are deliberately ordinary. The hierarchy matters more than clever
notation.

## A Hierarchy Of Learning

### Level 1: Lists And Simple Collections

The user starts with familiar transforms:

```python
numbers
    |> map(x => x * 2)
    |> where(x => x > 10)
    |> fold(0, (total, x) => total + x)
```

Or, with current-element shorthand if accepted:

```python
numbers
    |> map(_ * 2)
    |> where(_ > 10)
    |> sum
```

Core concepts:

```text
element binding
predicate
transform
fold/reduce
pipeline
```

### Level 2: Records And Tables

A table is a collection of row records with schema:

```python
data Order:
    id: OrderId
    customer_id: CustomerId
    status: str
    amount: Money
    created_at: DateTime

orders: Table[Order]
```

Basic query:

```python
paid =
    orders
    |> where(.status == "paid")
    |> select(.id, .customer_id, .amount)
```

Core concepts:

```text
row binding
field/column access
schema
projection
filtering
```

### Level 3: Groups And Aggregates

Grouped query:

```python
customer_totals =
    orders
    |> where(.status == "paid")
    |> group_by(.customer_id)
    |> summarize(
        total = sum(.amount),
        count = count(),
        first_order = min(.created_at),
    )
```

The group context changes what expressions mean:

```text
.amount inside summarize means the amount column within each group
sum(.amount) reduces each group to one value
```

Core concepts:

```text
group key
group context
aggregate
group result schema
```

### Level 4: Joins

Joins should be explicit about keys and cardinality:

```python
orders
    |> join(customers, on=.customer_id == customers.id, how="left")
    |> select(.id, customers.name, .amount)
```

Better possible Nomi shape:

```python
orders
    |> join customers:
        on customer_id == customers.id
        keep left
    |> select id, customers.name, amount
```

Core concepts:

```text
left/right input
key relationship
cardinality
missing match policy
name conflict policy
```

Diagnostics should catch:

- missing join keys;
- duplicate keys when one-to-one was expected;
- many-to-many joins that were not requested;
- ambiguous column names;
- backend-specific null/missing semantics.

### Level 5: Windows And Ordered Computation

Windowed query:

```python
orders
    |> partition_by(.customer_id)
    |> order_by(.created_at)
    |> derive(
        running_total = scan_sum(.amount),
        previous_amount = lag(.amount),
    )
```

SQL window functions are powerful but hard to remember. Nomi should make the
hierarchy visible:

```text
partition -> order -> frame -> compute
```

Possible syntax:

```python
orders
    |> window by .customer_id order .created_at:
        derive running_total = sum(.amount) over rows_to_current
        derive previous_amount = lag(.amount)
```

Core concepts:

```text
partition
ordering
frame
window expression
```

### Level 6: Reshape

Reshape deserves first-class treatment:

```python
long =
    wide
    |> unpivot(
        id = [.country, .year],
        names_to = "metric",
        values_to = "value",
    )
```

```python
wide =
    long
    |> pivot(
        index = [.country, .year],
        columns = .metric,
        values = .value,
    )
```

Core concepts:

```text
wide vs long
identifier columns
measure columns
nest/unnest
explode
```

## SQL-Like Query Blocks

Pipelines are excellent for composition, but structured table work may benefit
from a query block whose grammar is stable and SQL-like.

Possible Nomi query block:

```python
customer_totals = query orders:
    where status == "paid"
    group by customer_id
    summarize:
        total = sum(amount)
        count = count()
    order by total desc
    limit 20
```

This should reduce to the same plan as:

```python
customer_totals =
    orders
    |> where(.status == "paid")
    |> group_by(.customer_id)
    |> summarize(total=sum(.amount), count=count())
    |> order_by(.total desc)
    |> limit(20)
```

The query block is not a separate language. It is structured syntax for a
query plan.

### Clause Order

SQL's written order is familiar, but not always cognitive. Nomi could use a
flow order:

```text
source -> where -> derive -> group -> summarize -> where group -> select ->
order -> limit
```

Potential Nomi clauses:

```text
from/query  source
where       row predicate before grouping
derive      add row-level fields
group by    group keys
summarize   aggregate group values
having      group predicate after aggregation
select      final projection/renaming
order by    result ordering
limit       bounded result
```

Open decision:

```text
Should select appear early like SQL, or late like a pipeline projection?
```

Recommendation:

For Nomi, prefer flow order in query blocks. Let `select` near the end mean
"final shape" and `derive` mean "add intermediate columns." This is easier to
trace and teach.

## Column And Row Reference

A first-class query language needs a clean answer to "what does this name mean?"

Possible rules:

```text
Inside query orders:
  unqualified field names first refer to row fields
  local bindings require explicit let
  outer variables require explicit capture or different syntax
```

Example:

```python
threshold = 100

large = query orders:
    let min_amount = threshold
    where amount > min_amount
    select id, amount
```

Alternative subject-dot style:

```python
large =
    orders
    |> where(.amount > threshold)
    |> select(.id, .amount)
```

Design pressure:

- unqualified names are pleasant in query blocks;
- dotted subject names are safer in expression pipelines;
- both can lower to the same row-binding primitive.

## The Core Verb Set

Nomi should keep a small verb set and make variants regular.

### Row-Level Verbs

```text
where      keep rows
select     choose fields/columns
derive     add/replace fields
rename     change names
drop       remove fields
distinct   remove duplicates by key or selected fields
order_by   sort rows
limit      bound rows
```

### Group-Level Verbs

```text
group_by    partition rows
summarize   aggregate each group
having      filter group summaries
ungroup     return to row/table context
```

### Two-Input Verbs

```text
join        combine by key or predicate
semi_join   keep left rows with matches
anti_join   keep left rows without matches
union       stack compatible rows
intersect   keep common rows
except      remove rows present in another collection
```

### Shape Verbs

```text
pivot       long -> wide
unpivot     wide -> long
nest        rows -> nested collection field
unnest      nested collection field -> rows
explode     list values -> rows
```

### Ordered/Window Verbs

```text
partition_by
window
lag
lead
rank
scan
rolling
```

### General Collection Verbs

```text
map
where
fold
reduce
scan
flat_map
zip
chunk
sort
take
drop
```

Open naming issue:

```text
filter vs where
map vs select vs derive
reduce vs summarize
sort vs order_by
```

Recommendation:

- Use `where` for predicates in query/table contexts.
- Use `map` for element-to-element transforms in general collections.
- Use `select` for projection.
- Use `derive` for adding/replacing fields.
- Use `summarize` for named aggregations over groups or whole tables.
- Use `fold` for explicit accumulator logic.
- Use `reduce` for operator-style reductions where no explicit accumulator is
  named.
- Use `order_by` for table rows, `sort` for plain collections.

## Structured Collection Values

Nomi should treat tables as values with metadata:

```text
Table:
  rows
  schema
  keys
  order
  grouping, if any
  backend, if any
  plan, if lazy or symbolic
```

Schema:

```text
field name
type
constraints
missingness
role, such as key, measure, label, timestamp
source span or provenance
```

This lets diagnostics say:

```text
QueryError: unknown column total
  query: order by total desc
  available after this stage: customer_id, amount
  note: total is defined in summarize, so order by must appear after summarize
```

## Query As Computation Description

The collection/query feature should connect directly to symbolic structural
computation.

```python
plan = describe query orders:
    where status == "paid"
    group by customer_id
    summarize total = sum(amount)
```

Inspectable plan:

```text
Scan orders
Filter status == "paid"
Group key customer_id
Aggregate total = sum(amount)
```

Backend choices:

```python
plan.run(with=interpreter)
plan.run(with=duckdb_backend)
plan.run(with=polars_backend)
plan.run(with=spark_backend)
```

The user should be able to ask:

```python
explain plan
explain plan.with_backend(duckdb_backend)
```

This answers:

- which columns are required;
- which predicates can be pushed down;
- which aggregations are supported;
- whether schema constraints are satisfied;
- where the result order comes from;
- whether execution is eager, lazy, streaming, or backend-lowered.

## Map, Filter, Reduce, And SQL

Map/filter/reduce are still useful, but they are not enough for structured
tables unless the language adds names, schemas, grouping, and joins.

Relationship:

```text
where      -> filter rows by predicate
derive     -> map row to row with added/replaced fields
select     -> map row to projected row
summarize  -> reduce rows or groups to summary rows
group_by   -> partition collection before reduction
join       -> combine two collections by relationship
window     -> map row with ordered neighborhood context
```

This gives users one conceptual ladder:

```text
plain collection:
  map / where / fold

table:
  select / where / derive / summarize

grouped table:
  group_by / summarize / having

relational collection:
  join / union / intersect / except

ordered table:
  partition_by / order_by / window / scan
```

## APL And Shape-Aware Collections

APL suggests another dimension: collection operations should know shape and
rank, not just rows.

Nomi should support readable shape concepts:

```python
matrix |> reduce(axis="rows", with=sum)
matrix |> scan(axis="cols", with=sum)
array |> map_cells(rank=2, normalize)
```

For tables:

```python
sales
    |> group_by(.region, .month)
    |> summarize(total=sum(.amount))
    |> pivot(index=.region, columns=.month, values=.total)
```

Design rule:

```text
Prefer named shape-aware functions before symbolic rank notation.
```

## q/kdb+ And First-Class Tables

q's lesson is that tables can be normal language values with direct syntax,
keys, columns, and query operations.

Possible Nomi table literal:

```python
orders = table:
    id  customer_id  status  amount
    1   "c1"         "paid"  20
    2   "c1"         "open"  15
    3   "c2"         "paid"  30
```

Or schema-first:

```python
orders = table Order:
    (1, "c1", "paid", 20)
    (2, "c1", "open", 15)
    (3, "c2", "paid", 30)
```

Key declaration:

```python
orders keyed by id
customers keyed by id
```

This should not silently enforce database constraints unless declared:

```python
orders: Table[Order], unique(.id)
```

## Good Diagnostics

A collection language needs diagnostics that understand tables, schemas, and
query stages.

Examples:

```text
SchemaError: column amount is Money?, but sum requires non-missing Money
  stage: summarize total = sum(amount)
  suggestion: use sum(skip_missing amount) or require amount:Money
```

```text
JoinError: join may be many-to-many
  left key customer_id has duplicates
  right key id has duplicates
  note: declare many_to_many=True if this is intended
```

```text
GroupError: column amount is not available after summarize
  available: customer_id, total, count
  source: select customer_id, amount
```

```text
BackendError: csv_backend cannot execute rolling median
  stage: derive med = rolling_median(amount, 7)
  supported backends: interpreter, polars_backend
```

These diagnostics require the query to be structural, not just a stream of
opaque callbacks.

## Syntax Candidates

### Candidate A: Pipeline First

```python
customer_totals =
    orders
    |> where(.status == "paid")
    |> group_by(.customer_id)
    |> summarize(total=sum(.amount), count=count())
    |> order_by(.total desc)
```

Strengths:

- compositional;
- works for lists and tables;
- fits existing Nomi pipeline direction;
- easy to lower to calls.

Weaknesses:

- table queries can become punctuation-heavy;
- grouping context may be less visible;
- complex joins/windows may need nested calls.

### Candidate B: Query Block First

```python
customer_totals = query orders:
    where status == "paid"
    group by customer_id
    summarize:
        total = sum(amount)
        count = count()
    order by total desc
```

Strengths:

- stable grammar;
- SQL-like without SQL's string boundary;
- easy for diagnostics to point to clauses;
- good for structured tables.

Weaknesses:

- another syntax category;
- needs careful name-resolution rules;
- must still compose as a normal value.

### Candidate C: Hybrid

Use pipelines for expression composition and query blocks for structured table
work.

```python
customer_totals =
    orders
    |> query:
        where status == "paid"
        group by customer_id
        summarize total = sum(amount), count = count()
    |> limit(20)
```

Strengths:

- keeps both composition and table grammar;
- query block becomes a transform stage;
- natural bridge to lazy/plan execution.

Weaknesses:

- more design work;
- needs a clean story for query input and output.

Recommendation:

Prototype both A and B as equivalent lowerings to a single `QueryPlan`.
Choose the surface that produces better examples and diagnostics.

## Reduction To Core

Collection queries should reduce to existing Nomi concepts:

```text
Source       source spans for each query clause
Value        tables, rows, groups, arrays, streams, plans
Binding      row, column, group, and alias binding
Constraint   schema and value checks
Function     transforms, predicates, aggregates
Call         each query stage is a call or plan node
Data         row records and schema declarations
Pattern      destructuring rows and nested data
Match        later for structural table/data branching
Collection   list/table/group/window/array/stream
Block        possible query blocks and row/group blocks
Example      sample input/output query examples
Trace        stage-by-stage plan and result summaries
Diagnostic   schema, grouping, join, backend failures
Module       exports table schemas and query helpers
```

No separate query universe.

## First Prototype Slice

Do not start with a full SQL clone. Start with a tight, inspectable subset:

```text
Table value with schema
where
select
derive
group_by
summarize
order_by
limit
explain
```

Example:

```python
data Order:
    customer_id:str
    status:str
    amount:int

orders: Table[Order]

customer_totals = query orders:
    where status == "paid"
    group by customer_id
    summarize total = sum(amount), count = count()
    order by total desc
```

Expected plan:

```text
Scan orders: Table[Order]
Filter status == "paid"
Group by customer_id
Aggregate total=sum(amount), count=count()
Order by total desc
```

Expected result schema:

```text
Table[
  customer_id: str,
  total: int,
  count: int,
]
```

## Open Questions

- Should Nomi's primary table syntax be pipeline, query block, or hybrid?
- Should unqualified names inside query blocks refer to columns by default?
- Should `select` appear at the beginning, SQL-style, or near the end,
  flow-style?
- How should row order be represented: guaranteed, unknown, or backend-defined?
- Should table keys be constraints, metadata, or both?
- How should missing values differ from Python `None`, SQL `NULL`, R `NA`, and
  pandas `NA`?
- What is the first-class representation of a grouped table?
- Should `summarize` over an ungrouped table return one-row table or scalar
  record?
- How much APL-style rank/axis language belongs in the first version?
- What backend capability information should be available in diagnostics?

## Design Principles

1. Collections are first-class values, not loops in disguise.
2. Tables are structured collections with schema, not just lists of dicts.
3. Query syntax lowers to a plan that can be inspected, optimized, and run.
4. The verb set should be small and memorable.
5. Grouping and windowing should be contexts, not magical side effects.
6. Joins should make keys, cardinality, and missing-match policy visible.
7. Reshaping should be part of the collection story, not a specialist corner.
8. Shape and rank should be readable concepts before symbolic notation appears.
9. Diagnostics should mention the query stage, schema, and available fields.
10. The same core should work for local values, lazy plans, files, and backend
    execution.
