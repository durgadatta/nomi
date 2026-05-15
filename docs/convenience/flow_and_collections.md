# Flow & Collections

> Normal form: Flow.  Values passed through calls, functions, collection
> transforms, or query plans.  Pipeline is the canonical spelling.
>
> Deep research: [array_languages_deep_dive.md](../research/array_languages_deep_dive.md),
> [scientific_languages_r_matlab_julia.md](../research/scientific_languages_r_matlab_julia.md),
> [structured_collections_query_language.md](../features/structured_collections_query_language.md).

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

Basic transforms are library functions, not syntax:

| Verb | Meaning |
|------|---------|
| `map` / `select` | Transform each item or project fields |
| `where` / `filter` | Keep items matching a predicate |
| `fold` / `reduce` | Combine items into one value |
| `sort` | Order by default or key |
| `count`, `sum`, `min`, `max` | Common reductions |

Table-specific verbs (`derive`, `group_by`, `join`, `window`, `pivot`)
and plan `explain` remain in the structured-collections source note
until the query vocabulary stabilises.

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
| K/Q table operations | Design-needed; subsumed by structured-collections work |
| Each/over/scan adverbs | Partial; `map`/`reduce` exist; `scan` is library-first |

For deep analysis, see [array_languages_deep_dive.md](../research/array_languages_deep_dive.md).

## 8. Rejected or Deferred

| Idea | Decision |
|------|----------|
| Implicit elementwise list arithmetic | Rejected; conflicts with Python list semantics |
| Dense APL/J/K rank notation | Future layer; start with named shape/rank functions |
| SQL-like query blocks | Design-needed; must reduce to collection/query plan verbs |
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
| Lazy collection adapters | library-first |
| Table/query plan verbs | design-needed |
| Explicit broadcasting | design-needed |
