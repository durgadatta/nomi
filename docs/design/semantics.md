# Nomi Semantics

> Status: canonical target semantics.
>
> This document specifies the behavioral commitments behind
> [Nomi syntax](syntax.md). It intentionally avoids inheriting behavior from
> Python AST, JavaScript, WebAssembly, or any current runtime backend.

## Semantic Priorities

When two plausible behaviors conflict, Nomi prefers this order:

1. preserve local reasoning;
2. reject invalid states before they spread;
3. make control, failure, effects, and time visible;
4. produce a structured explanation;
5. preserve deterministic behavior across backends;
6. optimize only after the contract is clear.

## Evaluation

Nomi is eagerly evaluated. Expressions are evaluated left to right unless an
operator's documented short-circuit behavior says otherwise. Function
arguments are evaluated once before parameter binding. Named argument order
does not change evaluation order.

The language has lexical scope and garbage-collected memory. Values do not
expose object addresses as semantic identity. Identity-sensitive resources are
represented by explicit handles.

`and`, `or`, `if`, `?.`, `??`, `match`, and postfix `?` short-circuit. No
other ordinary operator skips evaluation.

## Values And Types

Every value has a runtime type. Static analysis may prove operations and erase
redundant checks, but runtime type identity, constraints, diagnostics, decode,
and safe interop remain well-defined without static proofs.

Nomi uses progressive static typing:

- local bindings are inferred where the answer is direct;
- annotations may make local intent explicit;
- public package declarations require complete parameter and result types;
- `Any` is an explicit unchecked escape, never an inference fallback;
- `Unknown` is a safe top type that must be decoded or pattern-narrowed;
- generic parameters are explicit on public declarations but may be inferred
  at calls;
- public inference does not depend on whole-program analysis.

Nominal `data` types are the default for program concepts. Structural types are
limited to external values, protocols, and explicit patterns. The initial
language uses named variant data rather than untagged unions for alternatives.

## Binding

A binding operation has four phases:

```text
evaluate source once
-> tentatively bind names
-> check type and constraints
-> commit all names or commit none
```

Destructuring is atomic and its pattern must be statically irrefutable for the
source type. If a constraint fails, or unchecked foreign corruption violates
the proven structural shape, no capture becomes visible. Refutable
decomposition belongs in exhaustive `match`.

An immutable name cannot be rebound in the same lexical scope. Shadowing in a
nested scope is allowed but receives a lint when it obscures a public or long-
lived binding. A `var` binding retains its declared type and constraints on
every `set`.

Closures capture immutable bindings by value semantics. Capturing a mutable
binding creates an explicit mutable cell; tooling marks that capture because it
changes temporal reasoning.

## Constraints

A constraint is an executable predicate attached to a binding or data
declaration. It is not a second type language.

Constraint evaluation:

- happens after structural/type matching and before commit;
- must be deterministic and side-effect free;
- may refer to earlier fields and declaration-level peers;
- preserves its source expression and optional note;
- produces `ConstraintDiagnostic` data on failure;
- may be statically discharged when the compiler can prove it.

Direct construction, internal binding, and function precondition failures are
contract violations: they indicate invalid program logic and stop ordinary
evaluation. External input should cross `decode`, where the same constraint
failures become expected, accumulated `DecodeErrors`.

This distinction prevents routine user input from becoming a panic while still
making impossible internal states fail loudly.

## Functions And Calls

A function value contains:

- parameter bindings and defaults;
- a body;
- a result type;
- an effect set;
- async/sync calling convention;
- source and documentation metadata.

A call:

```text
evaluate callee and arguments
-> map positional and named arguments
-> bind and check parameters atomically
-> verify required effects are available
-> evaluate body
-> check result
-> return value
```

Arity and argument-name failures happen before the body. Defaults are evaluated
in declaration order at call time and may refer only to earlier parameters and
module constants.

`return` exits the nearest lexical `func`. It is never redirected by lowering,
resource scopes, match blocks, examples, or async state machines.

Anonymous functions use the same parameter and result model. They may omit a
result annotation when it can be locally inferred. There is no automatic
currying or implicit partial application.

## Data

Product `data` defines an immutable nominal value with ordered field metadata,
structural equality, stable hashing when every field is hashable, redaction-
aware display, and generated pattern/decoder descriptions.

Variant `data` defines a closed nominal type with a finite set of qualified
cases. Exhaustiveness analysis applies when the matched type is closed and all
variants are known in the current edition.

Constructors:

- never perform transport-format parsing;
- never silently coerce field types;
- apply defaults visibly in construction metadata;
- check all field and declaration constraints;
- produce a valid immutable value or fail atomically.

Generated behavior is ordinary protocol conformance, inspectable through
tooling. User-defined behavior cannot silently replace equality, display,
encoding, or decode rules without an explicit protocol implementation.

## Patterns And Choice

A pattern attempt has four ordered stages:

```text
test the already-evaluated subject structurally
-> accumulate tentative captures without mutating scope
-> evaluate one optional pure Bool guard
-> commit captures to a fresh arm scope or discard all of them
```

Structural non-match and guard rejection select the next arm. Constraints are
not patterns: `where` defines valid bindings and data, while decode reports
external validity failures. A guard only refines whether a structurally valid
arm applies.

Patterns never mutate the value they inspect. Captures are immutable and scoped
to their branch. Alternative patterns must bind the same names with compatible
types. Structural matching is pure, non-consuming, and limited to compiler-known
nominal values and strict structural values; it never invokes a user extractor
or iteration protocol.

`if` accepts only `Bool`. `match` chooses the first successful pattern in
source order, and every match is exhaustive. Guards are deterministic,
effect-free, evaluated once, and ignored as proof of coverage. Typed usefulness
analysis rejects wholly unreachable arms and reports witness patterns for
missing space. A value-producing match also unifies all reachable arm result
types.

The focused [Pattern Matching](pattern_matching.md) design specifies the
accepted pattern category, collection openness, transactional attempt model,
coverage, diagnostics, and Surface/Core contract.

## Collections, Streams, And Tables

Strict collections own their elements and execute operations eagerly. A
`Stream[T]` is an explicit one-pass or replayable lazy source whose capability
is visible in its type. Converting between them uses `stream` and `collect`.

Collection operations use protocol-based iteration and preserve order unless
their contract says otherwise. Hash-based collection iteration has a stable
language-defined order or is explicitly unordered; backend hash seed choices
must not change observable deterministic programs.

Pipelines are syntax-only call insertion. They do not imply laziness,
parallelism, query planning, mutation, or error propagation.

Tables are library values with schemas and rows. They use the ordinary
collection verbs where semantics align. A lazy table operation may construct a
plan, but the value's type and `explain` view make planning visible. SQL-like
query syntax is not required by the core language.

## Absence

`Option[T]` is either `Some(T)` or `none`. `none` is not a member of every type
and is not the no-payload value; successful completion without a payload uses
`()` of type `Unit`.

`option?.member` maps member access over `Some` and preserves `none`. Chained
safe calls evaluate each receiver once. `option ?? fallback` evaluates the
fallback only for `none`.

Postfix `?` on `Option[T]` is legal only inside a function returning
`Option[U]`; it returns `none` from that function when absent. It does not invent
an error or map absence to `Result` implicitly.

## Expected Failure

`Result[T, E]` is `Ok(T)` or `Err(E)`. Error values are ordinary nominal data
and should encode categories a caller can act on.

Postfix `?` on `Result[T, E]`:

```text
Ok(value) -> produce value
Err(error) -> return Err(error) from nearest function
```

The target function must return `Result[U, E]` or a statically known compatible
error type. Conversion is explicit with `map_error`, preserving the original
error as a cause. `?` cannot cross a resource or task cleanup boundary without
running required cleanup.

Validation that can report independent errors, especially data decoding,
accumulates them applicatively. Sequential computations using `?` fail fast.
Both behaviors are useful and must not be conflated.

## Unexpected Failure

`panic` signals a broken invariant or unrecoverable runtime condition. It
carries structured diagnostics and a cause chain. Routine library APIs do not
use panic for missing files, invalid user input, network responses, or decode
failures.

The core language does not promise recovery from arbitrary panics. Hosts may
isolate processes or tasks and supervisors may restart them. Foreign exceptions
are caught at an FFI boundary and either translated to a declared `Result`
error or classified as a host panic.

Cancellation is a distinct control signal. It is not an `Err`, panic, or
ordinary value, though APIs may record cancellation as outcome data after the
task has unwound.

## Decode And Encode Boundaries

External bytes become owned data through explicit stages:

```text
bytes -> format parser -> Value -> decoder -> owned data
```

`Value` is a closed structural interchange variant with `Value.Null`,
`Value.Bool`, `Value.Number`, `Value.Text`, `Value.Bytes`, `Value.List`, and
`Value.Map` cases. Host objects do not enter Nomi as trusted `data`.

`T.decode(value)` returns `Result[T, DecodeErrors]`. The generated decoder:

- is strict by default;
- rejects unknown fields unless openness is declared;
- never coerces unless a field names a decoder that does so;
- applies and records defaults;
- checks all independent fields and accumulates failures;
- reports paths, expected and actual forms, constraint source, notes, and
  provenance;
- redacts `Secret` and sensitive values;
- constructs `T` only after every required check succeeds.

Parsing and decoding remain separable so JSON, CSV, TOML, database rows, host
objects, and network protocols can share the same type boundary.

Encoding is also explicit. Protocol-specific encoders decide field names,
versions, omission, and compatibility. Default display is never treated as a
wire format.

## Resources And Scope

A `with` scope accepts a resource implementing the `Resource[T]` protocol:

```text
enter -> bind acquired value -> run body exactly once -> exit exactly once
```

Exit receives the body's outcome category so a transaction can commit on
success and roll back on failure, but user code does not need a second syntax
for that policy. If body and cleanup both fail, neither failure is discarded;
the result retains a primary failure and suppressed/secondary causes.

`defer` registers an action in the current lexical scope. Deferred actions run
in LIFO order on all exits. A deferred action cannot cancel an already active
return; its failure joins the outcome's cause group.

Scopes that may invoke a body zero or multiple times are not `with` resources.
They use explicit functions or domain APIs because execution multiplicity is a
semantic fact callers should see.

## Effects And Capabilities

An effect set records categories of world interaction, such as `ConsoleWrite`,
`FileRead`, `FileWrite`, `Network`, `Clock`, `Random`, `Process`, `Database`,
and `UnsafeHost`.

Effect order is not semantic. The formatter displays a set in stable type-name
order so equivalent public contracts have one source representation.

The static rule is transitive: a function may call an effectful operation only
when its resolved effect set includes that capability. Private inference is a
convenience; public `uses` clauses are stable API contracts.

The runtime rule is capability-based: a process, test, notebook, browser host,
or embedded application supplies concrete capability values. Declaring an
effect does not grant authority by itself. Hosts can deny, virtualize, record,
or replay capabilities.

Handles carry narrower authority than global effects. A function given a
read-only file handle cannot derive write or directory access merely because
its caller had broader filesystem authority.

## Async And Concurrency

Calling an `async func` creates a cold task value; it runs when awaited or
started in a task group. `await` suspends the current task without blocking its
executor thread.

Structured task groups obey these invariants:

- every child completes or is cancelled before the group exits;
- parent cancellation propagates to children;
- one child failure follows the group's declared policy (cancel siblings,
  collect all, or continue), never an undocumented runtime default;
- multiple failures are represented as an ordered `ErrorGroup` with causes;
- cleanup and `defer` finish before completion is observed;
- task-local capabilities cannot silently become process-global.

Detached tasks are a specialized runtime capability, not a default operation.
Channels, actors, locks, and parallel collection execution are libraries built
on the task/runtime model.

## Modules And Packages

A file has one module identity derived from its normalized package-relative
path. Import resolution never executes source code merely to discover names.
Module initialization is deterministic, cycle-checked, and free of undeclared
effects.

An executable script may contain direct top-level statements. Its complete
effect set is inferred, displayed, and granted or denied by the host before
execution. Published library modules allow declarations and deterministic
effect-free constants at top level; application entry points use explicit
`main` contracts.

Public declarations form the module interface. Package builds serialize a
typed interface artifact so dependents do not need implementation source for
analysis. Private implementation changes do not affect identity of the public
interface artifact.

Package manifests declare dependencies, targets, required capabilities,
language edition, and exported modules. Lockfiles pin exact content hashes.
Source import syntax names modules; package version resolution belongs entirely
to the package tool.

## Interop

Foreign calls cross a typed adapter generated from an interface description.
Adapters specify:

- ownership and lifetime of transferred values;
- blocking or async behavior;
- error and exception conversion;
- text, bytes, number, collection, and data representation;
- effects and capabilities;
- thread/executor requirements.

`Any` host objects may exist only inside an `UnsafeHost` capability boundary.
They do not define equality, exceptions, iteration, or object semantics for
Nomi itself.

## Diagnostics, Traces, And Explanation

Every parse, type, constraint, pattern, decode, effect, task, resource, and
example failure is structured data before rendering. A diagnostic minimally
contains:

- stable code and category;
- primary and related source spans;
- user-facing summary;
- expected and actual semantic values;
- cause chain or grouped failures;
- one or more concrete repairs when known;
- redaction policy;
- machine-readable metadata for editors and agents.

Renderers adapt detail to terminal, editor, notebook, browser, CI, and protocol
clients without changing meaning.

`nomi explain` is a tooling view over source, typed surface, lowering, effects,
plans, and runtime semantic events. It is not a keyword that changes program
semantics. Tracing is opt-in, bounded, redactable, and deterministic when run
against replayable capabilities.

## Examples

An `example` is a named executable declaration. It runs in an isolated scope,
uses declared or test-provided capabilities, and records each `check` as a
structured assertion.

Examples are discoverable documentation and valid tests, but they do not
replace property tests, fuzzing, integration tests, benchmarks, or conformance
fixtures. One mechanism may feed several tools without pretending one testing
style covers every risk.

## Determinism And Portability

The language defines evaluation order, numeric conversion, text encoding,
collection ordering, time-zone handling boundaries, random capability use,
diagnostic codes, and serialization profiles precisely enough that conforming
backends agree.

Target-specific behavior is exposed through explicit capability or platform
APIs. A backend may optimize aggressively only when observable source semantics
remain unchanged.
