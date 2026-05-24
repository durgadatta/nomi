# Design Lessons & Integration Critique

> Status: active synthesis. This document is the critical integration
> layer — it does not catalogue syntax. It analyses how features compose,
> conflict, and evolve across languages, then translates those lessons
> into Nomi integration decisions.
>
> Companion: [review_and_roadmap.md](review_and_roadmap.md) for feature
> status and phases. Source research lives in `docs/research/`.

## Purpose

Collecting syntax from other languages is easy. Understanding what
happens when you combine them — what breaks, what becomes redundant,
what splits the user community — is the real design work.

This document:

1. Names **systemic patterns** of language cruft (the kinds of mistakes
   that accumulate over a language's lifetime, not one-off bugs).
2. Maps **feature interactions** — what happens when surface sugar X
   collides with surface sugar Y.
3. Collects **community praise and regret** from established languages,
   with concrete designer quotes where available.
4. Gives **integration decisions** for each normal form, prioritising
   coherence over accumulation.

## 1. Systemic Cruft Patterns

These patterns repeat across languages. They are not about one bad
decision — they are about decision *structures* that reliably produce
accumulated complexity.

### 1.1 The Second Mini-Language

Every language eventually adds a second mini-language for validation,
configuration, templating, or querying. Once that second language exists,
it grows its own features, its own community, and its own incompatibility
with the host language.

| Language | Mini-language | Pain |
|----------|---------------|------|
| Python | `re` regex, `string.Formatter`, `configparser` format strings, `logging` format syntax | Each has different escape rules and expression power; none compose |
| JavaScript | JSX, CSS-in-JS, GraphQL, regex literals | JSX is not quite JS; template expressions don't compose |
| Ruby | ERB, regex with `$1`/`$&` globals, RSpec DSL | `$` globals leak between regex matches |
| SQL | String interpolation in every host language | The most famous second-language problem in programming |
| Scala | SBT build definitions (`.sbt` is its own dialect), ScalaCheck property DSL | Build definition is a third of the learning curve |
| Rust | `macro_rules!` (its own pattern language), proc macros (arbitrary Rust that writes Rust) | Two macro systems with different power and debugging |
| Kotlin | Gradle Kotlin DSL (looks like Kotlin, isn't quite), `build.gradle.kts` | Build script errors don't point at source lines |

**Lesson for Nomi:** Every time a feature proposal includes "a small
expression language," "a simple pattern syntax," or "a tiny query
dialect," that is the second-mini-language trap. The right response:
reduce it to an existing normal form or reject it. Nomi already has
binding, pattern, and function — three tools for expression. New syntax
must compose with these, not replace them.

### 1.2 The Convenience Stack-Collapse

A language adds convenience feature A, then feature B that overlaps with
A, then feature C that combines A and B differently. Users now have
three ways to express the same thing, and style guides grow chapters
about which to use.

| Language | Overlapping features | Resolution |
|----------|---------------------|------------|
| Python | `%` formatting, `.format()`, f-strings | f-strings won but the others remain |
| Python | `unittest`, `pytest`, `nose`, `doctest` | `pytest` is de facto standard, others linger |
| Scala | `implicit` parameters, `given`/`using`, context bounds | Scala 3 replaced `implicit` with `given`/`using` (painful migration) |
| Rust | `try!()` macro, `?` operator, `Try` trait | `?` replaced `try!()` cleanly (edition-based) |
| JavaScript | callbacks, Promises, `async/await` | `async/await` is preferred but Promises remain as values |
| Go | `GOPATH`, `vendor`, `dep`, Go Modules | Modules won after years of fragmentation |
| Ruby | `Test::Unit`, `MiniTest`, `RSpec` | Still fragmented after 15+ years |

**Lesson for Nomi:** When adding surface sugar, ask: "Does this replace
an existing spelling, or sit alongside it?" If it sits alongside, define
the sunset path for the older spelling. If there is no sunset path,
the sugar is probably not worth adding. Nomi's surface-convenience rule
(desugar to a normal form the tooling can show) is the right gate.

### 1.3 The Implicit Power Escalator

A language adds an implicit feature to reduce boilerplate. Users like
it. The language adds more implicit features. Now understanding a single
line of code requires reconstructing invisible context.

| Language | Implicit feature | Escalation |
|----------|-----------------|------------|
| Scala | `implicit` parameters | Grew into `implicit` conversions, `implicit` classes, type-class derivation — Scala 3 replaced the whole system |
| Ruby | `method_missing` | Every DSL framework used it differently; `respond_to_missing?` added to patch the hole |
| Python | `__getattr__`, `__getattribute__` | Proxy objects, RPC stubs, and ORMs all use different conventions |
| Haskell | `{-# LANGUAGE #-}` pragmas | Over 100 extensions; a module's meaning depends on its pragma header |
| Kotlin | `receiver` lambdas | Powerful for DSLs; `@DslMarker` added to prevent accidental outer-scope access |

**Lesson for Nomi:** Implicit power should be scoped and visible. Nomi's
design preference (explicit boundary words, one binding story, normal-form
reduction that tooling can show) is the right defence. The `where:` clause
is a good example — it makes local scope explicit rather than reaching
into surrounding scope implicitly.

### 1.4 The Performance-Transparency Cliff

A language starts with a simple performance model. As it adds features,
the performance model becomes unintuitive. Users learn rules of thumb
("never do X in a hot loop") that aren't in the docs.

| Language | Simple model | Reality |
|----------|-------------|---------|
| Python | Interpreted, everything is an object | `__slots__`, `@dataclass`, `namedtuple`, `array.array` — five ways to get "struct-like" memory |
| Ruby | Everything is an object, GC handles memory | Symbol GC, frozen strings, `ObjectSpace` — memory leaks from symbol accumulation were a multi-year bug |
| Julia | Type-stable code runs fast | "Type stability" is a learnable but non-obvious discipline; `@code_warntype` is essential |
| Go | Goroutines are cheap | Goroutine stack starts at 2KB, grows; blocking syscalls spawn OS threads; the model is leaky |
| Haskell | Lazy evaluation | Space leaks from thunk accumulation are a distinct debugging skill; `seq`, `deepseq`, `!` patterns |

**Lesson for Nomi:** For the first everyday layer, prefer predictable
eager evaluation with explicit laziness markers. Nomi follows Python
here, which is the right call. If laziness is added later (for streaming,
query plans, etc.), make it opt-in with visible syntax.

## 2. Feature Interaction Analysis

When two features from different source languages land in the same
language, the interaction is often the source of the worst bugs.

### 2.1 Holes + Blocks + Where

Nomi already has implicit function holes (`_`, `$1`, `$name`), block
calls (`f(x) -> p: body`), and where clauses (`expr where: defs`).

**Interaction risk:** A `$name` hole inside a block-call body inside a
where clause creates three nested scopes with different capture rules.

```
result = compute(x) where:
    factor = x * 2
    compute = each(data) -> item:
        step = item + $offset  # $offset captured from... where? caller?
```

The scoping rule ("innermost enclosing scope that has the name, or
outermost function scope for holes") needs to be precise and tested.
If `$offset` is resolved at the block parameter level, it shadows the
where-clause binding. If resolved at the function level, it ignores the
where clause entirely.

**Decision:** Holes (`_`, `$1`, `$name`) capture from the **containing
function scope**, not from where-clause or block-parameter scopes.
Block parameters (`-> item`) bind in the block body only. Where-clause
bindings are local to the where body. This is three explicit scopes,
each with one job. Diagnostics must name which scope a name was resolved
in.

### 2.2 Pipeline + Composition + Holes

`x |> f` threads a value. `f >>> g` builds a function. `_ + 1` creates
a function. All three reduce to the function normal form, but they
interact at the boundary.

**Interaction risk:**

```
data |> _ + 1        # Does _ capture data? Or is data passed as first arg?
data |> f >>> g      # Is this (data |> f) >>> g or data |> (f >>> g)?
```

**Decision:** Pipeline `|>` has lower precedence than composition
`>>>`/`<<<`. So `data |> f >>> g` is `data |> (f >>> g)`. Holes (`_`)
in pipeline position treat the piped value as their input: `data |> _ + 1`
is `(_ + 1)(data)`. This is consistent but must be documented in one
place (not scattered across functions.md, flow_and_collections.md, and
the implicit functions appendix).

### 2.3 Match Expression + Block Call + Try Expression

All three can appear in expression position. The current prototype may lower
some expression-position blocks through IIFE-like wrappers because Python AST
has statement/expression boundaries that Nomi is deliberately trying to escape.
That lowering is a backend tactic, not the source-level control model. If these
forms nest, the language must specify `return`, `yield`, and `break` in Nomi
terms, not in terms of hidden wrapper functions.

**Interaction risk:**

```
result = match each(users) -> user:
    case Ok(profile): try fetch(profile) except NetworkError: default
    case Err(_): "invalid"
```

Three value boundaries nested. Does `return` in the innermost block return from
the match, the block call, or the outer function?

**Decision:** Source-level Nomi semantics should not depend on IIFE wrappers.
`return` returns from the nearest user-authored `func`; `break`/`continue`
target user-authored loops; `yield` belongs to block-call policy invocation.
Expression-position blocks should produce values with their branch expression,
not by teaching users hidden-return semantics. See
[expression_statement_orientation.md](expression_statement_orientation.md) for
the full doctrine and implementation implications.

### 2.4 Optional Chaining + Pipeline + Error Propagation

`?.` handles absence. `|>` handles flow. `?` propagation (future) would
handle expected failure. These three can appear in the same expression.

**Interaction risk:**

```
data |> f?.(x) |> g    # Does ?. short-circuit the pipeline?
                        # Does it return None from the whole pipeline?
```

**Decision:** Optional chaining `?.` short-circuits to `None` at the
point of the `?.` call — not the whole pipeline. So `data |> f?.(x) |> g`
would pass `None` to `g` if `f` is None. This is Python-compatible
behaviour. If short-circuit behaviour is desired, use `match` or an
explicit `if` guard. A future `?` propagation operator for `Result`
types would short-circuit to the error value at the pipeline step.

## 3. Community Praise and Regret

What established language communities consistently praise or regret,
with concrete evidence where available.

### 3.1 Widely Praised (do this)

| Language | Feature | Why it worked |
|----------|---------|---------------|
| Python | f-strings | Visible interpolation with expression power; replaced three older mechanisms |
| Python | `@dataclass` | Eliminated boilerplate without changing the language |
| Rust | `enum` + `match` | Exhaustiveness checking eliminates an entire class of bugs |
| Rust | `?` operator | Replaced `try!()` macro cleanly via edition mechanism |
| Go | gofmt | Removed formatting arguments from the culture entirely |
| Kotlin | null safety (`?`/`!!`) | Interop with Java nullability; gradual migration |
| Swift | `guard let` | Early exit without rightward drift |
| Elixir | `|>` pipeline | Made functional composition read left-to-right |
| F# | Type providers | Compile-time schema ingestion without codegen |
| TypeScript | Structural typing + `as const` | Gradual typing that respects JavaScript patterns |
| Zig | `errdefer` | Deferred cleanup only on error — no equivalent in any mainstream language |
| Gleam | `use` expressions | Generalized callback flattening without async coloring |

### 3.2 Widely Regretted (avoid this)

| Language | Feature | Why it failed |
|----------|---------|---------------|
| Python | `lambda` single-expression limit | Forces `def` for multi-line callbacks, breaking visual flow |
| Python | `urllib`/`urllib2` split | Standard library fragmentation; `requests` won in the ecosystem |
| JavaScript | `var` hoisting | `let`/`const` were added to fix it; `var` persists forever |
| JavaScript | `==` implicit coercion | `===` exists but both remain; the "use triple equals" rule is a cultural patch |
| Scala | `implicit` overloading | One keyword for three different mechanisms; Scala 3 replaced the system |
| Go | No generics for 10 years | `interface{}` and code generation proliferated; generics (1.18) arrived too late to prevent ecosystem fragmentation |
| Ruby | `$1`, `$&`, `$~` regex globals | Implicit state that changes after every regex match; thread-unsafe |
| Haskell | `String = [Char]` | Performance disaster; `Text` and `ByteString` are the real string types |
| Haskell | Partial functions in Prelude (`head`, `tail`) | New learners hit runtime errors from functions that look safe |
| Rust | `async` function coloring | `Pin`/`Unpin` complexity; ecosystem split between sync and async |
| Swift | String indexing (grapheme clusters) | `str[5]` is O(n); newcomers from Python/JS are consistently surprised |
| Elm | No typeclasses | Every new type needs hand-written `map`/`andThen`; ports as only interop |

### 3.3 Language Designer Regrets (publicly stated)

- **Guido van Rossum (Python):** Regretted the `lambda` limitation and
  the `map`/`filter`/`reduce` design as not Pythonic enough. "I would
  have made `lambda` more powerful... the one-expression limit is
  arbitrary and confusing."
- **Rob Pike (Go):** Has said Go's error handling verbosity is "a
  deliberate tradeoff, not a mistake" but acknowledged that "if we had
  generics from day one, a lot of `interface{}` code would never have
  been written."
- **Graydon Hoare (Rust):** Noted that the `async`/`await` design was
  "rushed" and that "the `Pin`/`Unpin` story is the most common
  legitimate complaint about Rust."
- **Martin Odersky (Scala):** Called `implicit` the "most regretted
  feature of Scala 2" and designed Scala 3's `given`/`using` as an
  explicit replacement. "One keyword for three different things was a
  mistake."
- **Chris Lattner (Swift):** Has said that ABI stability "should have
  happened earlier" and that the delay "cost Swift years of adoption."
- **José Valim (Elixir):** Has noted that Elixir's `|>` being
  first-argument-only was a limitation; discussions about `then`/`tap`
  variants show the tension.
- **Evan Czaplicki (Elm):** Regretted not having a story for
  server-side Elm earlier, noting that "ports are too restrictive for
  many real applications."

## 4. Integration Decisions by Normal Form

Each normal form gets a synthesis: what worked across languages, what
conflicts, and what Nomi should lock in.

### 4.1 Binding Normal Form

**What worked everywhere:** One binding mechanism for all name
introduction. Rust's `let`, Swift's `let`/`var`, Kotlin's `val`/`var`.

**What failed:** Multiple binding mechanisms that interact. Python's
`=` assignment + `:=` walrus + `as` in `with`/`except` + `import as`
+ `for ... in` — five syntaxes for "bind a name."

**Nomi lock-in:** One binding story (`name:constraint = value`).
Constraints are optional (`name = value` is the common case). The walrus
(`:=`) is not needed because `if-let` and `match` already bind in
expression context.

**Open question:** Should Nomi have immutable-by-default bindings?
ML-family languages and Rust say yes; Python and Ruby say no. Nomi's
current position (constraint-based, not default-immutable) follows
Python. If immutable-by-default is added, do it as a `let` keyword that
reduces to the binding normal form.

### 4.2 Function Normal Form

**What worked everywhere:** Multiple function syntaxes for different
contexts. Haskell's equations for pattern dispatch, Scala's `_` holes
for conciseness, Elixir's `&` capture for references.

**What failed:** Too many function syntaxes that overlap. Scala had
`def`, `val f = (x) =>`, `_` holes, partial application, `Function1`
trait — five ways to make a function, with subtle differences in how
they interact with type inference.

**Nomi lock-in:** The coherence ladder: `func` for named → `=>` for
anonymous → equation `f(p)=e` for simple → piecewise equations for
dispatch → holes (`_`, `$1`, `$name`) for very short → composition
`>>>`/`<<<` for point-free → `where:` for local helpers. Each rung
has a distinct use case; they do not compete.

**Open question:** Should Nomi have a `&` capture operator (Elixir
style: `&String.upcase/1`) for function references? Currently rejected
as adding a second hole-family. Use `_.upcase()` instead.

### 4.3 Pattern Normal Form

**What worked everywhere:** Exhaustiveness checking. Rust's `match`,
OCaml's `match`, Swift's `switch` — all enforce that every case is
handled. This eliminates an entire class of bugs.

**What failed:** Pattern matching that looks like regular syntax.
Python's `match` had to avoid ambiguity with regular identifiers;
the solution (soft keywords) works but the design pressure is real.

**Nomi lock-in:** `match` for exhaustive choice, `if-let` for single
pattern, `while-let` for repeated destructuring, `guard` for early-exit
on mismatch. All reduce to the same pattern engine. Pattern synonyms
(named patterns) are a future extension point.

**Open question:** Mapping patterns (`{"key": pattern}`). Planned but
not yet designed. The tension is between dict-literal syntax and a
dedicated mapping-pattern syntax. Swift's `case let dict where dict["k"]
== v` is verbose; Rust doesn't have mapping patterns. Nomi should
evaluate before committing.

### 4.4 Flow Normal Form

**What worked everywhere:** Pipeline `|>`. Elixir, F#, Gleam, Julia,
R, Nushell — all converged on left-to-right threading as the natural
reading order for data transformations.

**What failed:** Multiple threading macros with subtle differences.
Clojure's `->` (thread-first), `->>` (thread-last), `as->` (named
threading), `some->` (nil-short-circuit), `cond->` (conditional
threading) — five macros for the same concept. Elixir's single `|>`
with first-argument threading is simpler and sufficient.

**Nomi lock-in:** One pipeline operator `|>`. One composition operator
`>>>` for building functions. Flow verbs (`map`, `filter`, `reduce`,
`sort`, `count`, `sum`, `min`, `max`, `group`) as named functions,
not syntax. Table/query/rank as future layer.

**Open question:** Should Nomi support pipeline placeholders? Elixir
does not (always first argument). Nomi currently follows Elixir.
Julia's `|>` with `_` placeholder is more flexible but more complex.
Decision: keep first-argument piping. Use `_` holes to build a function
when the argument position is not first.

### 4.5 Block Normal Form

**What worked everywhere:** Ruby blocks, Kotlin trailing lambdas,
Swift trailing closures, Gleam `use` — all solve "pass caller-side
code to a callee" with different syntax.

**What failed:** Too many block policies as keywords. Python has
`with` (resources), `for` (iteration), `try` (error handling), `@`
(decorators), context managers — five mechanisms for "code that wraps
other code." Each has different scoping, different name-binding rules,
and different composition behaviour.

**Nomi lock-in:** One block-call story (`f(x) -> p: body`). Callee uses
`yield` to invoke the block. Resources (`using`), retry, transaction,
tracing, fixtures, and future policies are all ordinary calls that
receive a block — they do not need dedicated keywords.

**Open question:** `errdefer` (Zig-style deferred only on error) is
the most novel block-policy pattern from recent languages. It could be
a standard library block policy (`on_error(cleanup_op, body_block)`)
rather than syntax.

### 4.6 Absence/Result Normal Form

**What worked everywhere:** Optional chaining `?.` (Swift, Kotlin,
TypeScript, C#, Ruby `&.`). Null coalescing `??` (same languages).
The combination of both handles the common absence case in one
expression.

**What failed:** Conflating absence with errors. JavaScript's
`null`/`undefined` split. Python's `None` as both "no value" and
"error occurred." Java's checked exceptions as control flow.

**Nomi lock-in:** `?.` and `??` handle absence only. `Result[T, E]`
handles expected failure. Exceptions handle unexpected errors. Three
distinct stories, three distinct syntaxes. Do not merge `?.` with
`Result` propagation — they are different semantic operations.

**Open question:** Should Nomi have a `?` error-propagation operator
(Rust/Swift/Zig style)? It would reduce to the pattern normal form
(`match result: case Ok(v): v; case Err(e): return Err(e)`). The risk
is that `?` for Result + `?.` for absence create two visually similar
operators with different semantics. Decision: defer `?` until `Result`
is widely used and the community asks for it.

### 4.7 Data Boundary Normal Form

**What worked everywhere:** Pydantic, CUE, Dhall, Rust's `serde` —
explicit boundary between external data and internal types. The key
insight: the boundary is a value in the language, not a separate
schema language.

**What failed:** Separate schema languages. JSON Schema, XSD, OpenAPI
— all define types in a language the host language cannot consume
directly. The impedance mismatch produces code generation, runtime
validation mismatches, and schema drift.

**Nomi lock-in:** `data` for owned types. `Data.decode(source,
Decoder)` for external boundaries. Constraints as first-class values.
No separate schema language. No code generation step.

**Open question:** Should Nomi support schema-from-data (like CUE's
unification)? Or only data-from-schema (like Pydantic)? CUE's
unification is powerful but brings a constraint-solving runtime.
Decision: start with data-from-schema (explicit decoding). Consider
schema-from-data as a future tool, not a language feature.

### 4.8 Explanation Normal Form

**What worked everywhere:** Rust's compiler error messages (the gold
standard). Elm's `--debug` mode. Darklang's trace-driven development.
Python's `doctest` for inline examples.

**What failed:** Error messages that report what happened in the
compiler, not what the user wrote. C++ template errors (pre-concepts).
Haskell's type errors without source spans (improving with GHC 9.x).

**Nomi lock-in:** `examples:` blocks for inline tests. `check:`
statements for invariants. Trace records for `explain`. Diagnostics
use normal-form vocabulary ("binding failed its constraint" not
"AttributeError on _ConstraintProxy").

## 5. Integration Rules

These are the rules Nomi applies when evaluating a new syntax proposal.
They are derived from the patterns, interactions, and lessons above.

1. **Reduce, don't add.** Every new surface form must reduce to an
   existing normal form. Tooling must show the reduction.

2. **One story per normal form.** If two features reduce to the same
   normal form, they must not compete. Document one as the canonical
   spelling and the other as a named special case.

3. **No second mini-language.** Validation, configuration, query, and
   templating must use Nomi syntax (binding, function, pattern, call)
   — no embedded DSLs with their own parser.

4. **Explicit boundaries for implicit power.** If a feature introduces
   non-local effects (context, scope, control flow), it must have a
   visible boundary keyword.

5. **Prefer library-first.** Before adding syntax, ask: can this be a
   function? A data value? A block policy? If yes, implement it there
   first. Syntax follows proven usage.

6. **Diagnostics before implementation.** Before committing syntax,
   write the error messages. If the diagnostics cannot use normal-form
   vocabulary, the syntax is probably too ad-hoc.

7. **No silent divergence.** If a feature changes meaning between
   Python parity mode and Nomi mode, the difference must be visible
   in the source, not hidden in a compiler flag.

8. **Sunset path required.** If a new feature overlaps with an existing
   one, define which spelling is preferred and when the older one will
   be deprecated. If no sunset path exists, the new feature is adding
   complexity without reducing it.

## 6. Language Design Mistakes Nomi Can Still Avoid

These are specific, named patterns that languages typically discover
too late. Nomi is young enough to avoid them.

### 6.1 The Escape Hatch That Becomes the Default

Every language adds an escape hatch for interop or performance. Over
time, the escape hatch becomes the idiomatic path, and the "safe"
path becomes friction.

- Python's C extensions became the performance strategy, splitting the
  ecosystem into CPython-only and portable code.
- Rust's `unsafe` is necessary but the `unsafe` keyword is the right
  design — it makes the boundary visible.

**Nomi:** Keep escape hatches visible and audit-able. Never make the
escape hatch the easiest path.

### 6.2 The Keyword That Should Have Been a Library Function

Languages add keywords for common operations. Later, the keyword's
semantics turn out to be too narrow, but changing it would break code.

- Python's `print` became a function in Python 3. The migration took
  a decade.
- Go's `go` for goroutines is fixed; you cannot parameterise the
  scheduler or add tracing without wrapping every `go` call.

**Nomi:** Prefer library functions over keywords. Even `print` is a
function in Nomi. New keywords must justify themselves against the
"could this be a function with a block?" test.

### 6.3 The Standard Library Split

When the standard library has two ways to do something, the ecosystem
splits around them. New users face a choice they cannot make
intelligently.

- Python: `urllib` vs `urllib2` → `requests` (third party won)
- OCaml: `Stdlib` vs `Base` vs `Core` vs `Containers`
- Haskell: `String` vs `Text` vs `ByteString` (and `Lazy` variants)
- Rust: `failure` → `anyhow`/`thiserror` → `std::error::Error`

**Nomi:** Ship one way in the prelude. Deprecate before adding a second.
If the ecosystem adds a third-party alternative that is clearly better,
promote it to the standard library and deprecate the old one (edition
mechanism).

### 6.4 The Too-Early Optimisation

A language commits to a performance model before understanding user
needs. The model constrains language evolution forever.

- Go's goroutine stack model made certain JIT optimisations impossible.
- Python's GIL made true parallelism a C-extension-only feature.
- Elm's lack of typeclasses was an intentional simplicity decision that
  later became a ceiling.

**Nomi:** The Python-hosted prototype is explicitly "a laboratory, not
the final boundary." Performance decisions can wait until the language
semantics are validated by real use.

## 7. Systemic Patterns Validated by Language History

The research across 25+ languages reveals patterns that repeat regardless of
paradigm. These are not opinions — they are empirically observable outcomes
of specific design structures.

### 7.1 Function Color Is Infectious

Every language that added a second function color (async/sync) later
regretted the split ecosystem. Python's `async def`, JavaScript's `async`,
Rust's `async fn`, Kotlin's `suspend` — all created:
- Executor/libraries that only work in one color
- "What color is my function" as a permanent cognitive overhead
- Bridging code at every color boundary

Without Boats (Rust team): "The async fn desugars to a state machine that
requires pinning. This is an implementation detail that leaked into the
user-facing language."

**Nomi:** The block/yield model is the ONE control abstraction. Async,
iteration, resource management, retry — all reduce to block policies, not
separate function colors. If concurrency is added, it must be via block
policies, not `async def`.

### 7.2 Implicit Power Compounds Into Unpredictability

Scala's `implicit` keyword carried five different meanings, all invisible
at the call site. Ruby's monkey-patching made every `require` a potential
behaviour change for every class. JavaScript's `==` coercion created bugs
that `===` was added to fix, but `==` can never be removed.

Martin Odersky (Scala): "Implicit has become too overloaded. In Scala 3,
we separate the different meanings."

Matz (Ruby): "Open classes are a double-edged sword. I don't regret them,
but I do think languages should provide better tools for controlling scope."

**Nomi:** Every shortcut that skips an explicit boundary is rejected
unless it has a visible boundary keyword. `where:` makes local scope
explicit. Block calls make policy explicit. There is no implicit
conversion, no ambient effect, no invisible receiver resolution.

### 7.3 Standard Library Warts Are Permanent

Python's `urllib`/`urllib2`, Ruby's `$` globals, JavaScript's `arguments`
object, TypeScript's `namespace`, Haskell's `String = [Char]`,
`Prelude.head` (partial) — once in the standard library, never removable.

Guido van Rossum (Python): "The lambda limitation is a consequence of
Python's grammar, not a philosophical commitment."

Brendan Eich (JavaScript, on `typeof null`): "That's literally a bug.
We can't fix it because it would break the web."

**Nomi:** The initial standard library (Prelude) must be minimal and
coherent. No partial functions. No type with known-performance problems
(as `String = [Char]` was). Every addition must pass the sunset test:
"If this turns out to be wrong, can we deprecate it without breaking
the ecosystem?"

### 7.4 Breaking Changes Without Migration Tooling Are Existential

Python 2→3 took 12 years (2008-2020). Scala 2→3 is still ongoing.
ES4 was abandoned entirely. The ONE success: Rust's edition system with
`cargo fix` automated migration.

**Nomi:** Plan the edition/migration story before 1.0. Automated migration
tooling is not optional. Every syntax addition should include a
desugaring that tooling can display, so migration between surface forms
is inspectable.

### 7.5 Type Systems Added Later Cause Ecosystem Fragmentation

Python's type hints churned across 4+ PEPs; `Optional[X]` vs `X | None`,
`List` vs `list`, `Union` vs `|` — all coexist. Go added generics in 2022
(10 years after 1.0); the entire ecosystem was built without them. Ruby
added RBS in 2022 (decades in). TypeScript's `strict` mode remains opt-in.

Rob Pike (Go): "We always knew we'd need generics. We just didn't know
how to do them well."

**Nomi:** Constraints are runtime-verified types. The constraint system
in `docs/features/binding_constraints_feature.md` should be coherent
from 1.0. Even if static checking arrives later, the runtime constraint
semantics must not change — static checking should be a zero-overhead
implementation of the same semantics, not a new type system.

### 7.6 Error Handling Needs Three Distinct Stories

Rust's `Result<T,E>` + `?` (success), Swift's `throws` + `Result`
(success), Kotlin's sealed classes + `?.` (success) all share one trait:
they distinguish expected failure from unexpected failure from absence.
Languages that conflate them (Python's `None` as both "no value" and
"error occurred," JavaScript's `null`/`undefined` split) produce permanent
confusion.

**Nomi:** Three distinct, non-collapsible stories:
- `?.` and `??` for absence only
- `Result[T, E]` + `match` for expected failure
- Exceptions for unexpected errors

Do not merge `?.` with `Result` propagation. Do not make `None` mean
"error."

### 7.7 Concurrency Primitives Must Be Part of the Initial Design

Go's goroutines (designed in), Erlang's actors (designed in), Rust's
async (added later, `Pin`/`Unpin` complexity), Python's GIL (30-year
constraint), Ruby's GVL (same) — languages that designed concurrency
from the start have cleaner stories.

Chris Lattner (Swift): "If I could do Swift over again, I'd make
concurrency part of the language from day one."

Matz (Ruby): "The GIL was a pragmatic implementation choice. A language
designed today should not have one."

**Nomi:** Even if the first layer is single-threaded, the concurrency
model should be architecturally designed before 1.0. The block call
model is the right primitive: concurrency policies (parallel map,
structured concurrency, actor mailboxes) should be block policies,
not language keywords.

### 7.8 Package Management Is Part of the Language Design

Go's GOPATH→modules pain. Python's `distutils`→`uv` odyssey. JavaScript's
CommonJS/ESM schism. The ONE success: Rust's Cargo. The lesson: version
resolution, reproducible builds, and dependency management must be
designed alongside the language, not bolted on.

**Nomi:** Modules, imports, versioning, and reproducibility should be
part of the binding/scope model. The `module` keyword and import syntax
should be stable from 1.0.

## 8. Designer Quotes

| Designer | Language | Quote |
|----------|----------|-------|
| Guido van Rossum | Python | "The GIL was a design decision that at the time seemed perfectly reasonable, and it's been with us for 30 years." |
| Brendan Eich | JavaScript | "I knew there would be mistakes. I didn't know they'd be set in stone." |
| Brendan Eich | JavaScript | "If I had more time, the equality operator would not coerce." |
| Brendan Eich | JavaScript | (On `typeof null`) "That's literally a bug. We can't fix it." |
| Anders Hejlsberg | TypeScript | (On `enum`) If designing TypeScript today, `enum` would likely not exist in its current form. |
| Graydon Hoare | Rust | "I had a lot of ideas that were terrible." |
| Without Boats | Rust | "The async fn desugars to a state machine that requires pinning. This is an implementation detail that leaked into the user-facing language." |
| Rob Pike | Go | "We always knew we'd need generics. We just didn't know how to do them well." |
| Rob Pike | Go | "I'm not going to say the way Go does error handling is perfect. But I will say it's deliberate." |
| Martin Odersky | Scala | "Implicit has become too overloaded. In Scala 3, we separate the different meanings." |
| Martin Odersky | Scala | "We learned from the Python 2/3 disaster." |
| Andrey Breslav | Kotlin | "If we were starting over, we might have fewer scope functions with more distinct names." |
| Chris Lattner | Swift | "If I could do Swift over again, I'd make concurrency part of the language from day one." |
| Matz | Ruby | "The Perl-style global variables are a legacy. In a new language, I would not include them." |
| Matz | Ruby | "The GIL was a pragmatic implementation choice. A language designed today should not have one." |

## 9. How to Synthesize: A Methodology

The previous sections catalogue patterns, interactions, praise, regret, and
integration rules.  This section describes *how to use* that catalogue — a
repeatable methodology for evaluating new proposals that goes beyond
checklists into genuine synthesis.

### 9.1 The Synthesis Stance

Synthesis is not the same as evaluation.  Evaluation asks "is this proposal
good?"  Synthesis asks "what would this proposal become inside Nomi, and
how would it interact with everything else?"

The right stance:

1. **Assume the proposal exists.**  Temporarily grant that the syntax is
   already in the language.  What breaks?  What becomes redundant?  What
   does a new user now have to learn before their first program compiles?

2. **Write the desugaring first.**  Before debating surface syntax, write
   the normal-form reduction.  If the reduction is awkward, the syntax is
   fighting the primitives.  If the reduction is clean, the surface
   spelling is mostly decoration.

3. **Find the interaction surface.**  For each existing feature, ask: does
   this proposal compose with it?  If they appear together in an expression,
   is the meaning unambiguous?  If they nest, do scoping rules compose?

4. **Write the diagnostic before the implementation.**  The hardest test:
   can you write a clear error message for when this feature is misused?
   If the error message must name implementation details, the abstraction
   is wrong.

### 9.2 The Synthesis Loop

```
Source proposal
  → desugar to normal form (which primitive?)
  → map interactions (collisions with existing features?)
  → check cruft patterns (does it match a known failure mode?)
  → check designer regrets (has someone already tried this and regretted it?)
  → write diagnostic (can error messages speak in normal-form vocabulary?)
  → decide: accept / accept with adaptation / reject with rationale
```

Each step produces concrete output:
- Desugaring: a Python AST or core-node sketch
- Interactions: a list of feature pairs and their combined behaviour
- Cruft check: which systemic pattern (section 1) does it risk?
- Designer check: which regretted feature (section 3.2) does it resemble?
- Diagnostic: at least one error message in normal-form vocabulary

### 9.3 Worked Example: `defer` Statement

```
Proposal: defer cleanup() at end of block (Go/Zig-style deferred execution)

Step 1 — Desugar to normal form:
  defer cleanup(); body
  →
  try: body
  finally: cleanup()
  Normal form: Block (try/finally is a block policy)

Step 2 — Map interactions:
  - defer inside a block call: does cleanup run when the block exits
    or when the enclosing function exits?  Decision: when the block exits
    (innermost block boundary).  Consistent with try/finally semantics.
  - defer inside a where clause: where-clause bindings are local to the
    expression.  defer in a where clause is unusual but should work —
    cleanup runs after the expression evaluates.
  - defer + return: cleanup runs before the return value is produced.
    This is Zig-compatible and what users expect.

Step 3 — Check cruft patterns:
  - Not a second mini-language (uses existing block/scope primitives)
  - Not a convenience stack-collapse (defer is orthogonal to existing
    cleanup mechanisms — it's a different use case from `using`)
  - Risk: implicit power escalator.  Defers accumulate invisibly.
    Mitigation: tooling should show accumulated defers at each scope exit.

Step 4 — Check designer regrets:
  - Zig's errdefer is widely praised.  Go's defer is uncontroversial.
  - No known language regrets about defer specifically.
  - Caution: Python's `__del__` and `weakref` finalizers are regretted
    (non-deterministic).  Defer is deterministic — opposite problem.

Step 5 — Write diagnostic:
  "defer in block call: cleanup will run when the block exits, not when
   the enclosing function exits.  Use defer in the outer scope if you
   need function-exit cleanup."

Decision: Accept.  Desugars cleanly to try/finally.  No new primitive.
Interactions are well-defined.  Go/Zig precedent is positive.
```

### 9.4 When the Loop Rejects a Proposal

The loop produces rejections too.  A rejection should name *which step*
failed and *why* — not just "we don't like it."

```
Example: unless...else

Step 1 — Desugar: unless x > 10: a else: b  →  if not x > 10: a else: b
  Clean desugaring.  But Step 2 (interactions) reveals the problem:
  unless x > 10 and y > 20: a else: b
  Does `else` attach to the `unless` or to the `and`?  Ambiguity.

Step 5 — Diagnostic:
  "'unless...else' is ambiguous when combined with 'and'/'or'.  Use
   'if not...else' for the general case.  'unless' without 'else' is
   fine."

Decision: Accept `unless` without `else`.  Reject `unless...else`.
```

### 9.5 Synthesis Traps

These are mistakes that happen during synthesis, not in the proposal itself.

**Trap 1: Designing in a vacuum.**  Evaluating a proposal without putting
it next to existing syntax.  Fix: always write a combined example — the
new syntax nested inside an existing form, and vice versa.

**Trap 2: Emulating the source language's semantics too closely.**  Copying
the syntax because the source language did it well, without checking whether
Nomi's primitives give a cleaner reduction.  Fix: write the normal-form
reduction first.  If the source language's semantics and Nomi's reduction
disagree, Nomi's reduction wins.

**Trap 3: Adding a feature because it's "small."**  Small features
accumulate.  Five small features that each add one syntax rule are worse
than one medium feature that replaces three of them.  Fix: count the total
syntax budget, not the per-feature cost.

**Trap 4: Focusing on the happy path.**  Proposals naturally describe what
the feature looks like when used correctly.  Synthesis must also describe
what happens when it's used incorrectly, nested deeply, or combined with
every other feature.  Fix: write the error case before the happy case.

**Trap 5: Citing precedent as proof.**  "Language X has this and it works"
is research, not synthesis.  The question is not whether it worked in
Language X — it's whether it works *with Nomi's specific primitives and
existing features*.  Fix: replace "X does this" with "X does this, which
reduces to Nomi's Y normal form, and here's how it interacts with Z."

## 10. References

- `docs/research/error_handling_defer_resource_cleanup_notes.md` — Zig, Hylo, Odin, Gleam, Roc
- `docs/research/modern_language_feature_survey.md` — Mojo, Jai, Darklang, Unison, CUE/Nickel/Pkl/Dhall, Wren, Janet, Lobster, D
- `docs/research/deep_language_feature_survey.md` — Haskell, OCaml, Agda/Idris, Swift, Kotlin, Scala 3, F#
- `docs/research/concatenative_languages.md` — Forth, Factor, Joy, Kitten, Cat
- `docs/research/array_languages_deep_dive.md` — APL, J, K, BQN, Uiua
- `docs/research/scientific_languages_r_matlab_julia.md` — MATLAB, R, Julia
- `docs/convenience/syntax_synthesis_matrix.md` — Cross-language feature families
- `docs/convenience/expanded_language_research.md` — Roc, Gleam, Zig, Unison, CUE, etc.
