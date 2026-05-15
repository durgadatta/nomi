# Syntax Synthesis Matrix

> Status: comparison evidence with design decisions folded into per-feature docs
> (May 2026). Many "Nomi recommendation" items are now design-settled in their
> respective convenience docs. This matrix remains the cross-language evidence
> for those decisions.
>
> Scope: documentation-only. This document broadens the language sample, groups
> near-equivalent syntax features by user need, and recommends how Nomi should
> combine them without becoming a feature collage.
>
> Consolidation note: keep this as comparison evidence. Stable decisions are
> folded into `review_and_roadmap.md` and the focused convenience docs. The
> 23-file deep dive research corpus backs the recommendations.

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
- Go, Cargo, Mix, npm, NuGet, Nix flakes, Maven: package management, module
  visibility, import paths, and supply-chain integrity models.
- Erlang/Elixir/Gleam (BEAM): supervision trees, let-it-crash, OTP patterns,
  and Gleam's `use` as a control-flow abstraction.
- Rustdoc, ExDoc, Python doctest, Sphinx, Go doc, Javadoc, TypeDoc: doc-as-test
  execution models, examples as assertions, diagnostic formats.
- gofmt, rustfmt, Prettier, Black, dart format, elm-format, Fourmolu: formatter
  design doctrines — config vs. no-config, output stability, shipping timeline.
- In-toto, Sigstore, SLSA, TUF, Go checksum DB, Dhall integrity checks:
  supply-chain attestation, content-addressed imports, and verifiable build
  provenance.
- Tree-sitter, Roslyn, rust-analyzer, tsserver, Dart LSP, ElixirLS:
  semantic token design, error recovery strategies, LSP architecture, and
  AI-readable representation choices.

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
| Code formatting | gofmt (no config), rustfmt (minimal config), Black (limited knobs), Prettier (opinionated), dart format (no config), elm-format (no config) | Configurable formatters create ecosystem forks; no-config formatters eliminate style debates. Every language that shipped a formatter late spent years on stylistic churn. | Ship `nomi fmt` from day 1. No configuration. Tabs. Canonical output on every save. The formatter is the style guide. |
| Supply-chain security | Go checksum DB, Nix fixed-output derivations, Dhall integrity checks, npm integrity hashes, Sigstore/SLSA attestation, TUF update framework | Some verify content at download; some attest build provenance; some sign packages. Each addresses a different link in the supply chain. | Content-addressed imports (`sha256:...`), domain-name import paths, no code execution during import, `nomi.lock` with transitive hashes. Attestation deferred to ecosystem layer. |
| Structured concurrency | Erlang/OTP supervision trees, Gleam `use`, Kotlin structured concurrency, Swift async/await with task groups, Python trio nurseries | Some are language keywords; some are library patterns; some couple concurrency to a function color. The key design fork is whether concurrency is a separate function family or a block policy. | Concurrency as block policies over `yield` — no second function color. Supervision, cancellation, and cleanup are callee-side policies. Defer channels/actors to library layer. |
| AI-readable semantics | Tree-sitter grammars, Roslyn green/red trees, rust-analyzer semantic tokens, tsserver program model, Dart LSP labels, ElixirLS semantic analysis | Some expose concrete syntax trees; some expose resolved semantics; some are lossy over whitespace. AI tools need different representations than human-facing diagnostics. | Ship Tree-sitter grammar and LSP from day 1. Semantic tokens layer over CST (not AST). Preserve source spans through all lowering passes. `explain` output is machine-readable by default. |

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
| gofmt, Black, Prettier, rustfmt, dart format | Some allow config; some forbid it. Configurable formatters create ecosystem forks and endless style debates. | No configuration. One canonical output. The formatter is the style guide — ship it day 1. |
| Checksum DB, TUF, npm integrity, Sigstore, SLSA | Some verify content at fetch; some attest build provenance; some sign packages at publish time. | Content-addressed imports for integrity at fetch. Build attestation deferred to ecosystem. No code execution during import. |

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
2. `data` for owned values, `Data.decode(...)` for external boundaries,
   `@secret`/`@pii` annotations for sensitive fields.
3. Pattern matching as the shared basis for `match`, if-let, guard-let, and
   destructuring.
4. One pipeline operator plus one placeholder family.
5. One block-call form for caller-side policy code — concurrency, resources,
   retries, and tracing are all block policies, not separate function colors.
6. `Result` as data before result propagation sugar. Three-story error taxonomy:
   absence (`?.`/`??`), expected failure (`Result` + `match`), unexpected error
   (exceptions).
7. Trace records as the substrate for diagnostics, examples, query plans, and
   boundary errors.
8. `nomi fmt` shipped day 1 — no config, tabs, canonical output on save.
9. Content-addressed imports with hash verification, domain-name import paths,
   no code execution during import.
10. Tree-sitter grammar + LSP from day 1, semantic tokens over CST,
    machine-readable `explain` output.

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
| Tier 1: surface sugar | Common, readable form with obvious desugaring and diagnostics. | `|>`, `_`, `??`, if-let, guard-let, `where`, equations, `nomi fmt` |
| Tier 2: library-first | Useful pattern that should prove itself as functions/data/block policy. | query plans, config merge, result pipelines, trace blocks, rank helpers, parallel collections |
| Tier 3: future layer | Powerful but likely to distort the first everyday language. | effect handlers, macros, ownership/regions, dense array notation, channels/actors |
| Tier 4: reject for now | Competing syntax for a need already served more coherently. | second placeholder family, separate `schema` peer to `data`, generic propagation for absence and errors, configurable formatter |

## Research Backlog

Focused follow-up passes should be small and comparative. Items marked ✓ have
deep-dive research completed; the decisions now live in per-feature convenience
docs and this matrix.

- **Adoption gap synthesis**: use
  [Language Direction And Gap Map](../language/language_direction_and_gap_map.md)
  to decide which syntax research supports first-hour learning, everyday data
  work, diagnostics, standard-library shape, and Python interop.
- **ML-family diagnostics**: compare OCaml/F#/Rust/Python match exhaustiveness,
  redundancy, guards, and error messages; extract diagnostics for Nomi match.
- **Structured pipeline vocabulary** ✓ — resolved in
  [table_and_flow_systems_deep_dive.md](../research/table_and_flow_systems_deep_dive.md)
  and folded into [flow_and_collections.md](flow_and_collections.md).
- **Boundary provenance** ✓ — resolved in
  [data_boundary_systems_deep_dive.md](../research/data_boundary_systems_deep_dive.md)
  and folded into [data_and_types.md](data_and_types.md).
- **Block policy semantics** ✓ — resolved in
  [cross_language_synthesis_master.md §4.5](../research/cross_language_synthesis_master.md)
  and [beam_languages_erlang_elixir_gleam.md](../research/beam_languages_erlang_elixir_gleam.md);
  folded into [concurrency.md](concurrency.md).
- **Tour regression**: after each accepted syntax decision, update
  [Target Language Tour](../language/target_language_tour.md) and remove any
  spelling that only works in an isolated snippet.
- **Placeholder discipline**: compare Scala `_`, Swift `$0`, Elixir `&1`,
  Clojure `%`, Kotlin `it`, and Haskell sections; finalize Nomi's implicit
  function scoping rule.
- **Formatter stability and CLI** — resolved in
  [formatting_and_style_deep_dive.md](../research/formatting_and_style_deep_dive.md).
  Spec-level decisions: no config, tabs, 100-char lines, shipped day 1.
- **Supply-chain integrity design** — resolved in
  [security_and_trust_deep_dive.md](../research/security_and_trust_deep_dive.md).
  Spec-level decisions: content-addressed imports, domain-name paths, `nomi.lock`,
  no code execution during import.
- **AI/tooling architecture** — resolved in
  [ai_readable_semantics_deep_dive.md](../research/ai_readable_semantics_deep_dive.md).
  Spec-level decisions: Tree-sitter + LSP from day 1, semantic tokens over CST,
  machine-readable `explain` output.
- **First-hour pedagogy design** — resolved in
  [first_hour_pedagogy_deep_dive.md](../research/first_hour_pedagogy_deep_dive.md).
  Awaiting implementation surface for validation.
- **Package management architecture** — resolved in
  [packaging_and_project_structure_deep_dive.md](../research/packaging_and_project_structure_deep_dive.md).
  Spec-level decisions: files-as-modules, `pub` visibility, optional `package.nomi`.

## Design Context

This matrix is a comparison tool — it surveys the design space so Nomi can
choose deliberately. For the rules that govern those choices and the process
for making them:

- [Syntax Design Rules](syntax_design_rules.md) — primitive budget, axis
  coherence, elimination form, and the other 5 concrete rules with nuance
  and conflict resolution.
- [Design Lessons and Integration §9](design_lessons_and_integration.md) —
  the synthesis methodology: stance → loop → worked examples → traps.
- [Language Foundation §Feature Admission Protocol](../language/language_foundation.md) —
  the 9 questions every syntax proposal must answer.
- [Language Degrees Of Freedom](../language/language_degrees_of_freedom.md) —
  the core/sugar/library/scoped/rejected ladder for classifying how much
  freedom a feature gets.
- [Language Design Dimensions §2 (Level 4)](../language/language_design_dimensions.md) —
  the 8 irreducible primitives that all syntax ultimately reduces to.

### Deep Dive Research (May 2026)

23 cross-language deep dives back the decisions in this matrix. Key dimensions:

- [Table and Flow Systems](../research/table_and_flow_systems_deep_dive.md) — collection verb vocabulary, query plans
- [Data Boundary Systems](../research/data_boundary_systems_deep_dive.md) — decode/validate/merge architecture
- [Security and Trust](../research/security_and_trust_deep_dive.md) — content-addressed imports, @secret/@pii, supply-chain integrity
- [Formatting and Style](../research/formatting_and_style_deep_dive.md) — no-config formatter doctrine, output stability
- [AI-Readable Semantics](../research/ai_readable_semantics_deep_dive.md) — Tree-sitter, LSP, semantic tokens
- [BEAM Languages](../research/beam_languages_erlang_elixir_gleam.md) — supervision, let-it-crash, structured concurrency
- [Packaging and Project Structure](../research/packaging_and_project_structure_deep_dive.md) — module visibility, import paths
- [Package Docs and Examples](../research/package_docs_and_examples_deep_dive.md) — doc-test execution models
- [Interactive Explanation](../research/interactive_explanation_deep_dive.md) — trace records, explain views
- [First-Hour Pedagogy](../research/first_hour_pedagogy_deep_dive.md) — onboarding, error message design

Full index: [Language Family Coverage Map](../research/language_family_coverage_map.md).
Capstone synthesis: [Cross-Language Synthesis Master](../research/cross_language_synthesis_master.md).

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
- gofmt design philosophy:
  <https://go.dev/blog/gofmt>
- Rustfmt configuration:
  <https://rust-lang.github.io/rustfmt/>
- Prettier philosophy:
  <https://prettier.io/docs/en/option-philosophy.html>
- Elm format (no config):
  <https://github.com/avh4/elm-format>
- Dart format:
  <https://dart.dev/tools/dart-format>
- Go checksum database:
  <https://go.dev/doc/modules/gomodref#checksum-database>
- Nix fixed-output derivations:
  <https://nix.dev/manual/nix/2.23/language/advanced-attributes>
- Dhall integrity checks:
  <https://docs.dhall-lang.org/tutorials/Language-Tour.html#sha256-integrity-checks>
- Sigstore:
  <https://www.sigstore.dev/>
- in-toto attestations:
  <https://in-toto.io/>
- Gleam `use` expressions:
  <https://gleam.run/language-reference/use-expressions/>
- Erlang/OTP supervision:
  <https://www.erlang.org/doc/design_principles/sup_princ>
- Tree-sitter:
  <https://tree-sitter.github.io/tree-sitter/>
- Semantic Tokens (LSP spec):
  <https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_semanticTokens>
- Elixir doctest:
  <https://hexdocs.pm/ex_unit/ExUnit.DocTest.html>
- Rust doc tests:
  <https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html>
