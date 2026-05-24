# Vertical Surface Pillars

> Status: active design review.
>
> Scope: documentation-only synthesis. This file identifies concrete surface
> pillars that users touch directly or indirectly across the language, in the
> same spirit as strings, functions, and collections. These are not automatically
> new normal forms. Each pillar must still reduce to existing normal-form owners
> until a capstone pass deliberately promotes it.
>
> Design posture: Nomi is exploratory. Treat this as a working map for research
> and feature packets, not a frozen taxonomy. Current docs and implementation
> are evidence; the goal is to follow the intended language: small semantic
> primitives, readable expression, explicit boundaries, inspectable reductions,
> and reversible implementation.

## Purpose

The previous pillar map over-indexed on support concerns such as trust,
lifecycle, and toolability. Those matter, but they are not the same kind of
thing as strings, functions, and collections. A user does not usually reach for
"trust" as a surface form. They reach for a path, a file, a URL, a result, a
duration, an import, a data value, or an example.

This document focuses on **tangible language surfaces**:

```text
thing users write/read -> cross-language pressure -> Nomi surface direction
```

Not:

```text
architectural concern -> governance guide -> vague principle
```

A vertical surface pillar is admitted when it:

- appears as a value, literal, declaration, call, block, pattern, or operator
  in ordinary programs;
- crosses several normal forms;
- affects syntax, interaction, diagnostics, tooling, and standard-library
  shape;
- is common enough that ad hoc library conventions would fragment the language;
- benefits from cross-language research before implementation;
- can still reduce to Nomi's small semantic primitives.

## Surface Pillar Map

| Priority | Surface pillar | What the user touches | Cross-cutting pressure | Current docs | Next packet |
|----------|----------------|-----------------------|------------------------|--------------|-------------|
| 0 | Strings And Text | `"..."`, `f"..."`, raw strings, regex, interpolation, display | Text crosses humans, formats, patterns, security, Unicode, logs, and diagnostics. | [strings.md](strings.md) | Continue string spec packet |
| 1 | Data Values And Variants | `data User`, fields, constructors, variants, records, enum-like cases | Values shape binding, patterns, decode, display, equality, examples, and schema export. | [data_and_types.md](data_and_types.md), [patterns.md](patterns.md) | `data_values_and_variants.md` or expand data doc |
| 2 | Resources And World Values | `Path`, `File`, `Url`, `Request`, `Response`, `Command`, `Secret`, capabilities | Programs touch files, network, env, subprocesses, secrets, and host authority through concrete values. | [strings.md](strings.md), [concurrency.md](concurrency.md), [data_and_types.md](data_and_types.md) | `resources_and_world.md` |
| 3 | Results, Absence, And Failure Values | `none`, `?`, `Result`, `Ok`, `Err`, `try`, errors, diagnostics | Non-success appears in access, parsing, IO, decode, match, pipelines, and block policies. | [absence_and_result.md](absence_and_result.md), [patterns.md](patterns.md) | Strengthen `absence_and_result.md` |
| 4 | Patterns And Selectors | `match`, destructuring, guards, regex capture, field/row selectors | Users choose by shape everywhere: data, external maps, rows, strings, results, and function clauses. | [patterns.md](patterns.md), [strings.md](strings.md) | `patterns.md` string-level review |
| 5 | Blocks, Policies, And Managed Calls | `using(...) -> x:`, `retry:`, `transaction:`, `defer`, `trace:` | Caller-attached code handles resources, transactions, tests, examples, concurrency, and control transfer. | [scope_context.md](scope_context.md), [concurrency.md](concurrency.md), [../features/block_calls_feature.md](../features/block_calls_feature.md) | `blocks_and_policies.md` |
| 6 | Numbers, Quantities, And Shape | integers, floats, decimals, money, units, ranges, arrays, dimensions | Numeric values drive correctness in loops, tables, formatting, money, time, measurement, and arrays. | [flow_and_collections.md](flow_and_collections.md), [data_and_types.md](data_and_types.md) | `numbers_quantities_and_shape.md` |
| 7 | Time And Temporal Values | `Duration`, `Instant`, `Date`, `TimeZone`, deadlines, schedules | Time shows up as values, parsed text, retries, timeout policies, tests, logs, and deterministic examples. | [concurrency.md](concurrency.md), [absence_and_result.md](absence_and_result.md) | `time_values.md` |
| 8 | Modules, Imports, And Packages | `import`, aliases, exports, package paths, versions, hashes | Names across files shape visibility, extension methods, package identity, reproducibility, and diagnostics. | [modules_imports.md](modules_imports.md), [scope_context.md](scope_context.md) | `modules_packages_and_identity.md` |
| 9 | Examples, Checks, And Explanation Surfaces | `examples:`, `check:`, `trace`, `explain`, structured logs | Users understand code through examples, diagnostics, traces, notebooks, LSP, and AI-readable events. | [meta_testing.md](meta_testing.md), [interaction_map.md](interaction_map.md) | `explanation_surfaces.md` |

Strings, functions, collections, and patterns are already prominent in the
convenience docs. The highest-value missing concrete surfaces are **Data
Values**, **Resources/World Values**, **Failure Values**, and **Blocks/Policies**.
They are tangible enough to improve syntax and interaction, while vertical
enough to require string-level research.

## Pillar 1: Data Values And Variants

### User Surface

```nomi
data User:
    id: UserId
    email: Email
    plan: Plan = Plan.Free

data Result[T, E]:
    Ok(value: T)
    Err(error: E)

user = User(id, email)
match user:
    case User(id, email, plan):
        ...
```

### Why It Is Vertical

Data values are where names, constraints, display, equality, patterns, decode,
serialization, examples, and schema export meet. If data is underdesigned,
every domain invents its own record/shape/schema/DTO convention.

### Normal-Form Ownership

| Surface | Owner | Reduction target |
|---------|-------|------------------|
| Field declaration | Binding | field value is tentatively bound and constrained |
| Constructor call | Function + Data boundary | ordinary call creates owned value |
| Variant case | Pattern + Data boundary | closed alternative with pattern form |
| Decode from JSON/CSV/config | Data boundary + Absence/result | parse/decode returns `Result` with paths |
| Display/equality/redaction | Explanation | generated event/display protocol |

### Cross-Language Evidence

- Rust, Swift, Kotlin, Scala, Haskell, and F# show that product/sum data is a
  central modeling surface.
- Python dataclasses/Pydantic show the ergonomic pull of runtime data models.
- TypeScript shows structural types are useful at boundaries but weak for
  exhaustiveness.
- Elm/serde/Pydantic show that decode diagnostics need field paths and
  accumulated errors.

### Nomi Direction

`data` should be the single owned-data declaration family. It should cover
records and variants without splitting into `struct`, `enum`, `class`,
`record`, `schema`, and `interface`.

Design-needed:

- exact constructor/display/equality generation;
- variant syntax and exhaustiveness diagnostics;
- field defaults and field-level constraints;
- decode provenance and error accumulation;
- schema export as tooling, not a second declaration language;
- extension methods and operator protocols for data values.

Rejected-for-now:

- a peer `schema` keyword for external data;
- structural type equivalence as the default owned-data model;
- generated magic methods that cannot be explained.

## Pillar 2: Resources And World Values

### User Surface

```nomi
path: Path = Path("./users.csv")
api: Url = Url("https://api.example.com")

using(open(path)) -> file:
    rows = file.read()
        |> Csv.decode(User)
        |> collect_results

cmd = Command("tar", ["-czf", archive, path])
```

### Why It Is Vertical

A resource is a concrete value that touches the outside world: file, URL,
socket, request, response, command, secret, random source, clock, database
connection. These are not just strings. They determine safety, permissions,
cleanup, failure, traces, and tests.

### Normal-Form Ownership

| Surface | Owner | Reduction target |
|---------|-------|------------------|
| `Path`, `Url`, `Command`, `Secret` | Data boundary + String pillar | typed value from text with explicit conversion |
| `File`, `Response`, `Connection` | Block + Absence/result | acquired value with scoped lifetime and failures |
| capability value | Data boundary + Explanation | authority with provenance and denial diagnostics |
| resource cleanup | Block | policy call owns cleanup and `yield` |
| logging/redaction | Explanation | structured event with safe display |

### Cross-Language Evidence

- Python `pathlib`, Rust `Path`/`Command`, Java `Path`, Go `os`/`exec`, and
  Swift `URL` show paths, URLs, and commands need typed APIs.
- Deno, Nix, and capability systems show authority should be visible.
- Shell languages show the danger of treating process invocation as string
  concatenation.
- Web and SQL APIs show that typed sinks prevent injection better than
  conventions.

### Nomi Direction

Make world-touching values typed and policy-shaped. A resource should either be
a plain inert value (`Path`, `Url`, `Command`) or an acquired value whose
lifetime is controlled by a block policy (`File`, `Connection`).

Design-needed:

- standard `Path`, `Url`, `Command`, `Secret`, `File`, `Request`, `Response`
  value contracts;
- `open`, `run`, `fetch`, and database APIs as typed sinks;
- capability manifests for Python, browser, Node, and future Wasm/WASI;
- redaction and `explain --unsafe`;
- how resource failures compose with `Result`, `defer`, and block cleanup.

Rejected-for-now:

- raw path/URL/command strings as the default API;
- shell-language string execution as the teaching path;
- ambient authority with no traceable capability.

## Pillar 3: Results, Absence, And Failure Values

### User Surface

```nomi
name = user.profile?.display_name ?? "Anonymous"

match parse_int(raw):
    case Ok(n): n
    case Err(problem): explain(problem)

guard Ok(config) = Config.decode(raw) else:
    return Err("bad config")
```

### Why It Is Vertical

Failure is not a subsystem. It appears in field access, parsing, decoding, IO,
networking, resource cleanup, validation, pattern matching, pipelines, examples,
and diagnostics. The user constantly sees and writes failure surfaces.

### Normal-Form Ownership

| Surface | Owner | Reduction target |
|---------|-------|------------------|
| `none`, `?.`, `??` | Absence/result | absence-only access and fallback |
| `Result`, `Ok`, `Err` | Data boundary + Pattern | expected failure as data |
| `try` expression | Absence/result + Explanation | local boundary around unexpected exception |
| `guard Ok(x) = ...` | Pattern + Flow | early exit on non-match |
| diagnostics/errors | Explanation | structured event with path, cause, and suggestion |

### Cross-Language Evidence

- Rust, Swift, Zig, Go, Gleam, Elm, Haskell, and Kotlin show the major failure
  forks: result values, exceptions, nullable values, and propagation operators.
- Python and JavaScript show the cost of mixing absence, falsey values,
  exceptions, and sentinel returns.
- Elm/Gleam show how strong result conventions improve everyday readability.

### Nomi Direction

Keep three stories separate:

- absence: `none`, `?.`, `??`;
- expected failure: `Result`, `Ok`, `Err`, pattern matching;
- unexpected failure: exception/diagnostic boundary.

Design-needed:

- exact `Result` and `Option` data declarations;
- whether a propagation operator exists and what it expands to;
- failure behavior in pipelines;
- error context chaining;
- cleanup failure vs body failure diagnostics;
- `collect_results` and related flow helpers.

Rejected-for-now:

- `?.` catching `Err` or exceptions;
- sentinel values like `-1` for search/parse failure;
- Go-style `(value, err)` as the primary surface.

## Pillar 4: Patterns And Selectors

### User Surface

```nomi
match event:
    case {"type": "click", "target": target}:
        record_click(target)
    case User(id, email):
        send(email)
    case re"(\w+)@(.+)" as name, domain:
        validate(name, domain)

active_names = users |> where(_.active) |> select(_.name)
```

### Why It Is Vertical

Patterns and selectors are how users pull meaning out of values. They appear in
`match`, `if-let`, `guard-let`, function clauses, data constructors, rows,
strings, regexes, table transforms, and query plans.

### Normal-Form Ownership

| Surface | Owner | Reduction target |
|---------|-------|------------------|
| `match` case | Pattern | shape test, tentative captures, constraints |
| `if/guard pattern = value` | Pattern + Flow | conditional binding or early exit |
| field selector `_.name` | Function + Flow | tiny function over selected field |
| regex capture | Pattern + String pillar | string test plus capture binding |
| row/group selector | Binding + Flow | visible row/group scope |

### Cross-Language Evidence

- ML/Rust/Swift/Kotlin/Scala show match as a major readability surface.
- Elixir/Gleam show pattern matching as everyday binding.
- SQL/LINQ/dplyr show selectors become their own language if row scope is not
  designed explicitly.
- JavaScript/Python destructuring show lightweight patterns are useful but can
  drift from full match semantics.

### Nomi Direction

Unify pattern use without making selectors magical. Pattern failure, constraint
failure, and `Err` should remain distinguishable.

Design-needed:

- function clause patterns vs explicit `match`;
- selector shorthand and row scope;
- regex capture syntax and typed groups;
- mapping/list pattern diagnostics;
- exhaustiveness for nominal variants;
- `explain match` trace shape.

Rejected-for-now:

- a second query selector language with hidden row scope;
- nil-specific binding syntax that bypasses patterns;
- regex literals as a grammar-level pattern language.

## Pillar 5: Blocks, Policies, And Managed Calls

### User Surface

```nomi
using(open(path)) -> file:
    text = file.read()

retry(3, on=NetworkError):
    send(request)

transaction(db):
    db.insert(user)

trace "import users":
    import_users(path)
```

### Why It Is Vertical

Blocks are concrete syntax users read constantly: resource scopes,
transactions, tests, examples, retries, traces, callbacks, concurrency, and
future effect policies. If every domain gets a keyword, the language becomes a
menu. If everything is a callback, the user experience collapses.

### Normal-Form Ownership

| Surface | Owner | Reduction target |
|---------|-------|------------------|
| attached block call | Block + Function | ordinary call plus caller-side code invoked by `yield` |
| block parameter | Binding | scoped binding with constraints |
| resource policy | Block + Absence/result | acquire, yield, cleanup, report failure |
| examples/checks | Block + Explanation | executable code with expected result |
| concurrency policy | Block + Flow | scoped scheduling/cancellation policy |

### Cross-Language Evidence

- Ruby blocks, Kotlin/Swift trailing closures, Python context managers, Gleam
  `use`, Go `defer`, and Zig `errdefer` all solve pieces of this surface.
- Effect-handler languages show the broader shape, but too much effect theory
  would burden ordinary code.

### Nomi Direction

Keep one visible attached-block story. Domain policies should be library calls
first, not new keywords.

Design-needed:

- exact block-call spelling and parameter binding;
- `yield` event semantics;
- cleanup/body failure ordering;
- block result and `Result` propagation;
- trace/example/check integration;
- structured concurrency as block policy.

Rejected-for-now:

- many domain keywords: `with`, `using`, `transaction`, `retry`, `test` as
  unrelated syntax families;
- implicit receivers that hide block scope;
- callback-heavy APIs as the primary teaching path.

## Pillar 6: Numbers, Quantities, And Shape

### User Surface

```nomi
count: int = 42
price: Money["USD"] = Money.usd("12.99")
timeout: Duration = 2.seconds
area = width.meters * height.meters
matrix.shape()
values |> window(7) |> select(mean)
```

### Why It Is Vertical

Numeric values are everywhere, but the hard parts are concrete: money,
decimals, units, durations, ranges, sizes, percentages, arrays, tables,
statistics, and display. This surface affects literals, parsing, constraints,
collection flow, formatting, and diagnostics.

### Normal-Form Ownership

| Surface | Owner | Reduction target |
|---------|-------|------------------|
| numeric literal | Data boundary | typed value construction |
| range/step | Flow | collection value or iterator |
| unit/quantity | Data boundary + Function | typed wrapper plus arithmetic protocols |
| array shape/rank | Flow + Explanation | named shape/rank functions with inspectable plans |
| formatting | String pillar + Explanation | display protocol with units/precision |

### Cross-Language Evidence

- Python/JavaScript show the cost of easy binary floats for everything.
- Julia/R/MATLAB/APL show the power and risk of numeric/array-first design.
- F#, Swift packages, and scientific libraries show units and quantities are
  valuable but can become type-heavy.
- Finance software shows money must not be casual float arithmetic.

### Nomi Direction

Start boring and explicit. Add domain power through typed values and named
shape/rank functions before dense notation.

Design-needed:

- integer/float/decimal/money boundaries;
- unit and quantity wrappers;
- range and shape vocabulary;
- display and parse protocols;
- overflow/precision policy;
- table numeric summary verbs.

Rejected-for-now:

- dense array glyphs as ordinary syntax;
- implicit unit conversion across domains;
- binary float in money examples.

## Pillar 7: Time And Temporal Values

### User Surface

```nomi
timeout = 2.seconds
started: Instant = clock.now()
due: LocalDate = Date.parse("2026-05-24") |> require_ok

within(timeout):
    fetch(url)
```

### Why It Is Vertical

Time appears as values, parsed text, formatting, deadlines, retries,
observability, scheduling, tests, and cleanup. It is concrete, user-facing, and
easy to get wrong if represented as strings or raw numbers.

### Normal-Form Ownership

| Surface | Owner | Reduction target |
|---------|-------|------------------|
| `Duration`, `Instant`, `Date` | Data boundary | typed temporal values |
| parse/format | String pillar + Absence/result | explicit `Result` from text |
| timeout/deadline block | Block + Absence/result | scoped policy with failure reason |
| test clock | Explanation + Data boundary | deterministic clock capability |
| logs/traces | Explanation | event time source recorded |

### Cross-Language Evidence

- Java/.NET histories show ambiguous date-time APIs are long-lived mistakes.
- Rust and Go separate monotonic and wall-clock concerns.
- JavaScript shows how a single weak `Date` abstraction leaks everywhere.
- Kotlin/Swift structured concurrency shows deadlines and cancellation should
  be scoped.

### Nomi Direction

Make time visible as typed values and scoped policies, not raw seconds or
ambient globals.

Design-needed:

- `Duration`, `Instant`, `LocalDate`, `DateTime`, and `TimeZone` contracts;
- monotonic vs wall-clock split;
- parse/format behavior and locale boundaries;
- deterministic test clocks;
- timeout, cancellation, cleanup failure interaction.

Rejected-for-now:

- one universal `DateTime`;
- implicit global clock in examples/tests;
- raw integer seconds as the everyday API.

## Pillar 8: Modules, Imports, And Packages

### User Surface

```nomi
import "example.com/acme/users" as users
import "example.com/schemas/user.nomi" sha256:abc123...

pub func normalize(user: User) -> User:
    ...
```

### Why It Is Vertical

Imports and packages are concrete syntax, but they also define identity,
visibility, extension availability, build reproducibility, examples, docs, and
diagnostics. A language can feel clean locally and still become unpleasant if
module identity is muddy.

### Normal-Form Ownership

| Surface | Owner | Reduction target |
|---------|-------|------------------|
| import | Binding + Data boundary | external module decoded into visible names |
| alias | Binding | local name for imported value/module |
| export/public | Binding + Explanation | visible API plus docs/examples |
| package path/version/hash | Data boundary + Explanation | provenance and reproducibility |
| extension visibility | Function + Binding | imported protocol/function visible at use site |

### Cross-Language Evidence

- Go and Deno make import paths explicit and domain-shaped.
- Rust/Cargo shows package identity, features, docs, examples, and editions
  need one coherent story.
- Python shows import-time side effects are powerful but surprising.
- Nix/Dhall show content-addressed imports as a reproducibility tool.

### Nomi Direction

Treat imports as binding events with provenance. Keep package identity visible
enough for diagnostics and reproducibility.

Design-needed:

- file path vs domain path vs package name rules;
- import-time side-effect policy;
- visibility/export syntax;
- extension method conflict diagnostics;
- `explain import`;
- package incubation and edition policy.

Rejected-for-now:

- implicit global package namespace;
- wildcard imports as the default path;
- hidden import-time configuration.

## Pillar 9: Examples, Checks, And Explanation Surfaces

### User Surface

```nomi
func normalize_email(email: str) -> str:
    examples:
        " A@B.COM " => "a@b.com"
    return email.strip().lower()

check:
    normalize_email("x@y.com") == "x@y.com"

explain:
    users |> select(User.decode) |> collect_results
```

### Why It Is Vertical

Examples, checks, traces, diagnostics, and explanation are concrete surfaces a
user sees while writing and debugging. This pillar is not just tooling: it is
how Nomi makes reductions inspectable and keeps advanced syntax humane.

### Normal-Form Ownership

| Surface | Owner | Reduction target |
|---------|-------|------------------|
| `examples:` | Explanation + Block | executable examples attached to code |
| `check:` | Explanation + Block | assertion block with diagnostics |
| `trace` | Explanation + Block | contextual event scope |
| `explain` | Explanation | render semantic events and reductions |
| structured log | Explanation + Data boundary | event with redaction/provenance |

### Cross-Language Evidence

- Rust and Elm show diagnostics are architecture, not prose polish.
- Racket, Smalltalk, Jupyter, Pluto, and Observable show interactive
  explanation shapes the language experience.
- LSP and AI-readable traces show why events should be structured, not just
  strings.

### Nomi Direction

Make examples, checks, traces, logs, and `explain` views share one event
vocabulary.

Design-needed:

- canonical event schema;
- example/check execution timing;
- redaction and unsafe reveal;
- expansion display for sugar and scoped extensions;
- query/flow plan explanation;
- notebook/LSP/AI rendering targets.

Rejected-for-now:

- string logs as the only observability surface;
- stack traces as the main user diagnostic;
- macro/DSL features with opaque expansion.

## Support Concerns

Trust, effects, lifecycle, style, editions, and toolability are still crucial.
But they should usually enter through one of the concrete surfaces above:

| Support concern | Concrete surfaces where it manifests |
|-----------------|---------------------------------------|
| Trust/security | Resources, strings, data boundaries, examples, modules |
| Lifecycle/cancellation | Blocks, resources, time values, results |
| Formatting/style | Every syntax surface; especially data, patterns, flow, blocks |
| Toolability/AI-readability | Examples, explanation, modules, generated artifacts |
| Evolution/editions | Modules/packages, syntax surfaces, formatter, migrations |

This keeps the design tangible. A support concern becomes actionable when it
changes what users write, read, inspect, or diagnose.

## Recommended Next Passes

Do not fully specify every pillar at once. The highest-value sequence is:

1. **Data Values And Variants** — concrete, central, and currently too
   compressed inside `data_and_types.md`.
2. **Resources And World Values** — immediately improves paths, URLs, commands,
   files, secrets, IO, security, and browser/runtime capability design.
3. **Results, Absence, And Failure Values** — sharpens failure ergonomics
   across parse/decode/IO/pipelines.
4. **Blocks, Policies, And Managed Calls** — turns resource handling, retry,
   examples, tracing, and concurrency into one visible interaction.
5. **Numbers, Quantities, And Shape** and **Time Values** — prevent quiet
   correctness bugs before the standard library ossifies.

Each pillar should eventually get a string-style packet:

```text
user surface
design pressure
normal-form ownership
cross-language evidence
Nomi direction
status table
spec packet needed
rejected alternatives
implementation/research next steps
```

## Design Context

- [Strings](strings.md) — model for a concrete cross-cutting surface that
  reduces to existing normal forms instead of becoming a new primitive by
  default.
- [Data & Types](data_and_types.md) — current home for data declarations,
  aliases, decode, secrets, and type-shaped boundaries.
- [Absence & Result](absence_and_result.md) — current home for absence,
  expected failure, exceptions, `try`, and cleanup.
- [Flow & Collections](flow_and_collections.md) — current home for collection
  and pipeline surfaces.
- [Interaction Map](interaction_map.md) — global/local feature interactions
  and one-way synthesis choices.
- [Syntax Design Rules](syntax_design_rules.md) — primitive budget and axis
  coherence rules.
- [Cross-Language Synthesis Master](../research/cross_language_synthesis_master.md) —
  capstone normal-form synthesis and risk that the normal-form count may be
  wrong.
