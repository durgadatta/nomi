# Cross-Language Synthesis: The Capstone

> Status: capstone research synthesis.  This document draws on all 13 research
> files in `docs/research/` and the active Nomi design docs to produce a single
> decision surface.  It names what every language family converges on, what
> genuinely cannot be unified, what breaks when features combine, and how Nomi
> resolves each tension into a coherent design.
>
> Companion docs: [Language Foundation](../language/language_foundation.md)
> (canonical design), [Language Design Dimensions](../language/language_design_dimensions.md)
> (axes of variation), [Design Lessons & Integration](../convenience/design_lessons_and_integration.md)
> (integration rules), [Syntax Synthesis Matrix](../convenience/syntax_synthesis_matrix.md)
> (feature-family mapping).

## Table of Contents

1. [Universal Convergences](#1-universal-convergences)
2. [Genuine Design Forks](#2-genuine-design-forks)
3. [Hidden Incompatibilities](#3-hidden-incompatibilities)
4. [The Nomi Synthesis](#4-the-nomi-synthesis)
5. [Design Decision Record](#5-design-decision-record)
6. [Risks and Open Questions](#6-risks-and-open-questions)

---

## 1. Universal Convergences

These are features where 7+ languages from different families independently
arrived at the same semantics, even when the surface syntax differs.  They
represent genuine discovery, not fashion.  A new language that omits them must
have a deliberate reason — they are not optional.

### 1.1 Data Classes / Records / Value Types

Every modern language has converged on nominal product types with structural
equality, typically carrying field-level validation:

| Language | Spelling | Structural equality | Validation | Year added |
|----------|----------|---------------------|------------|------------|
| Kotlin | `data class` | Yes (compiler-generated) | `init` block | 1.0 (2016) |
| Java | `record` | Yes | Compact constructor | 14 (2020) |
| C# | `record` / `record struct` | Yes (value-based) | `init` only | 9.0 (2021) |
| Swift | `struct` | Yes (value type) | Property wrappers | 1.0 (2014) |
| Dart | `class` with `==` override | Manual | Constructor asserts | 3.0 |
| Python | `@dataclass` | Manual opt-in | `__post_init__` | 3.7 (2018) |
| Rust | `struct` + `#[derive(Eq)]` | Opt-in derive | Builder or `new` | 1.0 (2015) |
| Scala 3 | `case class` | Yes | `require` in body | 3.0 (2021) |
| TypeScript | `interface` / `type` | Structural (not nominal) | N/A (compile-time) | — |

**What converged:** Named fields, value-based equality as the default for
product types, field-level validation, and immutability as the preferred
default (though enforcement varies).

See: `csharp_java_dart_modern_features.md` §2 (records/data classes across
C#/Java/Dart), `typescript_type_system_deep_dive.md` §3 (structural vs nominal
interfaces).

**Nomi translation:** `data` declarations with constrained fields.  Nomi takes
the Kotlin/Swift/Rust path (nominal, value-semantic, field-level constraints)
and rejects the TypeScript path (structural, compile-time-only).  No separate
`class`, `struct`, `record`, and `dataclass` keywords — one `data` for all
owned product and sum types.

### 1.2 Pattern Matching + Exhaustiveness

Pattern matching moved from ML-family specialty to universal expectation within
a decade:

| Language | First release with match | Exhaustiveness | Guards | Destructuring |
|----------|------------------------|----------------|--------|---------------|
| SML/OCaml | 1980s | Yes | `when` | Yes |
| Haskell | 1990 | Yes | `\|` guards | Yes |
| F# | 2005 | Yes | `when` | Yes |
| Scala | 2004 | Sealed only | `if` | Yes |
| Rust | 2015 | Yes | `if` | Yes |
| Swift | 2014 | Yes | `where` | Yes |
| Kotlin | 1.0 | Limited (sealed) | `if` | Yes |
| C# | 7.0-12.0 | Limited (sealed) | `when` | Yes |
| Python | 3.10 | No (catch-all required) | `if` | Yes |
| Dart | 3.0 | Sealed only | `when` | Yes |
| Elixir | 1.0 | Warning on open | `when` | Yes |

**What converged:** The `match`/`case` structure, destructuring bindings inside
patterns, guards as boolean filters on matched values, and exhaustiveness
checking for closed type families (sealed classes / ADTs).

See: `pattern_matching_synthesis.md` §2 (structural convergence), §3 (semantic
differences), §4 (feature matrix); `beam_languages_erlang_elixir_gleam.md`
§3 (pattern matching evolution across BEAM).

**Nomi translation:** `match` as the single structural-choice form.  Nomi
accepts exhaustiveness checking for nominal `data` variants and structural
matching for external values.  It rejects making `match` a statement (Python's
mistake) or adding `switch`/`case` as a parallel keyword family.

### 1.3 Option/Maybe Types (Null Safety Through the Type System)

Every statically-typed language since 2014 has converged on representing
absence through the type system rather than a universal null:

| Language | Mechanism | Type | Safe access |
|----------|-----------|------|-------------|
| Haskell | `Maybe a` (1990) | `data Maybe a = Nothing \| Just a` | `case` / `fmap` |
| Rust | `Option<T>` (2015) | `enum Option<T> { None, Some(T) }` | `match` / `?` / combinators |
| Swift | `T?` (2014) | Sugar for `Optional<T>` | `if let` / `guard let` / `?.` |
| Kotlin | `T?` (2016) | Compiler-level nullable | `?.` / `!!` / `?:` |
| C# | `T?` (8.0, 2019) | `Nullable<T>` | `?.` / `??` / `!` |
| Dart | `T?` (3.0, 2023) | NNBD type system | `?.` / `??` / `!` |
| TypeScript | `T \| undefined` | Union type | `?.` / `??` / `!` |
| Scala 3 | `Option[T]` | `enum Option[T] { case Some, case None }` | `match` / `map` |
| Zig | `?T` | Nullable type | `if (opt) \|v\| ...` / `orelse` |
| OCaml | `'a option` | `type 'a option = None \| Some of 'a` | `match` |

**What converged:** Absence is a type-level property, not a runtime sentinel
value.  Postfix `?` for nullable syntax.  `?.` for short-circuit property
access.  `??` / `orElse` / `unwrap_or` for default values.  Pattern matching
as the general deconstruction mechanism.

See: `csharp_java_dart_modern_features.md` §3 (null safety across C#/Java/Dart
with comparison matrices), `typescript_type_system_deep_dive.md` §2
(discriminated unions), `error_handling_defer_resource_cleanup_notes.md` §4
(Rust/Haskell/Swift/Kotlin option types).

**Nomi translation:** `none` as the absence value (not `null`, not `None`, not
`nil`, not `undefined`).  `?.` and `??` for absence short-circuit.  `Result`
for expected failure.  Three distinct stories, never conflated.

### 1.4 Result/Either Types (Expected Failure as Values)

Every language that adopted Option types naturally extended the pattern to
expected failure:

| Language | Result type | Propagation | Error payload |
|----------|-------------|-------------|---------------|
| Rust | `Result<T, E>` | `?` operator | Arbitrary `E: Error` |
| Haskell | `Either e a` | `do` / `>>=` | Arbitrary `e` |
| Swift | `Result<T, E>` + `throws` | `try` / `try?` / `try!` | `E: Error` |
| Kotlin | `Result<T>` (stdlib) | `getOrThrow` / `fold` | `Throwable` (regrettably) |
| OCaml | `('a, 'e) result` | `let*` (binding operator) | Arbitrary `'e` |
| Zig | `!T` / error union | `try` / `catch` | Error set |
| Go | `(T, error)` | `if err != nil` | `error` interface |
| Scala 3 | `Either[E, T]` | `for` comprehension | Arbitrary `E` |
| Gleam | `Result(a, e)` | `use` + `try` | Arbitrary `e` |
| Roc | `Task a e` | `!` / `?` / `try` | Tag union |

**What converged:** Expected failure is data (a tagged union), not a non-local
control transfer.  Pattern matching deconstructs it.  A short propagation
operator (`?`, `try`, `!`) reduces boilerplate.  Errors carry structured
information, not just strings.

See: `error_handling_defer_resource_cleanup_notes.md` §2 (Zig error sets,
Hylo ownership errors, Odin `or_return`), §3 (Gleam `use`/`try`, Roc tag
unions, Swift typed throws), `beam_languages_erlang_elixir_gleam.md` §4
(error handling across BEAM), standard-library-design-comparative.md §4
(error types in stdlib).

**Nomi translation:** `Result[T, E]` as a `data` type.  `match` for
deconstruction.  `?` propagation deferred until `Result` patterns are
validated by real usage.  Never conflate `Result` with `Option` — they
are semantically different operations (see §3.3).

### 1.5 Expression-Oriented Conditionals

Languages that started with statement-only `if` have all moved toward
`if`-as-expression:

| Language | `if` as expression | `match` as expression | Block returns last value |
|----------|-------------------|----------------------|--------------------------|
| Rust | Yes | Yes | Yes |
| Kotlin | Yes | Yes | Lambda only |
| Scala | Yes | Yes | Yes |
| Swift | Partial (closure only) | Yes | Yes (implicit return) |
| Python | No (`x = a if cond else b`) | No (statement) | No |
| Go | No | No | No |
| C# | No (ternary only) | No (statement, 8.0+) | No |
| Dart | No (ternary only) | No (statement) | No |
| OCaml | Yes | Yes | Yes |
| Haskell | Yes | Yes | N/A (single expression) |
| Elixir | Yes | Yes (via clauses) | Yes |
| Julia | Yes | N/A (multiple dispatch) | Yes |

**What converged:** The ML-family expression orientation is winning.  `if`
returns a value.  `match` returns a value.  Blocks return their last
expression.  C-family languages that resist this (Go, C, C++) are the
holdouts.

See: `go_design_philosophy_deep_dive.md` §4 (Go's deliberate statement
orientation), `beam_languages_erlang_elixir_gleam.md` §5 (expression
orientation across BEAM), `pattern_matching_synthesis.md` §3.4 (match as
expression vs statement).

**Nomi translation:** Everything is an expression — `if`, `match`, blocks,
pipelines.  Nomi takes the ML/Rust/Kotlin path and rejects the C/Go/Python
statement/expression split entirely.

### 1.6 Pipeline Operators (Left-to-Right Data Flow)

Languages from shell, functional, and data-science families independently
converged on left-to-right threading for readability:

| Language | Operator | Threads into | Year |
|----------|----------|-------------|------|
| Elixir | `\|>` | First argument | 1.0 (2014) |
| F# | `\|>` | Last argument (convention) | 2005 |
| Julia | `\|>` | First argument | 1.0 (2018) |
| R | `%>%` (magrittr) | First argument | 2014 |
| Gleam | `\|>` | First argument | 1.0 (2024) |
| Roc | `\|>` | First argument | (pre-release) |
| Nushell | `\|` | Structured record | 2019 |
| Clojure | `->` / `->>` | First / last | 2007 |
| ReScript | `->` | Placeholder `_` | 2020 |
| OCaml | `\|>` (4.14+) | First argument | 2022 |

**What converged:** Left-to-right reading order for data transformations.
Single operator (not a family of threading macros).  First-argument
threading is the dominant convention.

What did NOT converge: composition vs application (pipeline applies now,
composition builds a reusable function).  Placeholder position (first
arg vs last arg vs explicit `_` hole).  Table-vs-scalar semantics
(shells thread text, functional languages thread values, data languages
thread tables).

See: `beam_languages_erlang_elixir_gleam.md` §6 (Elixir pipe philosophy),
`scientific_languages_r_matlab_julia.md` §2 (Julia broadcasting and pipes),
`array_languages_deep_dive.md` §4 (rank-polymorphism vs broadcasting in
arrays), `syntax_synthesis_matrix.md` §Feature-Families (pipeline).

**Nomi translation:** One `|>` operator.  Default first-argument threading.
`_` placeholder when the argument position is not first.  Composition
`>>>` / `<<<` as a separate concept.  Nomi explicitly rejects Clojure's
`->`/`->>` family (too many threading macros for one concept) and Nushell's
text-stream model (pipelines carry typed values, not byte streams).

### 1.7 Deterministic Resource Cleanup

Every language has converged on scope-based, deterministic cleanup
(not GC finalizers, not `__del__`):

| Language | Mechanism | Error-only variant | Scope |
|----------|-----------|-------------------|-------|
| Go | `defer` | No (always runs) | Function |
| Zig | `defer` + `errdefer` | `errdefer` | Block/function |
| Swift | `defer` | No (always runs) | Scope |
| Python | `with` statement | `__exit__` receives exc | Block |
| C# | `using` statement | No | Block |
| Java | try-with-resources | No | Block |
| Kotlin | `use` extension | No | Block |
| Rust | `Drop` trait (RAII) | No (always runs) | Scope exit |
| C++ | RAII / destructors | No (always runs) | Scope exit |
| D | `scope(exit)` / `scope(failure)` | `scope(failure)` | Scope |
| Nim | `defer` | No | Scope |
| Gleam | `use` expression | No | Block |
| Ruby | block with ensure | No | Block |
| Odin | `defer` | `or_return` (partial) | Scope |

**What converged:** Cleanup attached to lexical scope, not runtime lifetime.
`defer` (register cleanup to run on scope exit) and context-manager (acquire
resource, run body, release) are the two dominant models.  Zig's `errdefer`
(error-only deferred cleanup) is the most praised innovation in this space.

See: `error_handling_defer_resource_cleanup_notes.md` §1 (Zig `try`/`errdefer`),
§5 (Swift `defer`/`throws`, Kotlin `use`, C# `using`), §7 (Haskell `bracket`,
C++ RAII), `modern_language_feature_survey.md` §3 (D `scope`, Jai `using`,
Wren fibers).

**Nomi translation:** `defer` for local scope-exit cleanup.  Block policies
(`using`, `retry`, `transaction`) for resource acquisition/release with
structured diagnostics.  `errdefer` as a library block policy, not syntax.
Nomi accepts the lexical-scope model, rejects GC-finalizer approaches,
and makes block policies the composable primitive.

### 1.8 Structured Diagnostics (Error Messages as a Design Discipline)

The quality bar for compiler/interpreter diagnostics has permanently risen,
led by Rust, Elm, and Gleam:

| Language | Diagnostic quality | Source spans | Error codes | FixIts | blame |
|----------|-------------------|--------------|-------------|--------|-------|
| Rust | Gold standard | Yes | `E0001` etc. | `rustc --explain`, `cargo fix` | Borrow checker blame |
| Elm | Excellent | Yes | No (prose) | No | Type mismatch narrowing |
| Gleam | Excellent | Yes | No (prose) | No | Type diff formatting |
| Swift | Very good | Yes | FixIts in Xcode | Yes | — |
| Scala 3 | Good | Yes | Some | Some | Implicit resolution |
| TypeScript | Good | Yes | Numeric codes | Quick fix | Type narrowing |
| Python 3.10+ | Improving | Partial | No | No | Match redundancy |
| Zig | Good | Yes | No | No | Comptime traces |
| Go | Adequate | Yes | No | No | — |
| Clojure | Poor | Optional | No | No | Stack traces |
| Haskell | Improving | GHC 9.x | `-fdefer-type-errors` | HLS | Unification errors |
| C++ | Poor (pre-concepts) | Yes | Template backtrace | No | SFINAE |

**What converged:** Error messages report what the user wrote, not compiler
internals.  Source spans point to the exact location.  Structured messages
with sub-diagnostics (primary + secondary labels).  Machine-readable error
codes for tooling.  FixIts (suggested corrections) as a standard feature.

See: `diagnostics_and_explanations_comparative.md` (10-language diagnostic
architecture comparison), `modern_language_feature_survey.md` §5 (Darklang
trace-driven development, Unison structured diagnostics).

**Nomi translation:** Explanation as a first-class normal form.  Trace
records carry source spans from parse time.  Diagnostics speak in
normal-form vocabulary ("binding failed its constraint" not internal
error names).  `explain` as a user-facing operation.  Nomi accepts the
Rust/Elm standard as the target and rejects the "stack trace is enough"
minimalism of Go and Clojure.

---

## 2. Genuine Design Forks

These are choices where languages made irreconcilable decisions — not
convergence toward one answer but a genuine fork where both branches
have working languages with different tradeoffs.  Nomi must pick a
branch and live with the consequences.

### 2.1 Structural Typing vs Nominal Typing

The deepest fork in type systems, dividing languages at the identity level:

| Branch | Languages | "X is a User" means... | Extensibility | Exhaustiveness |
|--------|-----------|----------------------|---------------|----------------|
| Nominal | Java, Rust, Haskell, Swift, Kotlin, C#, OCaml | X was declared as User | Closed: only author adds variants | Possible |
| Structural | TypeScript, Go (interfaces), OCaml (objects), C++ (templates) | X has the same shape as User | Open: any module can satisfy | Impossible |

TypeScript proves structural typing works at scale.  Rust and Haskell
prove nominal typing with exhaustiveness is invaluable.  The two cannot
be reconciled: if types are structural, a function can never know all
callers (open world), so it can never prove it handled all cases.

See: `typescript_type_system_deep_dive.md` §3 (structural typing in
TypeScript, deliberate omissions), `language_design_dimensions.md` §3.2
(type discipline axis), `pattern_matching_synthesis.md` §3.5 (structural
vs nominal in pattern matching).

**Nomi's choice: Nominal `data` for owned types.  Structural matching for
external recognition.**  This is the bifurcated approach: close the world
for types you define (exhaustiveness possible), open it for values you
receive (extensibility retained).  Nomi explicitly rejects TypeScript's
"structural by default" and Go's "structural-only interfaces."  See
[Language Design Dimensions §5](../language/language_design_dimensions.md)
for the Expression Problem analysis that motivates this split.

### 2.2 Checked vs Unchecked Exceptions

Java bet on checked exceptions (every exception must be declared or caught).
The industry verdict is in: checked exceptions lost.

| Branch | Languages | Cost | Benefit |
|--------|-----------|------|---------|
| Checked | Java (partially), Swift (typed throws) | Method signatures grow; wrapping proliferates | Compiler verifies handling |
| Unchecked | Python, C#, Kotlin, Ruby, JavaScript | Can miss error paths | Signatures stay clean |
| No exceptions | Rust, Go, Zig, Gleam, Roc, Elm | Must propagate errors explicitly | All error paths visible |

The Rust/Go/Zig branch ("exceptions are non-local control flow; errors are
values") is winning over both checked and unchecked exceptions.  Swift's
typed throws is an attempt to recover checked-exception benefits with
lighter syntax, but it is too early to judge.

See: `error_handling_defer_resource_cleanup_notes.md` §4 (Java checked
exceptions, Kotlin `Result`/`Nothing`), §6 (Swift typed throws),
`go_design_philosophy_deep_dive.md` §3 (Go error handling philosophy).

**Nomi's choice: Unchecked exceptions for truly unexpected errors.  `Result`
data for expected failure.**  Nomi rejects Java's checked exceptions
(proven failure mode) and Go's `if err != nil` (too verbose, see §2.5).
It accepts the Rust/Zig/Gleam model: errors are data, exceptions are
exceptional, and the programmer chooses between them based on whether the
caller can reasonably recover.

### 2.3 RAII vs defer vs Context Managers

Three irreconcilable models for deterministic cleanup, each with deep
implications:

| Model | Languages | Resource state | Composition | Nested cleanup |
|-------|-----------|---------------|-------------|----------------|
| RAII (destructor-based) | C++, Rust | Value owns resource | Automatic via type nesting | Free (stack unwinding) |
| defer (scope-registered) | Go, Zig, Swift, Odin, D, Nim | Separate statement | Manual ordering | LIFO (reverse registration) |
| Context manager (block-based) | Python `with`, C# `using`, Java try-with-resources | Dedicated block | Nesting blocks | Explicit indentation |
| Block callback | Ruby blocks, Gleam `use`, Julia `do` | Function call | Call-site visible | Nesting calls |

RAII ties resource lifetime to value lifetime — elegant but requires
ownership tracking.  `defer` is lightweight but can accumulate invisibly.
Context managers are explicit but can't express "cleanup only on error"
without boilerplate.  Block callbacks are the most general but require
the language to have first-class blocks.

See: `error_handling_defer_resource_cleanup_notes.md` §4 (C++ RAII, Python
`with`, Java try-with-resources), §5 (Go/Zig/Swift `defer`), §3 (Gleam
`use`), `modern_language_feature_survey.md` §3 (D `scope`, Jai `using`,
Wren fibers), `csharp_java_dart_modern_features.md` §5 (C#/Java/Dart
resource patterns).

**Nomi's choice: Block policies as the unifying primitive.  `defer` for
local, always-run cleanup.**  Nomi's block-call model (`using(resource) ->
r: body`) subsumes context managers, block callbacks, and Gleam's `use`.
`defer` handles the "register cleanup now, run on scope exit" case.
`errdefer` is a library policy, not syntax.  Nomi rejects RAII (requires
ownership tracking that is deferred from the first layer) and Python's
separate `with` keyword (block calls are the general mechanism).

### 2.4 Expression Match vs Statement Match

The ML family treats `match` as an expression.  C-family languages
that adopted pattern matching late (Python, C#, Dart) made it a statement.
This is not mere syntax — it determines whether `match` composes in
expression position.

| Branch | Languages | Composes in expressions | Exhaustiveness forcing | Visual weight |
|--------|-----------|------------------------|----------------------|---------------|
| Expression | Rust, OCaml, Haskell, Scala, Swift, Kotlin, F# | Yes | Compiler error | Light |
| Statement | Python, C#, Dart | No (need wrapper) | Warning or none | Heavy |

Python's `match` as statement means you cannot write `x = match value: case
A: 1 case B: 2`.  C# 12's `switch` expression is an attempt to have both,
creating the very convergence problem (see §1.5).

See: `pattern_matching_synthesis.md` §3.4 (expression vs statement match),
`csharp_java_dart_modern_features.md` §4 (C# and Dart match), `go_design_philosophy_deep_dive.md` §2 (Go's statement orientation).

**Nomi's choice: Expression match.**  `match` returns a value.  Every branch
is an expression.  This is non-negotiable — statement match is a half-measure
that creates the second-spelling problem.  Nomi accepts the Rust/ML approach
and rejects the Python/C/Go statement approach entirely.

### 2.5 Upward Propagation vs Inline Error Handling

How a language handles the common case ("try this, and if it fails, propagate
the error upward") reveals a deep fork:

| Branch | Languages | Mechanism | Visual noise | Composability |
|--------|-----------|-----------|-------------|---------------|
| Inline | Go (`if err != nil`), pre-? Rust | Explicit at every call | High (30-50% of code) | Poor (breaking flow) |
| Propagation operator | Rust `?`, Swift `try`, Zig `try` | Single character | Low | Good (expressions compose) |
| Monadic bind | Haskell `>>=`, Scala `for`, OCaml `let*` | Composable | Medium | Excellent |
| Context flattening | Gleam `use`, effect handlers | Generalized | Low | Excellent |

Go's `if err != nil` is deliberately verbose but produces predictable
code.  Rust's `?` is concise but hides the propagation point.  Monadic
bind is elegant but requires understanding Functor/Applicative/Monad.
Gleam's `use` is the newest contender: it generalizes the pattern of
"set up a callback context" without monad comprehension or special
syntax for each effect.

See: `go_design_philosophy_deep_dive.md` §3 (Go `if err != nil` philosophy),
`error_handling_defer_resource_cleanup_notes.md` §2 (Zig `try`, Gleam `use`),
§7 (Haskell `ExceptT`, Scala `Either`), `beam_languages_erlang_elixir_gleam.md` §4 (BEAM error handling, Gleam `use`).

**Nomi's choice: `Result` with pattern-matching as the primary story.
Block calls for context flattening.  `?` propagation deferred until
proven necessary.**  Nomi accepts that inline `match result: case
Ok(v): v ...` is more verbose than `?` but makes every error path
visible.  It rejects Go's `if err != nil` (too noisy) and defers
judgment on whether `?` is needed — the decision depends on real
usage data, not research precedent.

### 2.6 Function Coloring vs Unified Control Model

The `async`/`await` fork has split every language that added it:

| Branch | Languages | Problem | Cost |
|--------|-----------|---------|------|
| Colored (async/sync split) | Python, JS/TS, Rust, C#, Kotlin, Swift, Dart | Ecosystem split; bridging code; "what color is my function" | Permanent |
| Unified (single control model) | Go (goroutines), Erlang/Elixir (processes), Gleam (no async), Roc (platform passing) | Simpler model; no color boundary | Requires runtime support |
| Effect systems | Koka, Eff, OCaml 5, Unison | User-defined effects; no built-in colors | Research-stage |

Without Boats (Rust team): "The async fn desugars to a state machine that
requires pinning. This is an implementation detail that leaked into the
user-facing language."

Chris Lattner (Swift): "If I could do Swift over again, I'd make concurrency
part of the language from day one."

See: `design_lessons_and_integration.md` §7.1 (function color analysis),
`beam_languages_erlang_elixir_gleam.md` §2 (BEAM concurrency model),
`modern_language_feature_survey.md` §4 (Unison abilities, Gleam `use`).

**Nomi's choice: Block calls as the single control abstraction.  No
`async`/`await`.  No function colors.**  A callee uses `yield` to invoke
caller-side code.  Iteration, resource management, retry, tracing, and
future concurrency models all reduce to block policies — not separate
function colors.  Nomi explicitly rejects the `async`/`await` model as
a design mistake that every language that adopted it now regrets (see
designer quotes in design_lessons_and_integration.md §8).

### 2.7 Macros vs Code Generation vs No Metaprogramming

How a language exposes metaprogramming to users:

| Branch | Languages | Power | Cost |
|--------|-----------|-------|------|
| First-class macros | Lisp, Racket, Clojure, Julia, Nim | Arbitrary syntax extension | Debugging opaque; hygiene complex |
| Declarative macros | Rust `macro_rules!`, Elixir macros | Pattern-based rewrite | Limited to token patterns |
| Proc macros / compiler plugins | Rust proc macros, Scala 3 macros | Full AST manipulation | Complex; build-time cost |
| Compile-time execution | Zig `comptime`, Jai, D `static if` | Run code at compile time | Predictable; limited to values |
| Code generation | Go, protobuf, GraphQL | Separate build step | Impedance mismatch; drift |
| None | Python, Java, C, C# | No metaprogramming | Boilerplate; reflection |

Every macro system that succeeded (Lisp, Rust, Julia) had the language's
AST as a first-class value before macros were added.  Adding macros to a
language without inspectable ASTs produces uninspectable magic.

See: `modern_language_feature_survey.md` §2 (Jai compile-time execution),
§6 (Janet PEGs, Nim templates), `typescript_type_system_deep_dive.md` §5
(TypeScript type-level programming as metaprogramming).

**Nomi's choice: Defer global macros.  Build the desugaring pipeline as
the inspectable foundation first.**  Nomi already has a desugaring pipeline
(lowering + desugar passes + surface nodes) that shows how surface syntax
reduces to the core.  This pipeline IS the macro infrastructure — when
macros are added, they emit surface nodes or normal-form reductions, not
raw text.  Nomi explicitly rejects Lisp-style `defmacro` (too low-level,
too uninspectable) and Go's "no macros" (too limiting).  It pursues the
Rust/Zig path: expose the AST, keep source spans, and make macro output
inspectable.

### 2.8 Sound vs Unsound Type Systems

Languages choose whether type safety guarantees are absolute or pragmatic:

| Branch | Languages | Guarantee | Escape hatch |
|--------|-----------|-----------|--------------|
| Sound (proven safe) | Haskell (no unsafe), OCaml (no Obj), Elm | Every well-typed program has defined behavior | None (or very restricted) |
| Sound with escape | Rust (`unsafe`), Haskell (`unsafePerformIO`), Swift (`unsafePointer`) | Types are guarantees outside `unsafe` blocks | Deliberate, visible |
| Unsound by design | TypeScript, Go (interface{}, nil), Dart (dynamic) | Pragmatic interop; migration path | Pervasive |
| Deliberately gradual | TypeScript (`strict` mode opt-in), Python/mypy, Ruby/RBS | Typed boundary, untyped body | Type assertions |

TypeScript is the most successful unsound type system ever built.  Its
designers deliberately chose pragmatism over soundness: the type system
helps at scale but does not *guarantee* safety.  This was the right call
for migrating JavaScript, but it is not the right call for a new language.

Anders Hejlsberg (TypeScript): If designing TypeScript today, `enum` would
likely not exist in its current form.  `as` casts are a deliberate escape
hatch that users abuse.

See: `typescript_type_system_deep_dive.md` §6 (deliberate omissions and
unsafe features), `language_design_dimensions.md` §3.2 (type discipline
axis), `go_design_philosophy_deep_dive.md` §2 (Go's structural interfaces
and `interface{}`).

**Nomi's choice: Runtime constraints as the first-layer type discipline.
Static checking as a zero-overhead upgrade.**  Nomi rejects TypeScript's
deliberate unsoundness (right for TS, wrong for a new language) and C's
"void pointer" escape hatches.  It accepts the Rust model: a safe default
with visible, audit-able escape boundaries.  Constraints (`name:Type,
predicate = value`) are checked at binding time in the first layer; static
checking can later verify them at compile time without changing semantics.

---

## 3. Hidden Incompatibilities

These are features that look compatible in isolation but break when combined.
They are not found by surveying individual languages — they emerge from
detailed feature-interaction analysis across languages that tried to combine
them.

### 3.1 Structural Typing + Exhaustiveness Checking

This is the most important hidden incompatibility in type-system design,
and it is formally irreconcilable.

Structural types are open-world: any value with the right fields satisfies
the type.  Exhaustiveness checking requires a closed-world: the checker
must know ALL possible variants to verify every case is handled.

If your language has structural typing as the default (TypeScript), you
cannot have full exhaustiveness checking — you can only approximate it
with `never`-type tricks and `satisfies` assertions.  If your language
has exhaustiveness checking (Rust, OCaml), you must have nominal types
for the checked variants.

TypeScript's `never` hack proves this incompatibility in practice:
```typescript
// TypeScript: exhaustiveness via 'never'
function assertNever(x: never): never { throw new Error("Unexpected: " + x); }
// This works for discriminated unions, but breaks if someone adds a
// structurally-compatible value from another module.
```

**Result:** Languages that try to have both (Scala 3's sealed traits +
structural types, Swift's enums + protocols) define a split: nominal for
exhaustive matching, structural for protocol conformance.  This split is
not a compromise — it is the correct recognition that structural and
nominal types serve different purposes.

See: `typescript_type_system_deep_dive.md` §3 (structural typing) and
§6 (never-based exhaustiveness), `pattern_matching_synthesis.md` §3.5
(structural typing + extractors vs exhaustiveness).

**Nomi's position:** Explicitly bifurcate.  Nominal `data` for owned types
(exhaustiveness possible).  Structural matching for external values
(extensibility retained).  Do not try to unify them — see
[Language Design Dimensions §5](../language/language_design_dimensions.md).

### 3.2 Unsafe Cast + Null Safety

Every language with null safety also has an unsafe escape hatch
(`!!` in Kotlin, `!` in TypeScript, `unwrap()` in Rust).  The
existence of the escape hatch means null safety is a convention,
not a guarantee.  Worse: as codebases grow, `!!` calls proliferate
and null-safety becomes a runtime crash waiting to happen.

Kotlin example: `val x: String? = null; x!!  // NPE at runtime`
TypeScript: `const x = null as any as string; x.length  // runtime error`

The incompatibility is socio-technical: the language guarantees safety,
but the escape hatch exists for interop, and interop is the whole point
of gradual migration.  If migration requires `!!` at every boundary,
the safety guarantee dissolves.

See: `csharp_java_dart_modern_features.md` §3 (Dart NNBD escape hatches,
Kotlin `!!`), `typescript_type_system_deep_dive.md` §4 (union types
and narrowing with `as`).

**Nomi's position:** No `!!`-style unsafe cast.  No `as`-style type
assertion for null bypass.  `?.` and `??` handle absence.  `match`
handles deconstruction.  If an API returns nullable and the caller
knows it's not null, use pattern narrowing (`if ok_value = result:`),
not an unsafe assertion.  Nomi rejects the Kotlin/TypeScript/Dart
pattern of safe-by-default with unsafe-escape — the escape hatch
becomes the default (see §6.1 of design_lessons_and_integration.md).

### 3.3 Macros + Inspectable Diagnostics

Macro systems that operate on raw tokens (C preprocessor) or
unannotated AST nodes (Lisp `defmacro`) destroy source-span
information.  When the macro expands, the diagnostic says "error
in expanded code at line X" but line X is inside generated code
the user never wrote.

Rust's proc macros and Scala 3's `inline`/`quote` system show the
partial solution: macros carry source spans from input to output,
and the compiler can attribute errors to the macro call site, not
the expanded code.  But this requires every macro to be written
correctly — a single macro that drops source spans poisons the
diagnostic experience for all its callers.

See: `diagnostics_and_explanations_comparative.md` §8 (blame assignment
in Rust diagnostics), `modern_language_feature_survey.md` §2 (Jai
compile-time execution with source spans), `typescript_type_system_deep_dive.md` §5 (type-level programming as uninspectable metaprogramming).

**Nomi's position:** Build the diagnostic infrastructure (source spans,
trace records, `explain`) BEFORE adding macros.  When macros arrive, they
must surface-source-spans through the transformation.  Nomi's existing
desugaring pipeline already carries spans from parse to interpreter; this
infrastructure is the macro hygiene mechanism.

### 3.4 Duck Typing + Static Analysis

Python's structural pattern matching (3.10) hit this incompatibility
head-on.  Python is dynamically typed: any value can be any type at
runtime.  But pattern matching needs to know: does `case Point(x, y)`
match a `Point` class, a dict with those keys, or any object with
`x` and `y` attributes?  Python chose class-based matching with
`__match_args__` — a protocol that feels like duck typing but works
like nominal dispatch.

The deeper problem: any static analysis tool (mypy, Pyright) can reason
about nominal types but not about duck-typed patterns.  The tool can
check exhaustiveness for sealed classes but not for "anything with an
`x` field."

Go faces the same tension: interfaces are structural, so exhaustiveness
over interface implementations is impossible.  The `switch v.(type)`
statement can never be checked for completeness because any package can
add a new implementation.

See: `typescript_type_system_deep_dive.md` §5 (narrowing with
`typeof`/`in` vs nominal), `go_design_philosophy_deep_dive.md` §2
(interfaces as structural types).

**Nomi's position:** Nominal `data` for owned types.  Structural matching
via mapping patterns for external dicts/records.  Keep the two distinct.
`data` variants are closed; match over them is exhaustive.  Mapping
patterns (`{"key": pattern}`) are open; match over them is NOT
exhaustive.  This visibility is the right design — the user knows which
matches are checked and which are not.

### 3.5 Lazy Evaluation + Side Effects + Error Messages

Haskell's laziness is elegant in isolation.  But combining lazy evaluation
with I/O (side effects), exceptions, and error reporting creates an
execution order that is nearly impossible to predict from source reading
alone.

```haskell
-- The error might fire now, later, or never, depending on evaluation order
let x = error "boom" in const 1 x  -- returns 1? throws "boom"? depends on optimization
```

Space leaks from thunk accumulation are a distinct debugging skill that
takes Haskell programmers years to master.  The `seq` / `deepseq` / `!`
pattern ecosystem exists to work around the evaluation model, not to use
it.

See: `language_design_dimensions.md` §3.1 (evaluation axis),
`design_lessons_and_integration.md` §1.4 (performance-transparency cliff
including Haskell laziness).

**Nomi's position:** Eager evaluation as default, following Python.  Lazy
evaluation opt-in with a visible marker (future `lazy` keyword or `~`
prefix).  Nomi accepts that laziness is powerful for streaming, query
plans, and infinite structures but rejects it as the default evaluation
model for a language that prioritizes readable diagnostics.

### 3.6 Immutable Data + Copy-with-Modify

Immutable-by-default languages (Haskell, Clojure, Elm) need a copy-with-modify
story.  Updating a deeply nested field in an immutable record requires
writing out the entire path:

```haskell
-- Update user.address.city — rebuild the entire path
user { address = (address user) { city = "new city" } }
```

Lenses solve this but introduce a library with its own vocabulary,
laws, composition rules, and type errors.  Functional-update syntax
(like Haskell's record update, OCaml's `{ record with field = value }`)
helps for shallow updates but does not compose for nested paths.

Python's `dataclasses.replace()` and Swift's `struct` copy are partial
solutions that don't compose.  Rust's struct-update syntax is the most
ergonomic: `User { city: "new", ..user }` — but even this does not
compose for nested fields.

See: `csharp_java_dart_modern_features.md` §2 (C# `with` expressions in
records), `language_design_dimensions.md` §3.3 (memory/ownership including
immutability), `syntax_synthesis_matrix.md` §Feature-Families (data
declaration).

**Nomi's position:** Recognize this as an open tension, not a solved problem.
For the first layer, shallow copy (field-level with-syntax) is sufficient.
Deep functional updates should be a library pattern (lens-like functions),
not syntax.  Nomi declines to add functional-update syntax until usage
patterns prove which copy shapes are common enough to deserve sugar.

### 3.7 Dynamic Dispatch + Pattern Match Exhaustiveness

Pattern matching over dynamically-dispatched values cannot be exhaustive.
If `match value: case Dog: ... case Cat: ...` dispatches on the runtime
type of a class hierarchy (as in Python), any subclass can be loaded
dynamically and the match is incomplete.

Java's sealed classes (Java 17) solve this by closing the hierarchy:
`sealed interface Animal permits Dog, Cat` means only those two subtypes
can exist.  Scala 3's `enum` and Swift's `enum` do the same.  The
incompatibility is not between dynamic dispatch and exhaustiveness per
se — it is between *open* dispatch (any subclass) and exhaustiveness.

See: `pattern_matching_synthesis.md` §3.5 (extractors + exhaustiveness),
`csharp_java_dart_modern_features.md` §4 (Java sealed classes, Dart
sealed family).

**Nomi's position:** `data` variants define closed type families.
Exhaustiveness is guaranteed.  If extensibility is needed, use
structural matching (`match raw: case {"kind": "dog", ...}`) where
exhaustiveness is NOT guaranteed.  The user chooses which guarantee
they want by choosing nominal or structural matching.

---

## 4. The Nomi Synthesis

This is the central section.  For each of Nomi's eight normal forms, it
shows how Nomi resolves the tensions from sections 1-3 into a coherent
design.  Each subsection: (a) the convergence it builds on, (b) the fork
it navigates, (c) the incompatibility it dissolves, (d) the Nomi resolution.

### 4.1 Binding Normal Form — One Story for Name Introduction

**Convergence built on:** Type annotations at binding sites (1.1), expression-
oriented binding (1.5).

**Fork navigated:** Structural vs nominal in binding (2.1).  Nomi's binding
is always nominal — a name is associated with a value in a scope, optionally
with constraints.  Structural recognition happens through patterns, not
through structural type equivalence (see §4.3).

**Incompatibility dissolved:** Duck typing + static analysis (3.4).  By
making binding always nominal, every binding site can be reasoned about
locally.  A binding `age:int, age >= 13 = raw_age` tells you everything you
need to know about `age` at that point.

**Nomi resolution:**
```text
name:constraint, constraint else "...message" = value
```
Every binding (assignment, parameter, block parameter, pattern capture,
loop variable) uses this same form.  Bindings reduce to:
```text
evaluate value → create tentative binding → check constraints → commit or BindingError
```
- Constraints are re-checked when rebinding.  No stale constraint.
- `BindingError` carries the value, the binding path, the failing constraint, and the user message.
- No `let`/`var`/`const`/`val` distinction.  One binding story.
- Immutability is a constraint, not a keyword family (`name:(const)`).

See: `design_lessons_and_integration.md` §4.1.

### 4.2 Function Normal Form — Block Policies Dissolve Coloring

**Convergence built on:** Expression-oriented conditionals (1.5), pipeline
operators (1.6).

**Fork navigated:** Function coloring vs unified control (2.6).  Nomi's
block/yield model avoids the async/sync split by making `yield` the single
control-transfer mechanism instead of creating a second function type.

**Incompatibility dissolved:** Lazy evaluation + side effects + error
messages (3.5).  Nomi's eager evaluation means execution order follows
source order.  `yield` points are explicit — you can see where control
transfers to the caller's block.

**Nomi resolution:**
```text
// Named function with constrained parameters
func add(x:int, y:int) -> int:
    return x + y

// Block call: caller attaches code; callee controls when it runs
using(open(path)) -> file:
    text = file.read()

// The callee uses yield to invoke the block
func using(resource) -> block:
    try:
        yield resource     // invoke caller's block with resource
    finally:
        resource.close()
```

Key properties:
- One block-call form (`f(x) -> p: body`), not five parallel mechanisms.
- `yield` is the control verb — it invokes the attached block.
- Resources (`using`), retry, transaction, tracing, and future concurrency
  models are all block policies — not dedicated keywords.
- No function coloring.  A function with `yield` is the same function type
  as one without.
- The block's lexical scope is the CALLER's scope — block parameters are
  bound at the call site, not at the callee's definition site.

See: `design_lessons_and_integration.md` §4.5 and §7.1.

### 4.3 Pattern Normal Form — Structural Choice Dissolves Fragmentation

**Convergence built on:** Pattern matching + exhaustiveness (1.2), Option/Maybe
types (1.3), Result/Either types (1.4).

**Fork navigated:** Expression match vs statement match (2.4).  Nomi's match
is always an expression.  This is non-negotiable.

**Incompatibility dissolved:** Structural typing + exhaustiveness (3.1),
dynamic dispatch + exhaustiveness (3.7), duck typing + static analysis (3.4).
Nomi's bifurcation (nominal `data` for owned types, structural matching for
external values) makes the incompatibility visible rather than hiding it.

**Nomi resolution:**
```text
// Exhaustive match over nominal data variants
match result:
    case Ok(value): use(value)
    case Err(error): explain(error)

// Structural match over external values (non-exhaustive)
match raw:
    case {"email": email:str, "age": age:(int, >= 13)}:
        SignupInput(email=email, age=age)

// Single-pattern binding (not nil-specific, works with any pattern)
if Ok(user) = fetch(id):
    send(user.email)

// Early exit on mismatch
guard Ok(user) = fetch(id) else:
    return Err(UserNotFound(id))
```

Key properties:
- One pattern engine for `match`, `if-let`, `guard-let`, destructuring,
  and block parameters.
- Pattern failure (structure didn't fit) and constraint failure (structure
  fit but value unacceptable) are distinct — diagnostics name which happened.
- Mapping patterns (`{"key": pattern}`) for external recognition without
  declaring a nominal type.
- Guards (`if condition`) as additive boolean filters after structural match.
- No `switch`/`case` as a parallel keyword family.

See: `design_lessons_and_integration.md` §4.3.

### 4.4 Flow Normal Form — Pipeline as the Single Flow Operator

**Convergence built on:** Pipeline operators (1.6), collection transforms (1.1
data classes + 1.2 pattern matching for element operations).

**Fork navigated:** Inline vs propagation error handling (2.5).  Pipelines
with `Result` values need to decide: does `|>` propagate `Err` or pass it
through?  Nomi chooses: pass through (like any other value).  `Result` is
data; the pipeline does not treat it specially.  Pattern matching at the end
of the pipeline inspects the result.

**Incompatibility dissolved:** Pipeline + composition + holes interaction
(see design_lessons_and_integration.md §2.2).  Nomi resolves precedence:
`|>` has lower precedence than `>>>`, and holes (`_`) in pipeline position
treat the piped value as input.

**Nomi resolution:**
```text
active_names =
    users
    |> where(_.active)
    |> select(_.name)
    |> sort
```
- One pipeline operator `|>` (not five threading macros).
- Default first-argument threading.
- `_` placeholder when the argument position is not first.
- Composition `>>>` / `<<<` for building reusable functions (separate concept).
- Collection verbs (`where`, `select`, `map`, `fold`, `group`, `sort`, `join`)
  as library functions, not syntax.
- Table/query semantics as future layer over the same pipeline primitive.
- Pipe diagnostics: each stage is traceable; `explain` can show intermediate values.

Nomi explicitly rejects:
- Clojure's `->`/`->>` family (five macros for one concept).
- Nushell's text-stream model (pipelines carry typed values, not byte streams).
- Multiple placeholder families (no `it`, `$0`, `%` alongside `_`).

See: `design_lessons_and_integration.md` §4.4 and §2.2.

### 4.5 Block Normal Form — Call + Attached Code Dissolves Effect Proliferation

**Convergence built on:** Deterministic resource cleanup (1.7), expression-
oriented blocks (1.5).

**Fork navigated:** RAII vs defer vs context managers (2.3), macros vs code
generation (2.7).  Block calls unify resource management, retry, transaction,
tracing, and iteration into one call-site-visible pattern.

**Incompatibility dissolved:** Macros + inspectable diagnostics (3.3).  Block
calls carry source spans through the `yield` boundary.  Diagnostics can trace
from the `yield` in the callee back to the caller's block body.

**Nomi resolution:**
```text
// Resource management
using(open(path)) -> file:
    text = file.read()

// Retry policy
retry(3, on=NetworkError):
    send(request)

// Transaction
transaction(db):
    db.insert(user)
    db.update(profile, user.id)

// Tracing
trace "import people":
    rows = read_csv(config.input)
    |> where(_.age >= config.min_age)
    |> select(Person.decode)
```

Key properties:
- Block calls look like ordinary calls with an attached block.
- `yield` is the control verb — the callee invokes the caller's block.
- Block parameters use the shared binding engine (same as assignment, function
  parameters).
- Diagnostics show yield/resume/failure events through the block boundary.
- `defer` for local always-run cleanup; `errdefer` as a library block policy.
- No `with` keyword (Python), no `do` keyword (Julia), no `using` as a
  dedicated statement (C#) — one block-call form handles all policies.

See: `design_lessons_and_integration.md` §4.5.

### 4.6 Data Boundary Normal Form — Explicit Decode Dissolves Schema Languages

**Convergence built on:** Data classes/records (1.1), Option/Maybe types (1.3).

**Fork navigated:** Structural vs nominal typing (2.1).  `data` is nominal
(owned types).  Decode is the boundary crossing from structural external
values to nominal internal values.

**Incompatibility dissolved:** The second mini-language for validation
(design_lessons_and_integration.md §1.1).  By making constraints the
validation mechanism, Nomi avoids a separate schema language (JSON Schema,
XSD, OpenAPI-style) — validation reuses the binding engine.

**Nomi resolution:**
```text
// Owned data declaration (nominal, closed)
data User:
    id:UserId
    email:str, contains(email, "@") else "Invalid email"
    age:int, age >= 13 else "Must be at least 13"
    plan:Plan = Plan.Free

// Sum type
data Result[T, E]:
    Ok(value:T)
    Err(error:E)

// Explicit boundary crossing
signup_input = SignupInput.decode(request.json)

// Or through structural match
match request.json:
    case {"email": email:str, "age": age:(int, >= 13)}:
        SignupInput(email=email, age=age)
```

Key properties:
- `data` creates constructors, fields, equality/display rules, and pattern forms.
- Fields reuse the binding normal form (same constraints, same diagnostics).
- `Data.decode(source)` is the explicit boundary crossing — external to internal.
- No separate `schema`, `shape`, `interface`, or `contract` keyword that competes
  with `data`.
- Structural matching for external values (mapping patterns, destructuring).
- Field provenance and merge policy for config are library-first.

Nomi explicitly rejects:
- Separate schema/config languages (CUE, Pkl, JSON Schema as separate DSLs).
- Implicit external-to-internal conversion (no automatic `pickle`/`Marshal`).
- A peer `shape`/`schema` keyword that competes with `data` for field declaration.

See: `design_lessons_and_integration.md` §4.7.

### 4.7 Absence/Result Normal Form — Three Distinct Stories

**Convergence built on:** Option/Maybe types (1.3), Result/Either types (1.4),
structured diagnostics (1.8).

**Fork navigated:** Checked vs unchecked exceptions (2.2).  Unchecked exceptions
for truly unexpected errors.  `Result` data for expected failure.  `none`/`?.`
for absence.  Three branches, each with clear criteria.

**Incompatibility dissolved:** Unsafe cast + null safety (3.2).  By removing
`!!` and `as`-style escape hatches, Nomi makes absence handling uniform:
always use `?.`/`??` for short-circuit or `match` for deconstruction.  No
runtime null-pointer exceptions from unsafe bypasses.

**Nomi resolution:**
```text
// Absence: Option-like
name = user?.profile?.display_name ?? "Anonymous"

// Expected failure: Result
func load_config(path) -> Result[Config, Error]:
    match read_file(path):
        case Ok(content):
            match parse_config(content):
                case Ok(config):
                    return Ok(config)
                case Err(e):
                    return Err(ConfigError("Parse failed", cause=e))
        case Err(e):
            return Err(ConfigError("Read failed", cause=e))

// Unexpected: exceptions (truly unrecoverable)
// No special syntax — just let it propagate
```

Key properties:
- `?.` and `??` handle absence ONLY.  They do not short-circuit on `Err`.
- `Result[T, E]` handles expected failure.  Pattern matching deconstructs it.
- Exceptions are for unexpected errors — truly unrecoverable at the call site.
- Three distinct stories, three distinct syntaxes, three distinct diagnostic paths.
- `?` propagation operator deferred — `match` + patterns is the primary story.

Nomi explicitly rejects:
- Merging `None` with "error occurred" (Python's mistake).
- `null`/`undefined` split (JavaScript's mistake).
- Java-style checked exceptions.
- Go-style `if err != nil` (but accepts its explicitness as a design pressure).

See: `design_lessons_and_integration.md` §4.6 and §7.6.

### 4.8 Explanation Normal Form — Trace Records Before Feature Proliferation

**Convergence built on:** Structured diagnostics (1.8).

**Fork navigated:** Sound vs unsound type systems (2.8).  Runtime constraints
with structured diagnostics provide the safety guarantee in the first layer.
Static checking is a future compile-time upgrade of the same semantics.

**Incompatibility dissolved:** Macros + inspectable diagnostics (3.3), lazy
evaluation + error messages (3.5).  By building trace records and source-span
infrastructure first, Nomi ensures that every later feature (macros, lazy eval,
effect handlers) can integrate with the diagnostic system rather than working
around it.

**Nomi resolution:**
```text
// Examples as executable documentation
func normalize_email(email:str) -> str:
    examples:
        " A@B.COM " => "a@b.com"
        "user@domain.com" => "user@domain.com"
    return email.strip().lower()

// Trace blocks for contextual diagnostics
trace "user import":
    rows = read_csv(path)
    |> where(_.active)
    |> select(User.decode)

// Diagnostics use normal-form vocabulary
// BindingError: constraint 'age >= 13' failed
//   value: 12
//   binding: field 'age' in SignupInput.decode(request.json)
//   note: Must be at least 13
```

Key properties:
- Every semantic event produces a trace record with source spans.
- Diagnostics speak in normal-form vocabulary, not internal implementation names.
- `examples:` blocks are tests, docs, and `explain` anchors.
- `trace` blocks add context to diagnostics without changing behavior.
- `explain` is a user-facing operation that renders trace records.
- The implementation spine preserves source spans from parse through to diagnostic output.

Nomi explicitly rejects:
- Error messages that report compiler internals (pre-concepts C++, early GHC).
- Stack traces as the only diagnostic (Clojure, pre-3.10 Python).
- Separate testing languages (no `pytest`/`RSpec` alternative — examples ARE tests).

See: `design_lessons_and_integration.md` §4.8, `diagnostics_and_explanations_comparative.md`.

---

## 5. Design Decision Record

This table records Nomi's position on every significant design tension
identified in the research corpus.  Each row cites the primary research
file and section for that decision.

| Decision | Source traditions | Nomi's position | Rationale | Ref |
|----------|------------------|-----------------|-----------|-----|
| **Evaluation order** | Eager (Python/Java/C) vs Lazy (Haskell/R) | Eager; lazy opt-in with visible marker | Predictable execution order; readable diagnostics | design_dimensions §3.1 |
| **Type discipline** | Static (Rust/Haskell) vs Dynamic (Python/JS) vs Gradual (TS) | Runtime constraints first; static as zero-overhead upgrade | Avoids TS's deliberate unsoundness; preserves runtime behavior | design_dimensions §3.2 |
| **Type identity** | Nominal (Java/Rust) vs Structural (TS/Go interfaces) | Nominal `data` for owned; structural matching for external | Exhaustiveness possible on owned types; extensibility on external | design_dimensions §5, ts_deep_dive §3 |
| **Data declaration** | `data class`/`record`/`struct`/`dataclass` — 5+ keywords | One `data` for owned product and sum types | One story; no competing keywords; fields reuse binding engine | cs_java_dart §2, lang_foundation §Data |
| **Pattern matching** | Expression (ML/Rust) vs Statement (Python/C#) | Expression match always | Returns value; composes in expression position | pattern_matching §3.4 |
| **Exhaustiveness** | Checked (Rust/OCaml) vs Unchecked (Python/Go) vs Approximate (Scala sealed) | Checked for nominal `data`; unchecked for structural match | Closed-world possible for owned types; user chooses guarantee | cs_java_dart §4, pattern_matching §3.5 |
| **Null/absence handling** | `Optional`/`Maybe`/`?`/`nil` — many spellings | `none`/`?.`/`??` for absence only | Never conflate absence with error | err_handling §4, absence_and_result |
| **Error handling** | Exceptions (Java/Python) vs `Result` (Rust) vs `(v, err)` (Go) vs Error sets (Zig) | `Result` data + `match`; exceptions for unexpected; `none`/`?.` for absence | Three distinct, non-collapsible stories | err_handling §2-7, design_lessons §7.6 |
| **Error propagation** | `?` (Rust/Swift) vs `try` (Zig) vs `if err != nil` (Go) vs `use` (Gleam) | `match` primary; `?` deferred until proven needed | `?` for Result + `?.` for absence create similar operators; wait for usage data | go_deep_dive §3, beam §4 |
| **Resource cleanup** | RAII (C++/Rust) vs `defer` (Go/Zig/Swift) vs `with` (Python) vs `use` (Gleam) | Block policies (`using`) + `defer` for local; `errdefer` as library | Block calls unify resources, retry, transaction; `defer` for simple cases | err_handling §1-5, design_lessons §4.5 |
| **Control model** | `async`/`await` (colored) vs Go/Erlang (unified) vs Effect handlers | Block calls + `yield` as single control abstraction | No function coloring; concurrency future policies | design_lessons §7.1, modern_survey §4 |
| **Pipeline** | `\|>` (Elixir/F#) vs `->`/`->>` (Clojure) vs Shell pipes vs Composition | One `\|>`; `>>>` for composition; first-arg threading | One operator, not a family; separate pipe from composition | syntax_matrix §Feature-Families, beam §6 |
| **Implicit functions** | `_` (Scala) vs `$0` (Swift) vs `it` (Kotlin) vs `%` (Clojure) vs `&1` (Elixir) | `_` for one hole; `$1, $2` for multi-hole; reject `it` | One placeholder family; no competing hole spellings | syntax_matrix §Pleasant-Syntax |
| **Metaprogramming** | First-class macros (Lisp) vs Compile-time (Zig/Jai) vs Code-gen (Go) vs None | Deferred; build desugar pipeline as macro substrate first | Macros need inspectable AST + source spans; pipeline already has both | modern_survey §2-6, design_lessons §4.5 |
| **Diagnostics** | Rust (gold standard) vs Elm vs Gleam vs Minimal (Go/Clojure) | Trace records + source spans + normal-form vocabulary | Diagnostics built before feature proliferation | diagnostics §2-8 |
| **Configuration** | Separate DSL (CUE/Nickel/Pkl) vs Host-language (Dhall/Terraform) | `Data.decode()` boundary; constraints for validation | No second schema language; config = data + constraints | syntax_matrix §Feature-Families, design_lessons §4.7 |
| **Concurrency model** | Threads (Java) vs Actors (Erlang) vs Goroutines (Go) vs Structured (Kotlin) | Block policies as primitive; structured concurrency as future | Concurrency model designed before 1.0; block call is the right abstraction | design_lessons §7.7, beam §2 |
| **Standard library** | Large (Python/Java) vs Small (Go/Zig) vs Layered (Rust/Haskell) | Lean prelude shaped by normal forms; explicit imports | Ship one way; deprecate before adding second; edition mechanism | stdlib_design §3-6, design_lessons §7.3 |
| **Module system** | Files-as-modules (Go/Python) vs First-class modules (OCaml/Racket) | Files-as-modules initially; simple import/export; stable from 1.0 | No functors; no module types; keep module syntax stable | design_dimensions §3.7 |
| **Array/rank** | Dense glyphs (APL/J/K) vs Dot broadcasting (Julia/MATLAB) vs Explicit (NumPy) | Named shape/rank functions first; explicit broadcasting later | Don't make dense notation the everyday default | array_lang §3-5, scientific §2 |
| **Packaging/build** | Cargo (Rust) vs Modules (Go) vs `uv` (Python) | Plan edition/migration before 1.0; automated migration tooling | Rust's Cargo + edition system is the only successful model | design_lessons §7.8 |
| **Binding mutability** | Immutable-by-default (Rust/ML) vs Mutable-by-default (Python/Java) | One binding story; immutability as constraint, not keyword | No `let`/`var`/`const`/`val` distinction; `name:(const)` if needed | design_lessons §4.1, design_dimensions §3.6 |
| **Collection verbs** | Query language (SQL/LINQ) vs Pipeline verbs (dplyr/Nushell) vs Combinators | Pipeline verbs over plan values; query syntax only if row/group binding needs it | Don't add a second query language; `where`/`select` are library functions | syntax_matrix §Feature-Families, scientific §3 |

---

## 6. Risks and Open Questions

These are not unresolved design details.  They are structural risks that
could invalidate assumptions in this synthesis or create ceiling effects
that limit Nomi's growth.

### 6.1 Risks to the Synthesis

**Risk 1: The normal-form count may be wrong.**  Nomi has 8 normal forms.
The research shows languages need somewhere between 1 (Lisp, Forth, APL)
and ~20 (Java, C++) primitives.  The sweet spot argued here is 6-8, but
this is unproven.  If Nomi's normal forms are too few, users will encode
missing concepts in awkward patterns.  If too many, users will face the
convenience stack-collapse (see design_lessons_and_integration.md §1.2).

**Risk 2: Runtime constraints may not carry static checking.**  Nomi's
position (runtime constraints first, static checking as future upgrade)
assumes that the same constraint vocabulary can serve both.  TypeScript
proves that gradual typing works for migration but NOT that a
runtime-first type system can be statically analyzed without changing
semantics.  If the runtime semantics must change for static analysis,
the "upgrade" is really a new language.

**Risk 3: Block policies may not generalize to concurrency.**  The synthesis
asserts that block calls can encode structured concurrency, actors, and
data parallelism without new keywords.  This is unproven.  Gleam's `use`
is the closest precedent, and Gleam does not have concurrency.  If block
calls cannot carry concurrency semantics, Nomi may need a separate
concurrency model — violating the "no second function color" principle.

**Risk 4: `?` propagation deferral may backfire.**  Deferring `?` until
"proven necessary by usage" means early Nomi code will be verbose (`match
result: case Ok(v): ... case Err(e): return Err(e)`).  Users may reject
Nomi for the same verbosity that Go users tolerate.  The bet is that `match`
is more composable than `if err != nil`, but this is unproven until Nomi
has real users writing real programs.

**Risk 5: The structural/nominal bifurcation may confuse users.**  Nomi
asks users to understand when exhaustiveness is guaranteed (nominal `data`)
and when it is not (structural match).  This is a subtle distinction that
even experienced ML programmers sometimes get wrong.  The diagnostic story
(§4.8) is the mitigation, but it may not be enough.

### 6.2 Open Questions

**Q1: Should Nomi adopt Zig-style error-set typing for Result?**  Zig's
error sets have the unique property that the compiler can infer the
complete set of possible errors from a function's implementation, without
the programmer declaring them.  This is lighter than Rust's `Error` trait
but gives the same exhaustiveness benefit.  Nomi could adopt error-set
inference for `Result[T, E]` where `E` is inferred.  Open until Nomi's
type inference (future) is designed.

See: `error_handling_defer_resource_cleanup_notes.md` §2 (Zig error sets).

**Q2: Should `defer` run on block exit or function exit?**  Go's `defer`
runs on function exit.  Zig's `defer` runs on scope exit (block exit for
defer in a block).  The semantic difference matters for block calls: if
`defer` inside a block body runs on block exit, the cleanup happens
before the callee's cleanup.  If it runs on function exit, deferred
cleanup from inside a block call leaks past the block boundary.  Zig's
scope-exit semantics are more composable with block calls.

See: `error_handling_defer_resource_cleanup_notes.md` §1 (Zig `defer` and
`errdefer` semantics).

**Q3: Should Nomi have an edition/version mechanism?**  Rust's edition
system (2015, 2018, 2021, 2024) is the only proven mechanism for making
breaking changes without ecosystem fragmentation.  Nomi should design
its edition story before 1.0.  But editions require compiler support
for multiple surface syntaxes — which requires the desugaring pipeline
to handle edition-specific lowering.  This is architecturally possible
(Nomi already has a lowering pipeline) but requires deliberate design.

See: `design_lessons_and_integration.md` §7.4.

**Q4: How should mapping patterns work?**  Nomi's planned mapping patterns
(`match raw: case {"key": pattern}: ...`) need to decide: do they match
only exact keys, or at-least-these-keys (structural matching)?  The syntax
synthesis matrix notes this is a research backlog item.  The question
interacts with exhaustiveness: if mapping patterns are at-least-these-keys,
they are open-world and cannot be exhaustive.  If they are exact-keys, they
are closed-world but fragile (a new key in the source breaks the match).

See: `syntax_synthesis_matrix.md` §Research-Backlog, `design_lessons_and_integration.md` §4.3.

**Q5: Should `trace` emit records or just side-effects?**  The current
intent is that `trace` blocks add context to diagnostics.  The open question
is whether trace records are first-class values (can be queried, filtered,
aggregated) or opaque diagnostic attachments.  First-class trace records
enable powerful tooling (Darklang-style trace-driven development) but
create new design pressure around serialization, privacy, and performance.

See: `diagnostics_and_explanations_comparative.md` §10 (first-class trace
records design), `modern_language_feature_survey.md` §3 (Darklang trace-
driven development).

**Q6: Collection verbs — library or syntax?**  Nomi currently positions
collection verbs (`where`, `select`, `map`, `fold`, `group`) as library
functions.  The risk is that without query syntax, complex operations
(multi-table joins with row/group binding) become awkward.  SQL, LINQ,
and dplyr all have dedicated syntax for this.  Nomi's bet is that pipeline
verbs over plan values are sufficient until proven insufficient, but the
threshold of "proven insufficient" is not defined.

See: `syntax_synthesis_matrix.md` §Feature-Families (collection transforms).

**Q7: How many primitives is too many for the first-hour experience?**
The design dimensions document sets the "first-hour test": can a newcomer
write a useful program after one hour?  Nomi's 8 normal forms may be too
many for one hour.  The mitigation is that normal forms are layered:
binding + function + calls are learned first; data + match + pipeline
follow; block + absence + explanation come later.  But this layering is
not yet validated.

See: `language_design_dimensions.md` §9.

---

## Sources

Every section of this document draws from specific files and sections in
the research corpus.  Primary sources for each major finding are cited
inline.  The complete source files:

### Research Files (read in full)

1. `docs/research/error_handling_defer_resource_cleanup_notes.md` — Zig, Hylo, Odin, Gleam, Roc, Swift, Kotlin, Rust, Haskell, C++, Python, Java, Scala, C# error handling and resource cleanup (1,814 lines).
2. `docs/research/csharp_java_dart_modern_features.md` — C# (7-12), Java (17-21), Dart (3.0) records, pattern matching, null safety, and metaprogramming (1,187 lines).
3. `docs/research/go_design_philosophy_deep_dive.md` — Go's design philosophy, structural interfaces, error handling, goroutines, and package design (871 lines).
4. `docs/research/typescript_type_system_deep_dive.md` — TypeScript's structural typing, type narrowing, union/intersection types, discriminated unions, and deliberate omissions (1,039 lines).
5. `docs/research/pattern_matching_synthesis.md` — 10-language pattern matching synthesis: convergences, semantic differences, key tensions, and feature matrices (666 lines).
6. `docs/research/modern_language_feature_survey.md` — Mojo, Jai, Darklang, Unison, CUE/Nickel/Pkl/Dhall, Wren, Janet, Lobster, D (1,805 lines).
7. `docs/research/beam_languages_erlang_elixir_gleam.md` — BEAM platform, Erlang/Elixir/Gleam comparison, pattern matching, error handling, OTP supervision trees (1,080 lines).
8. `docs/research/array_languages_deep_dive.md` — APL, J, K, BQN, Uiua rank polymorphism, broadcasting semantics, and Nomi transfers (574 lines).
9. `docs/research/scientific_languages_r_matlab_julia.md` — Julia broadcasting, R formula interface, MATLAB array-first philosophy (769 lines).
10. `docs/research/diagnostics_and_explanations_comparative.md` — 10-language diagnostic architecture comparison: Rust through Zig (890 lines).
11. `docs/research/standard_library_design_comparative.md` — 10-language stdlib design: Go, Rust, Python, Kotlin, Swift, Elixir, Zig, C#, Haskell, Racket (939 lines).
12. `docs/research/language_family_coverage_map.md` — Coverage map of language families and research priorities (231 lines).
13. `docs/research/research_notes_synthesis.md` — Distilled research notes organized by 9 major themes (742 lines).

### Nomi Design Docs

- `docs/language/language_foundation.md` — Canonical design foundation, operational core, syntax runway, feature admission protocol (964 lines).
- `docs/language/language_design_dimensions.md` — 8 core primitives, axes of variation, convergence thesis, Expression Problem analysis (1,000 lines).
- `docs/convenience/syntax_synthesis_matrix.md` — Cross-language feature families, pleasant syntax principles, admission ladder (344 lines).
- `docs/convenience/design_lessons_and_integration.md` — Systemic cruft patterns, feature interactions, community praise/regret, designer quotes, synthesis methodology (864 lines).
