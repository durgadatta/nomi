# Cross-Language Design Convergences

> Status: consolidated research synthesis.
>
> These findings survived comparison across language families, boundary
> systems, tooling, pedagogy, security, and deployment. Each section separates
> broad convergence from the design fork Nomi still had to choose.

The [feature comparisons](features/README.md) deepen these findings along one
axis; the [language reviews](languages/README.md) expose each language's costs
and the [active synthesis](../design/synthesis.md) tests their combined shape.

The [data/workflow evidence](data_workflows/README.md) and
[notation atlas](notation_atlas.md) add a cross-disciplinary convergence:
useful notation makes relationships local by omitting recoverable context.
Its unresolved fork is how much context should be explicit in source versus an
inspectable model/view. Similar chains/arrows can denote calculation, query,
training, dependency, replay, constraint or argument; visual resemblance alone
never establishes interchangeable laws. This is synthesis, not syntax admission.

## 1. Low Floor And High Ceiling Are Different Problems

**Convergence:** successful first experiences produce a visible result with no
project ceremony. Successful large systems expose interfaces, effects,
failures, dependencies, and stable tools.

**Fork:** some languages impose declarations from line one; others never make
contracts firm.

**Nomi choice:** inferred script locals and direct top-level execution, then
complete checked public contracts, locally inferred or declared. Exploration
retains unknowns; selected boundary obligations require evidence. The language
grows by adding information at boundaries, not by replacing beginner syntax.

## 2. Local Reasoning Requires Visible Change

**Convergence:** mutation, non-local control, implicit context, and hidden
dispatch are the main reasons a reader must search far from a line.

**Fork:** dynamic languages optimize for writable flexibility; pure languages
for immutability; systems languages often expose ownership.

**Nomi choice:** immutable bindings and data by default, `var`/`set` for local
mutation, explicit effects and suspension, no invisible extension imports, and
GC rather than ownership syntax in the general profile.

## 3. Algebraic Data And Pattern Matching Are The Stable Domain Core

**Convergence:** Rust enums, Swift enums, ML variants, Kotlin sealed classes,
TypeScript discriminated unions, and similar systems represent closed
alternatives with tagged data and exhaustive elimination.

**Fork:** structural versus nominal identity; open extension versus closed
exhaustiveness.

**Nomi choice:** nominal, closed `data` for owned concepts; explicit structural
patterns and decoders for received values. `match` is the sole multi-way
structural choice. The focused evidence, including capture transactionality,
coverage, guards, and extractor tradeoffs, is in
[Pattern Matching Research](pattern_matching.md).

## 4. Types And Runtime Constraints Solve Different Problems

**Convergence:** static types catch compositional mistakes; runtime validation
is still required for user input, files, networks, databases, configuration,
and host interop.

**Fork:** erased structural types, retained dynamic contracts, or fully static
nominal systems.

**Nomi choice:** progressive static typing plus retained constraints. Static
proof may remove a check, but decode and diagnostic semantics do not depend on
one compiler's inference power.

## 5. Parse, Do Not Merely Validate

**Convergence:** the strongest boundary systems return a trusted typed value or
structured errors. They do not return `true` while leaving an untrusted map in
place.

Common invariants:

- schema intent lives with the owned type;
- parse and decode can be separated;
- crossing is visible and typed;
- coercion is explicit;
- nested decoders compose;
- errors carry paths and accumulate;
- construction is atomic;
- defaults and source provenance are explainable.

**Nomi choice:** `Value -> T.decode -> Result[T, DecodeErrors]`, strict and
closed by default. Configuration uses the same language and boundary model.

## 6. Absence, Expected Failure, And Broken Invariants Must Stay Distinct

**Convergence:** modern languages repeatedly rediscover three stories:

```text
Option       value may be absent
Result       operation may fail normally
panic/crash  program or runtime invariant failed
```

Collapsing them into null or exceptions weakens APIs and diagnostics.

**Fork:** exceptions versus result values; fail-fast versus accumulation;
implicit versus explicit propagation.

**Nomi choice:** `Option`, typed `Result`, and panic are separate. `?.`/`??`
belong only to absence. `?` propagates `Option` or `Result` from the nearest
function. Decode accumulates independent errors; sequential `?` fails fast.

## 7. Resource Cleanup Is Lexical; Retry Is Not Resource Scope

**Convergence:** RAII, `with`, try-with-resources, bracket, and `defer` all make
cleanup deterministic around lexical use.

**Fork:** type-owned destructors, general context managers, or defer actions;
whether a block may execute several times.

**Nomi choice:** exactly-once `with` and unconditional lexical `defer`.
Multi-invocation policies such as retry receive explicit functions. This avoids
hiding execution multiplicity behind a pleasant block shape.

## 8. Structured Concurrency Is More Fundamental Than Async Spelling

**Convergence:** async systems need visible suspension, cancellation,
backpressure, child lifetime, cleanup, and multi-error behavior. Merely turning
callbacks into blocks does not solve these.

**Fork:** colored async functions, effect-based suspension, actors, green
threads, or runtime-transparent blocking.

**Nomi choice:** explicit `async func`/`await` with structured task groups.
Actors, channels, supervisors, and parallel collections are libraries/runtime
profiles. The design accepts function color because hidden suspension is a
larger cognitive cost.

## 9. Collection Syntax Must Not Lie About Evaluation

**Convergence:** most ecosystems need mapping, filtering, grouping, folding,
sorting, streaming, and materialization. Tables and query systems additionally
need schema, planning, and explanation.

**Fork:** eager versus lazy by default, methods versus free functions, query
syntax versus ordinary calls, and implicit versus explicit parallelism.

**Nomi choice:** strict collections by default, explicit `Stream`, one common
verb family, and `|>` as call insertion only. Tables may share verbs but expose
plan values. No query syntax until library programs prove it necessary.

## 10. Syntax Coherence Is Stronger Than Desugarability

**Convergence:** languages accumulate cruft when every attractive shorthand is
accepted because it can lower to an existing construct.

**Fork:** maximize local brevity or minimize the number of recognition paths.

**Nomi choice:** one canonical spelling per common act, plus only a few
high-value reductions. `_`, `where`, arrows, `?`, `with`, and `|>` each have a
narrow visual job. The target rejects implemented conveniences when they make
the whole language harder to remember.

## 11. Effects And Authority Need Two Layers

**Convergence:** explicit dependencies aid review; capabilities and sandboxes
control actual authority. Either one without the other is incomplete.

**Fork:** pass every capability as an argument, infer effects, use global
permissions, or rely on process isolation.

**Nomi choice:** public `uses` effect sets plus runtime capability handles.
Hosts grant permissions, runtimes mint authority, and handles delegate narrower
rights. Tests replace capabilities without patching global state.

## 12. Diagnostics Are A Semantic Artifact

**Convergence:** the best beginner, compiler, decoder, and operations errors
say what happened, where, why, and what to try. That requires source spans,
typed expectations, causes, and domain context before rendering.

**Fork:** prose-only errors, compiler-internal dumps, or structured records.

**Nomi choice:** stable diagnostic/event data shared by CLI, editor, notebook,
browser, CI, and agents. Explanation is a tooling view over semantics, not a
new execution model.

## 13. One Test Form Cannot Cover Every Risk

**Convergence:** executable examples improve documentation and first use;
property, fuzz, integration, conformance, and benchmark tests cover different
failure classes.

**Fork:** inline examples as the entire testing language or separate framework
conventions.

**Nomi choice:** `example` and `check` are first-class, but ordinary test
modules and specialized test libraries remain necessary. Shared structured
results unify tooling without pretending all tests are examples.

## 14. A Lean Prelude Needs A Strong Package Story

**Convergence:** all languages need text, collections, files, time, errors,
testing, and concurrency. Broad standard libraries improve early reach but
become compatibility burdens. Modern ecosystems use incubation packages.

**Fork:** batteries included, minimal stdlib, or configurable preludes.

**Nomi choice:** small prelude, explicit domain imports, protocol-based APIs,
and an excellent secure package manager. Stable stdlib promotion follows real
package maturity.

## 15. Industrial Trust Starts Before Version 1

**Convergence:** content hashes, lockfiles, deterministic builds, immutable
publication, signatures, sandboxes, and least authority repeatedly underpin
trustworthy ecosystems.

**Fork:** central registries versus federated names; version ranges versus
minimal/explicit upgrades; install scripts versus pure fetch.

**Nomi choice:** organization/domain-scoped identity, exact lockfiles, pure
fetch, no dependency code execution during install, sandboxed builds, and
content-addressed artifacts. Compatibility can wait; supply-chain hygiene
cannot.

## 16. Advanced Notation Must Be Scoped

**Convergence:** macros, symbolic expressions, SQL, parsers, templates, and
array notation can be extraordinarily productive inside their domain and
destructive when they silently alter ordinary code.

**Fork:** make the whole language homoiconic/extensible or use explicit domain
boundaries.

**Nomi choice:** ordinary functions and values first. A future notation layer
must be lexically entered, typed at its boundary, hygienic, source-mapped,
effect-controlled, formatter-aware, and inspectable after expansion.

## 17. Tooling Is Part Of Language Semantics In Practice

**Convergence:** formatting, navigation, diagnostics, package resolution,
documentation, execution, and migration determine whether a language remains
understandable at scale.

**Fork:** specification-first with external tools or an integrated toolchain.

**Nomi choice:** one toolchain and versioned artifacts, with replaceable
implementations behind shared contracts. Parser acceptance alone is never
feature completion.

## 18. Research Should Now Be Program-Driven

The [human-interaction edge extension](interfaces/edge_cases.md) follows this
rule through shared invoice/import/cancellation programs and
[composition experiments](interfaces/composition_cases.md). It adds original
counterexamples where reset counters, converged merges, plausible sensor values,
or identical displays conceal changed context. The
[philosophical translation](cognition.md) asks which facts justify a claim;
[local probes](interfaces/experiments.md) distinguish finite-model evidence from
language conformance and usability. Breadth reveals pressures, while a bounded
comparison must earn any change to the target.

The corpus is broad enough to start bounded comparisons. New mechanisms and
disciplines can still reveal pressures it does not contain. The
[maintainer synthesis guide](synthesis_guide.md) deepens selected languages and
routes those discoveries into shared feature owners. The next unit of evidence
for a mature language choice is:

```text
a target program
an alternative surface
a formatter rendering
a failure transcript
a lowering/explain view
a user or implementation experiment
```

Broad discovery remains useful when it exposes a new pressure or genuine
alternative. Before admitting a feature, connect it to an explicit contract,
whole program, and discriminator; additional language names alone are insufficient.
