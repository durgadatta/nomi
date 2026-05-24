# Vertical Pillars

> Status: active design review.
>
> Scope: documentation-only synthesis. This file identifies language
> experience pillars that cut vertically across Nomi's normal forms. They are
> not new normal forms by default. Like [strings.md](strings.md), each pillar
> must reduce to existing normal-form owners until a capstone pass deliberately
> promotes it.
>
> Design posture: Nomi is exploratory. Treat this as a working map for research
> and feature packets, not a frozen taxonomy. Current docs and implementation
> are evidence; the goal is to follow the intended language: small semantic
> primitives, readable expression, explicit boundaries, inspectable reductions,
> and reversible implementation.

## Purpose

Some concerns are too pervasive to live comfortably in a single feature doc.
Strings are one: they touch data boundaries, patterns, flow, absence/result,
security, display, diagnostics, and tooling. Functions and collections are
similar: they are normal-form owners, but also shape the entire feel of the
language.

This document asks:

```text
Which other concerns are vertical enough to deserve string-level treatment?
```

A vertical pillar is admitted when it:

- appears in first-hour programs and in serious production programs;
- crosses at least four normal forms;
- affects syntax, runtime behavior, diagnostics, tooling, and standard-library
  shape;
- becomes dangerous or incoherent if handled as ad hoc library calls;
- benefits from cross-language research before implementation;
- can still reduce to Nomi's small semantic primitives.

## Priority Map

| Priority | Pillar | Why vertical | Current owner docs | Next artifact |
|----------|--------|--------------|--------------------|---------------|
| 1 | Trust, Effects, And Capabilities | Every program touches files, network, env, secrets, subprocesses, clocks, randomness, and host authority. | [concurrency.md](concurrency.md), [absence_and_result.md](absence_and_result.md), [data_and_types.md](data_and_types.md), [../research/security_and_trust_deep_dive.md](../research/security_and_trust_deep_dive.md) | `trust_effects_and_capabilities.md` |
| 2 | Time, Scheduling, And Lifecycle | Timeouts, cancellation, clocks, retries, resources, async, tests, and determinism cut through control flow and reliability. | [concurrency.md](concurrency.md), [absence_and_result.md](absence_and_result.md), [../research/error_handling_defer_resource_cleanup_notes.md](../research/error_handling_defer_resource_cleanup_notes.md), [../research/standard_library_design_comparative.md](../research/standard_library_design_comparative.md) | `time_and_lifecycle.md` |
| 3 | Names, Scope, Modules, And Identity | Every binding, import, export, package, capability, type, field, and diagnostic depends on stable name identity. | [scope_context.md](scope_context.md), [modules_imports.md](modules_imports.md), [data_and_types.md](data_and_types.md), [../research/packaging_and_project_structure_deep_dive.md](../research/packaging_and_project_structure_deep_dive.md) | `names_scope_and_identity.md` |
| 4 | Explanation, Observability, And Examples | Diagnostics, traces, examples, logs, notebooks, LSP, AI-readable semantics, and `explain` should share one event vocabulary. | [meta_testing.md](meta_testing.md), [interaction_map.md](interaction_map.md), [../research/diagnostics_and_explanations_comparative.md](../research/diagnostics_and_explanations_comparative.md), [../research/ai_readable_semantics_deep_dive.md](../research/ai_readable_semantics_deep_dive.md) | Expand `meta_testing.md` or create `explanation_observability.md` |
| 5 | Data Exchange, Formats, And Boundaries | JSON, CSV, config, CLI/env, databases, schemas, serialization, provenance, and redaction need one boundary story. | [data_and_types.md](data_and_types.md), [strings.md](strings.md), [../research/data_boundary_systems_deep_dive.md](../research/data_boundary_systems_deep_dive.md) | Expand `data_and_types.md` into a boundary packet |
| 6 | Numbers, Quantities, And Shape | Money, decimal, units, dates, array/rank, table columns, numeric precision, and display formatting shape daily correctness. | [flow_and_collections.md](flow_and_collections.md), [strings.md](strings.md), [../research/array_languages_deep_dive.md](../research/array_languages_deep_dive.md), [../research/scientific_languages_r_matlab_julia.md](../research/scientific_languages_r_matlab_julia.md) | `numbers_quantities_and_shape.md` |
| 7 | Evolution, Style, And Toolability | Formatting, editions, migration, package stability, semantic tokens, generated artifacts, and AI-readability decide whether the language can grow. | [../language/spec_readiness_map.md](../language/spec_readiness_map.md), [../orientation/ai_collaboration.md](../orientation/ai_collaboration.md), [../research/formatting_and_style_deep_dive.md](../research/formatting_and_style_deep_dive.md), [../research/package_docs_and_examples_deep_dive.md](../research/package_docs_and_examples_deep_dive.md) | `evolution_style_and_toolability.md` |

The first four are the highest leverage. They govern safety, control,
identity, and understanding: the places where inconsistency becomes expensive
fast.

## Pillar 1: Trust, Effects, And Capabilities

### Design Pressure

Most real programs touch the world: files, network, environment variables,
databases, secrets, subprocesses, randomness, clocks, package downloads, and
foreign APIs. If Nomi treats these as ordinary strings and functions, safety
will depend on convention. If it makes every effect a heavyweight type-system
problem, ordinary scripts become scholastic.

Nomi needs a humane middle layer: effects are explicit at boundaries, authority
is represented as values/capabilities, and block policies describe scoped use.

### Normal-Form Ownership

| Concern | Owner | Reduction target |
|---------|-------|------------------|
| Files, network, env, subprocesses | Block + Data boundary | capability value enters a scoped block or typed sink |
| Secrets, PII, credentials | Data boundary + Explanation | wrapped values with redacted display and explicit reveal |
| Expected failure from external world | Absence/result | `Result`, not sentinel values or swallowed exceptions |
| Resource cleanup | Block | caller code attached to policy; `yield` controls lifetime |
| Permissions and host authority | Data boundary + Explanation | manifest/capability table plus traceable denial diagnostics |

### Cross-Language Evidence

- Rust, Zig, Go, and Swift show the value of explicit resource and error
  boundaries.
- Nix, Deno, and capability systems show that authority should be visible,
  not ambient.
- Perl/Ruby taint systems show that whole-ecosystem taint tracking is too
  costly unless every library participates.
- Web frameworks and SQL APIs show that typed sinks beat stringly conventions.

### Nomi Direction

Prefer capability values and typed sinks over ambient authority:

```nomi
with_capability(FileRead("./data")) -> files:
    rows = files.open("users.csv")
        |> Csv.decode(User)
        |> collect_results
```

Design-needed:

- capability value shape and import/export policy;
- host capability manifests for Python, browser, Node, and future Wasm/WASI;
- typed sinks for SQL, HTML, URL, shell/process, logs, and secrets;
- redaction and `explain --unsafe` rules;
- how effects appear in examples, tests, and traces.

Rejected-for-now:

- full information-flow control as the everyday layer;
- ambient string permissions as the only authority model;
- shell-language strings as the default process API.

## Pillar 2: Time, Scheduling, And Lifecycle

### Design Pressure

Time is everywhere and notoriously easy to get wrong: durations vs instants,
wall clocks vs monotonic clocks, time zones, cancellation, retries, deadlines,
test determinism, cleanup ordering, and async lifecycle. These concerns touch
block calls, flow, result, explanation, and standard-library design.

### Normal-Form Ownership

| Concern | Owner | Reduction target |
|---------|-------|------------------|
| Deadlines and timeouts | Block + Absence/result | policy block returns value or timeout `Result` |
| Cancellation | Block + Flow | structured cancellation scope, not hidden global state |
| Clocks | Data boundary + Explanation | explicit clock capability; traces show time source |
| Retry/backoff | Block | caller code attached to retry policy |
| Time parsing/formatting | Data boundary + String pillar | typed `Instant`, `LocalDate`, `Duration`; explicit parse result |

### Cross-Language Evidence

- Go's `context` shows cancellation must be pervasive, but manual context
  threading can infect APIs.
- Kotlin and Swift structured concurrency show lifetimes should be scoped.
- Java/.NET date-time histories show that early ambiguous APIs live for
  decades.
- Rust separates `Instant`, `Duration`, and system time; this is a useful
  model for avoiding wall-clock confusion.

### Nomi Direction

Time should start library-first but policy-shaped:

```nomi
within(2.seconds) -> deadline:
    response = fetch(url, deadline)
    return response.decode(Json)
```

Design-needed:

- `Duration`, `Instant`, `LocalDate`, `DateTime`, and `TimeZone` boundaries;
- monotonic vs wall-clock API split;
- cancellation event vocabulary;
- deterministic test clocks for examples/checks;
- how timeout, cancellation, cleanup failure, and body failure compose.

Rejected-for-now:

- one universal `DateTime` type;
- implicit global clock in tests;
- unstructured cancellation tokens threaded through every ordinary function.

## Pillar 3: Names, Scope, Modules, And Identity

### Design Pressure

Names are how users orient themselves. Nomi already has a strong binding story,
but name identity cuts wider: local bindings, parameters, pattern captures,
fields, data variants, imports, aliases, package names, capability names,
extension methods, generated symbols, and diagnostics.

If this pillar is underspecified, every later feature invents its own lookup
rules.

### Normal-Form Ownership

| Concern | Owner | Reduction target |
|---------|-------|------------------|
| Local variables and parameters | Binding | tentative bind, constraint check, commit |
| Pattern captures | Pattern + Binding | match then scoped binding |
| Imports and exports | Binding + Data boundary | external module decoded into visible names |
| Package identity | Data boundary + Explanation | domain path, version, hash, provenance |
| Extension methods/operators | Function + Binding | imported function/protocol visible at use site |

### Cross-Language Evidence

- Go and Deno make import paths explicit and domain-shaped.
- Rust and Swift show that extension/protocol visibility needs disciplined
  import rules.
- Python shows the power and cost of import-time execution and dynamic module
  state.
- Nix/Dhall show content-addressed identity for reproducible external inputs.

### Nomi Direction

Make imports ordinary binding events with provenance:

```nomi
import "example.com/acme/users" as users
import "example.com/schemas/user.nomi" sha256:abc123...
```

Design-needed:

- exact module identity: file path, domain path, package name, version, hash;
- import-time side-effect policy;
- extension method visibility and conflict diagnostics;
- generated-name rules for desugar and macro-like futures;
- `explain import` view showing source, version, hash, exports, and aliases.

Rejected-for-now:

- implicit global package namespace;
- wildcard imports as the default teaching path;
- dynamic import side effects as an ordinary configuration mechanism.

## Pillar 4: Explanation, Observability, And Examples

### Design Pressure

Every feature has two user experiences: writing it and understanding it when it
fails. Nomi's ambition depends on making the second one excellent. Diagnostics,
examples, traces, logs, notebooks, query plans, expansion views, and AI-readable
semantics should share one event vocabulary.

### Normal-Form Ownership

| Concern | Owner | Reduction target |
|---------|-------|------------------|
| Diagnostics | Explanation | structured event with source spans and suggested fixes |
| Examples/checks | Explanation + Block | executable examples scoped to the code they explain |
| Logging/tracing | Explanation + Data boundary | structured events with redaction and provenance |
| Query/flow plans | Flow + Explanation | inspectable intermediate stages |
| Desugar/macro-like futures | Explanation | expansion events preserving source spans |

### Cross-Language Evidence

- Rust and Elm show that diagnostics are architecture, not prose polish.
- Racket and Smalltalk show the value of interactive explanation surfaces.
- Jupyter/Pluto/Observable show that execution history and examples shape the
  language experience, not just tooling.
- LSP, Tree-sitter, typed ASTs, and AI-readable traces show why machine-readable
  semantics matter.

### Nomi Direction

Explanation should be the shared rendering layer for diagnostics, examples,
logs, traces, and expansion views:

```nomi
explain:
    rows
    |> where(_.active)
    |> select(User.decode)
    |> collect_results
```

Design-needed:

- canonical event schema;
- redaction and unsafe reveal rules;
- relation between examples, tests, notebooks, and docs;
- query/flow plan explanation;
- expansion display for sugar, typed strings, and future scoped extensions.

Rejected-for-now:

- string logs as the only observability surface;
- stack traces as the primary user diagnostic;
- macro or DSL features that cannot explain their expansion.

## Pillar 5: Data Exchange, Formats, And Boundaries

### Design Pressure

Nomi's `Data.decode()` story is already strong, but the vertical pillar is
wider than `data` declarations: JSON, CSV, TOML, YAML, HTML forms, CLI args,
environment variables, databases, schemas, config merge, generated clients,
schema export, provenance, redaction, and partial/lax decoding.

### Nomi Direction

Treat external formats as parse layers feeding the same decode boundary:

```nomi
config =
    Config.decode(Toml.parse(file.read()))
    |> require_ok
```

Design-needed:

- parse vs decode separation;
- source provenance for every decoded field;
- strict/lax coercion policy;
- config merge semantics;
- schema export as tooling, not core syntax;
- typed string wrappers integrating with decode.

## Pillar 6: Numbers, Quantities, And Shape

### Design Pressure

Numbers look primitive until programs handle money, measurement, precision,
statistics, arrays, tables, units, dates, byte sizes, percentages, and display.
This pillar deserves early design attention because numeric mistakes are quiet.

### Nomi Direction

Start with boring numeric clarity, then add domain power through typed values
and explicit shape/rank functions:

```nomi
price: Money["USD"] = Money.usd("12.99")
timeout: Duration = 2.seconds
area = width.meters * height.meters
```

Design-needed:

- integer/float/decimal/money boundaries;
- units and quantities as library-first typed wrappers;
- array shape/rank vocabulary;
- display and formatting protocol interaction;
- parse failures as `Result`, not silent coercion.

Rejected-for-now:

- dense array glyphs as ordinary syntax;
- implicit unit conversion across domains;
- using binary float for money examples.

## Pillar 7: Evolution, Style, And Toolability

### Design Pressure

A language is not just syntax. It is formatting, migration, package stability,
editions, deprecation, generated artifacts, LSP, semantic tokens, examples,
documentation, and AI/tool readability. If these are afterthoughts, early
design wins become hard to keep.

### Nomi Direction

Treat evolution as a designed surface:

- `nomi fmt` as a stabilizing force;
- editions/migration before 1.0 hardening;
- feature status labels in docs and manifests;
- generated artifacts with freshness checks;
- semantic events consumable by LSP, notebooks, and AI tools;
- packages incubating outside the core before promotion.

Design-needed:

- edition policy;
- migration tooling expectations;
- package incubation tiers;
- canonical formatting choices;
- semantic token taxonomy;
- doc/example/test integration.

## Recommended Next Passes

Do not try to fully specify every pillar at once. The highest-value sequence is:

1. **Trust, Effects, And Capabilities** — because it constrains strings, IO,
   security, resource handling, web/runtime, and package execution.
2. **Time, Scheduling, And Lifecycle** — because it clarifies concurrency,
   retries, cancellation, test determinism, and cleanup.
3. **Names, Scope, Modules, And Identity** — because it will decide imports,
   extension methods, packages, capabilities, and generated names.
4. **Explanation, Observability, And Examples** — because every other pillar
   should emit events and diagnostics through the same surface.

Each pillar should eventually get a string-style packet:

```text
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

- [Strings](strings.md) — model for a cross-cutting pillar that reduces to
  existing normal forms instead of becoming a new primitive by default.
- [Interaction Map](interaction_map.md) — global/local feature interactions
  and one-way synthesis choices.
- [Syntax Design Rules](syntax_design_rules.md) — primitive budget and axis
  coherence rules.
- [Cross-Language Synthesis Master](../research/cross_language_synthesis_master.md) —
  capstone normal-form synthesis and risk that the normal-form count may be
  wrong.
- [Language Family Coverage Map](../research/language_family_coverage_map.md) —
  research corpus index and under-covered dimensions.
