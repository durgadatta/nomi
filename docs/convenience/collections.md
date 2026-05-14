# Collections And Iteration Convenience

> Status: syntax-facing convenience doc.
>
> Source research for tables, grouping, joins, windows, query plans, and
> backend lowering lives in
> [Structured Collections And Query Language](../features/structured_collections_query_language.md).

## Normal Form

Collection conveniences should reduce to ordinary values, calls, functions,
patterns, and flow:

```text
collection value -> transform call -> collection value or result
```

The first everyday surface should stay close to Python where Python is already
clear, and add syntax only where it makes common transforms easier to read.

## Pipeline

Pipeline is the main value-flow syntax:

```nomi
active_names =
    users
    |> where(_.active)
    |> select(_.name)
    |> sort
```

Reduction:

```text
x |> f        -> f(x)
x |> f(_, y) -> f(x, y)
```

Pipeline applies a value now. Function composition builds a function for later;
keep those separate.

## Transform Verbs

Basic collection verbs should begin as library functions:

| Verb | Meaning |
| --- | --- |
| `map` / `select` | Transform each item or project fields. |
| `where` / `filter` | Keep items that satisfy a predicate. |
| `fold` / `reduce` | Combine many items into one value. |
| `sort` | Order values by default or key. |
| `count`, `sum`, `min`, `max` | Common reductions. |

Table-specific verbs such as `derive`, `group_by`, `join`, `window`, `pivot`,
and plan `explain` belong to the structured collection source note until the
query vocabulary is stable.

## Ranges

Nomi keeps readable range syntax:

```nomi
1..10        # inclusive end; lowers to range(1, 11)
1..<10       # exclusive end; lowers to range(1, 10)
1..10 by 2   # lowers to range(1, 11, 2)
1..<10 by 2  # lowers to range(1, 10, 2)
```

The `by` step form is word-based because `//` already means floor division.

## Spread And Destructuring

Python-style spread and destructuring remain the preferred first layer:

```nomi
combined = [*a, *b]
merged = {**defaults, **overrides}
first, *rest = items
```

These forms should reuse the same binding and pattern semantics used
elsewhere.

## Slices

Slice syntax follows Python-compatible expectations:

```nomi
items[1:5]
items[:5]
items[1:]
items[::-1]
items[::2]
```

## Comprehensions And Lazy Values

Python-compatible list, set, dict, and generator expressions remain useful.
Future lazy adapters should be library-first unless diagnostics or plan
inspection require syntax.

## Rejected Or Deferred

| Idea | Decision |
| --- | --- |
| Implicit elementwise list arithmetic | Rejected for the first layer; conflicts with Python list semantics. |
| Dense APL/J/K rank notation | Future layer; start with named shape/rank functions. |
| SQL-like query blocks | Design-needed; must reduce to collection/query plan verbs. |
| Multiple pipeline spellings | Avoid; keep `|>` as the main value-flow operator. |

## Implementation Priority

| Feature | Status | Priority |
| --- | --- | --- |
| `|>` pipeline | implemented/prototype surface | high |
| `1..10` ranges | implemented | high |
| `1..10 by 2` range step | implemented | medium |
| spread in literals | partial / Python-compatible paths | medium |
| slices | Python-compatible | stable |
| lazy collection adapters | library-first | later |
| table/query plan verbs | design-needed | after structured collection spec |
