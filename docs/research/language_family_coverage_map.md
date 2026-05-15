# Language Family Coverage Map

> Status: source research map; not an active syntax spec.
>
> Scope: documentation-only. This document tracks which language families Nomi
> is learning from, what each family contributes, what it warns against, and
> where follow-up research should go.
>
> Consolidation note: use this file to check source-family coverage. Fold
> stable language decisions into `../convenience/syntax_synthesis_matrix.md`,
> `../convenience/review_and_roadmap.md`, or focused syntax docs.

## Purpose

Nomi's research should be broad without becoming encyclopedic. The point is not
to mention every language. The point is to sample enough traditions that Nomi's
design decisions are not accidentally provincial.

Use this map to answer:

```text
Which language experiences have we synthesized?
Which dimensions are under-covered?
Which lessons should become Nomi docs, examples, or feature specs?
```

For syntax-level grouping, see
[Syntax Synthesis Matrix](../convenience/syntax_synthesis_matrix.md). For the
adoption-facing steering layer, see
[Language Direction And Gap Map](../language/language_direction_and_gap_map.md).

## Coverage Table

| Family | Examples | Durable lessons | Nomi use | Caveat |
| --- | --- | --- | --- | --- |
| Python lineage | Python, Pydantic, Jupyter | Readability, indentation, batteries, notebooks, dynamic interop | Surface baseline, migration bridge, data-boundary inspiration | Runtime dynamism can hide boundary failures. |
| ML/Haskell lineage | ML, OCaml, F#, Haskell, Elm, Roc, ReScript | ADTs, pattern matching, type-shaped modeling, pipelines, purity pressure | `data`, `Result`, match, composition, coherent variants | Do not make everyday code feel scholastic. |
| Lisp/Scheme lineage | Lisp, Scheme, Racket, Clojure | Small core, code-as-data, macros, contracts, threading macros | explicit `quote:`, scoped expansion, contracts/diagnostics, flow ideas | Global macro power can destroy local readability. |
| BEAM lineage | Erlang, Elixir, Gleam | Pattern matching everywhere, result tuples, actors, supervision, pipe ergonomics | pattern/binding discipline, block/concurrency research, result conventions | Concurrency model should not dominate first-language learning. |
| Pragmatic typed app languages | Kotlin, Swift, Dart, C#, TypeScript | Null safety, data classes/records, extensions, async ecosystems, pattern growth | absence design, data ergonomics, extension caution, teaching syntax | Too many feature families can become a menu of local conveniences. |
| Systems safety languages | Rust, Zig, Go, Mojo, Swift systems layer | Result/error discipline, ownership/resource cleanup, defer/errdefer, explicitness | failure taxonomy, block cleanup policies, future capability/state model | Ownership and low-level performance concerns can distort Nomi's daily layer. |
| Object/message languages | Smalltalk, Ruby, Objective-C | Blocks/closures, message style, humane DSLs, object exploration | block calls, library-authored policies, interactive feel | Implicit receivers and open classes can reduce predictability. |
| Data/query languages | SQL, LINQ, dplyr, pandas, Polars, DuckDB | Declarative filtering, grouping, joins, lazy plans, backend lowering | collection/table verbs, query plans, `explain` | Query syntax can become a second language if not tied to flow. |
| Array languages | APL, J, K, Q, BQN, Uiua, Julia broadcasting | Whole-data thinking, rank/shape, dense transformation | future rank/shape functions, readable whole-array operations | Glyph density and tacit code are not the default Nomi style. See also [array_languages_deep_dive.md](array_languages_deep_dive.md) for rank polymorphism, trains, BQN combinators, Uiuia model. |
| Concatenative / stack languages | Forth, Factor, Joy, Kitten, Cat | Point-free composition, stack effect declarations, combinators (dip/dup/swap/bi), quotations | pipeline `\|>` and composition `>>` operators, block values, where: bindings | Stack shuffling as a daily programming model is too cognitive-load heavy. See [concatenative_languages.md](concatenative_languages.md) for full survey. |
| Numerical/scientific languages | Julia, R, MATLAB, Mathematica | Notebooks, broadcasting, multiple dispatch, symbolic/math workflows, formula interfaces | data notebooks, dispatch research, explicit symbolic boundaries, table column-name scoping | Domain power may conflict with general-purpose readability. See also [scientific_languages_r_matlab_julia.md](scientific_languages_r_matlab_julia.md) for R formulas, tidy eval, Julia broadcasting, MATLAB array model. |
| Shell/workflow languages | Bash, PowerShell, Nushell, Make, Just | Process orchestration, structured pipelines, tabular shell data | CLI/process standard library, structured flow, task fixtures | Shell convenience often relies on weak typing and stringly boundaries. |
| Configuration languages | CUE, Nickel, Pkl, Dhall, Nix, Terraform/HCL, JSON Schema | Declarative data, constraints, defaults, merge, provenance, reproducibility | explicit decode, config merge, field paths, redaction, package/build lessons | Config can become a separate field language unless folded into `data` and boundaries. |
| Proof/research languages | Coq, Lean, Idris, Agda, Koka, Eff, Flix, Unison | Effects, proofs, algebraic handlers, abilities, totality, typed holes | future capability/effect layer, examples as checks, explanation discipline | Proof and effect machinery must not be required for ordinary scripts. |
| Educational languages | Logo, Scratch, Racket teaching languages, BASIC, Pascal | First-hour success, visible state, simple errors, pedagogy | first-hour Nomi path and beginner diagnostics | Simplicity can become a ceiling if not layered. |

## Deep Dive Index

Individual-language and cross-cutting deep dives (May 2026 research expansion):

| File | Coverage | Lines |
|------|----------|-------|
| [array_languages_deep_dive.md](array_languages_deep_dive.md) | APL, J, K, Q, BQN, Uiua — rank polymorphism, trains, combinators | ~650 |
| [beam_languages_erlang_elixir_gleam.md](beam_languages_erlang_elixir_gleam.md) | Erlang, Elixir, Gleam — OTP, supervisors, pattern matching, pipe, `use` | ~1100 |
| [csharp_java_dart_modern_features.md](csharp_java_dart_modern_features.md) | C#, Java, Dart — pattern matching, records, null safety, async | ~1200 |
| [concatenative_languages.md](concatenative_languages.md) | Forth, Factor, Joy, Kitten, Cat — stack effects, combinators, quotations | ~400 |
| [diagnostics_and_explanations_comparative.md](diagnostics_and_explanations_comparative.md) | Rust, Elm, Racket, Swift, Scala 3, Clojure, Zig, TypeScript, Gleam, Python — 10-language diagnostic architecture | ~650 |
| [error_handling_defer_resource_cleanup_notes.md](error_handling_defer_resource_cleanup_notes.md) | Zig, Hylo, Odin, Gleam, Roc + Swift, Kotlin, Scala, Java, Python, C++, Haskell — 12-language error/defer/resource survey | ~1400 |
| [go_design_philosophy_deep_dive.md](go_design_philosophy_deep_dive.md) | Go — simplicity thesis, structural interfaces, goroutines, defer, zero values | ~870 |
| [modern_language_feature_survey.md](modern_language_feature_survey.md) | Mojo, Gleam, Roc, Hylo, Odin, Darklang, Verse, Koka, Unison — novel features | ~800 |
| [pattern_matching_synthesis.md](pattern_matching_synthesis.md) | Rust, Swift, Kotlin, Scala 3, OCaml, Haskell, F#, Elixir, Gleam, Racket — 10-language pattern matching synthesis | ~665 |
| [scientific_languages_r_matlab_julia.md](scientific_languages_r_matlab_julia.md) | R, MATLAB, Julia — formulas, tidy eval, broadcasting, array model | ~500 |
| [standard_library_design_comparative.md](standard_library_design_comparative.md) | Go, Rust, Python, Kotlin, Swift, Elixir, Zig, C#, Haskell, Racket — 10-language stdlib design | ~940 |
| [typescript_type_system_deep_dive.md](typescript_type_system_deep_dive.md) | TypeScript — type narrowing, structural typing, conditional types, `satisfies` | ~1040 |
| [cross_language_synthesis_master.md](cross_language_synthesis_master.md) | Capstone synthesis across all deep dives — convergences, forks, incompatibilities, Nomi resolution | ~1317 |
| [first_hour_pedagogy_deep_dive.md](first_hour_pedagogy_deep_dive.md) | Python, Go, Dart, Racket, Scratch, Logo, BASIC, Elm, Khan Academy, Swift Playgrounds — first-hour success design | ~1735 |
| [packaging_and_project_structure_deep_dive.md](packaging_and_project_structure_deep_dive.md) | Python, Cargo, Go modules, Mix, npm, NuGet, Nix flakes, Maven — manifest design, resolution, workspaces | ~1369 |
| [data_boundary_systems_deep_dive.md](data_boundary_systems_deep_dive.md) | Pydantic, CUE, Nickel, Pkl, Dhall, Terraform, JSON Schema, TypeScript, serde, Elm decoders — decode/validate/merge | ~1891 |
| [table_and_flow_systems_deep_dive.md](table_and_flow_systems_deep_dive.md) | SQL, LINQ, dplyr, Polars, DuckDB, Nushell, pandas, K/Q — verb vocabulary, query lowering, explain | ~2182 |
| [interactive_explanation_deep_dive.md](interactive_explanation_deep_dive.md) | Jupyter, Pluto, Darklang, Smalltalk, Racket, Light Table, Observable, Swift Playgrounds, Bret Victor, Elm debugger | ~1470 |
| [formatting_and_style_deep_dive.md](formatting_and_style_deep_dive.md) | gofmt, Black, Rustfmt, Prettier, elm-format, clang-format, Ormolu, dart format, zig fmt, ocamlformat | ~2033 |
| [package_docs_and_examples_deep_dive.md](package_docs_and_examples_deep_dive.md) | Rustdoc, ExDoc, Julia, Python/Sphinx, Racket Scribble, Go, Javadoc, TypeDoc, Literate Programming, Diataxis | ~2248 |
| [deployment_and_operations_deep_dive.md](deployment_and_operations_deep_dive.md) | Go, Python, Node/Deno/Bun, Docker, Serverless, Rust, Java/JVM, Nix/NixOS, Wasm, Homebrew | ~1303 |
| [security_and_trust_deep_dive.md](security_and_trust_deep_dive.md) | Nix, capabilities, secrets, supply-chain, sandboxing, memory safety, IFC, crypto hygiene, auth, redaction | ~1934 |
| [ai_readable_semantics_deep_dive.md](ai_readable_semantics_deep_dive.md) | LSP, typed ASTs, Tree-sitter, semantic tokens, code actions, proof traces, design fixtures, notebooks, expansion display, gradual typing | ~1826 |

## Under-Covered Dimensions

The current docs have strong coverage of syntax, constraints, blocks, patterns,
error handling, diagnostics, null safety, pattern matching, and stdlib design.
The following dimensions still need more focused research:

All eight previously under-covered dimensions are now researched (May 2026).
The deep dive index above covers the full matrix. Remaining work is consolidation:
folding stable decisions into `../convenience/` and `../language/` artifacts.

New research themes should be driven by implementation needs, not coverage gaps.

## Family Notes

### Python And Its Ecosystem

Python's lesson is not only syntax. Its success comes from a complete adoption
surface: readable code, library reach, teaching material, notebooks, a REPL,
package availability, and a culture of examples.

Nomi should keep Python as the migration bridge, but improve the places where
Python makes large programs fragile:

- external data becomes explicit `decode`;
- optional and failed values are not silently mixed;
- pattern and binding semantics are unified;
- transformations are easier to read left-to-right;
- diagnostics explain constraints and data boundaries.

### ML, Haskell, And Typed Functional Languages

These languages show how much clarity comes from making alternatives explicit.
Nomi should learn algebraic data, pattern matching, result values, composition,
and type-shaped thinking without copying visual density or theory-first
pedagogy.

The Nomi question is always:

```text
Can this help an ordinary program say what cases exist?
```

If yes, it may belong. If it mainly demonstrates type-system power, it should
remain future-layer research.

### Lisp, Racket, And Clojure

This family teaches regularity, homoiconic pressure, macros, contracts, and
threading forms. Nomi should preserve the insight that code can be data, but
only through explicit boundaries:

```nomi
quote:
    x + 0
```

Clojure-style threading strengthens Nomi's flow story, while Racket-style
contracts strengthen the explanation and boundary story. Macro freedom remains
fenced until expansion, source spans, and diagnostics are mature.

### Elixir, Erlang, And Gleam

The BEAM family shows pattern matching as an everyday binding operation and
supervision as a practical reliability model. Elixir's pattern reference
emphasizes shapes, guards, subset map matching, and predictable guard limits.
Gleam adds a typed result-oriented surface and `use`-style callback flattening.

Deep dive: [beam_languages_erlang_elixir_gleam.md](beam_languages_erlang_elixir_gleam.md) — OTP patterns,
let-it-crash philosophy, Erlang/Elixir/Gleam comparison tables, Nomi
Adopt/Refuse/Adapt decisions.

Nomi should extract:

- pattern plus guard as a normal form;
- result values as expected failure;
- pipes as readable flow;
- supervision/structured concurrency as later block-policy research.

### Kotlin, Swift, Dart, C#, And TypeScript

These languages show how mainstream languages absorb safety and functional
ideas incrementally: null safety, pattern matching, records/data classes,
extension methods, and async workflows.

Dart's sound null safety and pattern work are especially useful cautionary
pressure: absence is easier to reason about when nullability is visible and
flow analysis helps the programmer. C# shows that query syntax can coexist with
method chains because query expressions lower to ordinary operators, but it
also shows the complexity cost of supporting both surfaces.

Deep dives:
- [csharp_java_dart_modern_features.md](csharp_java_dart_modern_features.md) — C#/Java/Dart records, pattern matching, null safety, async models, cross-language convergence tables.
- [typescript_type_system_deep_dive.md](typescript_type_system_deep_dive.md) — type narrowing/flow typing, structural vs nominal, conditional types, `satisfies`, erased types, Nomi adopt/refuse decisions.

Nomi should extract:

- visible absence;
- pattern matching that scales gradually;
- records/data ergonomics;
- query syntax only if it lowers cleanly to flow verbs.

### Rust, Zig, Go, And Systems Pragmatism

Rust and Zig show the value of expected failure as data and explicit resource
cleanup. Go shows that a small language plus tooling, simple deployment, and a
large standard library can matter more than elegant syntax. Go's explicit error
returns are readable but can become repetitive; `defer` is simple and useful,
but cleanup and error handling interact subtly.

Deep dives:
- [go_design_philosophy_deep_dive.md](go_design_philosophy_deep_dive.md) — simplicity thesis, structural interfaces, goroutines/CSP, `defer` semantics, package design, zero values, adopt/refuse table.
- [error_handling_defer_resource_cleanup_notes.md](error_handling_defer_resource_cleanup_notes.md) — 12-language error handling survey spanning Zig/Hylo/Odin/Gleam/Roc + Swift/Kotlin/Scala/Java/Python/C++/Haskell.

Nomi should extract:

- expected failure is not the same as exception;
- cleanup should be policy-visible;
- standard tooling and deployment matter;
- ownership-style syntax is future research, not daily Nomi.

### SQL, LINQ, Dataframes, And Structured Pipelines

Real programs often transform collections and tables. LINQ is a useful warning
and inspiration: query syntax can be readable, but it must lower to a shared
operator vocabulary. Polars and DuckDB show the importance of lazy plans and
explanation.

Nomi should start with a shared vocabulary:

```text
where select derive group join sort window fold
```

Only after that vocabulary is stable should Nomi consider scoped query syntax.

### Config, Reproducibility, And Boundary Languages

CUE, Nickel, Pkl, Dhall, Nix, Terraform, and JSON Schema all show that
configuration is not "just dictionaries." It needs defaults, constraints,
documentation, merge, provenance, reproducibility, and precise diagnostics.

Nomi's key decision remains:

```text
config is a data-boundary problem, not a second data declaration language
```

`data`, constraints, `Data.decode(...)`, merge policies, and field provenance
should carry this work.

## Coverage Priorities

Completed (May 2026): All 8 priority dimensions are now researched. The research
corpus spans 23 deep-dive files covering language families, cross-cutting
design dimensions, and synthesis across 60+ language/system sources.

The next phase is consolidation into design artifacts:

1. **Fold decisions into convenience docs** — stable Adopt/Refuse/Adapt
   conclusions should migrate to `docs/convenience/` as design specs.
2. **Nomi feature specs** — where research identifies a clear Nomi primitive
   (e.g., `Secret[T]`, `explain`, query verbs), create a feature doc.
3. **Implementation priorities** — use research to sequence implementation:
   data boundaries first, then flow/pipeline, then interactive tooling.
4. **Revisit capstone synthesis** — update `cross_language_synthesis_master.md`
   with insights from the new deep dives.

## Source Links

- Dart null safety: <https://dart.dev/null-safety>
- Dart patterns: <https://dart.dev/language/patterns>
- Dart pattern types: <https://dart.dev/language/pattern-types>
- C# pattern matching: <https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/patterns>
- C# LINQ overview: <https://learn.microsoft.com/en-us/dotnet/csharp/linq/>
- C# standard query operators:
  <https://learn.microsoft.com/en-us/dotnet/csharp/linq/standard-query-operators/>
- Go Effective Go: <https://go.dev/doc/effective_go>
- Go errors wiki: <https://go.dev/wiki/Errors>
- Go language specification, defer:
  <https://go.dev/ref/spec#Defer_statements>
- Elixir patterns and guards:
  <https://hexdocs.pm/elixir/patterns-and-guards.html>
- Elixir pipe operator:
  <https://hexdocs.pm/elixir/Kernel.html#%7C%3E/2>
