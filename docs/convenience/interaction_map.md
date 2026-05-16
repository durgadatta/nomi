# Convenience Interaction Map

> Status: active synthesis note.
>
> Scope: convenience syntax interactions, especially functions, patterns, and
> collection flow. This is a pass-1 local consolidation: it sharpens existing
> docs and records next research targets. It does not add implementation work.

## Purpose

The focused convenience docs are strongest when read one at a time. The next
risk is feature drift at their boundaries:

```text
function sugar + pattern sugar + collection sugar = accidental mini-language
```

This map keeps the interactions explicit. A feature that sits between normal
forms should not choose its spelling locally. It should preserve the same
normal-form story from all sides.

## Main Intersections

| Intersection | User pressure | Preferred Nomi path | Caveat |
| --- | --- | --- | --- |
| Function + Pattern | Compact classifiers, recursion, variant handling. | Piecewise equations are ordered pattern clauses over function parameters. | Promote to `func` plus `match` when branches need statements, tracing, or shared setup. |
| Function + Flow | Tiny transforms in pipelines. | Use `_`, `$...`, sections, or `=>` only when the stage remains visually obvious. | Do not let placeholders become a second lambda language. |
| Pattern + Flow | Filter/project collections by structure. | Start with `where`, `select`, `flat_map`, `collect_results`, and named predicate functions. | Avoid query syntax until row/group binding needs a clearer scoped surface. |
| Pattern + Data Boundary | Decode external maps, rows, JSON, CLI, config. | Use `Data.decode(...)`, structural patterns, and constrained captures. | Constraint failure at a boundary should diagnose with a path; ordinary match may skip the case. |
| Function + Block | Flatten callback-heavy APIs. | Use block calls for policy-owned caller-side code. | Do not add trailing-lambda punctuation as another function form. |
| Flow + Result | Transform values that may fail. | Prefer `Result` values plus `match`, `collect_results`, and library combinators first. | A generic `?` operator remains design-needed until propagation and conversion are specified. |
| Flow + Data Boundary | Clean external rows into owned values. | `rows |> select(Person.decode) |> collect_results` or an equivalent named helper. | Diagnostics must preserve source row/field paths through the pipeline. |
| Pattern + Absence | Optional value narrowing. | `if Some(value) = maybe:` or `guard Some(value) = maybe:` when using `Option`; `?.`/`??` for absence-only access. | Do not make optional binding a separate syntax family. |
| Flow + Explanation | Inspect transforms, query plans, and failures. | `explain` should show stages, intermediate schemas, and failing values. | Plan explanation and runtime trace should share event vocabulary. |

## Focus Area: Functions, Patterns, Collections

### Piecewise Functions Are Pattern Dispatch

This is the most important function/pattern intersection:

```nomi
label(0) = "zero"
label(n) when n > 0 = "positive"
label(n) = "negative"
```

Reduction:

```text
receive call arguments
try clause patterns in order
tentatively bind captures
check guards/constraints
evaluate selected body
```

The diagnostics should be able to say:

- no clause matched;
- a clause shape matched but a constraint failed;
- a guard rejected the clause;
- a later catch-all clause handled the value.

### Pipeline Stages Should Stay Readable

These are all acceptable, but they carry different cognitive load:

```nomi
users |> where(_.active)
users |> where(user => user.active and user.plan != none)
users |> where(is_billable_user)
```

Rule:

- use `_` for one obvious receiver;
- use `=>` when naming the parameter helps;
- use a named function when the predicate is domain logic;
- use piecewise equations when the predicate is really structural dispatch.

### Collection Verbs Need Binding Policy

Collection operations often introduce local names:

```nomi
pairs(headers) -> key, value:
    ...

users |> derive(domain = split_email(_.email).domain)
```

Open design pressure:

- Does a verb expression use placeholder `_`, column shorthand `.field`, or
  explicit `row => ...`?
- When is a row a binding target rather than an implicit receiver?
- How do grouped rows expose group keys, row fields, and aggregate values?

Pass-1 decision:

Keep these as library-first and plan-value questions. Do not add query syntax
until row/group binding has a feature packet.

## Candidate Ideas To Evaluate Next

These are promising but not admitted. They need external research and the
feature packet from `../language/spec_readiness_map.md`.

| Candidate | Source pressure | Nomi normal form | Initial status | Why it matters |
| --- | --- | --- | --- | --- |
| Pattern functions / recognizers | F# active patterns, Racket match expanders, Scala extractors | pattern + function | design-needed | Lets libraries define reusable shape tests without global macro power. |
| View patterns | Haskell view patterns, Elixir matches after transforms | pattern + function | research-only | Useful for normalized matching, but can hide work inside a pattern. |
| `let pattern = expr else:` | Rust `let else`, Swift `guard let` | pattern + binding | prototype-ready if syntax fits | Could make required destructuring clearer outside functions. |
| `scan` / prefix fold | APL scan, Haskell `scanl`, itertools `accumulate` | flow | library-first | Common in data work; should be a function before syntax. |
| `chunk` / `windowed` | Kotlin, more-itertools, SQL windows | flow | library-first | Bridges lists and table windows. |
| `partition_map` | Rust itertools, functional libraries | flow + result/pattern | library-first | Splits `Ok`/`Err`, `Some`/`None`, or matched/unmatched values cleanly. |
| Transducers | Clojure, functional stream libraries | flow + function | research-only | Could unify eager/lazy/stream transforms, but risks abstraction weight. |
| Named pipeline taps | Elixir `dbg`, Ruby `tap`, Unix `tee` | flow + explanation | prototype-ready as library | Helps inspect intermediate values without changing flow. |
| Pattern-aware `where` | Haskell guards/where, SQL CTEs | pattern + binding | design-needed | Lets complex match cases name helper values near the case. |
| Row/group scoped syntax | SQL/LINQ/dplyr/Polars | flow + binding | design-needed | May be necessary for readable table work, but must lower to verbs. |

## Admission Rules At Intersections

When a candidate touches multiple normal forms:

1. Name the primary normal form.
2. Show the expansion through existing syntax.
3. State which binding scope owns introduced names.
4. State whether failure skips, diagnoses, returns `Err`, or raises.
5. State how `explain` will show the generated operation.
6. Prefer library-first if the semantics can be expressed with ordinary calls.
7. Prefer a feature spec if it changes binding, control, failure, or
   diagnostics.

## Pass Notes

This pass intentionally stayed local. The next pass should do external
research for the candidate ideas above, prioritizing:

1. pattern functions / recognizers;
2. view patterns;
3. collection verb gaps (`scan`, `chunk`, `windowed`, `partition_map`);
4. row/group scoped syntax;
5. pipeline inspection/tap conventions.

Use official language references, standard library docs, or mature ecosystem
docs where possible. Fold the result back into `functions.md`, `patterns.md`,
`flow_and_collections.md`, and this map.
