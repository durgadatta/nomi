# Pattern Matching Research

> Status: consolidated design evidence for the registered pattern-matching
> pass. This document informs the target; it does not describe current
> implementation behavior.

## Pass Packet

- Research: `docs/research/pattern_matching.md`
- Canonical design: `docs/design/pattern_matching.md`
- Focused target: `docs/design/pattern_matching_target.nomi`
- Implementation bridge: `docs/review/pattern_matching.md`

The pass is registered in `config/design_passes.json`.

## Question

What is the smallest pattern system that lets Nomi express domain choice and
structural decomposition clearly while preserving exhaustiveness, atomic
bindings, deterministic evaluation, useful diagnostics, and a clean boundary
between inspection and validation?

The question is not whether Nomi can copy every pattern form from Python,
Scala, F#, or Racket. It is which mechanism remains understandable when used
for variants, collections, external values, guards, progressive typing,
multiple runtimes, and editor diagnostics at once.

## User Pressure

Patterns earn a core-language role from a small set of recurring jobs:

1. eliminate every case of a closed domain type;
2. inspect `Option` and `Result` without field or tag plumbing;
3. decompose nested products, tuples, lists, and maps;
4. classify a structurally known value while binding its useful parts;
5. express ordered exceptional cases before a general case;
6. make missing and unreachable cases visible to tools;
7. inspect an external `Value` before choosing a decoder or protocol path.

Patterns should not silently become parsing, arbitrary predicate dispatch,
validation, coercion, iteration, or method invocation. Those jobs have
different failure and effect stories.

## Cross-Language Evidence

### Closed algebraic data is the strongest center

OCaml, F#, Rust, Swift, Gleam, and sealed-type designs in languages such as
Kotlin all use closed alternatives to make structural elimination checkable.
The syntax differs, but the useful compiler questions converge: is the match
exhaustive, is an arm unreachable, and what bindings are available in the
selected arm?

Gleam also draws a useful line between irrefutable `let` decomposition and
refutable `case`: a `let` constructor pattern is accepted when the variant is
already known or the type has one variant. Swift's reference manual similarly
separates patterns that always match in bindings from patterns that may fail in
`switch` or conditional contexts.

**Nomi consequence:** closed nominal `data` is the primary pattern subject.
Ordinary binding patterns require static proof of irrefutability; refutable
choice belongs in `match`.

### Coverage and usefulness are one analysis problem

Luc Maranget's pattern-matrix work gives a practical common basis for
exhaustiveness, redundancy, and witness generation. Rather than treating these
as unrelated lints, a compiler asks whether adding a row contributes a value
not already covered. The same machinery can produce a missing example and
identify a useless arm.

This analysis is strongest over closed constructors and syntactic structural
patterns. It becomes conservative when arbitrary conditions or user code are
part of matching.

**Nomi consequence:** usefulness analysis is part of the initial semantic
contract, not future IDE polish. A wholly useless arm is an error. A
non-exhaustive match reports one or more witness patterns.

### Capture transactionality must be specified

Python's PEP 634 deliberately leaves partial bindings from failed matches
unspecified, while bindings from a successful `case` outlive the case suite.
That gives implementations freedom but makes local dataflow less predictable.
Rust scopes arm bindings to the guard and arm body. Functional languages also
normally present pattern variables as clause-local bindings.

**Nomi consequence:** all captures are tentative. Structural failure or guard
rejection discards every capture. Success exposes immutable captures only in
that arm. No capture leaks after `match`.

### Guards are applicability, not structure or validation

OCaml documents a guard as a condition tested after the pattern, at most once,
that may continue to the next case. Rust requires a Boolean guard but notes
that an or-pattern can cause the guard to execute more than once. Its compiler
also does not use guards as proof of exhaustiveness. Erlang restricts guards to
a defined guard expression subset and tests case clauses sequentially.

The examples agree on the role of a guard but expose a real fork in evaluation
freedom. Allowing arbitrary effects or repeated evaluation makes arm selection
observable in surprising ways.

**Nomi consequence:** `when` is a pure, deterministic `Bool` expression,
evaluated exactly once after the first successful structural alternative.
Guards refine applicability and never establish coverage. Constraints and
decode validation remain separate mechanisms.

### Ordered choice is useful policy

Python, Rust, OCaml/F#, Racket, and Erlang all try arms or clauses in source
order. This supports specific-before-general policies and is easy to explain.
The old Nomi corpus incorrectly suggested Erlang function clause order was not
guaranteed; Erlang's reference behavior is sequential.

**Nomi consequence:** the first applicable arm wins. Partial overlap is legal
and visible. A later arm with no possible new value is rejected as useless.

### Extensible patterns trade away semantic closure

Scala extractors invoke `unapply`/`unapplySeq`. F# active patterns run
user-defined recognizers. GHC view patterns apply a function before matching.
Racket supports predicates, applications, and match expanders, and explicitly
warns that embedded expressions may run in arbitrary order or more than once.

These mechanisms are powerful, especially for adapting representations that a
caller does not own. They also blur matching with calls, effects, allocation,
failure, and extension lookup. Coverage analysis must either trust declarations
or become conservative.

**Nomi consequence:** the initial core has no user extractors, active/view
patterns, predicate patterns, regex patterns, or match macros. A program calls
a pure normalization or parsing function first, obtains nominal data or
`Result`, and then matches that value. This keeps calls visible and patterns
closed.

### Rich context-specific syntax multiplies recognition paths

Dart deliberately permits patterns in declarations, assignments, loops,
`if-case`, switch statements and expressions, and collection control flow.
Swift permits refutable patterns in several conditional constructs. Rust adds
`if let`, `while let`, and related forms. These are credible ergonomic choices,
not mistakes.

For Nomi, however, the design goal is one visible answer to structural choice.
Adding every context creates several ways to recognize the same semantic act
and weakens the distinction between irrefutable binding and refutable choice.

**Nomi consequence:** `match` is the only refutable structural choice form.
There is no `case` keyword, `if let`, `while let`, `guard let`, pattern
parameter dispatch, or piecewise function syntax.

### Structural maps need visible openness

Python and Dart mapping patterns generally test named entries without requiring
the entire map to have exactly those keys. That is convenient for protocol
dispatch. Literal map syntax can nevertheless look like an exact shape, and
Nomi already treats openness at data boundaries as a fact worth exposing.

Python uses `*`/`**` for sequence and map capture, Dart uses `...` for a list
rest, and Rust/Gleam use `..` as a structural remainder. Nomi already reserves
`*` and `**` for arithmetic and rejects punctuation ranges in favor of
`range(...)`.

**Nomi consequence:** map patterns are exact by default. One pattern-only
marker works across collections: `..` accepts and ignores extra entries or
elements, while `..rest` captures them. This keeps `*`/`**` arithmetic-only.

## Convergences

The evidence supports these stable mechanisms:

- one subject evaluated once;
- ordered first-applicable arms;
- recursive structural patterns;
- `_` as a non-binding wildcard;
- immutable arm-local captures;
- alternatives that bind the same names and compatible types;
- guards evaluated after structural success;
- exhaustiveness and useless-arm diagnostics for closed spaces;
- an explicit catch-all for spaces the checker cannot finitely close;
- separate irrefutable binding and refutable choice contexts.

## Genuine Forks And Nomi Choices

| Fork | Credible alternatives | Nomi target |
| --- | --- | --- |
| Failed capture visibility | implementation freedom; leaked partial state; transactional rollback | transactional rollback |
| Successful capture scope | enclosing scope; arm scope | arm scope |
| Match completeness | expression only; statements may silently miss; every match exhaustive | every match exhaustive |
| Guard effects | arbitrary expression; restricted/pure subset | pure deterministic `Bool`, once |
| Extensibility | extractors/views/macros; closed built-ins | closed built-ins initially |
| Map openness | partial by default; exact by default | exact, explicit `..`/`..rest` |
| Refutable contexts | many convenience forms; one structural form | `match` only |
| Nonlinear captures | repeated name means equality; duplicate is error | duplicate is error, equality in guard |
| Unreachable arm | warning; error | compile-time error |
| Pattern validation | constraints inside patterns; guard; decoder | guard for applicability, decoder for validity |

## Rejected Initial Mechanisms

- **Class/type-test patterns:** Nomi's owned model is nominal `data`, not open
  inheritance. Foreign objects cross an interop boundary first.
- **User extractors and view patterns:** they hide calls and weaken coverage.
- **Predicate and regex patterns:** call a named parser/predicate, then match
  the returned nominal value or `Result`.
- **Range patterns:** comparisons in a `when` guard are explicit and avoid a
  second interval notation before Nomi has settled ranges generally.
- **AND patterns:** nested patterns and guards cover current uses without a new
  precedence rule.
- **Nonlinear captures:** `Pair(x, x)` hides an equality check. Write
  `Pair(left, right) when left == right`.
- **Refutable destructuring assignment:** failure is hidden in what looks like
  ordinary binding. Use exhaustive `match`.
- **Constraint patterns:** domain constraints validate construction/decode;
  they are not a reason to skip an arm silently.

## Remaining Bounded Experiments

The core decision is closed, but these syntax details should be tested with
real code before implementation promotion:

1. whether multi-field product and variant patterns remain positional or need
   a single named-field pattern form;
2. whether exact map patterns create excessive `..` noise in protocol-heavy
   programs;
3. how many missing witnesses diagnostics should show for nested patterns;
4. whether partially overlapping or-patterns with captures need an additional
   ambiguity diagnostic beyond deterministic left bias.

These experiments may refine `docs/design/pattern_matching.md`; they do not
justify reopening aliases or computational extractors. They are indexed as
question 16 in `docs/research/open_questions.md` so the focused packet does not
become a hidden second backlog.

## Primary Sources

- Luc Maranget, [Warnings for pattern matching](https://www.cambridge.org/core/journals/journal-of-functional-programming/article/warnings-for-pattern-matching/3165B75113781E2431E3856972940347), *Journal of Functional Programming*.
- Python, [PEP 634: Structural Pattern Matching - Specification](https://peps.python.org/pep-0634/).
- Rust, [Match expressions](https://doc.rust-lang.org/reference/expressions/match-expr.html) and [Patterns](https://doc.rust-lang.org/reference/patterns.html).
- OCaml, [Common pattern-matching errors](https://ocaml.org/docs/common-errors) and [A Tour of OCaml](https://ocaml.org/docs/tour-of-ocaml).
- F#, [Pattern Matching](https://learn.microsoft.com/en-us/dotnet/fsharp/language-reference/pattern-matching) and [Active Patterns](https://learn.microsoft.com/en-us/dotnet/fsharp/language-reference/active-patterns).
- Scala 3, [Option-less pattern matching and extractors](https://docs.scala-lang.org/scala3/reference/changed-features/pattern-matching.html).
- GHC, [Patterns](https://ghc.gitlab.haskell.org/ghc/doc/users_guide/exts/patterns.html) and [View patterns](https://ghc.gitlab.haskell.org/ghc/doc/users_guide/exts/view_patterns.html).
- Racket, [Pattern Matching](https://docs.racket-lang.org/reference/match.html).
- Erlang/OTP, [Pattern Matching](https://www.erlang.org/doc/system/patterns.html) and [Expressions](https://www.erlang.org/doc/system/expressions.html).
- Dart, [Patterns](https://dart.dev/language/patterns) and [Pattern types](https://dart.dev/language/pattern-types).
- Swift, [Patterns](https://docs.swift.org/swift-book/ReferenceManual/Patterns.html) and [Control Flow](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/controlflow/).
- Kotlin, [Sealed classes and interfaces](https://kotlinlang.org/docs/sealed-classes.html).
- Gleam, [Case expressions](https://tour.gleam.run/flow-control/case-expressions/), [List patterns](https://tour.gleam.run/flow-control/list-patterns/), [List recursion](https://tour.gleam.run/flow-control/list-recursion/), [Record pattern matching](https://tour.gleam.run/data-types/record-pattern-matching/), and the [Language Tour](https://tour.gleam.run/table-of-contents/).
