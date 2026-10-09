# Nomi Language Synthesis

> Status: active whole-language design synthesis; open contracts are not accepted.

Packet: `docs/research/features/README.md`,
`docs/design/targets/overall.nomi`,
`docs/review/2026-09-29-language-synthesis.md`.

## Read The Language

Start with the [first-product contract](#first-product-contract) and
[local report program](targets/overall.nomi), then consult the relevant
[category fixture](targets/README.md). The
[language reviews](../research/languages/README.md) and
[feature comparisons](../research/features/README.md) supply evidence when a
concrete fork needs it. Reading or implementing the entire research inventory
is not a release prerequisite. No usability study or comparative benchmark was
conducted by this synthesis.

This synthesis connects those views. Accepted source and behavior still belong
to [syntax](syntax.md), [semantics](semantics.md), [industrial contracts](industrial.md),
and [the decision ledger](decisions.md). Proposed library signatures in target
comments are hypotheses, not exports. The current playground runs a different,
supported prototype surface. Do not advertise these fixtures as executable.

The [cognitive/interface expansion](interaction_model.md) adds 18 non-standard
interface threads and a second coherence fixture without admitting grammar.
Use the [design-first agenda](redesign_agenda.md) for cross-cutting gaps and
closure order; the sequence below continues to own import-workflow admission.

## First Product Contract

October 9 synthesis selects **small scripts and trustworthy local data reports**
as the first useful product. The primary user is a person who can read simple
code and wants a calculation or a small data transformation to work, explain
mistakes, and become reusable. Local library authors are the next user, reached
through the same journey. Services, research computing, notebooks and larger
automation remain destinations, not simultaneous launch requirements.

The product promise is: **start with a short script; turn imperfect input into
an understandable result; reuse that logic without changing its meaning**.
This is a scope decision and a contract to validate, not evidence of adoption
or a claim that the prototype already supplies it.

| Journey | Concrete result | Evidence required before release |
| --- | --- | --- |
| Calculate | Change invoice quantity from 3 to 4; result changes from 3850 to 5050 integer cents | Correct calculation, visible source/result revision, useful wrong-argument error, no annotation ceremony to begin. |
| Validate and report | Paste two customer rows; obtain received=2, eligible=1, skipped_ineligible=1; inspect Ada's normalized row | Decode precedes filtering; malformed name and age produce both original input paths; no success report on error. |
| Reuse | Import the calculation/report function in a second local module and run the same inputs in the CLI and browser | Same values/errors and checked boundary, no private-body access by consumers, unknown dependencies remain visible. |

The report is local and pure: Text and options enter, a typed Result leaves.
The host explicitly supplies input and saves an encoded output on request.
Inspecting a report, encoding it and successfully saving it are three distinct
outcomes. No public network service, secret, task scheduler or language resource
scope is needed to explain this first complete workflow.

### Selected Core And Library Boundary

This selects an initial supported profile from the target. It neither invents
a second language nor reverses accepted semantics for omitted features. Each
row must have source, diagnostics, formatting and portable behavior before
being advertised. The existing prototype may support additional experimental
forms while the release profile remains explicit.

| Include for the first product | Coherent rule | Boundary on the commitment |
| --- | --- | --- |
| Names and local state | Lexical binding; immutable by default; mutation uses `var`/`set` | No separate reactive assignment, automatic dependency tracking or hidden shared state. |
| Values | Int, Bool, Text, Unit; strict List; structural `Value` at external boundaries | Numeric/text details must pass the bounded closure below; Float/Decimal/Bytes/time APIs are later scope. |
| Calls | One `func` form, ordinary calls, explicit expression lambdas, accepted argument/default laws | No currying, holes, overload resolution or user generic/protocol declaration syntax required for release. |
| Owned concepts | Nominal immutable products and closed variants with explicit constraints | A small declared shape is enough; no universal object hierarchy or arbitrary schema generator. |
| Choice and repetition | Bool `if`, exhaustive `match`, ordinary loops | Ship the needed accepted pattern subset honestly; advanced pattern optimization is not a gate. |
| Expected outcomes | Option and Result as closed alternatives; explicit mapping and `?` | Panic remains separate; no implicit Err filtering, exception-to-Result conversion or changed evaluation order. |
| Data boundary | Strict JSON parse/decode, accumulated independent errors, explicit encode | JSON only initially; CSV conversion, rolling schemas and arbitrary host objects need separate adapters. |
| Collection library | Ordered eager map/filter/fold; synchronous, non-retaining pure callbacks for the selected checked path | Closed type instances still require real contracts and effect checking; user polymorphism is not inferred from examples. |
| Reuse | Local modules, private/public boundary, inferred-or-declared closed public contracts | No registry, solver, remote package install or general public inference algorithm needed first. |
| Touching the world | Explicit console and host input/save adapters with ordinary operation failures | Host-owned transport does not silently introduce source-level File/Network authority or pretend to settle fallible `with`. |
| Understanding | Format, run, inspect a value, follow an error to source/input, inspect a public signature | Explain actual facts; advanced graphs, editable projections and agent-suggested changes are later experiments. |

The notation budget stays the one in [syntax](syntax.md). Accepted conveniences
such as interpolation, `?` and `|>` can share their existing normal forms; they
do not justify extra spellings. The first report uses named intermediate values
and ordinary collection calls so its stages remain easy to inspect. Remove a
convenience from the initial profile if it adds disproportionate implementation
work without improving these journeys; retain its target disposition explicitly.

### What Waits And What Keeps It Possible

| Later capability | Why it waits | Re-entry pressure and preserved boundary |
| --- | --- | --- |
| HTTP, services and concurrent jobs | They add authority, timing, cancellation and remote outcome to an otherwise local task | A second real workflow needs remote work; resource/task packets own grants, bounds and completion. |
| Fallible scoped resources and regions | Host adapters can own the first bounded read/save operations | User code must manage a live handle; preserve explicit owned-value versus scoped-handle distinction. |
| Public generics, protocols and effect polymorphism | Closed exports and checked library instances cover the selected examples | Repeated local libraries cannot express a useful contract; use the existing callback/shared-storage witnesses. |
| Rich numeric, table, array, ML and document APIs | Domain laws and performance costs differ | Add ordinary packages with explicit codecs and effects; only consider scoped notation after calls fail a real program. |
| Editable tables/graphs, notebook semantics and collaboration | Source plus read-only results can complete the first task | Measured creation/repair trouble triggers the paired representation trial; source/revision identity remains available. |
| Package registry, native optimizing engine and multiple polished IDEs | Distribution breadth is not needed to test a small reusable program | Local module identity, portable conformance and versioned producer/consumer contracts leave room for these later. |

Existing research is a reserve of alternatives. Reuse it when a selected
program exposes a missing contract; do not turn every mechanism surveyed into
a required subsystem. No generic plugin framework or universal IR is needed
merely to keep extension possible.

### Bounded Closure Before Coding The Target Slice

These are the remaining first-product decisions. Recommendations are starting
candidates; their owners must accept concrete rules and independent vectors
before a runtime implements them. Broader D1-D3 questions remain open outside
this profile without blocking it.

| Owner / decision | Starting candidate | Discriminator and required result |
| --- | --- | --- |
| D3 / scalar and text contract | Exact Int semantics; reject unsupported numeric inputs without rounding; Text operations have explicit units and no hidden normalization | Compare exact Int with checked fixed width using literal/arithmetic/JSON round trips, bool-versus-Int, huge/negative/fractional values, supplementary characters and offsets. Choose one meaning, document host limits and budget failures; no browser-specific silent range or rounding. |
| D3 / data and codecs | Strict declared fields, duplicate JSON keys rejected, no coercion; explicit normalization; derived codecs limited to supported data shapes | Missing/extra/wrong fields, two simultaneous row errors, empty/128/129 rows, repeated IDs, constrained values and decode/encode round trips. Fix wire shape, path/order rules and bounded-error truncation before promotion. |
| D1 / callable and module boundary | Closed monomorphic public exports; checked pure synchronous library callbacks; local module identity | The invoice and report must resolve every call, default, capture and imported effect. Two passive consumers agree; unknown/private/changed-dependency cases cannot manufacture proof. Explicit adapters are preferable to unexplained inference. |
| D4/D5 / run and host contract | One selected source entry, explicit input/options, a Result inspector, user-requested encode/save; text remains authoritative | Pin entry binding and errors, data limits, source/input/run revisions, stop/restart and host failure behavior. A stale run cannot replace a new result; save failure cannot be shown as completed publication. |

If a candidate fails, simplify the program or library contract first. Any new
language law still needs its canonical syntax/semantics/decision update. A
handwritten demo result, a supplied type record or a passing link checker cannot
close these gates. No new general survey is needed before making the comparisons.

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

The earlier combined fixture improved those boundaries, but still made a useful
local report depend on network, task, resource and publication design. The
October 9 product synthesis removes that dependency from the active
[overall fixture](targets/overall.nomi). It now validates a maximum-128-row
batch, preserves original error paths, filters valid rows, normalizes names,
and returns an owned report. Repeated IDs are retained in source order because
rows are observations, not updates to an identity registry.

The pure function does not publish files. An explicit encoder and host save
operation follow inspection. Proposed codecs and callback contracts remain
labeled; byte/depth/work limits are not implied by a row count. The richer
network/resource program remains in Git at `915aea1`; category and focused
resource/concurrency fixtures retain its extension pressure.

## Interactions To Resolve First

Use the four [bounded closure decisions](#bounded-closure-before-coding-the-target-slice)
for this product. General cleanup outcomes, handle escape, task failure policy,
queue bounds, effect polymorphism and schema evolution remain owned by their
existing packets. They become release blockers only when a selected workflow
requires those guarantees. The executed resource comparison is useful symbolic
evidence for later expansion, not a prerequisite for a pure local report.

## Action Sequence

| Order | Reviewable deliverable | Visible outcome and admission |
| --- | --- | --- |
| 1 | Agree the three first-product journeys, source fixture and explicit exclusions | A person can explain the promised product before reading compiler plans. |
| 2 | Close the selected scalar, codec, closed-call/module and host-run contracts | Every operation in the local report has an owner, independent expected behavior and a useful failure. |
| 3 | Implement the smallest complete calculation path, then report decode/repair | Source, checking, lowering, formatting and diagnostics agree on the supported subset; no disconnected subsystem counts as a finished product slice. |
| 4 | Add reusable local boundaries to those same programs | Two consumers can use checked public evidence; unknown dependencies remain honest. |
| 5 | Promote supported examples and complete the browser/CLI journey | Actual user-path checks, matching values/errors, fresh assets and installed/browser evidence. |
| 6 | Validate distribution, then select the next real workflow | Traceable artifact and rollback; only measured pressure admits later resource, task or domain work. |

The [project roadmap](../orientation/project_roadmap.md#delivery-order-and-dependencies)
owns M0-M5 scheduling. The pattern pass continues within the accepted subset;
a whole-pattern rewrite, every callback mechanism and a new interface framework
are not prerequisites. The dated bridge records why this order changed.

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

The next language step is the bounded first-product closure above. Use runnable
collection traces as behavioral evidence, not as proof of typed callbacks.
Co-design general callbacks and resources when the later resource workflow is
selected; do not make their full D1/D2 resolution a prerequisite for this report.

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

Use `build_report` and `report_json` from
[the overall fixture](targets/overall.nomi). Inspect a Result on in-memory Text,
repair the input, then reuse the same function through an explicit host adapter.
Relaxed static checking never bypasses decoding.

| Prepared input/event | Expected observation | Repair or owner |
| --- | --- | --- |
| Empty name and age -1 | Both indexed paths, no successful report | Fix both fields; filtering may not hide malformed rows. |
| Valid age 12 with minimum 13 | received=1, eligible=0, skipped_ineligible=1 | Change the eligibility policy explicitly if intended. |
| Duplicate customer IDs | Preserve both rows in original order | This is a report over observations, not an update registry. |
| 128 rows with an enormous Text | Row count is insufficient to admit the input | Host/codec byte, depth, work and diagnostic budgets apply. |
| Unknown field, duplicate JSON key or rounded host number | Refusal under the selected strict codec contract | Never silently coerce, drop information or fabricate exactness. |
| New source/input while an old run finishes | Old result remains historical | Run identity prevents replacement of the current result. |
| Encode succeeds but host save fails | Report remains inspectable; save is failed or explicitly uncertain | Repair the host destination; do not rerun pure computation unnecessarily or claim publication. |

The pure `maximum_batch_size()` remains the first small public-inference
discriminator. Private comments may preserve its contract while invalidating
source verification; result/effect changes may break compatibility. Consumer
observations and backend switches cannot repair an incomplete public contract.

Network grants, response identity, lost remote acknowledgment and task cleanup
remain important later pressure in the resource/concurrency fixtures. They do
not belong to the first report's error type or release dependency chain.

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

At the local-reuse milestone, the contract experiment should use a locally
produced, closed monomorphic scalar contract. Unknown dependencies prevent checked export. An explicit dynamic
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
