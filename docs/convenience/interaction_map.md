# Global Feature Interaction Map

> Status: active synthesis note.
>
> Scope: cross-feature interaction and coherence control. This document maps
> the places where independently attractive language features collide, overlap,
> or reinforce one another. It does not add implementation work.

## Purpose

Nomi now has enough source-language research to make local feature design easy.
The harder problem is integration:

```text
many good features -> one teachable language
```

The focused docs answer local questions: functions, patterns, flow, blocks,
data, absence, and errors. This map answers the global question:

```text
When related features touch, which one owns the spelling, semantics, failure
mode, scope, and explanation?
```

A feature that sits between normal forms must not choose its spelling locally.
It should preserve the same normal-form story from every side.

## Global Integration Doctrine

The coherence rule is:

```text
user pressure -> related feature family -> one Nomi normal form -> one primary
surface -> explainable reduction
```

This avoids the common language-design failure where a language adopts several
individually pleasant features that become contradictory once combined.

| Design pressure | Related source ideas | Nomi owner | Integration rule |
| --- | --- | --- | --- |
| Name and check values | Type annotations, contracts, schemas, destructuring, imports, pattern captures | Binding | Every name introduction uses the same tentative-bind/check/commit model. |
| Express transformations | Lambdas, equations, holes, composition, methods, pipelines | Function + flow | Tiny transforms may be shorthand; nontrivial transforms get named parameters or named functions. |
| Choose by shape | Match, if-let, guard-let, variants, destructuring, extractors | Pattern | Conditional binding is pattern attempt plus scoped binding, not a separate optional/nil feature. |
| Move through many values | Pipelines, comprehensions, SQL/LINQ, dplyr, array/rank operations | Flow | Start with named verbs and plan values; syntax follows only when binding/explanation improve. |
| Describe work before running it | Symbolic expressions, lazy promises, query plans, rewrite rules, compiler IR | Flow + explanation | Ordinary code stays eager; `quote`, `describe`, `lazy`, and plan values are explicit boundaries with inspectable traces. |
| Attach caller code to policy | Ruby blocks, Kotlin/Swift trailing closures, Python context managers, Gleam `use`, fixtures | Block | One block-call form; policy comes from the callee, not from new keywords per use case. |
| Handle non-success | Option/null, Result/either, exceptions, validation failure, pattern failure | Absence/result + pattern + explanation | Missing, expected failure, unexpected failure, and mismatch stay distinct. |
| Trust external data | Pydantic, CUE, JSON Schema, Dhall, serde, config DSLs | Data boundary | Decode external values into owned `data`; no second schema/config language. |
| Understand behavior | Compiler errors, doctests, traces, query plans, notebook cells, AI-readable semantics | Explanation | Features must emit normal-form events with spans, paths, values, and redaction. |

The practical test is whether a feature can answer these six questions:

1. Which existing normal form owns it?
2. Which spelling is canonical when several source languages differ?
3. Which names does it introduce, and in which scope?
4. Does failure skip, return `none`, return `Err`, diagnose, or raise?
5. Can `explain` show the expansion and source path?
6. What attractive alternative is rejected to preserve coherence?

## Friction Patterns To Watch

These are the recurring conflicts that should trigger extra review before a
feature moves from research to spec-ready.

| Friction | Symptom | Coherent response |
| --- | --- | --- |
| Same need, many spellings | A proposal adds another way to bind, transform, filter, or handle missing values. | Pick the existing normal form spelling or deprecate the older one explicitly. |
| One spelling, many meanings | An operator handles absence, failure, pattern mismatch, and exceptions depending on context. | Split meanings even if the syntax is tempting. |
| Hidden scope | A placeholder, block parameter, row name, or context value resolves by invisible rules. | Require a visible binding site or a locally documented scoped form. |
| Second mini-language | Validation, config, query, templating, or tests get their own grammar. | Reduce to binding, functions, patterns, data, blocks, and explanation. |
| Local cleverness harms global taste | A feature is elegant in one family but changes the visual culture of ordinary code. | Keep it library-first or future-layer until the everyday surface stays calm. |
| Failure erasure | A form treats pattern failure, constraint failure, decode failure, and `Err` as interchangeable. | Preserve the distinction in diagnostics even when control flow skips. |
| Tooling opacity | A feature cannot show source spans, reductions, or trace events. | Keep it research-only or behind an explicit advanced boundary. |

## Community Voice Synthesis

The research corpus and integration critique show a consistent pattern in user
communities:

| Community signal | What people tend to praise | What people tend to regret | Nomi consequence |
| --- | --- | --- | --- |
| Python-like users | Readability, boring syntax, batteries, approachable errors. | Parallel standard-library choices, statement/expression splits, late migrations. | Keep first-hour syntax small; make ordinary IO/data tasks excellent before advanced notation. |
| ML/Rust/Swift users | Patterns, variants, exhaustiveness, value data, typed absence/failure. | Ceremony when simple scripts need heavy type machinery. | Use pattern/data/result clarity, but keep constraints gradual and examples concrete. |
| Ruby/Kotlin/Elixir/Gleam users | Blocks, pipes, callback flattening, readable policy code. | Magic receivers, DSL overreach, hidden scope. | Use block calls and pipelines with explicit parameters and explainable scopes. |
| Data/query users | Left-to-right transforms, named stages, table verbs, inspectable intermediate values. | Too many row scopes, stringly SQL, planner behavior hidden from source. | Use flow verbs and plan values first; make row/group binding a feature packet before syntax. |
| Config/schema users | Defaults, provenance, precise paths, safe boundaries. | Separate schema languages and code generation drift. | Treat config as decode into owned data with field paths, merge policy, and redaction. |
| Tooling/AI users | Stable format, spans, semantic tokens, expansions, examples as tests. | Macros or DSLs that only humans can infer after convention-learning. | Make reduction and `explain` machine-readable by design. |

This is not a popularity vote. It is friction evidence. A praised feature still
needs reduction into Nomi's normal forms; a regretted feature may still reveal
a real user need that Nomi should solve differently.

## One-Way Synthesis Table

For each related feature family, this table names the single Nomi path to
prefer. Focused docs can add detail, but should not fork these decisions.

| Related family | One Nomi way | Local caveat |
| --- | --- | --- |
| Type annotation, validation, contract, data field, import alias | Constrained binding | A constraint can be a type, predicate, or named checker, but the binding event is one operation. |
| Data class, record, struct, algebraic data type | `data` | External shape is decoded or matched; it is not another declaration family. |
| If-let, guard-let, destructuring, match case | Pattern attempt | Failure may skip or branch; diagnostics still know whether shape or constraint failed. |
| Lambda, hole, operator section, equation, composition | Function value | Holes are for tiny local transforms; named parameters win once scope matters. |
| Method chain, pipeline, query, collection transform | Flow through calls | Query syntax waits until row/group scope needs more than pipeline verbs. |
| Context manager, defer, transaction, retry, fixture, trace | Block policy | `defer` may stay small for local cleanup; richer policy uses block calls. |
| Optional chaining, null coalescing, Option | Absence-only access/default | `?.` and `??` do not catch `Err`, false, exceptions, or failed constraints. |
| Result, checked failure, parse/decode errors | `Result` plus pattern matching | A future `?` must expand to `match` and respect return constraints. |
| Exception, panic, impossible state | Unexpected error | Do not normalize these into ordinary `Result` without an explicit boundary. |
| Schema, config, CLI/env/JSON/CSV validation | Decode boundary | Boundary diagnostics carry path, source, provenance, and redaction metadata. |
| String interpolation, template, regex, path, URL, SQL, HTML | Typed string wrappers | f-strings are the one ordinary interpolation. `sql""`/`html""`/`re""`/`sh""` are a design direction for distinct typed values with per-target safety contracts. Paths and URLs are not strings. |
| Doctest, inline examples, trace, explain, query plan | Explanation event stream | Examples and traces should use the same semantic vocabulary as diagnostics. |
| Macro, template, quote, rewrite, domain notation | Future fenced reflection | No global syntax mutation in the first language. |
| Symbolic manipulation, lazy value, query plan, delayed backend execution | Explicit structural boundary | Keep `quote`, `describe`, `lazy`, and `collect` separate; all must feed `explain`. |

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
| Block + Result | Retry, transaction, resource, and fixture policies that can fail. | Block policy returns an ordinary value or `Result`; propagation remains explicit until specified. | Cleanup and rollback diagnostics must name whether failure came from body, policy, or cleanup. |
| Block + Data Boundary | Scoped authority for files, network, env, secrets, transactions. | `using`, `with_capability`, or similar policies pass checked resources into blocks. | Sensitive fields are redacted in traces by default. |
| Pattern + Result | Branch on expected failure and bind payloads. | `match result: case Ok(value): ... case Err(error): ...`. | `Err` payloads are data; exceptions are not silently converted. |
| Data + Explanation | Field construction, equality/display, redaction, examples. | `data` declarations produce construction and diagnostic events. | Display rules must not leak secret/PII fields. |
| Module + Binding | Imports introduce names. | Imports are binding events with explicit alias/export policy. | Bare global package names are avoided; domain import paths stay visible. |

## Local Interaction Clusters

The intersections above are easier to reason about in clusters. Each cluster
has one dominant owner and a local rule for conflict resolution.

### 1. Binding, Data, Pattern, Decode

This cluster owns names and trusted structure.

```nomi
data Person:
    name:str, len(name) > 0
    age:int, age >= 0

person = Person.decode(row)

match person:
    case Ok(Person(name, age)):
        ...
    case Err(problem):
        ...
```

Resolution:

- `data` constructs owned program values.
- `decode` crosses from external shape into owned value.
- patterns inspect owned or external structure.
- constraints judge bound values.
- diagnostics preserve whether the failure was missing field, wrong shape,
  failed constraint, or rejected variant.

Rejected local shortcuts:

- a peer `schema` language for config;
- nil-specific binding syntax that bypasses patterns;
- validation hooks that fire outside the binding event.

### 2. Function, Flow, Collections, Query

This cluster owns transformation.

```nomi
active_names =
    users
    |> where(_.active)
    |> select(_.name)
    |> sort
```

Resolution:

- pipeline applies a value now;
- composition builds a reusable function;
- `_` marks one obvious receiver;
- `=>` names parameters when scope matters;
- named functions carry domain logic;
- table/query/rank ideas begin as verbs and plan values.

Rejected local shortcuts:

- several pipeline operators for first/last/nil-aware/conditional threading;
- column shorthand that creates hidden row scope before row binding is designed;
- dense array notation as ordinary collection syntax.

### 3. Pattern, Result, Absence, Exceptions

This cluster owns non-success.

```nomi
email = user.profile?.email ?? "unknown"

match parse_int(raw_age):
    case Ok(age):
        ...
    case Err(problem):
        ...
```

Resolution:

- `none` means no value;
- `?.` and `??` are absence-only;
- `Result` means expected failure with payload;
- pattern failure means shape did not fit;
- constraint failure means shape fit but a value was unacceptable;
- exceptions mean unexpected failure unless explicitly caught at a boundary.

Rejected local shortcuts:

- one `?` that sometimes means optional access and sometimes expected failure;
- `??` catching false values, `Err`, exceptions, or decode failure;
- pattern matching that erases constraint-failure diagnostics.

### 4. Block, Resource, State, Capability

This cluster owns time-shaped control and authority.

```nomi
using(open(path)) -> file:
    text = file.read()

retry(3, on=NetworkError):
    fetch(url)
```

Resolution:

- block calls are ordinary calls plus caller-side code;
- the callee owns policy and invokes the block with `yield`;
- resource, retry, transaction, fixture, trace, and future concurrency policies
  reuse this shape;
- authority to touch files, network, clocks, subprocesses, or secrets should be
  visible in the policy or value being passed.

Rejected local shortcuts:

- one keyword per control policy;
- async/sync function color in the first everyday language;
- hidden ambient authority that cannot be traced.

### 5. Explanation, Examples, Tooling, AI

This cluster owns understanding.

```nomi
explain:
    rows |> select(Person.decode) |> collect_results
```

Resolution:

- every feature emits normal-form events;
- examples, traces, decode errors, constraint failures, and query plans share
  vocabulary;
- source spans survive parsing, lowering, desugaring, and evaluation;
- secret and PII values redact by default.

Rejected local shortcuts:

- macros or generated syntax that cannot show an expansion;
- diagnostics that report implementation internals instead of user concepts;
- examples that are documentation only and cannot become checks.

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
| Decode provenance policy | CUE/Nickel/Pkl/Pydantic/serde | data boundary + explanation | design-needed | Needed before config, CSV, API, and CLI data can diagnose consistently. |
| Failure taxonomy feature spec | Rust/Zig/Swift/Gleam/Python | absence/result + explanation | design-needed | Prevents `none`, `Err`, exceptions, pattern failure, and constraints from blurring. |
| Block policy prelude | Ruby/Kotlin/Swift/Gleam/Python context managers | block + result + explanation | library-first | Establishes `using`, `retry`, `transaction`, `trace`, and `test` as ordinary policies. |
| Capability values | Pony/OCap systems, effect systems, Go contexts, OS handles | block + data boundary + explanation | research-only | Makes world-touching authority visible without type-theory weight in the first layer. |
| Explanation event schema | Rust/Elm diagnostics, Darklang traces, notebooks, LSPs | explanation | prototype-ready as design doc | Gives all features a shared output contract for tools and AI. |

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
8. Record the rejected nearby spellings so future passes do not reopen them by
   accident.

## Promotion Targets

The next coherent specs should be written in this order because each one
unblocks several local feature families:

| Target spec | Why it comes next | Source anchors |
| --- | --- | --- |
| Failure taxonomy | `none`, `Result`, exceptions, pattern failure, and constraint failure affect every other feature. | `absence_and_result.md`, `design_lessons_and_integration.md`, `language_direction_and_gap_map.md` |
| Data decode boundary | Config, JSON, CSV, HTTP, CLI, env, and table rows all need one trusted boundary. | `data_and_types.md`, `binding_constraints_feature.md`, `data_boundary_systems_deep_dive.md` |
| Explanation event model | Diagnostics, examples, traces, query plans, and AI tooling need the same semantic event vocabulary. | `meta_testing.md`, diagnostics and interactive research, `spec_readiness_map.md` |
| Collection/table verb vocabulary | Pipelines, query, row/group scopes, and data work need stable verbs before syntax. | `flow_and_collections.md`, `structured_collections_query_language.md`, table/flow research |
| Block policy prelude | Resource, retry, transaction, trace, fixtures, and future concurrency should share one block-call story. | `block_calls_feature.md`, `concurrency.md`, error/resource research |

## Pass Notes

This pass promotes the map from local convenience interactions to global
feature integration. The next pass should refine the promotion targets above
into feature packets, prioritizing:

1. failure taxonomy;
2. data decode boundary;
3. explanation event model;
4. collection verb gaps (`scan`, `chunk`, `windowed`, `partition_map`);
5. row/group scoped syntax;
6. pattern functions / recognizers;
7. pipeline inspection/tap conventions.

Use existing deep dives first. If new research is needed, prefer official
language references, standard library docs, or mature ecosystem docs. Fold the
result back into focused feature specs, `functions.md`, `patterns.md`,
`flow_and_collections.md`, `absence_and_result.md`, `data_and_types.md`, and
this map.
