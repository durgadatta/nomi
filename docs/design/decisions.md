# Nomi Decision Ledger

> Status: canonical target decision ledger.
>
> This ledger records the current language-design choices after the 2026-07-16
> reset. `Accepted` means part of the target, not necessarily implemented.
> Reconsideration names the changed user direction, evidence or whole-activity
> pressure and its consequences for existing contracts.

## Decision Standard

A proposal is judged in this order:

1. Which real activity or program is hard to express, understand or change without it?
2. What meaning should its representation or interaction make visible?
3. Can an existing form express it without serious cognitive or diagnostic
   cost?
4. Does it compose with types, patterns, failure, effects, async, tooling, and
   formatting?
5. What does the language become unable to simplify if this is accepted?

Implementation effort and existing tests are not reasons to preserve a design.
They matter only after a target choice survives this review.

## Guiding Vision Direction — October 10

The user's direction establishes the [computational-medium vision](vision.md):
design language and environment around how people create, understand, revise,
share and authorize computational work. The prototype, current evidence map and
release milestones are revisable means toward it. Discovery may start beyond
the existing target programs and registered questions.

This accepts a guiding purpose and separates discovery from feature admission.
Text/structured/mixed authoring, partial execution, evidence-connected artifacts,
domain models and delegation remain competing hypotheses. No new syntax, API,
type rule or universal intermediate representation is accepted here. Existing
semantic decisions retain their status until a named revision supplies its own
coherent contract and consequences.

The later October 10 clarification makes easier thinking the shared purpose
across domains. The [vision continuation](vision.md#thinking-is-the-shared-design-goal)
and [scientific thinking workflow](scientific_discovery.md#design-from-thinking-activities)
organize discovery around distinctions, assumptions, consequences, alternatives
and revision. This updates the guiding design criterion; it does not accept a
universal mental calculus, new Core primitives or a measured usability claim.

## Accepted Foundations

| Area | Decision | Rationale |
| --- | --- | --- |
| Evaluation | Eager, left-to-right, lexical scope | Predictable across scripts, services, notebooks, and backends. |
| Typing | Dynamic exploration; selected restrictions; checked public contracts inferred locally or declared | Begin without annotation ceremony; unknowns never become fabricated proof. |
| Runtime types | Types and constraints remain inspectable; proven checks may be optimized away | Decode, diagnostics, interop, and explanation need runtime meaning. |
| First-product scalars | Exact mathematical Int; Bool distinct; Text is an exact Unicode scalar sequence | Same successful values across hosts, explicit capacity refusal, no numeric coercion or hidden normalization. |
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
| Effects | Checked public effect contracts, inferred or declared with `uses`, plus separate runtime capabilities | Reviewable evidence without granting ambient authority. |
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

Accepted as explicit contracts. Inferred public effects are also allowed when
the owner can establish and serialize them independently of private client
code. Tooling must show resolved effects and unknowns separately. A selected
annotation policy can demand written `uses`; it cannot change execution or
grant authority. The exact effect taxonomy and general inference remain open.

### Progressive assurance (October 8 revision)

The user's exploration-first direction replaces mandatory public source
annotations with complete checked interface evidence, inferred or declared.
Dynamic exploration may proceed with honest unknowns and defined runtime
checks. The [semantics](semantics.md#progressive-assurance) separates evidence,
policy, authority and engines. Reject a universal strictness switch that changes
successful meaning, invents proof, or implies native performance. Reject
mandatory `Any` as the only exploratory starting path.

The first experiment is scalar/direct-call analysis of module execution with
independent type/purity obligations. It cannot accept generic public contracts,
resource safety or deployment readiness. Public generalization, scoped policy
composition and dynamic/checked adapters remain open. The binding law and
`var`/`set` spellings remain current target choices; plain reassignment is a
reopened experiment requiring closure and notebook re-execution comparisons.

The October 9 [growth-journey plan](synthesis.md#growth-journeys-and-boundary-evidence)
and [function trial](function_contracts.md#bounded-contract-comparison-for-implementation)
select **experiment baselines, not additional accepted rules**: closed
monomorphic interface evidence before general public inference, exact positional
callback contracts before callable-shape subtyping, and explicit rejection of
unknown dependencies before dynamic adapters. Compare conservative
generalization against justified relaxation using shared-storage witnesses.
No Fn spelling, policy syntax or artifact schema is admitted. The paired
[representation trial](interaction_model.md#paired-representation-and-revision-trial)
keeps structured-document primary viable; prose comparisons do not select a
usability winner. Resource/defer timing and cleanup precedence remain proposed.

### First-product scalars (October 9 acceptance)

Accept [the bounded scalar contract](semantics.md#first-product-scalar-contract):
default Int is exact mathematical integer arithmetic; Bool is a distinct type;
Text is an exact Unicode scalar-value sequence with code-point units and
lexicographic scalar-value ordering. The initial Int arithmetic is unary
`+`/`-` and binary `+`/`-`/`*`, with the explicitly listed comparisons and Bool/Text
operations. Cross-type scalar equality never numerically identifies Bool with
Int. Implicit numeric coercion and hidden text normalization remain rejected.

The invoice, arithmetic beyond JavaScript Number and signed 64-bit ranges, Bool
separation and supplementary-character vectors distinguish this choice from
checked fixed width and host text behavior. Fixed width is rejected as default
Int meaning: it would introduce an arbitrary overflow boundary and still need
an exact representation on the browser route. Explicit fixed-width host types
and conversions remain possible later. This is a semantic choice, not a
performance result or full numeric-tower admission.

Budget exhaustion and unsupported backend capacity must refuse visibly rather
than change a successful value. The bounded report decision below selects its
trim/numeric/encoding laws; common measured capacities and tagged transport
remain implementation/admission work. The planned internal wire has validated Int tags
and decimal payloads, and refuses unknown major versions; no new schema version
is claimed implemented or accepted here. The current JS safe-integer fence,
Python Bool arithmetic and prototype `True`/`False` spellings are migration
facts, not target laws. Canonical source remains `true`/`false` and `none`.

The [independent vectors](semantics.md#independent-scalar-vectors) are acceptance
oracles. Keep separate capability evidence for source acceptance, checking,
lowering, execution, diagnostics and formatting. A passing operand-coercion
repair is not complete exact-Int or typed-call conformance; the existing
[synthesis bridge](../review/2026-09-29-language-synthesis.md#bounded-scalar-continuation-2026-10-09)
owns migration and unresolved work.

### First-report boundary (October 9 planning decision)

Select [the closed report rules](semantics.md#first-report-boundary-contract):
exact JSON numeric token preservation, integer-form tokens for Int fields,
duplicate decoded-key rejection, strict declared fields, independent ordered
errors before filtering, explicit normalization and bounded structural encoding.
Reject host JSON numeric conversion/overwrite and display-as-wire shortcuts.
Repeated customer IDs remain distinct ordered observations.

The initial report trim removes only U+0009 through U+000D and U+0020. U+0085
and U+FEFF remain intact and nonblank under this finite predicate. This narrow
choice gives the same inspectable operation on both hosts without accepting a
general Unicode whitespace API or inheriting their differing defaults.

Use [the ordinary-call experiment](synthesis.md#report-library-experiment) before
any schema framework: a versioned closed structural JSON tree with Number tokens,
two declarative `report-batch`/`report-options` descriptors, fresh validated compatibility records
and source-owned transformations. These library APIs/tree/outcome records are
selected lab interfaces, not newly admitted syntax, nominal Value/Result/data,
derived codecs or source-inferred purity. Validate supplied trees rather than
trusting tags. Manual metadata must be replaced by admitted DataDecl contracts
when they can represent the same rules and independent evidence. Options are a
separate boundary with a recorded default `minimum_age=13`; customer fields have
no defaults. Do not translate malformed options into a row error or pretend the
compatibility JSON entry implements target `ReportOptions` construction.

The input/depth/node/error/encode limits are provisional experiment values,
subject to pinned measurements. A budget/capacity refusal cannot create a
success report, fabricate a total error count or alter exact Int meaning.
Keep target promotion and runner/host/human gates explicit; a useful compatibility
sample is not completion of the canonical report. No general schema language,
numeric tower, package system or new evaluator feature is selected here.

The [October 9 synthesis closure](synthesis.md#report-admission-gaps) selects the
remaining bounded plan: operation kind plus stable codes, stage-scoped
completeness, options-first entry failure, escaped lossless paths, a
token-preserving scanner, deterministic writing, whitelisted structural
adapters and shared boundary accounting. Reject host-default JSON conversion,
resettable per-call budgets as proof of a bounded run, and guessed nominal
identity. Simultaneous options/batch error aggregation is deferred until a
repair journey demonstrates a need for its extra partial-stage states.

Prepared literal records are an implementation oracle; they have not been run
against report libraries. Planning closure means the next implementation does
not need to invent these rules. It does not close measured capacity, target
typing, source/tooling conformance or the language-coherence packet.

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
| Numeric tower beyond the first-product Int contract | Exact Int is accepted; Float/Decimal, explicit fixed width and conversion remain open | Scientific, finance, and systems-profile laws and benchmarks. |
| Scientific modeling layer | Five proposed contracts: spaces, bound expressions/relations, theories, joint observations and qualified realizations | [SP1-SP5](scientific_discovery.md#current-gap-and-ordered-implementation): no-input oscillator checks, premise-qualified derivation, approximation and inference counterexamples. |
| Foundational scientific-reasoning pivot | Investigate contextual terms, checked composition and explicit judgments; variation, selection and scale are supplied structures, not new domain keywords | [R0-R5](reasoning_algebra.md#one-integration-path-with-closure-receipts): audit and bounded exact map compositions now; scoped binders, independent rules/replay, continuum variation and qualified approximation remain gates. No minimality proof or accepted replacement Core. |
| AI framework development | Proposed semantic spaces, numeric programs, transformation rules, explicit state transitions, qualified realization and scoped evidence; no new source syntax | [AF0-AF6](ai_frameworks.md#integration-and-gap-analysis): bounded no-input named-axis checker first; independent gradient, state/resume and backend evidence remain open. |
| Data openness | Explicit rest field or decoder policy | API evolution and forward-compatible config programs. |
| Edition boundaries | Per-package editions normalized to Core | First real breaking migration. |

## Feature Admission Packet

The [cognitive/interface proposal](interaction_model.md) recommends testing
text-primary source with read-only projections before editable views. Stable
command identity, typed changes, explicit epochs, and evidence-aware explanation
are **proposals, not accepted contracts**. Structured-document primary remains
a competing candidate. The [design-first agenda](redesign_agenda.md) names
broader gaps; it does not accept new keywords, inference rules, or APIs.
The text-first recommendation is a reversible delivery baseline. It does not
require broader structured/mixed authoring research to wait for that baseline
to fail; the guiding vision can challenge either candidate.

The [interaction edge/composition extension](../research/interfaces/composition_cases.md)
adds counterexamples and HX1-HX8 comparisons. Model incarnation, proposal
repreparation, evidence completeness, and bounded inverse edits remain
**proposed, not accepted**. Target-only invoice cases now include reset histories
and row identity; executed local research models are not runnable Nomi conformance
or a decision to change ordinary Bool, match ordering, effects, or `where`.

The gap review additionally separates pure candidate validation from shared-state
publication, and required review scope from current execution authority. Both
are **open tool/application contracts**. The HX8 preparation protocol and
maintained research checks do not accept them or establish human comprehension.

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
