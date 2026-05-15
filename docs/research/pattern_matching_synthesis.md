# Pattern Matching: Cross-Language Synthesis

> Status: cross-language comparative research; active synthesis for Nomi design.
> Purpose: Systematically compare pattern matching across languages — what's
> structurally identical, what's semantically different, and what issues arise
> when combining approaches.

## 1. Why Pattern Matching Matters for Nomi

Pattern matching is the convergence point for three core primitives in Nomi's
design framework (see `language_design_dimensions.md`):

```
Choose (select case) + Contain (each body is a scope) + Bind (captures bound in that scope)
```

That makes it the richest normal form. A pattern match simultaneously tests
structure, binds parts, checks constraints, and selects computation paths. The
surface syntax varies enormously across languages, but the semantic bones are
strikingly similar. Understanding what's the same, what's genuinely different,
and what breaks when traditions collide is the prerequisite for designing Nomi's
pattern surface.

Every language below converges on the same core: test a value's shape, bind
useful parts, optionally filter with a boolean guard, select a body. The
differences are in exhaustiveness enforcement, binding style, extensibility, and
where patterns are allowed to appear.

---

## 2. Language-by-Language Analysis

### 2.1 Rust

Rust is the modern reference for exhaustiveness-driven pattern matching. `match`
is always an expression; every arm must produce a value of the same type.
Exhaustiveness is a compile error — the compiler refuses to compile if any value
of the matched type is unhandled. This is only possible because Rust's type
system makes variant sets known at compile time; for integers and strings, a
wildcard `_` is mandatory.

Pattern forms include constructors (`Some(x)`), tuples, structs, slices
(`[first, rest @ ..]`), ranges (`1..=10`), literals, `@` bindings, `ref`/`ref
mut` (explicit borrow), and or-patterns (`A | B`). Match ergonomics (Rust 2018)
automatically inserts `ref` when matching references, making the binding mode a
compiler inference rather than a programmer annotation. Guards use `if` after the
pattern; a critical interaction: Rust warns when the last arm has a guard
because exhaustiveness cannot be proven across a guard that could return `false`.
The language distinguishes irrefutable patterns (`let`, function parameters) from
refutable ones (`match`, `if let`), rejecting refutable patterns in irrefutable
positions at compile time.

### 2.2 Swift

Swift's `switch` is exhaustive for enums (compile error) but requires only a
`default` case for non-enum types. `switch` is primarily a statement, though
Swift 5.9 added expression forms. The key Swift innovation is the `~=` operator:
`case 1..<10:` calls `~=` with the range and the value, and types can override
`~=` to make themselves matchable against custom patterns. This is a middle
ground between closed patterns (Rust) and open extractors (Scala) — matching is
extensible but decomposition structure is not.

Swift uses `where` for guards (`case let person where person.age >= 18`) and
allows `let`/`var` anywhere in the pattern for per-variable mutability control.
`if case` and `guard case` handle single refutable pattern arms; `guard case let
.success(value) = result else { return }` is the idiomatic early-return pattern.
Swift lacks dedicated or-pattern syntax, using comma-separated values instead.

### 2.3 Kotlin

Kotlin's `when` is both expression and statement, with exhaustiveness only
enforced for sealed classes in expression position — a confusing distinction
where the same keyword has different checking behavior based on context.
Kotlin's fundamental mechanism is **smart casts** rather than pattern-introduced
bindings: after `when (x) { is String -> x.length }`, `x` is narrowed to
`String` via flow-sensitive typing. No new names are introduced; the existing
name acquires a more specific type.

Pattern forms include type-check (`is`), range (`in`/`!in`), literals, and
arbitrary boolean expressions (no guard keyword — just write the expression).
Destructuring declarations (`val (name, age) = person`) use `componentN()`
operators but are irrefutable, not pattern matches. Kotlin lacks or-pattern
syntax and relies on multi-line cases or comma-separated conditions instead.

### 2.4 Scala 3

Scala 3's `match` is the most extensible pattern system in any mainstream
language. Extractor objects via `unapply` make pattern matching open: any type
with `unapply` in its companion object can be decomposed in patterns. `unapply`
returns `Option[(A, B, ...)]` — `None` means no match, `Some(values)` provides
extracted parts. This is Scala's key innovation and key cost: `unapply` can have
side effects, allocate, and fail at runtime.

Pattern forms include constructors (via `unapply`), type patterns (`case x:
String =>`), stable identifier patterns, sequence patterns with `*:` (`case head
*: tail =>`), tuple patterns, `@` bindings, and `|` for or-patterns (same
bindings required on both sides). Exhaustiveness is a compiler warning (error
with `-Xfatal-warnings`) for sealed types only — you cannot prove an arbitrary
`unapply` covers all cases. Scala allows irrefutable patterns in `val`
definitions (`val Person(name, age) = getPerson()`), throwing `MatchError` on
failure.

### 2.5 OCaml

OCaml is the ML-family ancestor that modern pattern matching descends from.
`match` is always an expression. Exhaustiveness is a compiler warning by default
— OCaml is famous for precise warnings that list uncovered cases — but not a
compile error. The `function` keyword provides sugar for single-argument
matching without naming the argument (`function | Pat1 -> expr1 | Pat2 ->
expr2`), bridging pattern matching into function position.

Pattern forms include constructors (variants), records, tuples, lists (`h :: t`,
`[a; b; c]`), arrays (since 4.12), literals, `as` patterns, lazy patterns
(`lazy p`), and or-patterns. Guards use `when`. OCaml also has polymorphic
variants (structural, not nominal), where exhaustiveness is harder because the
compiler cannot enumerate all possible tags. All bindings are immutable — there
is no `mut` and OCaml's `ref` cells are a separate mutation mechanism, not a
pattern keyword.

### 2.6 Haskell

Haskell splits pattern matching across two positions with identical semantics:
`case` expressions and function definition clauses (each clause is tried top to
bottom). `case x of Pat1 -> expr1; Pat2 -> expr2` is always an expression.
Exhaustiveness is a compiler warning via GHC's coverage checker — precise about
uncovered cases, but a runtime exception if triggered.

Haskell's pattern system is the most layered of any statically typed language.
Beyond constructors, tuples, lists (`(x:xs)`, `[a, b, c]`), literals, and `@`
as-patterns, it offers: view patterns (`(f -> pat)` — apply `f`, match the
result), pattern synonyms (user-defined named patterns that expand to other
patterns), GADT patterns (type refinement through matching), irrefutable patterns
(`~(a, b)` — always succeeds, lazily binds), and or-patterns (`-XOrPatterns`).
N+k patterns (`(n+1)`) were removed in Haskell 2010 after community backlash.
Guards use `|` before `=` in function clauses and `| guard -> expr` in `case`.
View patterns and pattern synonyms are powerful but create subtle interactions
with or-patterns (same-binding requirements apply after expansion) and
exhaustiveness (pattern synonyms make coverage harder to prove).

### 2.7 F#

F# inherits OCaml's pattern matching but adds **active patterns** — the single
most distinctive feature in the F# pattern system. Three kinds: single-case
(always succeed, used as views), partial (return `Some` or `None` via `_|`
naming), and parameterized (take extra arguments). Active patterns are functions,
so they can fail, have side effects, and throw — all inside what looks like a
structural match. This breaks exhaustiveness: the compiler cannot know whether a
set of partial active patterns covers all cases.

Pattern forms include constructors (union cases), tuples, records, list/array
patterns, literals, `as` patterns, type test patterns (`:? Type as name`), and
active patterns. Guards use `when`. Exhaustiveness is a compiler warning for
discriminated unions only; `MatchFailureException` is the runtime fallback. `|`
provides or-patterns with same-binding restrictions.

### 2.8 Elixir

Elixir treats `=` as the fundamental pattern matching operator — even simple
assignment is a pattern match. `a = 1` matches the irrefutable variable `a`
against `1`. `1 = a` matches literal `1` against `a`'s value (failing if they
differ). The pin operator `^x` matches against the existing value of `x` without
rebinding. `case` is always an expression; exhaustiveness is a runtime error
(`CaseClauseError`) — the dynamic type system makes static exhaustiveness
impossible.

Elixir's most distinctive use of patterns is in function clauses: multiple
definitions of the same function are tried in first-match-wins order at the call
site. The `with` expression provides pattern-based monadic chaining without a
monad: `with {:ok, user} <- fetch(id), {:ok, email} <- validate(user) do
send(email) end`. Patterns include tagged tuples (`{:ok, value}` — Elixir uses
atoms as tags rather than nominal constructors), lists (`[head | tail]`),
maps, binary/bitstring patterns, and literals. Guards are restricted to a
whitelist of pure BIFs — arbitrary functions are forbidden because guards are
evaluated by the pattern compiler, and side effects would break optimization.
Patterns rebind variables by default; `^` opts out.

### 2.9 Gleam

Gleam is a typed language on the BEAM that gives Elixir/Erlang-style patterns
compile-time exhaustiveness (hard error, not warning). This is possible because
Gleam has static, nominal custom types on top of the BEAM's dynamic runtime.
`case` is always an expression. `let assert Ok(x) = result` is the irrefutable
pattern assertion — the `assert` keyword makes the assertion explicit, so you
cannot accidentally write a refutable pattern in `let` position.

Pattern forms include constructor patterns (from custom types), tuples, lists,
literals, variable captures, and `..` for discarding record parts. Gleam does
not yet have guards in `case` arms, or-patterns, or as-patterns — the community
is actively discussing adding guards, with exhaustiveness interaction as the
primary concern.

### 2.10 Racket

Racket's `match` is a macro-implemented library (not a built-in construct) with
the richest set of pattern forms of any language. `match` is always an
expression; exhaustiveness is a runtime error. Because `match` is a macro that
expands to lower-level code, user-defined pattern forms are possible via
`define-match-expander` — the pattern language grows with the program.

Pattern forms include `cons`/`list`/`list-rest` for list structure, `struct` for
struct types, `regexp`/`regexp-match` for regular expressions, `==` for equality
against computed expressions, `?` for predicate patterns (matches if `(predicate
value)` is true), `app` for view patterns (apply function, match result), `...`
(ellipsis) for repeated sub-patterns, `and` for conjunction, `or` for
or-patterns, `not` for negation, and quasiquote patterns. Predicate and `app`
patterns can have arbitrary side effects. The extensibility comes at the cost of
static analysis: exhaustiveness and reachability are impossible to prove for
user-defined pattern expanders.

---

## 3. Cross-Language Synthesis

### 3.1 What's Structurally The Same (Just Syntax Sugar)

These elements are identical across languages. Different naming, same semantics:

**The `match` keyword -> cases -> body shape.** Every language arranges patterns
as an ordered sequence of alternatives. Order is always top-to-bottom,
first-match-wins. Whether called `match`, `case`, `switch`, `when`, or `cond`,
the control flow is identical.

**Pattern bindings create local scope.** Variables bound in a pattern are
available in the corresponding body and guard, not in other arms. This is
universal — no language leaks pattern bindings across arms.

**Guards add a boolean filter after pattern match.** Every language with guards
places them between pattern and body. The guard has access to pattern bindings.
Guard failure is treated identically to pattern failure: continue to next arm.

**The `_` wildcard.** Nearly universal — Rust, Swift, Scala, OCaml, Haskell,
F#, Gleam all use `_`. Racket uses both `_` and `(var _)`. This is syntactic
convergence so strong it hardly counts as a design choice.

**Constructor patterns for algebraic types.** `Some(x)`, `Ok(v)`,
`Person(name, age)` — the same surface syntax across the entire ML family
(OCaml, Haskell, F#, Scala, Rust, Swift, Gleam). Constructor name followed by
sub-patterns.

**All forms reduce to Choose + Contain + Bind.** Every pattern matching system
decomposes to: test the shape (Choose), create a scope for the body (Contain),
bind the captured parts (Bind). A guard adds another Choose between pattern
success and body execution.

### 3.2 What's Semantically Different (Genuine Design Choices)

These are real forks in the design space. Compromises here create permanent
language character.

#### 3.2.1 Extensibility: Built-in-only vs Extractor/Active Patterns

This is the deepest divide. **Built-in-only** (Rust, OCaml, Gleam) means the
compiler knows every pattern form — exhaustiveness is provable, compilation is
optimal, but only the language designer can add patterns. **Extractor/active
patterns** (Scala `unapply`, F# active patterns, Racket `app`, Haskell view
patterns) make patterns open — any type can be decomposed — but exhaustiveness
is unprovable, `unapply` can have side effects, and pattern compilation must
generate function calls where it would normally do direct field access. **Swift's
`~=`** is a middle ground: matching is extensible but pattern structure remains
closed.

#### 3.2.2 Binding Mechanism: Smart Casts vs Explicit Pattern Binding

**Smart casts / flow typing** (Kotlin, Swift, TypeScript): the matched
variable's type is narrowed; no new names are introduced. This preserves the
"one name, refined understanding" model. **Explicit pattern binding** (Rust,
OCaml, Haskell, Scala, Elixir, Gleam): patterns introduce new names. You can
name both the whole and the parts (`match x { Person { name } as whole => ...
}`). The two approaches feel different to program in, even though they're
equivalent when desugared.

**Binding mode** (Rust's `ref`/`ref mut`, match ergonomics): Does the binding
create a reference or a value? Rust defaults to move-or-copy and uses `ref` for
borrowing; match ergonomics infers this from the matched reference. OCaml and
Haskell avoid this because everything is immutable and GC'd.

#### 3.2.3 Exhaustiveness Enforcement

```
                     Compile Error           Compile Warning          Runtime Error
                     ─────────────           ───────────────          ─────────────
Always               Rust, Gleam             (nobody — warnings
                                              can be silenced)
ADTs only            Swift (switch)          OCaml, Haskell           Scala (extractors
                                                                    on non-sealed types)
Never                                                            Elixir, Racket,
                                                                 Erlang, Clojure
```

The exhaustiveness choice depends on the type system: static makes it possible,
nominal makes it easier, dynamic makes it impossible. OCaml and Haskell's choice
of warnings over errors is pragmatic — iterate without fixing every case, then
promote to errors in production builds.

#### 3.2.4 Pattern Ordering

All languages but Erlang use top-to-bottom, first-match-wins. Erlang function
clauses have no ordering guarantee — the compiler may reorder for performance,
creating a subtle non-determinism absent from every other language surveyed.

#### 3.2.5 Or-Pattern Binding

Every language with or-patterns faces the same problem: what happens when only
one side binds a variable? **Rust, Scala 3, OCaml:** require both sides to bind
the same variables with the same types. `Some(x) | None` is rejected. **Racket:**
bindings depend on which side matched — a different semantic. **Elixir:** no
or-pattern syntax; multi-clause functions serve the same purpose.

#### 3.2.6 Where Patterns Can Appear

| Position | Rust | Swift | Haskell | Elixir | Scala |
|----------|------|-------|---------|--------|-------|
| `match`/`case` | Yes | Yes | Yes | Yes | Yes |
| `if let`/`if case` | Yes | Yes | No (use case) | No (use case) | No (use match) |
| `while let` | Yes | No | No | No | No |
| Function clause heads | No | No | Yes | Yes | No |
| Assignment (`let`/`val`) | Yes (irrefut.) | Yes (if case) | Yes (irrefut.) | Yes (= is match) | Yes (throws) |
| `for`/comprehension | Yes | Yes | Yes | Yes | Yes |

"Everything is a pattern" languages (Elixir, Haskell) put patterns everywhere
but blur matching vs binding. "Match as a dedicated construct" languages (Rust,
Scala) keep patterns inside match forms but make semantics clearer.

#### 3.2.7 Guards: Expression Restrictions

- **Unrestricted** (most typed languages): any boolean expression.
- **Restricted whitelist** (Erlang, Elixir): only built-in BIFs, no user
  functions — guarantees purity and enables pattern compiler optimization.
- **No guards** (Gleam, Go, early Python match): use `if` in the body instead.

---

### 3.3 Key Tensions When Combining Approaches

These are the places where picking features from different traditions creates
genuine semantic conflict. Each one is a decision Nomi must make explicitly.

#### Tension 1: Exhaustiveness + Guards

A guarded pattern can never be proven exhaustive because the guard can always
be `false`. Different responses: Rust warns when the last arm has a guard;
OCaml/F# emit non-exhaustiveness warnings even when all constructors are covered
(with guards); Scala marks the match as potentially non-exhaustive; Haskell/GHC
warns about non-exhaustive patterns despite guards.

**For Nomi:** The constraint system is the bridge. Guards are constraints on
bindings. Exhaustiveness becomes: "Can the constraint solver prove the
disjunction of all guard-constraints is `true`?" — undecidable in general. Nomi
should: (1) prove exhaustiveness for unguarded patterns over known types; (2)
emit a constraint-cannot-be-proven diagnostic when a guard appears on an
otherwise covering set; (3) never silently treat a guarded exhaustive set as
actually exhaustive.

#### Tension 2: Pattern Binding + Smart Casts

If a language has both flow-sensitive type narrowing AND pattern-introduced
bindings, what does `match x { Some(y) => ... }` mean? Is `y` a narrowing of
`x` or a new binding? Rust-style explicit bindings are simpler to specify and
debug. Smart casts are syntactic convenience that can be added later without
changing binding semantics.

**For Nomi:** Pick explicit pattern binding (Rust-style) for the first language.
Pattern-introduced names are new bindings, not type refinements of existing
names. `@` syntax names the whole matched value. This gives clean scope rules
and avoids cross-arm type tracking complexity.

#### Tension 3: Extractor Objects + Exhaustiveness

Scala's `unapply` and F#'s active patterns make patterns open, but
exhaustiveness requires a closed set. This tension has no clean resolution:
either allow extractors and weaken exhaustiveness, or enforce exhaustiveness
and restrict patterns to ADTs. No language handles both cleanly.

**For Nomi:** Prioritize exhaustiveness. The first language has closed pattern
forms. Active patterns are a Phase 3 feature if adopted at all — when added,
they must be marked as exhaustiveness-breaking with compiler diagnostics.

#### Tension 4: Deep Destructuring + Error Diagnostics

When `match user { Ok(Person { name: Email(addr) }) => ... }` fails, which layer
failed? Ok? Person? Email? No language in this survey provides layered
diagnostics for nested pattern failure. Rust prints the overall non-exhaustive
match; Scala throws `MatchError` with the value; F# throws
`MatchFailureException`.

**For Nomi:** This is where Nomi's explanation system differentiates. A pattern
failure should produce a structural trace: depth, pattern at each level,
expected vs actual shape, which sub-pattern failed. Pattern failure and
constraint failure should produce different diagnostic events that can be
inspected separately. A guard failure should be distinguishable from a shape
failure.

#### Tension 5: Pattern Matching in Function Position

Elixir and Haskell put patterns directly in function clause heads. Is this
worth the duplicate syntax? Arguments for: concise for single-argument dispatch,
visually groups behavior by function name, natural for recursion over inductive
types. Arguments against: duplicates pattern syntax in two grammar positions,
harder to see all cases at once, complicates exhaustiveness checking scope.

**For Nomi:** Nomi's piecewise equations (already in the spec) are this feature,
as sugar over `match`. The key rule: all clauses of a function must be
contiguous. No interleaving clauses for different functions. This preserves "all
cases together" while providing function-clause conciseness.

#### Tension 6: Match-as-Expression + Statement Bodies

Match-as-expression requires consistent return types across arms.
Match-as-statement allows mixed side effects. Rust's answer: `match` is always
an expression; use `()` for statement-like arms. Kotlin's answer: `when` is
context-dependent, but this creates the exhaustiveness asymmetry.

**For Nomi:** Keep match as always-expression (Rust/Scala model). The divergence
rule (arms that raise/return/break satisfy any type) handles statement context.
A match whose value is discarded is just an expression in statement position.

### 3.4 What Breaks When Combining Features From Different Traditions

**Smart casts (Kotlin) + explicit `ref` (Rust):** The type of a binding would
depend on HOW it was matched — reference type from flow narrowing vs borrowed
reference from `ref`. The approaches give different answers for nested patterns,
mutable values, and aliased references. Resolution: pick one model for v1
(explicit bindings).

**Active patterns (F#) + exhaustiveness checking (Rust):** Fundamentally
incompatible. Active patterns call arbitrary functions; exhaustiveness requires
knowing all outcomes. Every language that has both weakens one. Resolution:
prioritize exhaustiveness.

**Multiple clause functions (Elixir) + unrestricted guards (Haskell):** Elixir
restricts guards to a BIF whitelist; Haskell allows any expression. The conflict
is about when guards are evaluated — compile time (pattern compilation) vs
runtime (normal evaluation). For Nomi's Python-hosted interpreter, guards are
always runtime expressions.

**Pattern synonyms (Haskell) + or-patterns (Rust):** Do pattern synonyms
distribute over or-patterns? What bindings result? Haskell treats synonyms as
opaque — bindings are what the synonym declares, not what it expands to — but
GHC has open bugs in this interaction. Resolution: don't add pattern synonyms
to v1.

---

## 4. Comparison Tables

### 4.1 Feature Matrix

| Language | Match Expr? | Exhaustiveness | Guards | Or-Patterns | Active/Extractor | Binding Style | Irrefutable in Let? |
|----------|------------|----------------|--------|-------------|------------------|---------------|---------------------|
| Rust | Yes (always) | Compile error | `if` after pattern | Yes (same bindings) | No | New bindings, `ref`/`ref mut`, ergonomics | Yes (`let`, fn params) |
| Swift | Statement (expr 5.9+) | Compile error, enums | `where` after pattern | Comma-separated values | `~=` operator | `let`/`var` in pattern | `if case`, `guard case` |
| Kotlin | Both (context-dep.) | Error, sealed + expr | Boolean expr inline | No dedicated syntax | No (smart casts) | Smart cast (type narrow) | Destructuring only |
| Scala 3 | Yes (always) | Warning, sealed types | `if` after pattern | Yes (same bindings) | `unapply` extractors | New bindings, `@` | Yes (throws on fail) |
| OCaml | Yes (always) | Warning, all variants | `when` after pattern | Yes (same bindings) | No | New bindings, immutable | Yes (`let`, throws) |
| Haskell | Yes (always) | Warning, all types | `\|` before `=`, `if` in case | Yes (`-XOrPatterns`) | View patterns, pat synonyms | New bindings, immutable, `@` | Yes (lazy with `~`) |
| F# | Yes (always) | Warning, unions only | `when` after pattern | Yes (same bindings) | Active patterns (3 kinds) | New bindings, immutable, `as` | Yes (`let`, throws) |
| Elixir | Yes (always) | Runtime error only | Restricted BIF whitelist | No (multi-clause) | No | New bindings, rebindable, `^` | Yes (`=`) |
| Gleam | Yes (always) | Compile error | Not yet | Not yet | No | New bindings, immutable | `let assert` only |
| Racket | Yes (always) | Runtime error only | `?` predicate pattern | Yes (`or`) | `app`, `define-match-expander` | New bindings | `match-define` only |

### 4.2 Pattern Form Matrix

| Language | Constructor | Tuple | List/Array | Record/Map | Literal | Wildcard | Range | Type Test | Predicate | View/Extractor |
|----------|-------------|-------|------------|------------|---------|----------|-------|-----------|-----------|----------------|
| Rust | Yes | Yes | Yes (slice) | Yes (struct) | Yes | `_` | Yes (`..=`) | No | No (guards) | No |
| Swift | Yes (enum) | Yes | Yes | No (dict only) | Yes | `_` | Yes (`~=`) | `is` | No (where) | `~=` |
| Kotlin | Yes (sealed) | Yes (destr) | Yes | No (map acc) | Yes | `_` | Yes (`in`) | `is` | Yes (inline) | No |
| Scala 3 | Yes (ADT) | Yes | Yes (`*:`) | Yes (case cl) | Yes | `_` | No | `: Type` | No (if) | `unapply` |
| OCaml | Yes (var) | Yes | Yes (`::`) | Yes (record) | Yes | `_` | No | No | No (when) | No |
| Haskell | Yes (data) | Yes | Yes (`:`) | Yes (record) | Yes | `_` | No | No (GADTs) | No (guards) | View patterns |
| F# | Yes (union) | Yes | Yes (`::`) | Yes (record) | Yes | `_` | No | `:?` | No (when) | Active pat |
| Elixir | Yes (tagged) | Yes | Yes (`[\|]`) | Yes (map) | Yes | `_` | No | Guard `is_` | Guard BIFs | No |
| Gleam | Yes (custom) | Yes | Yes (list) | No | Yes | `_` | No | No | No | No |
| Racket | Yes (struct) | Yes | Yes (`cons`) | Yes (hash) | Yes | `_` | No | No | `?` | `app` |

---

## 5. Synthesis for Nomi

### 5.1 What Nomi Already Has Right

The Nomi spec already captures the correct normal form: `test structure ->
tentatively bind captures -> check constraints/guard -> choose body or fail
without committing captures`. The four-stage pipeline makes each failure mode
independently diagnosable and each stage independently implementable. The
surface forms (`match`, `if let`, `guard let`, `while let`, piecewise equations)
are the right set for a first language. The reduction of `if let` and `guard
let` to `match` is semantically clean and should be preserved.

### 5.2 Concrete Lessons

**Lesson 1: Exhaustiveness should be a compile error, not a warning.** Rust and
Gleam prove this is viable. For a language that aims to make failures
inspectable, an exhaustiveness gap the compiler knows about but only warns about
is a failure of the explainability goal. Make exhaustiveness a hard error for
known types. For open types (Python objects, external data), require an explicit
`_` or `else`.

**Lesson 2: Guards are constraints, not a separate language feature.** Nomi
already has a constraint system. `case Person(name, age) if age >= 18` desugars
to: bind `name`, `age`; check constraint `age: (>= 18)`. If constraint fails,
skip to next arm. The `if` keyword is sugar for attaching a constraint to a
binding. Guard failure and constraint failure use the same diagnostic path.

**Lesson 3: Bindings in patterns should be immutable and explicit.** Follow
Rust/Scala/OCaml, not Kotlin's smart cast model. Pattern-introduced names are
new bindings. Use `@` for naming the whole matched value. Smart casts create
cross-arm scope questions and type-tracking complexity that Nomi's first
language does not need.

**Lesson 4: Or-patterns require same-bindings on both sides.** Follow
Rust/Scala/OCaml. Racket's approach (bindings depend on which side matched) is
too dynamic for exhaustiveness checking and clear scoping. Reject `Some(x) |
None` at compile time.

**Lesson 5: Pattern failure must produce layered diagnostics.** No existing
language does this well. Nomi should. When a nested pattern fails, the
diagnostic should report depth, pattern at each level, expected vs actual, which
sub-pattern failed. This is a natural application of Nomi's explanation normal
form. Three diagnostic event kinds: structural failure (shape tree with depth
annotations), constraint failure (violated constraint with binding value), guard
failure (evaluated guard expression with sub-expression trace).

**Lesson 6: Defer extractors and active patterns.** The first language should
have closed pattern forms. Extractors break exhaustiveness, hide side effects,
and solve a problem (extensible decomposition) that a first language doesn't
have. All decomposition goes through the type system's constructors. Revisit in
Phase 3.

**Lesson 7: Keep match as expression, not statement.** Rust and Scala prove this
is cleaner. A match whose value is discarded is just an expression in statement
position. This avoids Kotlin's context-dependent exhaustiveness problem.

**Lesson 8: Piecewise equations as sugar over match.** Nomi's piecewise
equations desugar to `match` and should always be presented that way. All
clauses of a function must be contiguous to preserve "all cases together" and
make exhaustiveness tractable at the function level.

### 5.3 How Patterns Interact with Nomi's Constraint System

**Constraint failure during matching:** When a pattern binds `x` and a
constraint `x: (> 0)` is checked, constraint failure skips to the next arm — not
a runtime error. This is already in the Nomi spec. It keeps pattern matching
tentative: a failing constraint is "this arm doesn't apply," not "the program is
wrong."

**Guard = constraint sugar:** `case Person(name, age) if age >= 18` desugars to
binding + constraint check. The `if` keyword is inline constraint syntax on a
binding.

**Constraint composition:** Multiple constraints on a binding compose with
`and`/`or` but the semantics are: all must succeed for the arm to match. This is
the same model used for binding constraints elsewhere in Nomi.

**Constraint error vs pattern error:** These are different failure modes with
different diagnostics. Pattern failure: "expected Ok(value), got Err(error)."
Constraint failure: "binding age=17 did not satisfy constraint (>= 18)." This
distinction is essential for the explanation system.

### 5.4 Essential Pattern Forms for the First Language

1. **Literal patterns** — `42`, `"hello"`, `true` (implemented)
2. **Wildcard `_`** — match anything, bind nothing (implemented)
3. **Capture patterns** — bind a name to the matched value (implemented)
4. **Constructor patterns** — `Ok(value)`, `Some(x)` for Nomi's variant types
5. **Tuple patterns** — `(a, b, c)` for product types
6. **List patterns** — `[head, *tail]`, `[]` (starred rest implemented)
7. **Or-patterns** — `A | B` with same-binding restriction (implemented)
8. **Guards** — `if condition` after pattern (implemented)
9. **`@` as-patterns** — `whole @ pattern` for naming both levels

### 5.5 Pattern Forms to Defer

1. **Range patterns** (`1..=10`) — guard `if x >= 1 and x <= 10` covers this
2. **Extractor/active patterns** — breaks exhaustiveness; revisit Phase 3
3. **View patterns** — same problem; guard expressions cover it
4. **Pattern synonyms** — power-user feature; not for v1
5. **Regular expression patterns** — second mini-language problem; string
   methods + guards cover this
6. **Bitstring/binary patterns** — excellent for binary protocols but too
   domain-specific for v1

### 5.6 Pattern-Match Diagnostic Composition

This is Nomi's opportunity to improve on every language surveyed. Current
languages give "match error at line X" and maybe the value. Nomi can produce
structured diagnostic events:

**Structural failure:**
```
match result:
  case Ok(Person(name=FullName(valid), age=Adult(21..))):
      ...

Diagnostic: pattern match failed at depth 3
  depth=0: constructor Ok matched successfully
  depth=1: constructor Person matched successfully
  depth=2: field 'age' matched successfully
  depth=3: constructor Adult FAILED — expected Adult(age >= 21), got Adult(17)
  trace: result.Ok.Person.age.Adult
```

**Constraint failure:**
```
Diagnostic: constraint failure in guard
  binding: age = 17
  constraint: (>= 18)
  context: case Person(name, age) if age >= 18
```

**Guard failure:**
```
Diagnostic: guard evaluated to false
  guard expression: age >= 18 && verified
  bindings: age = 25, verified = false
  failing sub-expression: verified
```

These three diagnostic types should be separate event kinds in Nomi's
explanation system, each carrying the structured trace needed for tooling to
display failure at the right granularity.

### 5.7 The Red Line: What Nomi's Pattern System Must NOT Do

1. **Don't duplicate pattern syntax in function definitions and match
   expressions in the grammar.** Piecewise equations are sugar; keep one parse
   path.

2. **Don't make exhaustiveness depend on expression-vs-statement context.**
   Kotlin's `when` has different rules based on context. Nomi's `match` should
   always be exhaustive for known types, always require `_`/`else` for open
   types.

3. **Don't allow side effects in pattern decomposition.** Scala's `unapply` and
   F#'s active patterns let matching trigger arbitrary computation. This breaks
   the mental model of "pattern = structural check."

4. **Don't create a separate guard mini-language.** Elixir's guard BIF whitelist
   is a second mini-language (the anti-pattern from `design_lessons_and_integration.md
   section 1.1`). Nomi's guards are constraints, and constraints are expressions.

5. **Don't allow pattern-match failure to silently propagate as `none`.** Be
   explicit: exhaustively match when cases are known, require `else`/`_` when
   they aren't, and raise a diagnostic on failure — not silently propagate
   absence.

---

## 6. Sources Referenced

- Rust Reference: The `match` expression (https://doc.rust-lang.org/reference/expressions/match-expr.html)
- Rust Reference: Match ergonomics RFC 2005
- Swift Language Guide: Control Flow — Switch (https://docs.swift.org/swift-book/documentation/the-swift-programming-language/controlflow/)
- Swift Evolution: SE-0380 — `if` and `switch` expressions
- Kotlin Language Guide: Conditions and loops — `when` (https://kotlinlang.org/docs/control-flow.html)
- Scala 3 Reference: Pattern Matching (https://docs.scala-lang.org/scala3/reference/changed-features/pattern-matching.html)
- OCaml Manual: Patterns (https://ocaml.org/manual/5.2/patterns.html)
- GHC User's Guide: Pattern match coverage checking (https://downloads.haskell.org/ghc/latest/docs/users_guide/exts/pattern_match_coverage.html)
- F# Language Reference: Pattern Matching (https://learn.microsoft.com/en-us/dotnet/fsharp/language-reference/pattern-matching)
- Elixir: Pattern matching and guards (https://hexdocs.pm/elixir/patterns-and-guards.html)
- Gleam Language Tour: Case expressions (https://tour.gleam.run/data-types/case-expressions/)
- Racket Guide: Pattern Matching (https://docs.racket-lang.org/reference/match.html)
- Landin, P. J. "The Next 700 Programming Languages." Communications of the ACM, 1966.
- Nomi project: `language_design_dimensions.md`, `language_spec.md`, `convenience/patterns.md`,
  `convenience/design_lessons_and_integration.md`
