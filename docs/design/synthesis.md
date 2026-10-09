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

### October 8: exploration and selected assurance

The latest direction reopens mandatory public annotations. Canonical
[semantics](semantics.md#progressive-assurance) now accepts dynamic exploration
with honest unknowns and checked interfaces whose complete contracts may be
inferred locally or declared. Source semantics, selected checking restrictions,
runtime authority and engine choice remain independent. The whole-program
fixture includes an inferable public batch limit and a negative unknown-call
boundary; neither supplies a general inference algorithm.

The conservative scalar/direct-call module experiment is now preserved at
6aec9f3: an unannotated invoice, output that defeats purity, and an unknown
dependency that defeats closed evidence. Its type and purity requirements are
independent. The [checkpoint](../orientation/frontier_checkpoint_2026-10-08.md)
distinguishes passing analysis/integration checks from unresolved hosted
continuation failures. Call-context facts must not be generalized into public
proofs; uncalled function effects must not become module effects. This bounded
experiment leaves D1/D2 and dynamic package adapters open. Research
still routes through [the feature packet](../research/features/README.md) and
[the bridge](../review/2026-09-29-language-synthesis.md).

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

## Growth Journeys And Boundary Evidence

October 9 planning continuation. These are conditional design comparisons and
prepared expectations, not executed target programs or additional accepted
syntax. They connect the existing fixtures to the first reusable product slice.
The [frontier plan](../../FRONTIER_PLAN.md) owns execution order; this section
owns the whole-program questions. Do not replace the wider invoice/import/job
journeys with the scalar prototype simply because it is runnable.

### Invoice: Explore, Extract, Then Share

Start with the runnable `scripts/check_invoice.nomi`: `subtotal(1200, 3) + 250`
prints `3850`. Change quantity to 4 in a new source revision: the expected result
is `5050`. No floating-point money, currency conversion or rounding claim is
needed. The richer [invoice fixture](interaction_model_target.nomi) separately
uses Tea/Cup rows and totals `1500`; keep the same inputs within each paired
representation comparison.

The important transition is extracting a reusable function. The unannotated
`price * quantity` body does not by itself select Int multiplication from every
possible protocol. One observed Int call cannot select a universal public type.
Compare an inferred contract where the owner has sufficient evidence with an
explicitly directed boundary:

```nomi
pub func subtotal(price: Int, quantity: Int) -> Int:
    return price * quantity
```

This uses accepted target syntax but is not a claim the scalar checker can
verify annotations or export modules. Scalar operations still need an owned
numeric profile. The body and meaning stay the same; the public promise is now
checkable independently of clients. Negative-price validation would be a new
domain requirement, not something a stricter type policy may silently invent.

| Step | Prepared observation | Failure and repair |
| --- | --- | --- |
| Create and inspect | Calculation facts are distinct from the ConsoleWrite action | Unknown arithmetic dispatch stays an obligation, not a guessed Int. |
| Revise | New source gives 5050; old result keeps its source revision | A late 3850 result stays historical and cannot overwrite the new run. |
| Restrict | Type and purity checks examine the same source facts | `print` blocks whole-script purity; inspect/extract the pure calculation, or retain the effectful script policy. |
| Reuse | A checked consumer reads the exported contract without executing or inspecting private module code | Ambiguous public parameters require direction; do not specialize the library from its first client. |
| Repair | Explain the call site, public promise and missing evidence together | Fix a mismatched argument or establish the owner contract; an annotation alone cannot certify an unknown host call. |

Prepared policy matrix for the existing module-execution experiment:

| Source | Preview | known-types | pure | both |
| --- | --- | --- | --- | --- |
| Scalar calculation only | Facts available | Satisfied | Satisfied | Satisfied |
| Same calculation plus scalar print | Facts plus ConsoleWrite | Satisfied | Unfulfilled | Unfulfilled |
| Used unknown external call | Unknowns visible | Unfulfilled | Unfulfilled | Unfulfilled |
| Unknown call only in an uncalled plain function, with no defaults/annotations | Latent obligation visible | Module obligations can be satisfied | Module obligations can be satisfied | Module obligations can be satisfied |

The last row would **not** satisfy a complete exported-function policy for that
body. Every verdict names its scope. A malformed policy is a request error;
unknown or contradicted evidence cannot satisfy an obligation. Preview success
means a report was produced, not that the program is proved safe. Policy order
must not affect facts, obligations or admission; there is no `pure wins` rule.
Profiles may name sets of restrictions only if their expansion and prerequisites
are inspectable. Package syntax and a general prerequisite solver remain open.

Proposed terminal explanation for the reusable unannotated multiply:

```text
Cannot establish a checked public contract for subtotal.
The multiplication does not determine price and quantity's parameter types.
Declare the intended parameter types, or keep this definition exploratory.
The observed call subtotal(1200, 3) is evidence for that call only.
```

The editor relates the public declaration and multiplication; the machine record
needs an exported-function scope, unresolved parameter/protocol obligations,
evidence origin and those source relations. Code names/schema are not assigned
by this example. If the producer lacks real spans, show the function/source
revision without inventing a location. Adding Int declarations directs checking;
the body must still be verified against that contract.

### Import And Report: Keep The Boundary While Growing The Program

Use `decode_batch`, `eligible_customers` and `run` from
[the overall fixture](targets/overall.nomi). An exploratory entry can inspect
`decode_batch` on an in-memory Text and handle its Result; it does not bypass
decode because static checking is relaxed. Reuse the same pure decode/filter
functions in a module, then add the explicit file/network/write orchestrator.
This separates data validation from permission and from package evidence.

| Prepared input/event | Expected observation | Repair or unresolved owner |
| --- | --- | --- |
| Customer name empty and age -1 | Both indexed decode paths; zero profile requests and report writes | Correct both fields; do not offer only the first error as a sufficient repair. |
| Valid customer below minimum age | Count skipped_ineligible, not malformed | Change the eligibility policy explicitly if intended. |
| Host returns Text where a checked adapter promised Int | Boundary failure under the adapter's declared taxonomy | Decoder/result conversion must be explicit; annotation is not coercion. |
| Profile response names a different customer | ProfileIdentity error; no report publication | Preserve expected/received identity and input row context. |
| Network denied after a valid check | Runtime authority refusal before that network operation | Static evidence stays evidence; no cache hit recreates a grant. |
| Report publication acknowledgment lost | External outcome unknown; local Stop is not rollback | Inspect/reconcile by the adapter's operation identity before retry. |
| 128 rows containing one enormous Text | Row count alone does not bound bytes or decode work | File/response bytes, depth, per-field size and diagnostic budgets need explicit owners. |
| Duplicate customer IDs | Fixture exposes an unresolved duplicate policy | Decide rejection, deduplication or allowed multiplicity before relying on identity for updates. |

The whole-program target's pure `maximum_batch_size()` is the first small
public-inference discriminator. Change a private comment, change its result
from Int to Text, then change a dependency's effect footprint. Consumers must
distinguish source freshness, contract compatibility and execution identity.
Neither a backend switch nor downstream call observations may repair a missing
public contract. Full import promotion additionally needs D1-D3, bounded task
queues, codec laws and a real publication adapter; a good scalar demo does not
close those gates.

### Resource Job: Reuse The Operation Without Exporting Its Lease

Use `read_text`, `copy_text` and `receive` from
[the resource fixture](resource_lifetime_target.nomi). The library long form
already separates resource description, enter, body and release. Exploration
can omit static facts but cannot omit promised runtime revocation or cleanup.
Checked reuse must carry callback effects, the fresh region and whole-completion
non-escape; it may return owned Text or Bytes, never a hidden retained reader.

Creation-to-repair story: read owned text; inspect the enter/body/release trace;
extract the operation into a reusable function; select a lifetime obligation;
reject an escaping callback; repair by returning an owned value while the
resource is live. That repair changes when work happens and must be explained,
not applied as an allegedly equivalent rewrite. Body error plus release error
retains both causes. Cancellation is observed only after required join/cleanup,
or as explicitly incomplete when the host cannot finish. The
[resource discrimination table](resource_lifetime.md#remaining-completion-experiments)
owns exact expectations and remaining choices.

### Evidence That Must Survive All Three Journeys

Proposed artifact distinction, refining the accepted assurance direction:

| Record | Identity and validity basis | Consumer obligation |
| --- | --- | --- |
| Source evidence | Exact source revision, edition, producer/rule version, dependency basis and numeric/host assumptions actually used | Refuse unsupported or stale evidence; never promote supplied examples into inferred facts. |
| Public contract | Module/declaration identity, exported types/effects/call shape and supported contract version | Check compatibility without private client code; a same-named type from another package is not automatically identical. |
| Verification record | Contract plus the implementation/dependencies it was checked against | A private edit may preserve the contract while requiring a new verification record. |
| Build/run selection | Exact executable content, profile and input snapshot | Recheck current authority at effect boundaries; static evidence is not a transferable grant. |
| Explanation/view | Source or value epoch, completeness and redaction | Keep unavailable spans and omitted facts explicit; formatting a new revision cannot reuse old offsets blindly. |

The first experiment should use a locally produced, closed monomorphic scalar
contract. Unknown dependencies prevent checked export. An explicit dynamic
adapter remains a challenger for later work: runtime shape checks alone cannot
certify purity, non-escape or termination of arbitrary foreign code. Do not
design a universal adapter before stating which of those guarantees it enforces.

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
