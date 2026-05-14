# Expanded Language Research For Convenience Features

> Status: active source note for the convenience roadmap.
>
> Scope: documentation-only research pass. This document brings in ideas from
> newer languages, configuration languages, array languages, and PL research,
> then translates them into Nomi normal forms. It is not an implementation
> plan by itself.

## Purpose

Nomi's convenience features should make everyday programming more fun,
memorable, and scalable. The main risk is not a lack of ideas. The risk is
having several almost-equivalent features that force users to remember small
differences:

```text
optional chaining vs result propagation
if-let vs guard vs pattern match
callbacks vs block calls vs effect handlers
schema vs data vs shape vs decoder
pipe vs method chain vs query block
defer vs using vs finally vs transaction
```

This pass looks at additional source languages and PL research, then maps their
features back to the normal forms in
[review_and_roadmap.md](review_and_roadmap.md):

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

For a broader cross-language grouping of similar features and their subtle
differences, see [syntax_synthesis_matrix.md](syntax_synthesis_matrix.md).
That companion document adds OCaml, F#, Clojure, Racket, Scala 3, Nim, Crystal,
Julia, Nushell, Nix, Terraform/HCL, and related configuration/documentation
systems to the comparison surface.

For the aspirational whole-program check, see
[Target Language Tour](../language/target_language_tour.md). This research file
names source pressures; the tour tests whether the recommended Nomi spelling
still feels coherent when those pressures meet in one program.

The rule remains:

```text
Do not copy the feature. Extract the need, then reduce it to a Nomi normal form.
```

## Sources Reviewed

The pass looked at:

- Gleam: `use`, results, pattern matching, and list patterns.
- Roc: result-first error handling, `?`, tests, pipes, and list patterns.
- ReScript: pipe, pattern/destructuring, exhaustive variants, dictionary
  patterns, optional fields.
- Unison: abilities and handlers.
- Koka, Eff, and Flix: effect types, handlers, algebraic data, region-local
  state, and Datalog.
- Zig: error unions, `try`, `catch`, `defer`, `errdefer`, comptime, tests.
- Mojo: Python-shaped systems features, typed errors, ownership, traits, and
  context managers.
- Hylo and Vale: mutable value semantics, projections, regions, and pure
  blocks.
- Verse: failable expressions, failure contexts, and speculative rollback.
- CUE, Nickel, Pkl, and Dhall: configuration as constraints, contracts,
  defaults, merge/layering, typed config, and multi-format output.
- Darklang: saved traces, live values, deployless workflow.
- BQN and Uiua: modern array-language pressure around rank, shape, mapping,
  tacit style, and modifiers.

## High-Value Lessons

### 1. Callback Flattening Is A Block Story

Reference pressure:

- Gleam's `use` flattens callback-heavy code by turning following code into a
  final callback argument.
- Kotlin trailing lambdas, Ruby blocks, Python context managers, pytest
  fixtures, and Swift trailing closures solve related indentation problems.
- Unison/Koka/Eff/Flix effect handlers go further: they abstract operations
  like exceptions, async, state, streams, and nondeterminism through handlers.

Nomi translation:

```text
callback flattening -> block normal form
effect handler      -> future scoped block/effect policy
```

Candidate Nomi surface:

```nomi
using(open(path)) -> file:
    text = file.read()

retry(3, on=NetworkError):
    fetch(url)

trace "import people":
    rows = read_csv(path)
```

Coherence decision:

- Keep one caller-side block form for everyday control.
- Treat `use`, trailing lambda, context manager, fixture, retry, and trace as
  uses of the same normal form.
- Do not expose algebraic effect handlers as everyday syntax until block calls,
  diagnostics, cancellation, and capability scopes are stable.

Status:

```text
block calls: prototype-ready/design-needed depending on exact block semantics
effect handlers: research-only for now
```

### 2. Expected Failure, Absence, And Exceptions Must Stay Distinct

Reference pressure:

- Roc and Gleam emphasize explicit `Result` values.
- Roc and Zig provide propagation operators for result/error-like values.
- Zig error unions and `catch` keep errors as values rather than stack
  unwinding exceptions.
- Mojo keeps a Python-like `try` surface while also representing errors as
  alternate return values and supporting typed errors.
- Verse makes failure a control-flow concept inside special failure contexts.

Nomi translation:

```text
none/missing value    -> absence normal form
recoverable failure   -> Result data + pattern normal form
unexpected failure    -> error/exception normal form
speculative failure   -> future transaction/block normal form
```

Candidate Nomi surface:

```nomi
name = user?.name ?? "anonymous"

match parse_int(raw):
    case Ok(n):
        n
    case Err(error):
        explain(error)
```

Potential future:

```nomi
age = parse_int(raw_age)?
```

Coherence decision:

- `?.` and `??` are only for absence.
- `Result`, `Ok`, `Err`, and `match` are the main expected-failure story.
- A future `?` operator is only acceptable if it desugars to result matching
  plus an explicit return/propagation rule.
- Verse-style speculative failure is interesting, but it should reduce to a
  transaction-like block policy with rollback diagnostics, not general boolean
  control.

Status:

```text
absence operators: implemented/partial
Result values: design-needed
result propagation: design-needed
speculative failure contexts: research-only
```

### 3. Pattern, Destructuring, Decode, And Config Schema Are One Boundary Family

Reference pressure:

- ReScript combines destructuring, shape-based switch, and exhaustiveness under
  pattern matching.
- Roc and Gleam list patterns make head/tail cases visible.
- CUE treats data, schema, and policy constraints as coexisting values.
- Nickel composes configuration from records, defaults, contracts,
  documentation, and merges.
- Pkl and Dhall show the demand for typed, programmable, multi-output
  configuration.

Nomi translation:

```text
pattern matching       -> pattern normal form
config/schema/checking -> data boundary normal form
decode                 -> binding + constraints + diagnostic
config layering        -> merge policy + decode diagnostic
```

Candidate Nomi surface:

```nomi
data Config:
    input:Path, exists(input)
    output:Path
    min_age:int, min_age >= 0 = 13

config = Config.decode:
    defaults {"min_age": 13}
    file "app.toml"
    env prefix="APP_"
    args cli_args
```

Coherence decision:

- Do not add a second field system named `schema`, `shape`, `contract`, or
  `config` for everyday code.
- Owned domain values use `data`.
- External values cross through `Data.decode(...)` or structural patterns.
- Config layering is a library/block policy over source values before it is
  syntax.
- Defaults, optionality, documentation, and provenance belong on decoded fields
  and diagnostics, not in a separate config language.

Status:

```text
data decode: prototype-ready
config layering: library-first
schema/config keyword: rejected-for-now
named structural contracts: design-needed later
```

### 4. Pipelines, Method Chains, Query Blocks, And Array Modifiers Are One Flow Family

Reference pressure:

- Roc, ReScript, Elixir, F#, and many others make pipelines a readability tool.
- ReScript's pipe can pipe into a chosen placeholder position.
- SQL, dplyr, pandas, Polars, and DuckDB show the need for a stable transform
  vocabulary over rows and tables.
- BQN, Uiua, APL/J/K/Q, and Julia show the power of shape/rank-aware array
  transforms.

Nomi translation:

```text
pipe/method chain -> flow normal form
query block       -> scoped flow normal form over row/group bindings
array modifier    -> collection flow with shape/rank metadata
```

Candidate Nomi surface:

```nomi
names =
    users
    |> where(_.active)
    |> select(_.name)
    |> sort
```

Future library-first array pressure:

```nomi
matrix
|> cells(rank=1, normalize)
|> each(_ * 100)
```

Coherence decision:

- Pipeline is the primary flow syntax.
- Query blocks must reduce to the same verb vocabulary and expose query plans.
- Array rank/shape should start as named functions, not dense glyphs.
- ReScript-style placeholder piping is already covered by Nomi's `_` rule; do
  not add another placeholder family.

Status:

```text
pipeline: implemented/partial
collection verbs: library-first
query blocks: design-needed
rank/shape functions: research-only, library-first later
```

### 5. Cleanup, Resources, And Rollback Are Block Policies

Reference pressure:

- Zig has `defer` and `errdefer` for scope exit and error-only cleanup.
- Python, Mojo, and Swift have context/finalization surfaces.
- Verse failure contexts include speculative execution and rollback.
- Database transactions and tests need the same acquire/yield/commit/rollback
  shape.

Nomi translation:

```text
defer/finally          -> block exit policy
using/context manager  -> block resource policy
transaction/rollback   -> block policy with trace
errdefer               -> failure-only block policy
```

Candidate Nomi surface:

```nomi
using(open(path)) -> file:
    text = file.read()

transaction(db):
    db.users.insert(user)
```

Possible library naming:

```nomi
on_exit:
    cleanup()

on_error:
    rollback()
```

Coherence decision:

- Keep `defer` as small scope-exit convenience where already implemented.
- Use block policies for resource acquisition and rollback.
- Do not introduce `with`, `using`, `defer`, `finally`, `errdefer`, and
  `transaction` as unrelated mechanisms. Teach them as one block-policy family.

Status:

```text
defer: implemented/partial
using/retry/transaction/trace: prototype-ready/design-needed
errdefer-style failure cleanup: library-first
```

### 6. Ownership, Regions, Projections, And Purity Are Future Capability Work

Reference pressure:

- Mojo uses ownership, transfer, mutable/immutable references, and traits in a
  Python-like language family.
- Hylo's mutable value semantics and subscripts model reusable projections.
- Vale regions and pure blocks show a way to bound mutation and memory access.
- Flix combines effects with region-based local mutation.

Nomi translation:

```text
ownership/regions -> future effect/capability/world discipline
projection        -> future binding target or lens-like pattern
pure block        -> future capability restriction block
```

Potential future:

```nomi
pure:
    summary = rows |> summarize

world(fs, network) -> w:
    response = w.network.get(url)
```

Coherence decision:

- Do not bring systems-language ownership syntax into the first everyday
  layer.
- Local reasoning is valuable, but for Nomi it should first appear as
  diagnostics, explicit resource blocks, immutable data defaults, and
  capability scopes.
- Projection/lens features should wait until binding targets, patterns, and
  data mutation policy are stable.

Status:

```text
pure/capability blocks: research-only
projections/lenses: research-only
ownership syntax: rejected-for-now
```

### 7. Trace-Driven Development Is An Explanation Story

Reference pressure:

- Darklang saves request inputs and intermediate values as traces.
- Polars-style lazy plans and query explanations show the value of
  inspectable computation descriptions.
- CUE/Nickel/Pkl diagnostics show field paths and constraint sources.

Nomi translation:

```text
live values   -> trace normal form
query explain -> flow + explanation normal form
decode errors -> data boundary + diagnostic normal form
examples      -> explanation + test normal form
```

Candidate Nomi surface:

```nomi
trace "import people":
    rows = read_csv(input)
    accepted = rows |> where(valid_person)

explain(Config.decode(raw))
```

Coherence decision:

- Trace is not just logging. It is the shared substrate for diagnostics,
  examples, query plans, block policies, and decode reports.
- Keep logs, tests, examples, and explanations connected through trace records
  rather than inventing separate reporting formats.
- Use the target language tour to keep provenance, traces, and examples
  connected in one program instead of optimizing each feature in isolation.

Status:

```text
trace records: design-needed
trace block policy: library-first/prototype-ready
live production trace system: research-only
```

## Similar But Not Same: Consolidation Table

| Source features | Temptation | Nomi consolidation |
| --- | --- | --- |
| Gleam `use`, Kotlin trailing lambda, Ruby block, Python context manager | Add many block syntaxes | One block-call syntax with optional binding target. |
| Roc `?`, Zig `try`, Rust `?`, Gleam `Result`, Verse failure | One propagation operator for everything | Keep absence, result, exception, and speculative rollback separate. Add propagation only for `Result`. |
| CUE schemas, Nickel contracts, Pkl classes, Dhall types, JSON Schema | Add `schema` or `shape` as a peer to `data` | Use `data` for owned values, `Data.decode` for external values, patterns for one-off structure. |
| ReScript pipe, Roc pipe, Elixir pipe, method chaining | Add several pipe operators | Keep `|>` plus placeholder `_`; composition remains separate. |
| SQL query, dplyr verbs, pandas chain, Polars lazy plan | Embed a query language early | Start with pipeline verbs and plan values. Add query syntax only if scoped row/group binding needs it. |
| Zig `defer`, Swift `defer`, `finally`, context managers, transactions | Add separate cleanup forms | Teach cleanup/resource/rollback as block policies; keep small `defer` for local scope exit. |
| Mojo ownership, Hylo projections, Vale regions, Flix regions | Add safety syntax now | Keep as future capability/projection research until core data/binding/mutation policy exists. |
| BQN/Uiua tacit array style, Julia broadcasting, APL rank | Add dense array notation | Start with named collection and rank/shape functions. Dense notation is scoped advanced power only. |
| Darklang traces, test examples, query explain, decode diagnostics | Separate logging/testing/explain systems | Use trace records as shared explanation substrate. |

## New Candidate Features To Add To The Roadmap

### Field Provenance

Status: prototype-ready after `Data.decode`.

Normal form: data boundary + diagnostic.

Every decoded field should remember where it came from:

```text
source kind: default, file, env, arg, request, row
source name/path: APP_PORT, config.toml:12, --port
raw value
decoded value
constraint history
```

This absorbs lessons from CUE/Nickel/Pkl and makes config, CLI, CSV, and JSON
errors feel like one system.

### Merge Policies

Status: library-first.

Normal form: data boundary + flow + diagnostic.

Config layering needs explicit merge policy:

```nomi
config = Config.decode:
    merge defaults
    merge file("app.toml")
    merge env(prefix="APP_")
    merge args(cli_args)
```

The first version should be a library API, not new syntax.

### Result Pipelines

Status: design-needed.

Normal form: flow + result.

Roc, Gleam, Rust, Zig, and Elm all show that expected-failure code becomes
tedious without chaining. Nomi should first support clear `match` handling,
then consider pipeline-aware result helpers:

```nomi
user =
    raw
    |> parse_json_result
    |> then(User.decode)
    |> then(save_user)
```

Only after this is readable should `?` be considered.

### Failure-Only Cleanup

Status: library-first.

Normal form: block policy.

Zig's `errdefer` points to a useful need: cleanup only when the current block
fails. Nomi should express this as a policy:

```nomi
on_error:
    rollback()
```

This should integrate with transactions, block cancellation, and diagnostics.

### Pure/Read-Only Blocks

Status: research-only.

Normal form: effect/capability boundary.

Vale, Hylo, Flix, Koka, and Unison all point toward visible effect boundaries.
Nomi could eventually have:

```nomi
pure:
    summary = rows |> summarize
```

But the first everyday language should get block policies, diagnostics, and
data values right before adding purity syntax.

### Projection Bindings

Status: research-only.

Normal form: binding target + data mutation policy.

Hylo's subscripts and mutable projections are powerful, but they touch aliasing
and mutation. Nomi should defer them until it has a clear story for mutable
data, field updates, lenses, or copy-with-update.

### Query/Transform Plans

Status: design-needed.

Normal form: flow + explanation.

Collection transforms should be able to become values:

```nomi
plan =
    query(users)
    |> where(_.active)
    |> select(_.name)

explain(plan)
```

This bridges everyday pipelines, table queries, lazy execution, and
diagnostics without embedding SQL strings.

## Rejections For The First Everyday Layer

- Multiple callback syntaxes for the same block/call operation.
- A separate `schema`, `shape`, or `contract` field declaration language that
  duplicates `data` and binding constraints.
- A general `?` operator that propagates both absence and errors.
- Dense array glyphs as default syntax.
- Systems-language ownership or region annotations in everyday code.
- Full algebraic effect handlers before block calls and diagnostics are
  proven.
- Global macros or unscoped notation plugins.
- A build-system/task language before modules, process results, and diagnostics
  are stable.

## Recommended Follow-Up Docs

- Update `error_handling.md` with a Roc/Zig/Gleam/Rust comparison that keeps
  `Result`, exceptions, and absence separate.
- Update `scope_context.md` with Gleam `use` as evidence for block calls rather
  than a separate construct.
- Update `collections.md` with a pipe/query/array-modifier consolidation
  section.
- Update `types.md` with data/decode/config boundary guidance from CUE, Nickel,
  Pkl, and Dhall.
- Update `meta_testing.md` with trace-driven examples and Darklang-style saved
  values as research pressure.

## Source Links

- Gleam `use`: <https://tour.gleam.run/advanced-features/use/>
- Gleam list patterns: <https://tour.gleam.run/flow-control/list-patterns/>
- Roc tutorial and result handling: <https://www.roc-lang.org/tutorial>
- Roc error handling example: <https://www.roc-lang.org/examples/ErrorHandlingBasic/README>
- ReScript pattern matching: <https://rescript-lang.org/docs/manual/pattern-matching-destructuring/>
- ReScript pipe: <https://rescript-lang.org/docs/manual/v11.0.0/pipe>
- Unison abilities: <https://www.unison-lang.org/docs/language-reference/abilities-and-ability-handlers/>
- Koka overview: <https://www.microsoft.com/en-us/research/project/koka/>
- Koka book, effect handlers: <https://koka-lang.github.io/koka/doc/book.html>
- Flix introduction: <https://doc.flix.dev/>
- Eff language: <https://www.eff-lang.org/>
- Zig language reference: <https://ziglang.org/documentation/master/>
- Mojo ownership: <https://mojolang.org/docs/manual/values/ownership/>
- Mojo errors: <https://mojolang.org/docs/manual/errors/>
- Mojo traits: <https://mojolang.org/docs/manual/traits/>
- Hylo subscripts: <https://hylo-lang.org/docs/user/language-tour/subscripts/>
- Hylo overview: <https://www.hylo-lang.org/>
- Vale regions: <https://vale.dev/guide/regions>
- Verse quick reference: <https://dev.epicgames.com/documentation/en-us/uefn/verse-language-quick-reference>
- Verse language reference: <https://dev.epicgames.com/documentation/en-us/uefn/verse-language-reference>
- CUE docs: <https://cuelang.org/docs/>
- Nickel merging: <https://nickel-lang.org/user-manual/merging/>
- Pkl docs: <https://pkl-lang.org/main/current/index.html>
- Dhall: <https://dhall-lang.org/>
- Darklang traces: <https://docs.darklang.com/contributing/general-concepts>
- BQN arrays: <https://mlochbaum.github.io/BQN/doc/array.html>
- BQN mapping modifiers: <https://mlochbaum.github.io/BQN/doc/map.html>
- Uiua repository and docs pointer: <https://github.com/uiua-lang/uiua>
