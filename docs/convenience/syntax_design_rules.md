# Syntax Design Rules

> Status: active design framework.  Derives concrete syntax-design rules
> from the language design dimensions analysis.
>
> Source: [../language/language_design_dimensions.md](../language/language_design_dimensions.md).
> Companion: [design_lessons_and_integration.md](design_lessons_and_integration.md)
> for systemic cruft patterns and integration critique.

## Purpose

The [design dimensions analysis](../language/language_design_dimensions.md)
shows that all language features reduce to ~8 core primitives, and that
languages vary systematically along ~9 axes.  This document translates
those findings into **operational rules for designing Nomi's surface
syntax** — rules that tell you not just *whether* to add a feature, but
*how* to shape it.

## 1. The Primitive Budget Rule

**Derived from:** Level 4 (core primitives) of the convergence hierarchy.

Every new core primitive has a cognitive cost.  Nomi's 8 normal forms are
already near the upper limit of what fits in working memory.  New syntax
must consume the existing budget, not expand it.

```
Rule: A proposed syntax feature MUST reduce to an existing normal form.
      If it requires a genuinely new irreducible primitive, reject or
      defer to a future language layer.
```

**What this means in practice:**

| Proposal | Verdict | Why |
|----------|---------|-----|
| `unless x > 10: body` | Accept as sugar | Reduces to `if not x > 10: body` (Choose primitive) |
| `cond: case a: ... case b: ...` | Reject | Duplicates `match` (same Choose primitive, different spelling) |
| `list.map(_.name).filter(_.active)` | Already present | Flow verbs are Compose + Apply |
| `each(items) -> item: body` | Already present | Block call is Signal (suspendable) + Contain |
| Regex literals `/pattern/` | Library-first | A second pattern language — does not reduce to existing primitives |
| Embedded SQL `FROM users SELECT name` | Reject as syntax | Second mini-language; keep as library or scoped extension |

**The test:** Ask "which normal form does this reduce to?" If the answer
is "none of them," the proposal needs a new primitive.  New primitives
are allowed, but they are *language-design events*, not convenience
features.

## 2. The Axis Coherence Rule

**Derived from:** The 9 systematic axes of variation (§3 of the dimensions
analysis).

Nomi has chosen a position on each design axis (eager evaluation, nominal
typing, pattern-matching dispatch, explicit effects via block policies,
one binding story).  Syntax from languages that occupy different positions
on these axes will fight Nomi's grain.

```
Rule: Evaluate every syntax proposal against Nomi's axis positions.
      Syntax from languages in Nomi's family (ML-family: eager, nominal,
      pattern-matching) will integrate more cleanly than syntax from
      distant families.  Copy the semantic mechanism, not the surface
      spelling.
```

**Nomi's axis positions (the "family signature"):**

| Axis | Nomi's position | Family |
|------|----------------|--------|
| Evaluation | Eager (Python-compatible) | ML, Python, Rust, Go |
| Type discipline | Runtime constraints, nominal `data` | ML, Rust (nominal), Python (runtime) |
| Memory | GC (Python-hosted) | Python, Java, Go, Haskell |
| Effects | Explicit block policies | Ruby (blocks), Gleam (use), Rust (?), Zig (errdefer) |
| Dispatch | Pattern matching primary | ML, Rust, Swift, Scala |
| Binding | One story, rebindable, optional constraints | Unique to Nomi |
| Modularity | Files-as-modules | Python, Go, JavaScript |
| Concurrency | Block policies (future) | Gleam (use), Kotlin (coroutines as library) |
| Data | Nominal owned, structural external | Rust (nominal) + TypeScript (structural) — a deliberate hybrid |

**What this means in practice:**

- **ML-family syntax will feel native.**  OCaml's `match`/`with`, F#'s `|>`,
  Rust's `enum`, Swift's `guard let`, Scala's `case class` — these all
  assume eager evaluation, nominal types, and pattern matching.  Their
  surface syntax can be studied and adapted.

- **Haskell-family syntax needs translation.**  Haskell's `do` notation
  assumes monadic composition and lazy evaluation.  Don't copy `do`; instead,
  recognise that it encodes Compose (sequential) + Signal (effect threading),
  and express those through block calls and pipelines.

- **Lisp-family syntax needs translation.**  Lisp macros assume
  s-expression uniformity.  Don't copy `defmacro`; instead, recognise that
  macros are Apply (at compile time) over Abstract (syntax), and express
  that through `quote:` boundaries.

- **Array-family syntax needs translation.**  APL's implicit broadcasting
  assumes array-at-a-time rank polymorphism.  Don't copy `+.` notation;
  instead, recognise that broadcasting is Compose (element-wise) with
  implicit rank matching, and express it through explicit `.` broadcasting
  (Julia-style) or named shape functions.

## 3. The One-Elimination-Form Rule

**Derived from:** The elimination-form convergence point (§4.1 of the
dimensions analysis).

`match`, `if`, `?.`, `??`, method dispatch, and visitor pattern all
converge to the same Choose primitive.  Nomi should have one primary
elimination form with specialised short forms for common cases.

```
Rule: `match` is the canonical elimination form.  `if` is the short form
      for boolean conditions.  `?.` is the short form for absence.
      Do not add a fourth, fifth, or sixth elimination syntax.  Any new
      form of structural choice must be a `match` pattern, not a new
      keyword.
```

**What this means in practice:**

| Need | Use | NOT |
|------|-----|-----|
| Boolean choice | `if` / `unless` | — |
| Structural choice | `match value: case Pat: ...` | `switch`, `case`, `cond` |
| Absence short-circuit | `?.`, `??` | `try!`, `unwrap()`, `if let Some` |
| Early exit on mismatch | `guard pattern = value: body` | `let ... else` as separate syntax |
| Piecewise dispatch | Equation clauses (desugar to match) | Separate `case` keyword |

**Why `match` is the right canonical form:** It is the only elimination
form that supports exhaustiveness checking (for closed variants), pattern
binding, and guard clauses.  `if` cannot be exhaustive.  `switch` (C-style)
cannot bind.  `?.` cannot choose between more than two branches.  `match`
is the general case; everything else is a restriction.

## 4. The Context-Threading Rule

**Derived from:** The context-thread convergence point (§4.2).

Monads, effect handlers, implicit parameters, context receivers, and
dependency injection all converge to the same operation: threading
implicit context through computation.  Nomi's block calls are the
canonical form of this operation.

```
Rule: Use block calls (f(x) -> p: body) for all context-threading.
      Do not add monadic do-notation, async/await as keywords, implicit
      parameters, or effect handlers as separate mechanisms.  Each of
      these is a different surface spelling of the same underlying
      operation that block calls already encode.
```

**What this means in practice:**

| Use case | Block-call spelling | NOT |
|----------|-------------------|-----|
| Resource scope | `using(open(path)) -> file: body` | `with` statement, `try`-with-resources |
| Retry | `retry(3): body` | `retry` keyword, `@retry` decorator |
| Transaction | `transaction(db) -> tx: body` | `BEGIN`/`COMMIT` keywords |
| Iteration | `each(items) -> item: body` | `for` as a separate language construct |
| Tracing | `trace("op"): body` | `@trace` decorator, `span` context manager |
| Async (future) | `async(task_pool): body` | `async def`, `async`/`await` keywords |

**The function-coloring insight:** The dimensions analysis shows that
every language that added `async`/`await` as a second function color
regretted it.  Block calls avoid coloring because the policy is at the
call site, not in the function signature.  The callee uses `yield` —
a single, general mechanism — whether the caller is retrying, tracing,
transacting, or iterating.

## 5. The Closed/Open Distinction Rule

**Derived from:** The Expression Problem analysis (§5 of the dimensions
analysis) and the nominal/structural axis.

The Expression Problem is not solvable — it is a genuine tradeoff.
Nomi's strategy: nominal `data` for closed owned types, structural
matching for open external values.  This distinction should be VISIBLE
in the syntax.

```
Rule: `data` declarations create closed types (exhaustiveness possible).
      External data matching (`Data.decode`, pattern matching over dicts)
      is open (no exhaustiveness expected).  The syntax should make this
      distinction visible — the reader should know from the keyword
      whether a type is closed or open.
```

**What this means in practice:**

```nomi
# CLOSED: all variants known here.  Match can be exhaustive.
data Response:
    Ok(value: T)
    Err(error: E)

# The compiler/runtime CAN check that every variant is handled.
match response:
    case Ok(v): process(v)
    case Err(e): log(e)
# If we add a third variant, every match site must be updated.  Good.

# OPEN: external data, shape unknown at definition time.
config = Data.decode(source, Config.decoder)
# Pattern matching over config is open — you handle what you recognise,
# ignore what you don't.  No exhaustiveness expected.
```

**The syntax-level distinction:** `data` always means closed.  Structural
matching (over dicts, JSON, external inputs) is always open.  Never blur
these — a `data` declaration that silently permits new variants is a
design bug.  A structural match that claims exhaustiveness is lying.

## 6. The Cognitive Priority Rule

**Derived from:** The cognitive dimensions analysis (§8 of the dimensions
analysis).

Languages optimise for different cognitive properties.  Nomi's target is
**local reasoning** — a reader should understand a function by reading
that function and the `data` declarations it references, nothing else.

```
Rule: When choosing between multiple syntax proposals for the same
      normal form, prefer the one that improves local reasoning.
      Prefer syntax that makes constraints, control flow, and data
      boundaries visible at the use site.
```

**Priority ordering for syntax decisions:**

1. **Make constraints visible at the binding site.**
   `name:Type, predicate = value` — the reader sees what must be true
   without finding the caller.

2. **Make control flow explicit.**
   `yield` marks the suspension point.  `defer` marks cleanup.  Block
   boundaries are visible.  No hidden non-local control.

3. **Make data boundaries explicit.**
   `Data.decode(source, Decoder)` — the reader sees that external data
   crossed a boundary.  No implicit marshaling.

4. **Make desugaring inspectable.**
   Tooling can show `x?.y` desugared to `if x is None: None else x.y`.
   The sugar is never magic.

5. **Then, and only then, optimise for keystrokes.**
   Short forms (`_`, `$1`, `=>`) are welcome after the semantic form
   is clear.

## 7. The Under-Represented Normal Forms

**Derived from:** Mapping Nomi's convenience docs against the primitive
budget.

The current convenience docs cover Function, Pattern, Flow, and
Absence/Result well.  Two normal forms are under-represented and need
more syntax-facing design work:

### Explanation

The dimensions analysis identifies Explanation as a genuine primitive,
not an afterthought.  Yet `meta_testing.md` is one of the thinner convenience
docs and `language_spec.md §19` (Diagnostics, Trace, And Explain) is ~50 lines.

**Syntax design needed for:**
- `examples:` blocks — inline executable tests that live with the code
- `check:` statements — invariants that the runtime verifies
- Trace records — structured semantic events, not text logs
- `explain` — tooling that shows normal-form reduction, not compiler internals

### Data Boundary

`data_and_types.md` covers types and strings.  But the dimensions analysis
shows that the Data Boundary normal form is where the nominal/structural
tension is resolved, and where the Expression Problem tradeoff is made
concrete.

**Syntax design needed for:**
- `Data.decode(source, Decoder)` — explicit boundary crossing with structured diagnostics
- Decoder composition — how decoders compose (product, sum, optional, list)
- Constraint-bearing fields — `data User(name: str, age: int, age >= 0)`
- Provenance tracking — where did this value come from?  (for diagnostics)

## 8. The Family Coherence Test

**Derived from:** Level 2 (idioms/families) of the convergence hierarchy.

Nomi's axis positions place it in the ML family.  This is not an accident —
it reflects deliberate choices about evaluation, typing, dispatch, and
data.  New syntax should be tested for family coherence.

```
Rule: For any proposed syntax, find the closest equivalent in OCaml, F#,
      Rust, or Swift (ML-family, eager, pattern-matching).  If the
      equivalent exists and integrates cleanly, the proposal is likely
      coherent.  If the closest equivalent is in Haskell (lazy, monadic),
      Clojure (dynamic, macro-heavy), or APL (array-at-a-time), the
      proposal needs translation through Nomi's primitives — do not copy
      the surface syntax.
```

**The family-coherence table:**

| If the idea comes from | Translate through | Example |
|------------------------|-------------------|---------|
| OCaml, F#, Rust, Swift | Direct adaptation likely | `match`/`case`, `|>`, `data`/`enum` |
| Haskell | Translate laziness → eagerness, monad → block call | `do` → block call, list comprehension → pipeline |
| Scala, Kotlin | Translate implicit → explicit, receiver → block param | `given`/`using` → explicit block parameter |
| Clojure, Racket | Translate macro → scoped notation, dynamic → constraint | threading macro → `|>` pipeline |
| Python, Ruby | Direct for eager/dynamic parts; translate blocks to block calls | `with` → `using(...)`, `defer` → `defer` |
| Go, Zig | Translate error codes → Result, `defer` → `defer` | `if err != nil` → `Result` + `match` |
| APL, J, Julia | Translate implicit rank → explicit verb, array-at-a-time → pipeline | `+.` → explicit `.broadcast` |
| Erlang, Elixir | Translate actor → block policy, `!` → block call | `receive` → block call pattern |

## 9. Application: Evaluating a New Syntax Proposal

The full workflow for evaluating a convenience syntax proposal, using
all the rules:

```
1. Primitive Budget:  Which normal form does it reduce to?
2. Axis Coherence:    Does it assume Nomi's axis positions?
3. Elimination Form:  Is it a new Choose spelling?  Use match instead.
4. Context Threading: Is it a new Signal spelling?  Use block call instead.
5. Closed/Open:       Is the type distinction visible in the syntax?
6. Cognitive Priority: Does it improve local reasoning?
7. Under-Represented: Does it help the Explanation or Data Boundary gap?
8. Family Coherence:  What's the closest ML-family equivalent?
```

If a proposal passes all 8, it is a strong candidate.  If it fails any,
the failure tells you what to change.

### Worked Example: Adding `unless`

```
Proposal: unless x > 10: body  (Ruby-style inverted if)

1. Primitive Budget:   Reduces to `if not x > 10: body` → Choose ✓
2. Axis Coherence:     Ruby is eager, dynamically typed — Nomi is eager,
                       runtime-constrained.  Compatible axes. ✓
3. Elimination Form:   Not a new form — `if` already exists, `unless` is
                       an inverted spelling of `if`.  Sugar, not new primitive. ✓
4. Context Threading:  N/A (not a context-threading feature)
5. Closed/Open:        N/A (not a data type feature)
6. Cognitive Priority: Mildly positive — `unless x > 10` reads as "do this
                       unless the condition holds."  Local reasoning is fine. ✓
7. Under-Represented:  N/A
8. Family Coherence:   Ruby has `unless`; Python uses `if not`.  Both are
                       eager.  The ML family generally uses `if not`.  Mild
                       tension — Python-compatible Nomi users expect `if not`.
                       Verdict: accept as sugar if the community asks for it,
                       but don't evangelise it.

Decision: Accept as optional sugar, `unless x > 10:` desugars to
          `if not x > 10:`.  Do not add `unless...else` (becomes confusing).
```

### Worked Example: Adding `do` Notation

```
Proposal: do { x <- action1; action2 x }  (Haskell-style monadic bind)

1. Primitive Budget:   Tries to encode Compose + Signal.  Block calls
                       already encode this.  Redundant. ✗
2. Axis Coherence:     Assumes monadic composition (Haskell, lazy).
                       Nomi is eager, block-based.  Axis mismatch. ✗
3. Elimination Form:   The `<-` is a Choose-like binding in a monadic
                       context.  Nomi already has `yield` for this. ✗
4. Context Threading:  Block calls are Nomi's context-threading primitive.
                       `do` is a competing spelling of the same thing. ✗
5-8:                   N/A (already fails)

Decision: Reject.  Use block calls: `action1() -> x: action2(x)`.
          If the use case is iteration, use `each(items) -> item: body`.
```

## 10. Nuance: When Rules Bend

The eight rules above are design defaults, not absolutes.  This section
describes when a rule should bend, how to weigh conflicting rules, and how
to tell the difference between a legitimate exception and rationalisation.

### 10.1 Legitimate Exceptions

**Primitive Budget (Rule 1):** Bends when a genuinely new capability is
needed that cannot be expressed with existing primitives.  Example:
`data` declarations create a new primitive (closed nominal types) that
binding + function + pattern cannot express.  The bar: proven by
existence of a concrete, non-synthesised program that cannot be written
without the new primitive.

**Axis Coherence (Rule 2):** Bends when the axis position itself is under
revision.  Example: if Nomi later adopts lazy evaluation for a streaming
layer, Haskell-family syntax becomes more relevant.  The bar: the axis
change must be designed and documented before syntax that depends on it.

**One-Elimination-Form (Rule 3):** Bends for ergonomic short forms that
unambiguously desugar to `match`.  Example: `if-let` is a second
elimination syntax, but it reduces to `match` and handles a common
single-pattern case.  The bar: the short form must be a strict subset of
`match` — no new semantics, no different scoping rules.

**Context-Threading (Rule 4):** Bends when the block-call spelling is
genuinely too verbose for a common case.  Example: `with:` as sugar for
`using(expr) -> _: body` where the resource is unnamed.  The bar: the
short form must be a block call, not a parallel mechanism.

**Closed/Open Distinction (Rule 5):** Rarely bends.  The closed/open
distinction is load-bearing for exhaustiveness and for the data-boundary
story.  If a feature blurs this line, it needs a new normal form, not an
exception.

**Cognitive Priority (Rule 6):** Bends when local reasoning conflicts with
another priority and the other priority wins.  Example: `$1` holes have
worse local reasoning than explicit lambdas, but the keystroke savings
justify them for one-liners.  The bar: the tradeoff must be documented,
and the explicit form must exist as an escape hatch.

**Under-Represented Normal Forms (Rule 7):** Not a rule to bend — this is
a gap report.  It identifies where design work is needed.

**Family Coherence (Rule 8):** Bends when Nomi deliberately diverges from
ML-family practice.  Example: Nomi's block calls have no direct ML-family
equivalent (Ruby blocks are closer).  The bar: the divergence must be
documented as a deliberate choice, not an accident.

### 10.2 When Rules Conflict

Some proposals trigger opposing rules.  Resolution order:

```
1. Primitive Budget (Rule 1) overrides everything.
   If it needs a new primitive, stop — that's a language-design event.

2. Closed/Open Distinction (Rule 5) overrides Axis Coherence (Rule 2)
   and Family Coherence (Rule 8).
   Type system soundness > stylistic preference.

3. Cognitive Priority (Rule 6) overrides Family Coherence (Rule 8).
   Local reasoning > "this is how OCaml does it."

4. Family Coherence (Rule 8) overrides keystroke-counting.
   ML-family consistency > saving two characters.
```

**Worked conflict:** `?.` (optional chaining)

```
Rule 3 (Elimination) says: use match for structural choice.
Rule 6 (Cognitive) says: make absence handling visible at the use site.

Conflict: ?. is not match, and it's not a short form of match in the
way if-let is.  It introduces a third choice mechanism.

Resolution: Rule 6 wins.  ?. makes absence handling locally visible
in a way that match cannot (match requires unwrapping at every level).
The bar is met: ?. is a strict subset of match for the specific case
of "access this chain of attributes, short-circuit on None."  It does
not add new semantics — it is syntax sugar over:
  tmp = x
  if tmp is None: None else: tmp.y
```

### 10.3 Rules Are Conviction, Not Dogma

These rules encode lessons from languages that made the mistakes
catalogued in `design_lessons_and_integration.md`.  They should be
followed unless there is a specific, documented reason not to.

But they are not eternal.  If a rule consistently blocks good proposals,
the rule is wrong.  The process for changing a rule:

1. Document which proposals the rule blocked and why they were good.
2. Propose a revised rule that admits those proposals while still
   preventing the original failure mode.
3. Test the revised rule against the full proposal backlog.
4. Update both this document and the design decision ledger.

This is the same process as refactoring code: find the pattern, name it,
test it, and only then change the abstraction.

## 11. References

- [../language/language_design_dimensions.md](../language/language_design_dimensions.md) — full dimensions analysis
- [design_lessons_and_integration.md](design_lessons_and_integration.md) — systemic cruft patterns and integration rules
- [review_and_roadmap.md](review_and_roadmap.md) — normal-form status spine
- [../language/language_degrees_of_freedom.md](../language/language_degrees_of_freedom.md) — core/sugar/library/scoped freedom framework
