# Nomi Language Synthesis

> Status: active whole-language design synthesis; open contracts are not accepted.

Packet: `docs/research/features/README.md`,
`docs/design/targets/overall.nomi`,
`docs/review/2026-09-29-language-synthesis.md`.

## Read The Language

Start with [the overall import program](targets/overall.nomi), then the
[category suite](targets/README.md). Read the [44 language reviews](../research/languages/README.md)
for critical evidence and the [13 feature comparisons](../research/features/README.md)
for mechanisms along one dimension. The scope is selected, not exhaustive.
The reviews distinguish observed behavior from design judgment; no usability
study or comparative benchmark was conducted.

This synthesis connects those views. Accepted source and behavior still belong
to [syntax](syntax.md), [semantics](semantics.md), [industrial contracts](industrial.md),
and [the decision ledger](decisions.md). Proposed library signatures in target
comments are hypotheses, not exports. The current playground runs a different,
supported prototype surface. Do not advertise these fixtures as executable.

The [cognitive/interface expansion](interaction_model.md) adds 18 non-standard
interface threads and a second coherence fixture without admitting grammar.
Use the [design-first agenda](redesign_agenda.md) for cross-cutting gaps and
closure order; the sequence below continues to own import-workflow admission.

## One Coherent Model

Nomi should borrow semantic mechanisms, not accumulate familiar spellings.

| User act | Evidence synthesis | Nomi shape | Cost paid |
| --- | --- | --- | --- |
| Name | Python's immediacy plus lexical/immutable reasoning | Inferred immutable binding; `var`/`set` for change | Breaks Python assignment habits. |
| Transform | First-class functions without multiple call/control rules | `func`, explicit expression lambda, ordinary calls | More helpers and explicit partial application. |
| Model | ML-style alternatives plus nominal package identity | Immutable product/closed variant `data` | Adapters and breaking variant evolution. |
| Choose | Exhaustive structural choice without hidden extractors | Bool `if`, bounded transactional `match` | Explicit classifiers and host adapters. |
| Repeat | Familiar verbs with domain-specific execution laws | Eager List; explicit Stream/TablePlan/Array APIs | Multiple typed domain contracts, not one magical pipeline. |
| Fail | Typed expected outcomes distinct from absence and bugs | Option, Result, `?`, separate panic/cancellation | Explicit context mapping and outcome composition. |
| Touch the world | Resource and task ownership plus host boundaries | Lexical cleanup, `uses`, grants, cold tasks/groups | Signatures and lifecycle policies require care. |
| Understand | Live inspection, source provenance, package contracts | Shared diagnostic/artifact model, examples/checks | Tooling must be designed with semantics, not appended later. |

These choices largely reaffirm the accepted target. This pass does **not** add
keywords, extractors, implicit conversions, generic declaration syntax, macro
quotation, or a second query language. A beautiful short example is not enough
to admit any of them.

## Where The Previous Program Broke Down

The [legacy target](target.nomi) exposed useful ambitions but hid interactions:

1. CSV rows were decoded into Int and Instant fields without an explicit text
   conversion policy. Strict decoding cannot imply those conversions.
2. Mapping a per-row decoder and collecting Results did not specify preservation
   of original row paths or accumulation behavior.
3. "Rejected" counted age-ineligible valid rows, while malformed data aborted
   the workflow. That is misleading report terminology.
4. Normalization entered constrained constructors without a stated preservation
   argument. A transforming boundary needs validation if predicates can change.
5. TaskGroup had a running limit but no named abnormal-failure policy, queued
   memory bound, or public composed-outcome contract.
6. Config acquisition, retry, and generated codec APIs were underspecified;
   Clock and other inferred effects could disappear from an attractive signature.
7. Constructor values and callback generics/effects were assumed by examples
   before their declaration and dispatch rules were settled.

The revised fixture uses a maximum-128-row JSON batch, validates it as one
owned wrapper before network access, preserves nested decoder paths, and counts
`skipped_ineligible` separately. Trim normalization preserves its stated
nonempty constraints. Explicit lambdas avoid constructor-value assumptions.
Task start is in a loop rather than an apparently pure effectful map callback.
The response identity is checked. No report is written after an ordinary input
or enrichment error. The input bound limits handles in this example; it is not
a substitute for a future streaming/backpressure contract.

The program still relies on **proposed** codecs, task handles, HTTP/file APIs,
and publication guarantees. It deliberately leaves task panic/cancellation
outside ImportError and marks the missing envelope. This is honest pressure on
the design, not a claim the program is already well typed end to end.

## Interactions To Resolve First

| Gate | Competing Nomi-compatible choices | Evidence required |
| --- | --- | --- |
| Cleanup outcome | Domain-visible release Result versus distinct composed abnormal envelope | Body Err + release Err + cancellation, without losing any cause. |
| Handle escape | Static non-escape/lifetime rule versus runtime closed-handle checks | Return, callback capture, and child-task transfer, with exact diagnostic behavior. |
| Callback effects | Pure-only verbs initially versus explicit effect-polymorphic signatures | map/fold, resource callback, query translation, and effect diagnostics. |
| Task policy | Cancel siblings versus collect all on abnormal failure | Event traces separating returned Err, panic, cancellation, and multiple failures. |
| Bounds | Explicit bounded producer/queue versus whole finite batch | Peak active/queued counts and no children after lexical exit. |
| Numeric defaults | Arbitrary-precision Int versus checked fixed-width default | Native/JS/Wasm vectors, narrowing diagnostics, measured representation costs. |
| Boundary evolution | Strict closed schema versus explicit version/rest policy | Typos, unknown tags, rolling deployment, indexed errors, non-projectable constraints. |

Do not answer these with more broad language tours. Use the
[open experiment agenda](../research/open_questions.md). The per-language
exercises are candidate evidence, not 44 independent implementation tasks.

The first gate now has an [executed resource experiment](../research/resource_lifetime.md)
and [focused proposal](resource_lifetime.md): 32 candidate traces and 14
supplied-fact escape predictions. Recommendation: typed recoverable completion
and static scoped use backed by revocation. Status remains `designing`;
generic/callback/region typing and actual asynchronous cleanup are not validated.

## Action Sequence

Each step owns one reviewable deliverable and a visible user outcome. The
[dated bridge](../review/2026-09-29-language-synthesis.md) records the snapshot
and exact continuation, while this sequence is the live synthesis route.

| Order | Action and ownership | Acceptance | User-facing connection |
| --- | --- | --- | --- |
| 1 | Language design: settle cleanup carrier and handle escape together | Three representative programs, all exit traces, formatter renderings, diagnostic JSON, accepted/rejected escape cases | A failed import explains both body and release causes; no use-after-close surprise. |
| 2 | Language design: specify callback types/effects and minimal generic/protocol surface | Pure/effectful map, conflicting extensions, task handle typing, inspectable resolved calls | Editor hover and playground explain show the actual call/effects. |
| 3 | Runtime design: close cold-task/group policy and bounded queue contract | Deterministic scheduler traces for Err/panic/cancel; active and queued bounds; no lifetime escape | Run/stop is trustworthy and failures are not silently dropped. |
| 4 | Boundary/numeric design: specify codecs and portable scalar vectors | Indexed accumulated decode errors, no coercion, normalization tests, large integers/rounding agree across hosts | Users see accurate values and actionable input paths. |
| 5 | Frontend/tooling: admit the smallest completed category contract | Accepted/rejected source fixtures, typed Surface/Core, source maps, formatter, structured diagnostics | One honest new runnable playground category, not the whole aspirational suite. |
| 6 | CLI/browser owners: promote after cross-backend conformance | Add supported sample to `samples/`, regression coverage, fresh web manifest, browser smoke and CI | GitHub playground sample can actually run and reproduce documented results. |
| 7 | Product/design review: repeat the overall workflow | Locked host profile, bounded inputs, no secret leaks, publication/failure checks | A coherent import/report workflow rather than isolated feature demos. |

Keep the existing registered pattern pass moving in parallel; do not rewrite
its accepted contract from this survey. Current project-wide delivery and
playground work are routed through the
[project roadmap](../orientation/project_roadmap.md), with the
[September playground plan](../review/2026-09-29-github-playground-agentic-plan.md)
retained as evidence. The import-workflow admission route above remains a
target-design gate, not a claim that the prototype satisfies it.

## Prototype Evidence And Next Admission

The October 4 delivery pass converts selected research into bounded runnable
experiments and interaction repairs. It deliberately does not turn all research
categories into language primitives. These observations constrain future design
but do not settle its open contracts:

| Research pressure | Runnable evidence | Still unresolved |
| --- | --- | --- |
| Text as a composable interface | `samples/text_pipeline.nomi.nb`: explicit whitespace trimming, delimiter split, conversion, ordered state and bounded windows; code-point access fixtures in both JS parser routes | Strict format decoding, complete Unicode/offset/normalization contract, localization and safe rendering |
| Pragmatic generic operations | Ordinary `fold(items, seed, combine)` and seeded `scan`; empty, order, callback-failure and reference-history tests | Typed generic callbacks, effect checking, immutable history, parallel merge laws and conditional object protocols |
| Data dependencies and time | `samples/data_pipeline.nomi`: visible filter/map/fold stages and integer cents | Typed dependency descriptions, snapshot/time axes, incremental execution and durable provenance |
| Cognitive repair and observation | Source-linked known errors, per-execution output, document/run generations and stale-result labels; inspection distinguishes missing evidence from known empty/zero records | Full source maps, semantic commands, task unwinding, usability/accessibility study and durable revision identity |
| Portable values and boundaries | JavaScript exact-integer range rejection; shallow tagged slices; special text keys preserved without inherited host fields | Target numeric tower, Text/Bytes validity, equality/hash/map identity, scalar codecs and cross-host conformance |
| Eager failure and callable boundaries | Portable errors stop later eager work; partial Core call shapes reject unsupported names/parameter kinds before effects | Versioned named/default/callback binding, typed expected outcomes and composed abnormal completion |

The next language step remains D1: type one ordered collection callback, one
decoder callback and one scoped resource callback together under a resolved
generic/protocol/effect model. Use the runnable collection traces as behavioral
fixtures, not as a reason to erase target typing requirements. D2 must then
preserve all completion causes, and D3 must give values and transport one
explicit contract before D4 composes the import program.

AI/ML, web, scientific and documentary domains retain their distinct library/
plan owners in the proposal below. A browser worker being terminated is not a
language-level cancellation/cleanup implementation; a sequence of source edits
is not data time travel. Those distinctions keep a cohesive language possible
without claiming that small prototype experiments implement entire domains.

## Domain Layer Proposal

Status: designing hypothesis; no new syntax, core IR or public APIs accepted.
The [data/time research](../research/data_workflows/dependencies_and_time.md),
[AI/ML survey](../research/data_workflows/ai_ml.md) and
[cross-domain synthesis](../research/domain_composition.md) extend the existing
four-layer model. They test a language that can host rich domains coherently,
without assigning a new meaning to ordinary calls or pipelines.

The [messaging and event architecture continuation](../research/data_workflows/messaging_and_events.md)
adds durable communication pressure to this same proposal. Actors/channels stay
library-first; no broker syntax or universal reliable-delivery primitive is
accepted. Transport evidence does not establish business completion.

Existing typed values, immutable data, explicit functions, Result, constraints,
effects, lifetimes, tasks and modules are the common foundations. Candidate
shared contracts are contextual references, typed descriptions/relations,
domain-owned transitions, interpretation/execution boundaries, evidence and
revision-bound projections/commands. They initially belong to libraries,
protocols and tooling; metadata is attached only where the artifact needs it.
Do not add a universal object/graph wrapper to every value.

| Pressure | Proposed semantic owner | Boundary that must survive composition |
| --- | --- | --- |
| Dependencies | Typed relation library; checked DAG specialization | Prerequisite, lineage, attribution, numeric dependence and feedback differ |
| History | Storage/temporal library | Version, valid time, system/availability time, replay and compensation differ |
| Learning | Numeric/learning library; scoped numeric tool if earned | Specification, learned artifact, training checkpoint and evaluation differ |
| Messaging | Channel/transport/storage libraries and verified adapter profiles | Event versus attempt identity, ownership, settlement versus progress, atomic scope and replay versus authorized effects differ |
| Knowledge/documents | Reference/edition/interpretation library | Labels, entities, evidence, formal rules and human interpretation differ |
| Shared inspection | Tooling envelope, domain-owned payload and source maps | Captured evidence versus current observations; preview never executes |
| Execution adapters | Domain/profile owner, effects/resources/tasks | Checked description versus current grants, completion and uncertain outcome |

Recommendation: one source language with ordinary domain packages and explicit
scoped tools, not global web/data/ML modes. Domain IRs remain distinct and can
lower through versioned checked adapters. One diagnostic/evidence envelope
does not imply one algebra, optimizer, identity or truth system.

The [composition target](targets/research/domain_layers.nomi) supplies report,
train-only description and failure-heavy reviewed-publication long forms using
fictional facades. It has not been parsed/typechecked/executed. The
[local probes](../research/data_workflows/composition_experiments.md) execute
selected finite discriminators, not these APIs or foreign engines. No DAG,
time-travel, tensor, learning or natural-language keywords are admitted.

The [messaging target](targets/research/messaging.nomi) challenges ordinary calls
with a pure reconstruction, one-delivery local inbox/state/outbox transaction,
and failure-heavy relay/reconciliation. It is also fictional and untyped.
Candidate envelope, endpoint, delivery, position, transition and budget contracts
compose into queues, subscriptions, logs, projections, sagas and durable
workflows; they are not six new core types imposed on every object. Keep a
guarantee's participants, ordering scope, retention horizon and failure model
visible. Unknown remote outcome is not ordinary rejection; local cancellation
is not remote rollback; an old grant is not replay authority. Library receipts
must not interchange queue settlement and partition checkpoint semantics.

MSG1-MSG6 remain subgates of D1-D3 and DC1/DC5/DC6. The ten captured finite
countermodels falsify selected naive policies only. Admission still requires
typing the three programs and independent crash/recovery vectors for one pinned
adapter; no broker, durable storage, async scheduler or authenticated authority
was exercised by those models.

Admission order remains D1-D3 then D4: resolve generic/schema/callback/effect/
region and scalar/codec/identity contracts; type the composed program; compare
one data, one numeric and one documentary adapter under DC1/DC5. These studies
extend existing questions 4/7/8/9/11/12/15/17, not a second implementation backlog.
Only evidence that ordinary calls fail three representative programs can justify
scoped notation. A further core primitive needs a concrete missing semantic
contract, an independent conformance slice and an explicit removal criterion.

## Admission And Stop Rules

A target category becomes a supported sample only when it has one meaning
across source, typing, effects, lowering, runtime, diagnostics, and formatter.
Passing doc tests proves links/status/packet consistency, not target parsing or
execution. Keep these sources outside `samples/` until that gate is met.

Library-first is not ambition reduction: tables, arrays, actors, build plans,
and symbolic work remain important. It is a way to discover durable laws before
fixing notation. Admit a scoped surface only if explicit calls genuinely fail
a domain program and the alternative has hygiene, budgets, source maps,
inspection, and a removal path. Stop research when an experiment distinguishes
the candidates, and promote the result into the canonical contract.
