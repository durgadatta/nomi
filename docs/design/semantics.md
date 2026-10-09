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
- checked public interfaces require complete types, locally inferred or declared;
- exploratory definitions may remain dynamically checked with unresolved static facts;
- an unresolved fact is not an inferred `Any` or a proof of safe unchecked use;
- `Unknown` is a safe top type that must be decoded or pattern-narrowed;
- generic quantification is explicit in checked interface artifacts; source
  spelling and generalization rules remain in the function-contracts packet;
- public inference does not depend on private code in downstream clients.

Nominal `data` types are the default for program concepts. Structural types are
limited to external values, protocols, and explicit patterns. The initial
language uses named variant data rather than untagged unions for alternatives.

## First Product Scalar Contract

Accepted target, October 9: the calculation and local-report profile uses exact
`Int`, distinct `Bool`, and exact Unicode `Text`. Acceptance fixes their meaning;
it does not certify the current Python, Core, WASM or browser implementation.
The [synthesis](synthesis.md#bounded-closure-before-coding-the-target-slice)
separates this decision from the remaining codec, callable and host-run work.

`Int` denotes a mathematical integer. Its admitted operations compute exact
results, without wrapping, saturating, silently rounding or promoting to Float.
Checked fixed width is rejected as the meaning of this default type. A later
fixed-width type or host conversion must declare its own range and failure.
Finite implementation capacity is a resource limit, not a second Int meaning.
A backend must report unsupported capacity or an exhausted declared budget
instead of returning a different value. The first portable release still needs
common measured limits; this decision assigns no unmeasured budget values.

The initial primitive set is deliberately bounded:

| Operation | Result and rule |
| --- | --- |
| Unary `+`, `-` on Int; Int `+`, `-`, `*` Int | Exact Int. |
| Int `<`, `<=`, `>`, `>=` Int | Bool using mathematical integer order. |
| Scalar `==`, `!=` for Int, Bool and Text | Bool using the same runtime scalar type and equal exact value; distinct scalar types compare unequal. |
| Text `+` Text | Text concatenation, preserving both scalar sequences. |
| Text `<`, `<=`, `>`, `>=` Text | Bool using lexicographic Unicode scalar-value order; a proper prefix sorts first. |
| Bool `not`, `and`, `or`; Bool conditions and guards | Bool-only evaluation, with the documented left-to-right short circuit. |

Bool is not an Int subtype: `true` does not mean `1`, and `false` does not mean
`0`. Arithmetic, Int parameters and Int-valued indexing/count boundaries never
coerce Bool, Text or a fractional value. A typed boundary checks before entering
the body or committing a binding. Unsupported operand combinations produce a
structured type/contract diagnostic. An expected external decode failure stays
a Result error. Static facts describe normal completion; neither an Int fact
nor purity proves available capacity, termination or freedom from failure.

Division, remainder, exponentiation, bitwise operations, Text repetition,
Float/Decimal interaction and explicit numeric conversion are not settled by
this initial operation set. Existing experimental support remains a separately
described migration surface, rather than proof that those target contracts are
closed. No checking policy changes successful source meaning.

Text is a sequence of Unicode scalar values, excluding lone surrogates. Literal,
format and foreign boundaries must reject invalid text explicitly. Equality,
concatenation and ordering do not normalize or use locale-specific collation.
Length and text indexing/slicing units are code points, not grapheme clusters,
UTF-8 bytes or UTF-16 code units; admitting a particular indexing/slicing API
still requires its bounds contract. Normalization, case conversion and trimming
are explicit library operations. The first report selects the finite ASCII
operation below; broader Unicode trimming remains open. Python `strip` and
JavaScript `trim` do not agree on all characters, so neither host default
establishes the rule.

Source spans retain half-open UTF-8 byte offsets. Terminal code-point columns
and editor UTF-16 columns are derived views with named coordinate units and the
same source revision. A supplementary character occupies one Text code point,
four UTF-8 bytes and two UTF-16 code units; these quantities are not interchangeable.

### Independent Scalar Vectors

These are target oracles, independent of any runtime's result. They must become
conformance fixtures before the relevant capability is advertised. Source uses
the canonical scalar spellings; a backend's refusal is recorded separately.

| Input or operation | Exact expectation |
| --- | --- |
| `1200 * 3 + 250`; edited `1200 * 4 + 250` | Int `3850`; Int `5050`. |
| `1200 * 0 + 250`; `1200 * (-1) + 250` | Int `250`; Int `-950`. A non-negative quantity constraint separately rejects the negative argument. |
| `9007199254740993 + 1` | Int `9007199254740994`, beyond JavaScript Number's exact range. |
| `9223372036854775807 + 1` | Int `9223372036854775808`, beyond signed 64-bit range. |
| `1000000000000000000000000000001 * 3` | Int `3000000000000000000000000000003`. |
| `true == 1`; `false == 0`; `1 == "1"` | Bool `false` in every case. |
| `true + 1`; `1 + "2"`; `7 - "2"`; `+"2"`; `not 1` | Operand/type refusal, without coercion. |
| `"a" + "😀"`; length of `"😀"` | Text `"a😀"`; Int `1`. |
| Precomposed U+00E9 versus U+0065 followed by U+0301 | Unequal Text, with lengths `1` and `2`. |
| One-character Text U+1F600 compared with U+E000 | U+1F600 sorts after U+E000. |
| Lone high or low surrogate at a Text boundary | Explicit invalid-text refusal, never replacement or silent acceptance. |

### Wire And Capacity Admission Still Required

External format encoding and internal compiler/runtime transport have separate
owners. An external JSON Int field must round-trip exactly or refuse explicitly;
ordinary host JSON parsing is insufficient when it rounds an accepted integer.
Bool, numeric-looking Text and fractional input never silently decode as Int.
Integral decimal/exponent conversion remains part of the general numeric codec
contract. The first report's bounded rule below accepts integer-form tokens
only, alongside explicit duplicate-key/path/encoding rules.

The planned internal transport uses a versioned, explicitly tagged canonical
decimal representation for Int literals and recursive result values. Producers
and consumers must validate the tag and payload and refuse an unknown major
version before effects. This is a migration requirement, not an accepted schema
number or a claim that existing Core JSON implements it. A supplied tag is not
evidence of correct source checking. External JSON field shape cannot be inferred
from this internal representation or from human display.

Shared source/input byte, nesting, evaluation-work, integer-capacity, collection
growth and output budgets remain admission work. Publish only measured supported
limits, identify them in run/evidence records, and distinguish malformed input,
unsupported backend capacity and host budget exhaustion. Never produce a success
report, rounded value or invented cleanup guarantee after refusal.

## Progressive Assurance

Accepted direction: users can start with dynamic exploration and select
independent restrictions as the program grows. Written annotations are one
source of direction, not a universal prerequisite to useful code. This revises
the earlier mandatory-public-annotation rule. The exact general inference
algorithm, policy declaration syntax and dynamic package adapters remain open.

Separate source meaning, checking policy, runtime authority and engine choice.
A policy selects obligations and their required evidence; it does not change
evaluation order, successful values, default timing, binding/capture meaning,
cleanup or failure semantics. Promised runtime checks cannot simply be disabled.
Optimizations may discharge them only with sufficient evidence. Stricter
checking is neither permission to touch the world nor a performance guarantee.

Reports distinguish inferred facts, declared promises, verified contracts,
runtime-enforced boundaries, observed examples and unresolved obligations.
Checking a scalar call at one known argument type does not establish a generic
public signature. Checked interfaces serialize their complete contract and
provenance, independently of private downstream use; changed dependencies or
source invalidate affected evidence. A supplied annotation is checked against
the implementation, not trusted merely because it is written.

For example, `pub func answer(): return 42` can expose `() -> Int` with no world
effects when those facts are established locally. `func identity(value): return
value` remains usable in exploration; accepting a polymorphic public interface
also requires the generalization/capture law. An unknown foreign callback may
run under the host's ordinary runtime boundary, but cannot satisfy a selected
purity or closed-interface obligation without evidence or an approved adapter.
Here "approved" means supported by the language/host contract, not inferred
from a user's description of intent.

Restrictions need not form a total ladder: a schema requirement need not imply
purity, and a pure computation can still have unresolved type information.
The scope and unfulfilled obligation must appear in diagnostics. A strict
run/build policy completes required admission before effects; this admission
path is a target requirement, not a claim the prototype implements it.

The `known-types`/`pure` prototype experiment reports facts about module
execution in a small scalar/direct-call subset. It does not establish whole
package interfaces, lifetimes, termination or freedom from runtime failure.
Unsupported syntax and indirect calls remain explicitly unresolved.

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

### First-Report Boundary Contract

The selected first report is a closed JSON batch, not a general schema system.
These rules guide the next library experiment; they do not establish a working
target decoder, nominal values, `Result`, checked imports or derived codecs.
The target remains [the overall program](targets/overall.nomi). Its compatibility
bridge is specified in [synthesis](synthesis.md#report-library-experiment).

Parse before decode, decode the complete admitted batch before filtering, and
normalize only valid rows. JSON objects must reject duplicate decoded keys,
including escape-equivalent spellings such as `name` and `\u006eame`. Distinct
Unicode scalar sequences remain distinct keys. A duplicate is a format error
with its original structural path; it is not overwritten or confused with a
repeated customer ID. The parser rejects invalid syntax and lone surrogates in
text/keys, with no replacement or normalization.

Every number preserves its original JSON token as Text in the parser's
structural output. Parsing performs no Float conversion. Int decoding accepts
only the grammar `-?(0|[1-9][0-9]*)`; `1.0` and `1e0` retain non-integer-token
identity and fail an Int field even though their mathematical values are whole.
Bool and numeric Text fail likewise. Accepted Int values are exact. A backend
that cannot represent a value must return an explicit capacity refusal, never
round it or turn that capacity into a new age constraint. Python exact Int and
the current JS safe range remain different implementation capacities; complete
portable exact-Int execution is still pending.

For this report, trim removes only leading/trailing U+0009 through U+000D and
U+0020. It retains interior characters and all other scalar values. In
particular U+0085 and U+FEFF are retained and do not count as blank under this
finite predicate. This deliberate initial operation is not a general Unicode
whitespace claim. A later Unicode-aware policy needs another named, versioned
library contract; changing a checking policy cannot silently change trimming.

The initial schema is exactly:

| Shape | Required fields and checks |
| --- | --- |
| Batch | A map containing only `customers`, a strict list of at most 128 rows. |
| Row | A map containing only `id`, `name`, `age`; no absent-field defaults. |
| `id`, `name` | Text whose finite trim is nonempty; decoding retains the original Text. |
| `age` | Integer-form Number token decoded exactly as Int, then checked `>= 0`. |
| Report options | A separate closed map containing only `minimum_age`, an integer-form Number decoded as Int `>= 0`; an absent field applies and records the declared default `13`. |

Options and customer input are separate boundaries. Invalid options do not
become customer-row errors, and the options default does not grant defaults to
missing batch/row fields. Decode records whether `minimum_age` was supplied or
defaulted; explicit `13` and omitted input have the same value but different
default provenance. The compatibility entry takes explicit options JSON,
`build_report(text, options_text="{}")`, parses and decodes it through the
options descriptor before report construction. This is not the target typed
`ReportOptions` constructor or an implicit global input binding.

Container shape and cardinality are prerequisites for its child checks. A
129-row list reports the batch-size error at `customers` and does not apply row
schema checks or construct decoded rows. Parsing and structural validation of
the supplied Value tree still precede schema decoding. Within an admitted list,
rows are checked in index
order; each row checks `id`, `name`, `age`, then unexpected fields in Unicode
scalar-value key order. Root unexpected fields follow its known field's checks.
Missing/wrong fields and validly typed constraint failures accumulate
independently. A failed field type suppresses that field's predicate, not
neighboring checks. No partially decoded row/batch escapes.

Error paths are ordered Text/Int segments, for example
`["customers", 0, "name"]`; these segments are authoritative. Display begins
at `$`, renders indexes in brackets, and quotes/escapes non-identifier keys.
Diagnostics refer to the original input revision; unavailable source spans
remain unavailable. Syntax/duplicate-key/invalid-text, schema/constraint,
unsupported numeric capacity and resource limits need distinct error rules.
The compatibility error record has exactly `code`, `path`, `path_text`,
`expected`, `message`: a stable rule code, authoritative segment list, escaped
`$` rendering, expectation and repair explanation. Do not echo raw field values
or entire input. Existing passive DecodeError fields may be adapted to this
record; their presence does not establish a decoder or nominal error value.

The first encoding experiment accepts only null, Bool, Int, Text, strict List
and Text-keyed maps. It rejects Float, foreign/callable objects, cycles,
non-Text keys, invalid Text and unsupported numeric capacity. Only plain
structural records cross this compatibility boundary; foreign class instances
and host objects cannot borrow map status. Encoding does not
parse human display or infer a codec from runtime nominal tags. The report wire
contains `received`, `eligible`, `skipped_ineligible`, `customers`; each customer
has `id: {"value": Text}`, `name: Text`, `age: Int`. A flat ID needs an explicit
different codec. Rows and repeated IDs retain original order. Every map is
encoded in Unicode scalar-value key order, with minimal separators and literal
UTF-8 scalar characters except required JSON escapes for control characters,
quotation marks and backslashes. Do not use insertion order, host locale or
JavaScript's default UTF-16 sort. Int encoding uses canonical decimal spelling.

The experiment's provisional limits are 256 KiB input UTF-8 bytes, 32 nested
map/list containers, 8,192 structural Value nodes, 64 retained errors and 64 KiB
encoded UTF-8 bytes. Depth counts simultaneously nested map/list containers;
the root container counts as one and primitive leaves add no depth. Each
structural Value scalar/container counts once; map keys are not nodes and are
bounded by the byte limit.
Validate scalar Text before computing bytes. Supplied Value trees receive the
same structural limits. These numbers are experimental configuration, not
measured support, language meaning or a general execution-work bound. Measure
limit/limit-plus-one cases on pinned hosts before advertising capacity.

Keep the first 64 errors. Observing a 65th error stops accumulation and returns
failure with `complete=false`; do not invent an omitted total count or a
successful partial batch. Exactly 64 errors remain complete if validation
finishes with no omissions. Other resource refusals distinguish incomplete
validation explicitly. An encoding limit preserves the inspectable report.
Source/evaluation work, UI display retention, worker Stop and host save remain
separate runner contracts; byte/row bounds alone do not establish them.

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
when its resolved effect set includes that capability. Checked public effect
sets are stable API contracts whether inferred or written with `uses`.
Unknown effects cannot satisfy a closed effect requirement; inference is not
authorization.

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

An executable script may contain direct top-level statements. Its known and
unresolved effects are displayed; the host independently grants or denies
runtime authority. A selected closed policy requires a complete supported
effect contract before execution. Published checked library modules allow declarations and deterministic
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
