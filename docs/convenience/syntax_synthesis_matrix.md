# Syntax Synthesis Matrix

> Status: active research synthesis.
>
> Scope: documentation-only. This document broadens the language sample, groups
> near-equivalent syntax features by user need, and recommends how Nomi should
> combine them without becoming a feature collage.

## Purpose

Nomi should be pleasant because its surface is memorable, not because it copies
every pleasant feature from other languages. The right research move is:

```text
source language -> user need -> semantic difference -> Nomi normal form
```

This matrix complements [review_and_roadmap.md](review_and_roadmap.md) and
[expanded_language_research.md](expanded_language_research.md). It adds more
coverage from ML-family languages, Lisp-family languages, pragmatic modern
languages, shells, configuration languages, and numerical languages, then folds
their ideas back into Nomi's existing normal forms:

```text
binding
function
pattern
flow
block
absence/result
data boundary
explanation
```

For the large single-file stress test of these recommendations, see
[Target Language Tour](../language/target_language_tour.md). The tour should
change when this matrix changes, because syntax research is only useful if the
chosen forms still compose in a memorable whole program.

## Additional Source Coverage

This pass adds or sharpens pressure from:

- OCaml and F#: variants, exhaustive pattern matching, guards, pipelines, and
  function composition.
- Clojure and Racket: threading macros, nil-aware threading, pattern matching,
  contracts, and macro discipline.
- Scala 3: placeholder-function caution, extension methods, contextual
  parameters, and syntax simplification after Scala 2.
- Nim: uniform method-call syntax, command-call syntax, templates, macros, and
  indentation blocks as call arguments.
- Crystal: Ruby-like blocks, nilable type narrowing, `as?`, and expression
  control.
- Julia: `do` blocks, pipes, function composition, multiple dispatch, and
  explicit dot broadcasting.
- Nushell: structured pipelines over records and tables rather than text-only
  streams.
- Nix and Terraform/HCL: declarative records, scoped names, interpolation,
  dynamic blocks, splats, and the cost of too much generated structure.
- Racket contracts, CUE, Nickel, Pkl, Dhall, JSON Schema, and Pydantic-style
  systems: boundary validation, defaults, documentation, and error paths.

For a broader map of source-language families, adoption lessons, and
under-covered research dimensions, see
[Language Family Coverage Map](../research/language_family_coverage_map.md).

## Feature Families

| Need | Source-language forms | Nuanced difference | Nomi recommendation |
| --- | --- | --- | --- |
| Left-to-right value flow | F# `|>`, Elixir/Roc pipes, Clojure `->` and `->>`, ReScript/R placeholder pipes, Nim method-call syntax, Nushell pipelines | Some pipe into first argument, some into last, some into a placeholder, and shells carry streams or structured tables. | Keep one `|>` operator. Default to first-argument application. Use `_` when the value belongs elsewhere. Treat table/query flow as the same flow normal form over richer values. |
| Function composition | F# `>>`/`<<`, Haskell `.`, Julia `∘`, Elm/Roc composition | Composition builds a reusable function; pipelines apply a value now. Users confuse them when both are taught as "flow." | Keep composition separate from pipeline. Teach `|>` for data in hand and `>>>`/`<<<` or named `compose` for functions. |
| Callback flattening | Ruby blocks, Kotlin trailing lambdas, Swift trailing closures, Julia `do`, Nim indented call blocks, Gleam `use`, Python context managers | Some are just final callback sugar; some imply resource cleanup; some invert callback nesting. | Use one block-call normal form: ordinary call plus attached caller-side block, optionally with block parameters. Resource, retry, fixture, trace, and transaction are policies over the same form. |
| Conditional binding | Rust `if let`, Swift `guard let`, Crystal `if var`, Clojure `when-let`, Python walrus in `if`, ML `match` | Some test optional presence, some pattern-match variants, some merely narrow a local variable after a truthiness test. | Treat all successful conditional binding as pattern plus binding. Prefer `if pattern = value:` and `guard pattern = value:` over nil-specific forms. |
| Structural choice | OCaml/F#/Rust/Scala/Racket `match`, Python structural pattern matching, Elixir function clauses | Some languages make pattern matching the primary branch form; Python keeps it statement-like; Racket patterns are broad and macro-extensible. | Keep one pattern normal form for `match`, destructuring, if-let, guard-let, data variants, mapping/list patterns, and decoder fields. |
| Defaults and fallback | TypeScript `??`, Kotlin Elvis, Ruby `||=`, Terraform `null`, Clojure `or`/`some->`, Option defaults | Fallback can mean "missing only," "falsey," "failed result," or "omit this config field." | Reserve `??` for absence only. Do not let it catch `Err`, exceptions, or false values. Boundary defaults belong in data/decode diagnostics. |
| Expected failure | Rust `?`, Zig `try`, Roc/Gleam `Result`, Swift `throws`, Go `(value, err)`, Verse failure contexts | Some errors are data, some unwind the stack, some are speculative control with rollback. | Model expected failure as `Result` data plus patterns first. Add `?` only after propagation, conversion, and return constraints are specified. Keep speculative failure as a future block policy. |
| Cleanup and resources | Go/Zig/Swift `defer`, Python `with`, Julia `open(...) do`, Ruby blocks, transactions | `defer` is local scope exit; context managers acquire and release; transactions need commit/rollback diagnostics. | Keep small `defer` for local cleanup. Express resources, transactions, retries, and failure-only cleanup as block policies. |
| Data declaration | Python dataclasses, Kotlin/Swift data-like records, OCaml records/variants, TypeScript interfaces, CUE/Nickel contracts | Some construct owned values; some only describe external shape; some validate; some generate docs. | Use `data` for owned program values. Use `Data.decode(...)`, patterns, and binding constraints for external values. Avoid a peer `schema`/`shape` keyword in the first layer. |
| Configuration records | Nix attrsets, Terraform/HCL blocks and arguments, CUE unification, Nickel merge/contracts, Pkl typed config | Config wants defaults, merge, provenance, docs, redaction, and good field paths. Dynamic blocks can obscure intent when overused. | Make config a data-boundary problem: explicit decode, field provenance, merge policy, diagnostics. Keep generated/dynamic structure library-first. |
| Collection transforms | Python comprehensions, Haskell list comprehensions, LINQ, SQL, dplyr, pandas/Polars, Nushell table commands | Some are eager collections, some lazy query plans, some stream structured records, some optimize through planners. | Start with pipeline verbs over collections and plan values: `where`, `select`, `derive`, `group`, `join`, `sort`, `window`, `fold`. Add query syntax only if row/group binding needs it. |
| Array/rank computation | APL/J/K/Q adverbs, BQN/Uiua modifiers, Julia dot broadcasting, MATLAB/R vectorization | Dense glyphs are powerful but can dominate a language's visual culture. Julia's dot is explicit and general. | Prefer named shape/rank functions first. Consider explicit broadcasting syntax only after collection flow and diagnostics are strong. Do not make dense array notation the everyday default. |
| Implicit functions | Scala `_`, Kotlin `it`, Swift `$0`, Elixir `&1`, Clojure `%`, Haskell sections, Nim `it` templates | Each shorthand has a scope rule. Multiple shorthands quickly create memory burden. | Keep `_` for one obvious hole and `$1`, `$2`, `$name` for multi-hole clarity. Avoid adding `it` as another everyday spelling. |
| Local derivations | Haskell `where`, ML `let/in`, Nix `let/in`, Python assignment expressions, SQL CTEs | Some put definitions before use; some keep the main expression first; CTEs name intermediate query plans. | Keep `where` as expression-local explanation and reuse normal binding constraints inside it. Use pipeline stage names or plan values for complex data flows. |
| Metaprogramming | Lisp/Racket macros, Nim templates/macros, Scala inline, Terraform dynamic blocks, Julia macros | Macros can make elegant domain languages or create uninspectable private syntax. | Postpone global macros. Let normal forms, source spans, and desugaring explanations mature first. Prefer library functions, block policies, and explicit plan values. |
| Documentation as execution | Rust doc tests, Python doctest, Julia docstrings, Racket contracts, Darklang traces, examples in specs | Some test snippets; some enforce boundaries; some keep live values for debugging. | Make examples, trace records, and diagnostics one explanation story. Examples should be docs, tests, and anchors for `explain`. |

## Similar But Not Same

These features look interchangeable until the failure mode matters.

| Similar features | Key distinction | Recommended Nomi rule |
| --- | --- | --- |
| `?.`, `??`, `Option`, `Result`, exceptions | Missing value, expected failure, and unexpected failure are different user stories. | `?.`/`??` only handle absence. `Result` uses match/propagation. Exceptions remain exceptional. |
| `if-let`, `guard-let`, `match`, destructuring | They differ mainly in where code continues after success or failure. | Define them all as pattern attempts with tentative bindings and clear success/failure scope. |
| Pipeline, method chain, query block, shell pipe | They all read left-to-right, but their data model differs. | Use flow normal form. The value passed between stages may be a scalar, collection, table, stream, or query plan. |
| `do` block, trailing closure, context manager, fixture, transaction | The surface looks like callback sugar, but the callee's policy is different. | One block-call syntax; policy comes from the callee and trace records. |
| `data`, `schema`, `shape`, `contract`, interface | Owned construction, structural recognition, validation, and capability requirements are separate. | `data` constructs owned values. Patterns recognize structure. Constraints validate. Decoders cross boundaries. |
| `defer`, `finally`, `with`, `errdefer`, rollback | Some always run; some run only on error; some acquire resources first. | Keep `defer` small. Use named block policies for resource and rollback behavior. |
| Comprehensions, query `select`, splat, map/filter | They transform collections, but they expose different binding scopes. | Prefer pipeline verbs until a query form proves it improves row/group binding and explanation. |
| `_`, `$0`, `%`, `it`, operator sections | Shorthand is pleasant only while the reader can infer parameters instantly. | Use at most one primary placeholder family; require explicit `=>` once the transform is not tiny. |
| Macros, templates, decorators, annotations | Some transform syntax; some attach metadata; some wrap runtime behavior. | Decorators/annotations may remain ordinary metadata. Syntax-transforming macros are future layer. |

## Pleasant Syntax Principles

### 1. One Read Direction Per Expression

Nomi should avoid expressions that ask the reader to bounce between prefix,
postfix, implicit receiver, and placeholder rules in the same line.

Good:

```nomi
names =
    users
    |> where(_.active)
    |> select(_.name)
    |> sort
```

Risky:

```nomi
names = sort(select(where(users, _.active), _.name))
```

The second form is still legal as ordinary calls, but it should not be the
teaching style for transform-heavy code.

### 2. One Placeholder Family

Placeholder syntax should be a small convenience, not a second lambda language.

Recommended:

```nomi
_.name
$1 + $2
(x, y) => x + y
```

Avoid admitting all of these as everyday equivalents:

```text
_
it
$0
%1
&1
```

### 3. Visible Boundaries For Messy Inputs

External input should cross a named boundary before becoming trusted program
data.

```nomi
data SignupInput:
    email:str, contains(email, "@") else "Invalid email"
    age:int, age >= 13 else "Must be at least 13"

signup_input = SignupInput.decode(request.json)
```

This absorbs lessons from CUE, Nickel, Pkl, Dhall, Terraform, Nix, JSON Schema,
and Pydantic-like systems without creating a separate configuration language.

### 4. Sugar Must Explain Itself

Every pleasant form should have a normal-form expansion that tools can show.

```nomi
age = parse_int(raw)?
```

must be explainable as:

```nomi
match parse_int(raw):
    case Ok(value):
        value
    case Err(error):
        return Err(error)
```

Until that expansion is correct for return types, conversion, source spans, and
diagnostics, `?` remains design-needed.

### 5. Advanced Notation Gets A Fence

APL-family glyphs, macro systems, effect handlers, region systems, and
type-level computation are all valuable research pressure. They should not be
the first everyday surface. Nomi can later provide advanced layers if they
preserve the same explanation model.

## Recommended Combination For Nomi

The coherent bundle for the next design pass is:

1. Binding constraints everywhere a name is introduced.
2. `data` for owned values and `Data.decode(...)` for external boundaries.
3. Pattern matching as the shared basis for `match`, if-let, guard-let, and
   destructuring.
4. One pipeline operator plus one placeholder family.
5. One block-call form for caller-side policy code.
6. `Result` as data before result propagation sugar.
7. Trace records as the substrate for diagnostics, examples, query plans, and
   boundary errors.

Together, those choices allow pleasant code without adding isolated syntax:

```nomi
data Config:
    input:Path, exists(input)
    min_age:int, min_age >= 0 = 13

func import_people(raw_config:dict) -> Result[list[Person], Error]:
    config = Config.decode(raw_config)

    trace "import people":
        rows =
            read_csv(config.input)
            |> where(_.age >= config.min_age)
            |> select(Person.decode)

        match collect_results(rows):
            case Ok(people):
                return Ok(people)
            case Err(error):
                return Err(explain(error))
```

The syntax is pleasant because the same ideas recur:

- `Config.decode` is a data boundary;
- field annotations are bindings plus constraints;
- `|>` is flow;
- `_.age` is a small implicit function;
- `match` handles expected failure;
- `trace` is a block policy and explanation anchor.

The same bundle is exercised at larger scale in
[Target Language Tour](../language/target_language_tour.md), which should be
used as the coherence check before promoting a research idea into the everyday
syntax layer.

## Admission Ladder

Use this ladder when deciding whether research becomes syntax.

| Tier | Meaning | Examples |
| --- | --- | --- |
| Tier 0: core normal form | User-facing concept Nomi should teach directly. | binding, function, call, data, pattern, match, block, diagnostic |
| Tier 1: surface sugar | Common, readable form with obvious desugaring and diagnostics. | `|>`, `_`, `??`, if-let, guard-let, `where`, equations |
| Tier 2: library-first | Useful pattern that should prove itself as functions/data/block policy. | query plans, config merge, result pipelines, trace blocks, rank helpers |
| Tier 3: future layer | Powerful but likely to distort the first everyday language. | effect handlers, macros, ownership/regions, dense array notation |
| Tier 4: reject for now | Competing syntax for a need already served more coherently. | second placeholder family, separate `schema` peer to `data`, generic propagation for absence and errors |

## Research Backlog

Focused follow-up passes should be small and comparative:

- **Adoption gap synthesis**: use
  [Language Direction And Gap Map](../language/language_direction_and_gap_map.md)
  to decide which syntax research supports first-hour learning, everyday data
  work, diagnostics, standard-library shape, and Python interop.
- **ML-family diagnostics**: compare OCaml/F#/Rust/Python match exhaustiveness,
  redundancy, guards, and error messages; extract diagnostics for Nomi match.
- **Structured pipeline vocabulary**: compare Nushell, dplyr, Polars, SQL,
  LINQ, and Clojure transducers; define Nomi verbs and plan/explain behavior.
- **Boundary provenance**: compare CUE, Nickel, Pkl, Dhall, Terraform, Nix,
  JSON Schema, and Pydantic; specify field source paths, defaults, redaction,
  and merge diagnostics.
- **Block policy semantics**: compare Ruby blocks, Julia `do`, Nim block
  arguments, Swift trailing closures, Python context managers, Gleam `use`,
  and effect-handler research; specify `yield`, cancellation, and result flow.
- **Tour regression**: after each accepted syntax decision, update
  [Target Language Tour](../language/target_language_tour.md) and remove any
  spelling that only works in an isolated snippet.
- **Placeholder discipline**: compare Scala `_`, Swift `$0`, Elixir `&1`,
  Clojure `%`, Kotlin `it`, and Haskell sections; finalize Nomi's implicit
  function scoping rule.

## Source Links

- OCaml pattern matching:
  <https://ocaml.org/docs/basic-data-types>
- F# functions, pipeline, and composition:
  <https://learn.microsoft.com/en-us/dotnet/fsharp/language-reference/functions/>
- Clojure threading macros:
  <https://clojure.org/guides/threading_macros>
- Racket pattern matching:
  <https://docs.racket-lang.org/reference/match.html>
- Scala 3 syntax summary:
  <https://www.scala-lang.org/files/archive/api/3.7.3/docs/syntax.html>
- Nim method-call syntax:
  <https://nim-lang.org/2.0.0/manual.html#procedures-method-call-syntax>
- Nim code blocks as arguments:
  <https://nim-lang.org/docs/tut3.html#code-blocks-as-arguments>
- Crystal nil narrowing:
  <https://crystal-lang.org/reference/latest/syntax_and_semantics/if_var.html>
- Crystal `as?`:
  <https://crystal-lang.org/reference/latest/syntax_and_semantics/as_question.html>
- Crystal blocks and procs:
  <https://crystal-lang.org/reference/latest/syntax_and_semantics/blocks_and_procs.html>
- Julia functions, `do` blocks, pipe, and composition:
  <https://docs.julialang.org/en/v1/manual/functions/>
- Nushell pipelines:
  <https://www.nushell.sh/book/pipelines.html>
- Nix language basics:
  <https://nix.dev/tutorials/nix-language.html>
- Nix language constructs:
  <https://nix.dev/manual/nix/2.23/language/constructs>
- Terraform language overview:
  <https://developer.hashicorp.com/terraform/language>
- Terraform expressions:
  <https://developer.hashicorp.com/terraform/language/expressions>
- Terraform dynamic blocks:
  <https://developer.hashicorp.com/terraform/language/expressions/dynamic-blocks>
