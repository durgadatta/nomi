# Language Family Findings

> Status: consolidated research evidence by language family.
>
> This document records transferable mechanisms and failure modes. It does not
> treat language popularity or familiarity as proof that a surface belongs in
> Nomi.

For source-backed critical detail, use the [language index](languages/README.md)
and [feature index](features/README.md). This page retains the compact family
view; recommendations are Nomi judgments, not rankings of the source languages.

## Everyday Dynamic Languages

### Python

**Keep:** indentation, low-ceremony scripts, direct calls, named arguments,
readable collection literals, a strong REPL/notebook story, rich libraries,
and an idiom-first teaching path.

**Repair:** nullable-by-convention values, exception collapse, implicit
truthiness, mutable records, weak boundary validation, runtime-only public
contracts, packaging fragmentation, and implementation details leaking through
errors.

**Do not inherit:** statement/expression accidents, magic methods as the
primary semantic protocol, broad ambient authority, or compatibility with
every historical corner.

Nomi's relationship to Python is cognitive, not syntactic compatibility.

### Ruby And Smalltalk

**Keep:** humane APIs, message-oriented readability, blocks that make library
control pleasant, and an emphasis on programmer joy.

**Repair:** implicit block invocation count, non-local return surprises,
open-class action at a distance, and runtime-only interface discovery.

The transferable lesson is to design fluent libraries. It is not to turn every
control construct into a trailing block.

### JavaScript And TypeScript

**Keep:** excellent interactive reach, structural handling of external data,
async ecosystem lessons, discriminated unions, safe `Unknown`, and strong
editor feedback.

**Repair:** coercion, two null values, structural typing as the default for
durable domain concepts, erased runtime contracts, ecosystem supply-chain
risk, and callback/Promise/async historical layering.

Nomi uses nominal owned data with explicit structural boundaries. It adopts
`Unknown`-style caution, not TypeScript's fully structural center.

### Shells, Tcl, PowerShell, And Interface Languages

**Keep:** direct composition of real tools, visible data flow, command values,
interactive feedback, and easy environment access when intentionally granted.

**Repair:** text as the only interchange type, quoting traps, ambient process
authority, error-code conventions, and invisible platform dependence.

Commands should be structured values with explicit execution, argument,
environment, capability, and result contracts. Nomi should not recreate a
shell parser inside ordinary source.

## Functional And Algebraic Languages

### ML, OCaml, F#, Elm, And Gleam

**Keep:** nominal algebraic data, exhaustive pattern matching, local type
inference, expression-oriented value choice, typed expected failure, and small
semantic cores.

**Repair for Nomi's audience:** punctuation density, currying assumptions,
specialized module/type-system vocabulary, and tutorial paths that foreground
types before concrete tasks.

This family supplies Nomi's strongest semantic center. Nomi translates it into
Python-like visual calm, explicit calls, and a progressive type surface.

### Haskell

**Keep:** separation of pure values from effects, compositional abstractions,
algebraic modeling, principled resource brackets, and a deep library culture.

**Do not copy directly:** lazy-by-default evaluation, automatic currying,
typeclass and monad vocabulary as first-hour requirements, `do` notation, or a
broad historical prelude.

Haskell often reveals the underlying algebra. Nomi then looks for a direct,
eager, locally explainable surface.

### Lisp, Scheme, Racket, And Clojure

**Keep:** program-as-data insight, lexical simplicity, REPL-driven development,
hygiene lessons, language-oriented design, Racket's pedagogy, and explicit
transformation boundaries.

**Defer:** unrestricted macros and arbitrary compile-time evaluation. Prefix
uniformity is elegant for transformation but is not Nomi's intended everyday
reading order.

Future Nomi metaprogramming should be scoped, typed, hygienic, source-mapped,
and sandboxed. Ordinary modules should remain readable without expansion
knowledge.

## Mainstream Typed Languages

### Rust

**Keep:** `Result`/`Option`/panic separation, postfix propagation, exhaustive
enums, explicit mutation, strong diagnostics, editions, Cargo-like workflow,
and a culture of executable documentation.

**Do not import:** ownership and lifetime syntax into the general profile,
trait complexity before protocols are proven, procedural macro authority, or
performance-driven ceremony for ordinary scripts.

Rust demonstrates that explicitness can remain ergonomic when tooling and
diagnostics are designed with the language.

### Swift And Kotlin

**Keep:** approachable static typing, safe optional access, expressive enums,
good collection APIs, named arguments, structured async work, and readable
modern APIs.

**Repair:** multiple overlapping closure conventions, implicit receiver scopes,
context/extension lookup complexity, exception/Result overlap, and build-system
weight.

Nomi keeps their friendly surface instincts while making extensions, effects,
and error carriers more explicit.

### Go And Zig

**Keep:** small language discipline, explicit dependencies, fast tools,
straightforward deployment, `defer`, reproducible modules, and visible system
boundaries.

**Repair:** repetitive error handling, nil, limited algebraic modeling, and in
Zig's case allocator/compile-time machinery that serves a lower-level target.

Go's restraint is a useful warning against convenience accumulation. Nomi adds
typed variants and `Result` while preserving tooling directness.

### Java, C#, And Dart

**Keep:** package-scale interfaces, mature tooling, async and pattern evolution,
sealed types, deployment experience, and long-lived ecosystem lessons.

**Avoid:** class-first ceremony, nullable legacy, annotation/decorator forests,
deep namespace histories, and framework configuration as a substitute for
language coherence.

Nomi needs their industrial contracts without making classes or inheritance
the universal model.

## Concurrent And Distributed Languages

### Erlang, Elixir, And The BEAM

**Keep:** supervision, isolated processes, message protocols, failure as an
operational reality, structured observability, and deployment/upgrade lessons.

**Translate:** actor semantics are a library/runtime profile, not a reason to
make every value or function concurrent. Pattern matching and tagged outcomes
transfer directly; "let it crash" still requires isolation boundaries.

### Async Runtimes Across Languages

The corpus does not support the claim that one generalized block/yield form
eliminates concurrency's hard problems. Cancellation, task lifetime,
backpressure, executor affinity, multiple failures, and resource cleanup remain
semantic obligations.

Nomi therefore accepts the familiar cost of explicit `async func` and `await`,
then removes the more dangerous cost: unstructured child lifetime.

## Data, Query, And Scientific Languages

### SQL, LINQ, Dataframes, And Table Systems

**Keep:** declarative operations, named columns, lazy plans, explainability,
schema-aware diagnostics, and optimizer-visible intent.

**Do not collapse:** a list, stream, table, and distributed query plan have
different evaluation and failure behavior. Shared verbs are useful; pretending
they are the same runtime value is not.

Nomi begins with protocol-based `map`/`filter`/`group_by` and visible plan
values. Query syntax must earn admission through real table programs.

### R, MATLAB, Julia, APL, J, BQN, And Uiua

**Keep:** whole-data thinking, broadcasting, shape/rank awareness, multiple
dispatch pressure, interactive numerical work, concise transformations, and
visual feedback in notebooks.

**Fence:** dense glyphs, implicit rank, recycling, vectorization surprises,
and dispatch that is difficult to explain locally.

Fast scientific code does not require symbolic everyday syntax. Typed array
and shape protocols should prove the semantics first; scoped notation may come
later.

### Mathematica And Symbolic Systems

**Keep:** expressions as inspectable values, assumptions, rewriting,
provenance, and interactive explanation.

**Fence:** pervasive symbolic evaluation, global rewrite rules, context-
sensitive names, and evaluation control that ordinary readers cannot see.

Symbolic work belongs behind an explicit quotation/staging boundary that
returns typed expression values.

## Data Boundary Systems

Pydantic, zod, serde, Elm decoders, CUE, Nickel, Pkl, Dhall, JSON Schema, and
Terraform converge on strong boundary needs even while choosing different
engines.

Nomi adopts:

- the `data` declaration as the source of owned type and schema intent;
- explicit parse/decode stages;
- `Result` output rather than boolean validation;
- strict, closed defaults and explicit coercion;
- composable decoders;
- accumulated, path-addressed errors;
- defaults and provenance that remain explainable.

Nomi refuses a separate schema language and defers unification/solver
semantics. Validation checks concrete values; it does not search for values
that satisfy a constraint system.

## Teaching And Human-Computer Interaction

Python, Racket teaching languages, Logo, BASIC, Scratch, Elm, the Go Tour,
Khan Academy, and Swift Playgrounds repeatedly show:

- visible output must arrive immediately;
- learners need to explain each token they just used;
- abstraction should follow experienced repetition;
- errors are part of teaching;
- tutorial, editor, execution, and output should share a surface;
- working programs should be easy to modify rather than rebuilt from blank
  pages.

Nomi keeps the full language available but designs a narrow first-hour path and
diagnostics that use the vocabulary introduced so far. It does not require a
separate beginner language.

## Systems, Security, And Deployment

Nix, Go modules, Cargo, Deno, Wasm, capability systems, Sigstore, containers,
and reproducible-build work converge on content identity, explicit authority,
sandboxing, immutable publication, and deterministic artifacts.

Nomi treats package/build/security design as part of the language product from
the beginning. Friendly syntax cannot compensate for an ecosystem that runs
install scripts, leaks secrets, silently upgrades dependencies, or builds a
different artifact in production.
