# Nomi Decision Ledger

> Status: canonical target decision ledger.
>
> This ledger records the current language-design choices after the 2026-07-16
> reset. `Accepted` means part of the target, not necessarily implemented.
> Reconsideration requires new user evidence or a failed whole-program test.

## Decision Standard

A proposal is judged in this order:

1. Which real program is hard to read or write without it?
2. What semantic fact should its syntax make visible?
3. Can an existing form express it without serious cognitive or diagnostic
   cost?
4. Does it compose with types, patterns, failure, effects, async, tooling, and
   formatting?
5. What does the language become unable to simplify if this is accepted?

Implementation effort and existing tests are not reasons to preserve a design.
They matter only after a target choice survives this review.

## Accepted Foundations

| Area | Decision | Rationale |
| --- | --- | --- |
| Evaluation | Eager, left-to-right, lexical scope | Predictable across scripts, services, notebooks, and backends. |
| Typing | Progressive static typing; inferred locals, explicit public APIs, no implicit `Any` | Low ceremony without sacrificing package-scale contracts. |
| Runtime types | Types and constraints remain inspectable; proven checks may be optimized away | Decode, diagnostics, interop, and explanation need runtime meaning. |
| Memory | Garbage-collected general profile | Cognitive cost is better spent on domain logic than ownership syntax. |
| Binding | Immutable `name = value`; mutation uses `var` and `set` | Creation and change are visually distinct. |
| Constraints | `where` attaches executable predicates to bindings and data | One validation vocabulary, retained source, no schema mini-language. |
| Functions | `func` for named behavior; `(args) => expr` for anonymous behavior | One long form and one explicit value form. |
| Data | Immutable nominal product and closed variant `data` | Durable domain identity plus exhaustiveness. |
| External structure | `Unknown`/`Value` plus explicit decode | Structural convenience stays at visible trust boundaries. |
| Choice | `if` for Bool; exhaustive `match` for structure | Two genuinely different questions, no aliases or silent unmatched statements. |
| Collections | Loops plus `map`/`filter`/`fold` family and one `|>` | Familiar verbs, readable left-to-right flow. |
| Absence | `Option`, `?.`, `??` | Absence is not error or general truthiness. |
| Expected failure | `Result` and postfix `?` | Typed and concise at the call site. |
| Unexpected failure | Panic/host failure kept separate | Bugs do not look like expected domain outcomes. |
| Resource lifetime | Exactly-once `with` plus unconditional `defer` | Acquisition and cleanup remain lexical and deterministic. |
| Effects | Public `uses` sets plus runtime capabilities | Reviewable APIs without ambient authority. |
| Concurrency | `async func`, `await`, structured task groups | Suspension and child lifetime remain explicit. |
| Modules | Files are modules; private by default; explicit imports and `pub` | Scales from script to package with little ceremony. |
| Packages | Manifest, exact lockfile, content addressing, sandboxed build | Reproducibility and supply-chain trust begin at ecosystem birth. |
| Diagnostics | Structured records shared by every frontend | Humane messages require semantic data, not backend strings. |
| Examples | Top-level `example` plus `check` | Executable documentation without a function-body sublanguage. |

## Syntax Simplification Decisions

The old corpus often accepted every form that could reduce to a common core.
That is not enough: two reducible forms can still make readers learn two ways
to recognize the same act.

| Previous candidate | Decision | Canonical replacement |
| --- | --- | --- |
| Equation functions `f(x) = expr` | Reject | `func f(x): return expr` |
| Piecewise equations | Reject | one `func` with `match` |
| No-parentheses function equations | Reject | declarations and calls always use parentheses |
| `_`, `$1`, `$name` lambda holes | Reject | explicit `(name) => expr`; `_` only wildcard |
| Operator sections | Reject | explicit lambda |
| `>>>`, `<<<`, or another composition operator | Reject | `compose` library function |
| Local `where` helper clauses | Reject | nested/local bindings or local `func`; reserve `where` for constraints |
| `unless` | Reject | `if not condition` |
| Postfix conditional | Reject | inline or block `if` |
| `if let`, `guard let`, `while let` | Reject | `match`, loops, and small helper functions |
| `case` keyword inside `match` | Reject | indentation already establishes pattern-arm context |
| Refutable patterns on the left of `=` | Reject | statically irrefutable destructuring or exhaustive `match` |
| User extractors, view/active patterns, and match macros | Reject from the initial core | visible normalization/parsing call followed by closed patterns |
| Non-exhaustive statement `match` | Reject | explicit complete cases or catch-all arm |
| Open map patterns by default | Reject | exact maps; spell openness with `..` or `..rest` |
| `select`/`where` collection aliases | Reject | `map`/`filter` |
| Augmented assignment such as `count += 1` | Reject | `set count = count + 1` |
| Implicit multiplication such as `2x` | Reject | `2 * x`; scoped scientific notation may be proposed later |
| Range punctuation such as `1..10 by 2` | Reject from the initial core | `range(1, 10, step=2)` and iterable libraries |
| `try`/`except` expressions for expected failure | Reject | typed `Result`, `match`, and postfix propagation |
| Implicit partial application | Reject | explicit lambda |
| Whitespace function application | Reject | ordinary calls with parentheses |
| Implicit string formatting vs f-string split | Reject both split forms | all ordinary quoted text interpolates; raw text opts out |
| `call(...) -> value:` block call | Reject | `with ... as ...` for exactly-once resources; explicit lambda otherwise |
| General `yield` as policy control | Reject from core | reserve `yield` for a future generator design if justified |
| Block calls as all concurrency | Reject | explicit async functions, await, and task groups |
| Query block syntax | Reject from core | table library and visible plan values first |
| Decorator-based core semantics | Reject | ordinary declarations, protocols, or explicit metadata |
| `shape` as second record declaration | Reject | nominal `data`, structural patterns, and decode |
| `const` as a constraint | Reject | immutability is the binding default |
| Implicit truthiness | Reject | `if` requires Bool |

## Punctuation Discipline

The target deliberately narrows overloaded punctuation:

- `->` means a declared function result, never a block binding.
- `=>` means an explicit pattern/parameter maps to one expression.
- `_` means a pattern wildcard, never a generated parameter.
- `where` means a constraint, never local definitions or filtering.
- `?` means propagation of `Option` or `Result`, never exception catching.
- `??` and `?.` mean absence handling only.
- `|>` means call insertion only, never lazy, parallel, fallible, or query
  execution.
- `..` means structural remainder in list/map patterns, never a range.
- `=` creates a binding or supplies a named/default value, never equality or a
  function equation.

This is a stronger coherence test than "can it desugar?"

## Accepted But Deliberately Narrow

### Inline `if`

Accepted only as `if condition then value else value`. Multi-step control uses
the block form. This avoids a second ternary punctuation and prevents hidden
value rules in arbitrary statement suites.

### Match expressions

Accepted because structural choice is pervasive. `=>` arms are single
expressions. Colon arms are statement-only and make the enclosing match a
statement. Multi-step value logic moves into a small function, avoiding an
implicit final-expression rule for blocks. Every match is exhaustive; captures
are transactional and arm-scoped; pure `when` guards do not prove coverage.
Capture names obey the ordinary reserved vocabulary, and primitive patterns
reuse the scalar literal codec rather than a pattern-only quoting or escape
dialect. Interpolated text is an expression, not a literal pattern.
The full contract is in [Pattern Matching](pattern_matching.md).

### Pipeline

Accepted with first-argument insertion. It does not imply partial application.
Libraries that want pipeline ergonomics design data-first functions.

### Postfix propagation

Accepted for `Option` and `Result` only. The carrier and target function make
the control transfer statically visible. Error conversion is explicit.

### `with`

Accepted for exactly-once acquire/use/release. Retry, iteration, callbacks,
event handlers, generators, and task scheduling do not borrow this syntax.

### Effect declarations

Accepted on public APIs. Private inference reduces ceremony, but tooling must
show the resolved effects. The exact initial effect taxonomy remains an
experiment listed below.

## Library-First Decisions

These are important capabilities but not grammar:

- collection transforms, streams, tables, and query plans;
- decoding, encoding, schema export, and configuration layering;
- retry, backoff, transactions, tracing, fixtures, and supervisors;
- units, quantities, arrays, tensors, rank operations, statistics, and
  symbolic algebra;
- actors, channels, locks, atomics, schedulers, and parallel collections;
- command construction, shell pipelines, process supervision, and deployment;
- secrets, cryptography, authentication, logging, metrics, and tracing;
- property testing, fuzzing, mocking, snapshots, and benchmarks;
- protocols, generic algorithms, and extension methods until their core shape
  is proven by libraries.

Library-first is a positive design choice. It lets real APIs discover which
operations are universal before the grammar makes them permanent.

## Scoped Future Layers

Some domains may eventually justify notation beyond ordinary calls. They must
be explicit lexical scopes that produce inspectable values:

- symbolic quotation and rewriting;
- relational/query notation;
- parser grammars;
- staged build or compile-time evaluation;
- array/tensor notation;
- safe template languages.

A scoped layer must specify entry and exit types, hygiene, effects, diagnostics,
formatting, expansion, and tooling. It cannot change the meaning of code outside
its boundary.

## Rejected For The Base Language

- global reader macros or syntax plugins;
- arbitrary compile-time code with ambient authority;
- default structural typing;
- untagged union types in the initial language; use named variant `data`;
- silent coercion or unchecked casts;
- nullable-by-default types;
- unstructured child tasks;
- ambient file/network/process access;
- automatic dependency upgrades;
- executable package-install hooks;
- separate schema, configuration, testing, and query languages;
- dense point-free or array glyph syntax in ordinary modules;
- magic methods whose names define core semantics indirectly;
- a class hierarchy as the universal data and dispatch model;
- hidden control transfer through decorators or callbacks.

## Open Experiments

These choices are not yet strong enough for permanent syntax:

| Experiment | Current hypothesis | Evidence needed |
| --- | --- | --- |
| Constraint note placement | `where predicate note "..."` | Formatting tests across bindings, fields, and parameters. |
| Effect taxonomy | Small capability categories in `uses` | Three real programs plus host/test substitution. |
| Protocol declarations | Explicit protocols with visible imports | Collection, display, numeric, decode, and FFI implementations. |
| Methods and extensions | Methods for owned data; imported extensions only | API discoverability and conflict experiments. |
| Generic constraints | Readable nominal bounds, no type-level language | Container and service-library pressure. |
| Error conversion | Explicit `map_error` first | Measure repetition in layered services. |
| Async resource scope | `async with` | Cancellation and cleanup conformance tests. |
| Generators | Dedicated design using reserved `yield` or streams | Cases where iterator objects are materially worse. |
| Table planning | Ordinary verbs on typed plan values | CSV, dataframe, SQL, and distributed execution prototypes. |
| Numeric tower | Exact defaults and overflow policy | Scientific, finance, and systems-profile benchmarks. |
| Data openness | Explicit rest field or decoder policy | API evolution and forward-compatible config programs. |
| Edition boundaries | Per-package editions normalized to Core | First real breaking migration. |

## Feature Admission Packet

The [cognitive/interface proposal](interaction_model.md) recommends testing
text-primary source with read-only projections before editable views. Stable
command identity, typed changes, explicit epochs, and evidence-aware explanation
are **proposals, not accepted contracts**. Structured-document primary remains
a competing candidate. The [design-first agenda](redesign_agenda.md) names
broader gaps; it does not accept new keywords, inference rules, or APIs.

The [interaction edge/composition extension](../research/interfaces/composition_cases.md)
adds counterexamples and HX1-HX8 comparisons. Model incarnation, proposal
repreparation, evidence completeness, and bounded inverse edits remain
**proposed, not accepted**. Target-only invoice cases now include reset histories
and row identity; executed local research models are not runnable Nomi conformance
or a decision to change ordinary Bool, match ordering, effects, or `where`.

The [function contract proposal](function_contracts.md) recommends testing
pure-only strict collection callbacks before effect-polymorphic callbacks.
This remains **open**: world effects, mutable captures, retained regions and
latent task effects require a coherent type model and source notation first.
Result-returning callbacks do not silently introduce propagation or rollback.

The [September synthesis](synthesis.md) reaffirms the accepted core without
admitting new syntax. [Category targets](targets/README.md) and
[the overall fixture](targets/overall.nomi) replace the legacy program as the
active coherence suite. API names in those files are explicitly proposals.

Additional interaction gates exposed by the whole program remain **open**:

| Gate | Not yet decided | Concrete evidence route |
| --- | --- | --- |
| Resource escape | Static lifetime/non-escape checking versus runtime closed-handle checks | Return, capture, child transfer in [resource comparison](../research/features/resources.md). |
| Composed outcomes | Typed domain cleanup errors versus an abnormal multi-cause envelope | Body Err plus close Err plus cancellation; preserve every cause. |
| Callback effects | Pure-only collection verbs versus effect-polymorphic signatures | [Functions](../research/features/functions.md) and [effects](../research/features/effects.md). |
| Task policy and memory | Abnormal failure policy, observation order, and separate queue bound | [Concurrency comparison](../research/features/concurrency.md). |
| Derived codec projection | Explicit encoding/decoding signatures and non-projectable predicates | [Decoding comparison](../research/features/decoding.md). |

These gates refine existing open questions; the corpus is not evidence that
their implementation or semantics are complete.

The [resource completion proposal](resource_lifetime.md) now recommends typed
scope failure through an explicit library Result carrier and checked non-escape
with runtime revocation. This is **recommended, not accepted**: the symbolic
comparison does not typecheck callback/region contracts or test a real scheduler.

Before an open experiment becomes accepted, its proposal must include:

- three representative programs, including one failure-heavy program;
- the explicit long form and any proposed shorthand;
- parse, name, type, effect, runtime, and concurrency semantics;
- interaction with every punctuation word it reuses;
- formatter output at narrow and wide widths;
- beginner, editor, and machine-readable diagnostics;
- lowering/explanation output;
- rejected alternatives and removal plan;
- cross-backend conformance fixtures;
- a target-program update proving whole-language coherence.

The burden belongs to the new feature, not to every existing user.
