# Convenience Review, Normal Forms, And Roadmap

> Status: active design review.
>
> Scope: documentation-only consolidation. This pass does not implement new
> syntax. It reviews the convenience-feature notes as a whole, adds candidate
> features, critiques overlap, and turns the folder into a roadmap for later
> implementation commits.

## Purpose

Nomi should make everyday programming pleasant without becoming a collage of
favorite language features. The convenience folder is valuable because it
collects ideas from Python, Ruby, Kotlin, Swift, Rust, Elixir, Gleam, Elm,
Julia, SQL, APL, Nushell, and other systems. The risk is that several ideas
solve almost the same problem with slightly different syntax and semantics.

This document sets the consolidation rule:

```text
source-language feature -> everyday need -> Nomi normal form -> surface syntax
```

If two features reduce to the same normal form, they should either share one
surface spelling or be documented as obvious special cases. If they cannot be
reduced to an existing normal form, they remain research until the core gains a
new primitive.

## Feature Status Labels

Every convenience note should use these labels when discussing a feature:

- **implemented**: behavior exists in the prototype and is covered by tests or
  runnable examples.
- **prototype-ready**: syntax and reduction are clear enough for an
  implementation slice.
- **design-needed**: the user model is promising, but semantics, diagnostics,
  or interaction with another feature are not settled.
- **library-first**: the idea should start as ordinary functions, data values,
  or block policies before becoming syntax.
- **research-only**: useful background, not a current language target.
- **rejected-for-now**: attractive elsewhere, but incoherent or too costly for
  the first everyday language.

## Current Prototype Surface

These are already present enough to teach, though individual docs may still
need stale wording removed.

| Area | Implemented surface | Normal form |
| --- | --- | --- |
| Functions | `func`, arrow functions, equations, defaulted equations, piecewise equations, guards | function declaration or function value |
| Implicit functions | `_`, `$1`, `$name`, operator sections | arrow function with generated parameters |
| Local bindings | block and inline `where` | expression plus local bindings |
| Composition | `|>`, `>>>`, `<<<` | call application or function composition |
| Control | `unless`, postfix `return ... if/unless`, if-let, while-let, guard-let | boolean branch or pattern binding plus branch |
| Pattern matching | match statements, guards, or-patterns, if-let, inline match expressions, indented expression cases | pattern test plus tentative binding |
| Null handling | `??`, safe attr/call/subscript with `?.` | absence-aware access or fallback expression |
| Error handling | single-line `try` expression, `defer` | expression boundary or exit policy |
| Collections | ranges, range step with `by`, spread literals, comprehensions, pipelines | collection value plus calls |
| Strings | normal strings, raw strings, triple strings, simple f-strings | string literal or string construction |
| Types | type aliases | name binding for constraint/type expression |

## Consolidated Normal Forms

The following normal forms should be the main teaching and implementation
surface for convenience features.

### Binding Normal Form

Use for assignment constraints, parameters, block parameters, loop variables,
pattern captures, data fields, imports, exception aliases, and future decoder
fields.

```text
receive value -> tentatively bind -> check constraints -> commit or diagnose
```

Canonical syntax:

```nomi
age:int, age >= 13 else "Must be at least 13" = raw_age

func signup(age:(int, age >= 13)):
    ...

each(users) -> user:User:
    ...

match raw:
    case {"age": age:(int, age >= 13)}:
        ...
```

Consolidation decisions:

- Do not create a second validation language for records, CLI arguments,
  config, JSON, or table rows.
- Do not add a first-layer `shape` keyword as a peer to `data`. Use owned
  `data`, structural patterns, constraints, and explicit `decode` boundaries.
- If a future `shape` keyword is admitted, it must mean named structural
  pattern/constraint, not a second data declaration.

### Function Normal Form

Use for named functions, arrow functions, equations, piecewise clauses,
implicit holes, operator sections, composition, and partial application.

```text
parameters are bindings -> body evaluates -> result optionally checked
```

Canonical syntax:

```nomi
func normalize(email:str) -> str:
    return email.strip().lower()

double = x => x * 2
double = _ * 2
add = $1 + $2
positive(n) when n > 0 = true
positive(n) = false
```

Consolidation decisions:

- Prefer `=>` when a reader needs named parameters or constraints.
- Prefer `_` for one obvious value in a small expression.
- Prefer `$1`, `$2`, or `$name` only when the implicit function would otherwise
  be clearer than a lambda.
- Keep point-free and tacit style optional. It is a tool for short transforms,
  not the default style of the language.

### Pattern Normal Form

Use for `match`, if-let, while-let, guard-let, destructuring assignment, data
variants, structural dictionary/list recognition, and future regex captures.

```text
test structure -> tentatively bind captures -> check constraints -> choose body
```

Canonical syntax:

```nomi
if [first, *rest] = items:
    ...

guard Ok(user) = fetch_user(id):
    return Err("missing user")

match event:
    case {"type": "click", "target": target}:
        record_click(target)
```

Consolidation decisions:

- `if-let`, `while-let`, and `guard-let` are special cases of pattern matching,
  not separate control systems.
- Pattern failure means the shape did not fit. Constraint failure means the
  shape fit but a value was unacceptable. Match cases may treat both as
  non-match before body entry, but diagnostics should preserve the difference.
- Exhaustiveness is a future diagnostic goal for closed data variants, not a
  blocker for the first runtime implementation.

### Flow Normal Form

Use for nested calls, pipelines, composition, collection transforms, query
verbs, result chaining, and calculational expressions.

```text
value flows through named transforms; each stage is a call or function value
```

Canonical syntax:

```nomi
clean =
    raw
    |> strip
    |> lower
    |> normalize_space

active_names =
    users
    |> where(_.active)
    |> select(_.name)
    |> sort
```

Consolidation decisions:

- Pipeline applies a value now. Composition builds a function for later.
- Collection verbs such as `where`, `select`, `derive`, `group`, `join`,
  `sort`, `fold`, and `window` should begin as functions over ordinary
  collections or query plans.
- SQL-like query blocks are design-needed until they reduce cleanly to the
  same transform vocabulary.
- APL/J/K-style array ideas should enter as readable shape/rank functions
  before any dense notation.

### Block Normal Form

Use for `using`, `retry`, `transaction`, `timeout`, `trace`, fixtures, scoped
capabilities, callback inversion, and possibly structured concurrency later.

```text
ordinary call + attached caller-side block; callee invokes block with yield
```

Canonical syntax:

```nomi
retry(3, on=NetworkError):
    fetch(url)

using(open(path)) -> file:
    text = file.read()

trace "import people":
    rows = read_csv(path)
```

Consolidation decisions:

- Do not add one keyword per control policy.
- Treat Swift `guard`, Ruby blocks, Kotlin trailing lambdas, Python context
  managers, pytest fixtures, and Gleam `use` as reference pressure for the same
  block/call idea.
- Structured concurrency should wait until block calls, cancellation,
  diagnostics, and result semantics are settled.

### Absence And Result Normal Form

Use for `none`, optional access, defaults, expected failure, parse/decode
errors, and early propagation.

```text
absence is a value; expected failure is data; unexpected failure is an error
```

Canonical syntax:

```nomi
name = user?.name ?? "anonymous"

match parse_int(raw):
    case Ok(n):
        n
    case Err(error):
        explain(error)
```

Consolidation decisions:

- `?.` and `??` are convenience syntax for absence-aware expressions, not a
  complete error-handling model.
- `Result[T, E]` belongs with data variants and pattern matching.
- A Rust-like `?` operator is design-needed until `Result`, return constraints,
  and conversion rules are specified.
- Elvis forms such as `value ?? return` remain rejected-for-now because they
  blur expression flow with statement-level exit before the result model exists.

### Data Boundary Normal Form

Use for config, CLI args, JSON, CSV rows, HTTP bodies, env vars, database rows,
forms, secrets, and typed templates.

```text
external value -> explicit decode -> binding constraints -> owned data or diagnostic
```

Canonical syntax:

```nomi
data Config:
    input:Path, exists(input)
    min_age:int, min_age >= 0 = 13

config = Config.decode(file("config.toml"))
```

Consolidation decisions:

- Boundary conversion should be explicit. Raw dictionaries should not silently
  become domain values.
- CLI, config, JSON, and CSV should share the same decode diagnostics:
  source path, field path, raw value, failed constraint, and user message.
- Secrets should be ordinary data values with redacted display policy, not a
  global logging special case.

### Explanation Normal Form

Use for diagnostics, examples, checks, trace, inspect, diff, query plans,
decode reports, and test output.

```text
semantic event -> trace record -> diagnostic or explanation view
```

Canonical syntax:

```nomi
func normalize_email(email:str) -> str:
    examples:
        " A@B.COM " => "a@b.com"
    return email.strip().lower()

check normalize_email(" A@B.COM ") == "a@b.com"

explain(Config.decode(raw))
```

Consolidation decisions:

- Examples should serve as docs, tests, and explanation anchors.
- `show`, `inspect`, and `diff` should be standard library/display concepts
  before they become syntax.
- Diagnostics must speak in user concepts: binding, field, parameter, block,
  case, path, command argument, query stage, or example.

## Newly Promoted Feature Candidates

These candidates extend the convenience roadmap while staying inside the
normal forms above.

For a broader second-pass survey of newer languages and PL research, including
Gleam, Roc, Unison, Koka, Flix, Zig, Mojo, Hylo, Vale, Verse, ReScript, CUE,
Nickel, Pkl, Dhall, Darklang, and modern array-language work, see
[expanded_language_research.md](expanded_language_research.md). That document
adds source-specific comparisons and keeps the admission decision tied to the
same normal forms.

| Candidate | Status | Normal form | Rationale | Critique |
| --- | --- | --- | --- | --- |
| Unified decode protocol for `data` | prototype-ready | data boundary + binding | Makes JSON/config/CLI/CSV one workflow. | Needs missing/extra field policy and source spans. |
| Result values with `Ok`/`Err` | design-needed | data + pattern | Gives expected failure a readable model. | Must coexist with Python exceptions during bootstrap. |
| Command functions | library-first | data boundary + call | Turns function/data constraints into CLIs. | `command` keyword may be unnecessary at first. |
| Config layering | library-first | decode + diagnostic | Defaults/file/env/args are common and repetitive. | Source precedence must be explicit and explainable. |
| Structured logs and trace blocks | library-first | block + trace | Makes logging data-shaped and inspectable. | Avoid hidden global logger semantics. |
| Path values and safe file helpers | library-first | data + constraint + block | Paths are not strings in everyday programs. | Must avoid bloating the core with OS policy. |
| Duration/date/time literals | design-needed | value + constraint | Timeouts, schedules, and cache TTLs need readable values. | Time zones and ambiguous local times require careful diagnostics. |
| Secret values | library-first | data + display policy | Prevents accidental leak in logs/diagnostics. | Must remain explicit at unwrap/use boundaries. |
| Typed templates | research-only for domains; prototype-ready for plain text | value + data boundary | Plain messages are common; SQL/HTML need escaping discipline. | Domain templates need typed output and escaping policy first. |
| Safe command execution | library-first | process result + diagnostics | Shell scripts need structured argv, status, stdout, stderr. | String shell mode must be explicit and visibly unsafe. |
| Small task definitions | design-needed | module + function + process | Project automation is everyday work. | Risk of becoming a build system too early. |
| Regex/string capture patterns | design-needed | pattern + binding | Useful for logs and text extraction. | Regex syntax must not become a second pattern language. |
| Query plans with `explain` | design-needed | flow + trace | Lets collection/table transforms scale to backends. | Needs plan/value boundary before syntax. |
| Shape/rank collection functions | research-only, library-first later | flow + collection | Learns from APL/J/Julia without glyph density. | Must not conflict with Python-compatible list arithmetic. |
| Field provenance for decoded values | prototype-ready after decode | data boundary + diagnostic | Makes CLI/config/JSON/CSV errors name source and raw value. | Requires source spans/provenance to survive decode. |
| Merge policies for layered config | library-first | data boundary + flow | Defaults/file/env/args need one predictable layering story. | Merge order and conflict policy must be explicit. |
| Result pipelines | design-needed | flow + result | Chaining expected failures should not force nested matches. | Must not hide error conversion or early exits. |
| Failure-only cleanup | library-first | block policy | Zig-style `errdefer` solves real cleanup friction. | Should integrate with transactions, not become a separate exit system. |
| Pure/read-only blocks | research-only | effect/capability boundary | Supports local reasoning without systems ownership syntax. | Too early before capabilities and mutation policy. |
| Projection bindings | research-only | binding target + data policy | Hylo-style projections could make focused updates expressive. | Aliasing and mutation semantics are not settled. |

## Cross-Feature Overlap And Decisions

### `shape` Versus `data.decode`

Older notes use `shape SignupPayload` for external data. The active foundation
now prefers no separate `shape` keyword in the first everyday layer. The
roadmap should therefore use:

```nomi
data SignupInput:
    email:str, contains(email, "@")
    age:int, age >= 13

input = SignupInput.decode(request.json)
```

Structural patterns remain available when the program does not want to name an
owned domain value:

```nomi
match request.json:
    case {"email": email:str, "age": age:(int, age >= 13)}:
        ...
```

### `guard`, `if-let`, `?`, And Early Exit

These are easy to confuse because all reduce indentation. They should be
taught as different special cases:

| Surface | Meaning | Normal form |
| --- | --- | --- |
| `if pattern = value:` | Continue only in this branch when the pattern fits. | pattern branch |
| `while pattern = value:` | Repeat while the pattern fits. | pattern loop |
| `guard pattern = value:` | Exit early when the pattern does not fit. | pattern branch plus explicit exit |
| `expr?` | Propagate expected failure. | result match plus early return |
| `value ?? fallback` | Use fallback only for absence. | absence expression |

Only the first three are prototype surface today. `expr?` should wait for
`Result` and return-type rules.

### Scope Functions Versus Blocks

Kotlin's `let`, `run`, `with`, `apply`, and `also` are useful, but Nomi should
not copy five overlapping names as language syntax. The Nomi split should be:

- use `where` for local expression bindings;
- use pipelines for value flow;
- use block calls for control policies;
- use ordinary library functions for occasional object-focused helpers.

### Trailing Lambda Versus Block Call

Kotlin trailing lambdas, Ruby blocks, and Gleam `use` solve similar indentation
problems. Nomi should make the caller-side block the canonical form:

```nomi
policy(args) -> bound_value:
    body
```

The function-call reduction must remain inspectable so users can understand
that `retry`, `using`, `trace`, and `test` are calls with attached blocks.

### Query Blocks Versus Pipelines

Pipelines should be the first user-facing flow story. Query blocks may be added
only when table/group/window semantics need a clearer scoped context:

```nomi
active_names =
    users
    |> where(_.active)
    |> select(_.name)
    |> sort
```

Future query syntax must reduce to the same verbs and expose an explainable
plan. It must not become embedded SQL with Nomi punctuation.

### Typed Templates Versus Strings

Plain interpolation is string construction. Typed templates are boundary
values with escaping and validation policy:

```nomi
message = f"Imported {count} rows"
query = sql"select * from users where id = {user_id}"
```

Only plain text belongs near-term. SQL/HTML/shell templates require typed
template values, diagnostics, and explicit escaping rules.

## Document Critique By File

### `functions.md`

Keep, but reorganize around the function normal form. Remove stale claims that
operator sections, holes, no-parens equations, defaults, composition, and
guards are future-only. Add usage guidance:

```nomi
double = _ * 2       # tiny one-argument transform
add = $1 + $2        # short positional relation
label = $user.name   # short named relation
full = (user) => ... # use when names or constraints matter
```

Reject-for-now: broad currying syntax and dense tacit style as everyday
defaults.

### `implicit_functions_nuance.md`

Keep as the living reference for `_`, `$1`, `$name`, operator sections, and
`=>`. Add a warning that implicit forms should not hide non-trivial control,
effects, or constraints.

### `patterns.md` And `if_let_detail.md`

Merge their teaching story around pattern normal form. Keep
`if_let_detail.md` for edge cases and make `patterns.md` the overview.
Document `guard-let` and `while-let` as implemented special cases of patterns.

Prototype-ready next slice: constrained captures in patterns.

### `collections.md` And `array_languages.md`

`collections.md` should teach pipelines, ranges, spread, and transform verbs.
`array_languages.md` should remain research-only until readable library
functions for shape/rank/axis exist.

Reject-for-now: implicit elementwise list arithmetic. It conflicts with
Python-compatible list behavior and is too easy to misread.

### `null_handling.md` And `error_handling.md`

Present absence and expected failure as related but distinct. `?.` and `??`
handle absence. `Result`, `Ok`, `Err`, `match`, and future `?` handle expected
failure. Exceptions remain for unexpected failure and Python interop.

Reject-for-now: `?? return` and mixed absence/error propagation without an
explicit result model.

### `scope_context.md`

Keep `where` as the primary local-binding feature. Treat Kotlin-style scope
functions as library-first helpers, not syntax. Point trailing-lambda and
builder-DSL ideas to block calls.

### `types.md`

Move `data`, variants, and decode discussion closer to `docs/language/`.
Type aliases remain a convenience feature. Extension methods and operator
overloading are design-needed; they touch dispatch, modules, and readability.

### `strings.md`

Update status for triple strings and simple f-strings. Add typed templates as
future boundary values, not as ordinary string sugar.

### `modules_imports.md`

Reframe imports as binding. Avoid many import spellings until module semantics
and export policy are stable.

Prototype-ready next slice: import diagnostics and explicit re-export policy,
not more syntax.

### `concurrency.md`

Demote broad concurrency to design-needed/research-only. Structured
concurrency should grow from block calls, cancellation, result values, and
capability boundaries, not from copied async syntax alone.

### `meta_testing.md`

Keep decorators as implemented Python-compatible surface. Treat examples,
checks, traces, and diffs as the near-term testing story. Keep macros
research-only until `quote:` and scoped expansion are specified.

### `others.md`

Keep as the broad survey, but do not let it drive the roadmap directly. Every
promoted idea should be copied into this review under a normal form and status.

## Roadmap

This roadmap is for later implementation. Each implementation commit should be
small, tested, documented, and reflected in samples.

### Phase 0: Documentation Cleanup

- [ ] Update each convenience doc with the status labels from this review.
- [ ] Use `expanded_language_research.md` as source material when updating
  feature docs with newer-language and PL-research comparisons.
- [ ] Remove stale "not implemented" claims for features already covered by
  tests or samples.
- [ ] Add a "Normal form" subsection to each feature doc.
- [ ] Move speculative material from convenience docs into research notes when
  it cannot reduce to a current primitive.
- [ ] Keep `docs/language/language_foundation.md` as the authority when it
  conflicts with older convenience notes.

### Phase 1: Binding, Patterns, And Diagnostics

- [ ] Constrained captures in match, if-let, while-let, and guard-let.
- [ ] Destructuring assignment through the shared binding engine.
- [ ] User-facing `BindingError` with source span, binding kind, failed
  constraint, raw value, and optional message.
- [ ] Examples that distinguish pattern failure from constraint failure.

Sample rule after implementation:

- add runnable examples to `samples/demo.nomi`;
- add the same feature in compressed form to `samples/demo_terse.nomi`;
- add or update focused tests first;
- only update samples after the focused and relevant broader tests pass.

### Phase 2: Data, Decode, And Everyday Boundaries

- [ ] Product `data` declarations with constrained fields.
- [ ] Explicit `Data.decode(value)` protocol for dict/JSON-like values.
- [ ] Missing/extra field policy with diagnostics.
- [ ] Library-first config layering and CLI decoding.
- [ ] Path values and safe file helpers.
- [ ] Secret values with redacted display.

Do not add a first-layer `shape` keyword in this phase.

### Phase 3: Result-Oriented Expected Failure

- [ ] `Result[T, E]` with `Ok` and `Err` data variants.
- [ ] Pattern examples for result handling.
- [ ] Parse/decode/file helpers that return results or diagnostic-rich errors
  consistently.
- [ ] Design a future propagation operator only after return-type rules and
  conversion semantics are explicit.

### Phase 4: Flow, Collections, And Query Plans

- [ ] Stabilize pipeline diagnostics and stage tracing.
- [ ] Standardize collection verbs: `map`, `where`, `select`, `derive`,
  `sort`, `fold`, `group`, `join`, `window`.
- [ ] Introduce table/row values as library concepts before query syntax.
- [ ] Add explainable query plans as values.
- [ ] Revisit query block syntax only after the verb model is stable.

### Phase 5: Blocks As Everyday Policy

- [ ] Standard library policies for `using`, `retry`, `timeout`,
  `transaction`, `trace`, and `test`.
- [ ] Block parameter binding through the same binding engine.
- [ ] Trace records for yield, resume, retry, cancel, and cleanup.
- [ ] Cancellation semantics before structured concurrency.

### Phase 6: Examples, Checks, Display, And Trace

- [ ] `examples:` blocks for functions and data declarations.
- [ ] `check` statements or expressions with diff-oriented output.
- [ ] `show`, `inspect`, and `diff` library functions.
- [ ] Trace records that can back diagnostics, logs, tests, and query plans.

### Phase 7: Scoped Advanced Power

- [ ] `quote:` boundary for code-as-data.
- [ ] Scoped rewrite rules and inspectable expansion.
- [ ] Typed templates for SQL/HTML/shell only after escaping rules are typed.
- [ ] Capability/world scopes after everyday blocks and result values are
  stable.
- [ ] Shape/rank collection functions as readable library features before any
  dense notation.

## Research References For This Pass

The pass used the existing Nomi docs plus primary/reference documentation for
languages that exercise similar design pressure:

- Kotlin scope functions and null safety:
  <https://kotlinlang.org/docs/scope-functions.html>,
  <https://kotlinlang.org/docs/null-safety.html>
- Rust patterns and recoverable errors:
  <https://doc.rust-lang.org/book/ch19-00-patterns.html>,
  <https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html>
- Swift control flow, optional chaining, and closures:
  <https://docs.swift.org/swift-book/LanguageGuide/ControlFlow.html>,
  <https://docs.swift.org/swift-book/LanguageGuide/OptionalChaining.html>,
  <https://docs.swift.org/swift-book/LanguageGuide/Closures.html>
- Elixir special forms and pattern-oriented control:
  <https://hexdocs.pm/elixir/Kernel.SpecialForms.html>
- Gleam results, case expressions, pipelines, and `use`:
  <https://tour.gleam.run/data-types/results/>,
  <https://tour.gleam.run/flow-control/case-expressions/>,
  <https://tour.gleam.run/advanced-features/use/>
- Elm `Maybe` and `Result`:
  <https://guide.elm-lang.org/error_handling/maybe.html>,
  <https://guide.elm-lang.org/error_handling/result>
- Nushell structured pipelines:
  <https://www.nushell.sh/book/pipelines.html>,
  <https://www.nushell.sh/book/types_of_data.html>
- Julia broadcasting:
  <https://docs.julialang.org/en/v1/manual/functions/>

## Admission Checklist

Before promoting a convenience feature to implementation:

1. Which normal form does it reduce to?
2. Does it duplicate another feature's user-facing role?
3. Can a user explain it as binding, function, pattern, flow, block, data
   boundary, absence/result, or explanation?
4. What is the smallest library-first version?
5. What diagnostic must it produce when it fails?
6. What syntax is deliberately rejected to keep the model coherent?
7. Which focused tests prove the behavior?
8. Which sample lines will be added to `samples/demo.nomi` and
   `samples/demo_terse.nomi` after tests pass?
