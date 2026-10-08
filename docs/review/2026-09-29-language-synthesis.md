# Language Research And Target Review

> Status: dated evidence and continuation snapshot; not a second live backlog.

Keep this file as evidence, not as a second backlog. Live priorities belong in
[the synthesis](../design/synthesis.md), [open questions](../research/open_questions.md),
and `config/design_passes.json`.

Packet: `docs/research/features/README.md`, `docs/design/synthesis.md`,
`docs/design/targets/overall.nomi`.

## Scope And Outcome

The user requested critical reviews by language, comparisons by feature,
category target files, one overall program, and one synthesis. This pass adds
44 bounded language reviews, 13 feature comparisons, 13 category sources and
an overall source, with navigation and authority made explicit. The pre-existing
uncommitted category drafts were preserved and corrected, not discarded.

Read the [language index](../research/languages/README.md),
[feature index](../research/features/README.md), and
[target index](../design/targets/README.md). Primary documentation supports
mechanism claims; Nomi recommendations remain design judgment. No foreign
program suite, user study, performance benchmark, or target type checker was
run. The comparison set is deliberately scoped, not a universal language survey.

The earlier playground implementation was committed as `e3b88d2`. This language
documentation work is a separate uncommitted change; runtime, parser, runnable
samples, and GitHub deployment are not modified by this pass.

## Findings

The accepted core is coherent in isolation, but the legacy overall program
overclaimed several library interactions: CSV conversions, indexed error
collection, normalization validity, callback typing, group policy, and cleanup
outcomes. Reusing an established language's spelling does not import its
contract. The revised program avoids unsupported coercion, uses a bounded JSON
batch, separates ineligibility from invalid input, and makes task policy and
codec assumptions visible. Legacy source is retained with a superseded header.

The highest-risk unresolved design pair is deterministic cleanup plus handle
escape. The next pair is callbacks/generics plus effects. Cold tasks require
observable start/stop and distinct ordinary versus abnormal outcomes; a running
limit is not a queue-memory bound. Portable numerics and strict boundary paths
are necessary for truthful browser results. These findings are promoted to
the decision ledger as **open gates**, not accepted new features.

## Validation Scope

Use the registered documentation checks and packet validator for this pass.
They establish lifecycle status, navigation, registration, and local consistency.
They do not prove target programs parse, typecheck, or execute. The target-only
sources remain outside `samples/`; no web manifest regeneration is required.
Validation on 2026-09-29: all 10 docs-lifecycle/design-pass tests passed using
the local Python 3.14 environment; both registered packets passed validation;
agent doctor passed; a local scan of 102 Markdown/Nomi files found no broken
relative file links, and new suite/research files had no trailing whitespace.
`git diff --check` passed. The ignored local RAG index was rebuilt with the new
documents. These results are documentation checks, not language conformance.

## Domain Composition Continuation, 2026-10-04

The user requested data dependencies/history first, AI/ML second, then coherent
extension across computational and human-knowledge domains. The existing
data/workflow dossier is extended with
[dependencies/time](../research/data_workflows/dependencies_and_time.md) and
[AI/ML](../research/data_workflows/ai_ml.md), followed by a
[twenty-family composition map](../research/domain_composition.md). These routes
link to the [canonical synthesis proposal](../design/synthesis.md#domain-layer-proposal)
and [target-only challenger](../design/targets/research/domain_layers.nomi).
No new packet, universal ontology/evaluator, grammar or production library was
created. Existing D1-D7 and open questions retain admission ownership.

### Pass 1: Mechanisms And Whole-Program Pressure

Selected primary sources distinguish task DAGs, lineage, relational plans,
provenance, streams/fixed points and differentiation. They also distinguish
retained historical reads, valid/system time, checkpoint restoration, replay,
recompute and compensation. ML evidence separates tracing from execution,
specification from learned/training state, seed from reproducibility, and
model inference from authorized tool action. The Nomi recommendation is our
inference: domain-owned models with compositional typed/effectful boundaries,
within the existing four layers. Framework prominence is not core admission.

The broader scan adds documentary/reference/evidence contexts, including legal
structure, scientific naming, catalog identity and communication profiles.
Reviewed, existing and discovery-level mechanisms are labeled. Inaccessible
entrypoints and deprecated/pinned editions are recorded; the pass does not
claim every cited system or human discipline has been comprehensively audited.

### Pass 2: Counterexamples And Capture Boundary

Thirteen [local probes](../research/data_workflows/composition_experiments.md)
execute original bounded models and graphlib/SQLite observations: alternate
topological orders, role mismatch, temporal correction/availability, deleted
content, independent snapshots, update-law failure, cache context/current read
policy, train-only statistics, axes, checkpoint scope, aliases/catalog identity
and exact review scope. Existing interaction probes retain uncertain external
outcomes and history/publication races; they are not recounted as integrations.

A new negative test exposed malformed environment metadata that produced an
attribute traceback. The checker now validates object shape before comparing
versions. It rejects duplicate fields, changed execution flags (including wrong
JSON types), malformed captures and outcome drift without rewriting evidence.
Historical host versions remain provenance. A supplied policy flag is still
not a real capability, and required-field presence is not exact training resume.

Validation at this checkpoint: 62 focused tests passed; all five design packets,
the thirteen-probe capture, lint and whitespace checks passed. Remaining full
repository validation is recorded below after completion. No target type
checker, AD engine, remote service, device, authenticated review or human study
was executed.

### Pass 3: Repository Integration And Final Evidence Audit

The full Python suite passed 1,533 tests with 76 skipped and four Jupyter path
deprecation warnings. Existing web/runtime checks passed 55 contracts plus
manifest and WASM freshness; no browser interaction trial was performed. All
five design packets, target-direction inspection, lint and whitespace passed.
A changed-document audit resolved 544 local file/anchor links across 20 Markdown
files. Runtime, parser, samples and generated web assets were not changed.

The final evidence audit tightened the text capture comparison to preserve JSON
types (`true` is not `1`) and require nonempty historical version strings while
allowing version-only differences. The six focused text checks passed after
that test-only tightening. This does not claim Nomi or foreign conformance.

## Pass Retrospective

### Frontier continuation, October 8

The new user direction and planned scalar/direct-call experiment reopen a
mandatory public source-annotation rule. The canonical spine now distinguishes
dynamic exploration, checked inferred/declared interface evidence, selectable
annotation policy, runtime authority and engines. This is a target-direction
revision; no general inference algorithm, dynamic package adapter or full
checker is established by these edits. The overall target gains a locally
inferable public constant function and an explicitly negative unknown call.

Evidence/verification for the executable slice belongs in the current roadmap
receipt. The first resumed lifecycle check failed because the earlier frontier
checkpoint was missing from the docs index; the index was repaired without
altering its existing test. That failure is the immediate feedback loop's first
concrete correction. Public callback generalization remains a separate D1 gate.

The planned durable process improvement is an explicit command-receipt tool and reusable
feedback-cycle prompt, routed from the existing agent collaboration owner.
They record actual checks and require findings to lead to a fix, a bounded
experiment, or a documented deferral. They do not certify semantics or accept
designs automatically. The next comparison is the analyzer's independent
type/purity matrix plus adversarial capture/rebinding/unknown-call fixtures.

### Evidence That Changed The Design

The combined program exposed misleading count semantics and an unstated CSV
conversion contract. Language evidence also separated declaration from authority,
GC from release, pipeline spelling from execution, and task return values from
task failure. Those distinctions changed the active fixture and experiment order,
not the accepted core vocabulary.

### Workflow Friction

The earlier session left category drafts with links to unwritten indexes and
synthesis, so a resumed agent could mistake intention for completion. Several
official sites expose sparse or inaccessible extracted pages; cited scope was
narrowed to retrievable primary documentation, with historical/version limits
stated. Breadth cannot substitute for conformance or user evidence.

### Durable Improvement

The registered `language-coherence` packet now gives subsequent agents one
research/design/target/bridge route. Two indexes satisfy the requested research
dimensions without multiplying authorities. Each page names an observable
experiment and each target labels proposed APIs. The complete docs inventory
and existing design-pass checks guard the routing, while canonical decisions
keep unresolved assumptions open.

### Next Pass (Original September Checkpoint)

Run `python3 -m tools.design_passes show language-coherence`, then read the
resource comparison and canonical resource semantics. Write three programs
(simple reader, staged acquisition, cancellation plus failed release), compare
two outcome carriers and two escape policies, and produce ordered event traces
and diagnostic JSON. Only after that decision should a frontend/runtime slice
and supported playground sample be proposed. Keep the pattern pass's existing
authority and avoid expanding this survey absent a concrete failed program.

### Domain Continuation Retrospective

**Evidence That Changed The Design:** a common graph drawing is not a common
executor; historical validity and availability differ; fitted state and training
resume differ; formal/documentary structure is not semantic truth or authority.
The candidate retains domain payloads and explicit adapters instead of one IR.

**Workflow Friction:** rolling docs redirected to versioned pages or unrelated
entrypoints, so versions/fetch limits were retained. Pure field-presence models
could otherwise be mistaken for static typing or engine guarantees.

**Durable Improvement:** the registered synthesis packet routes the new domains,
and deterministic capture/limit/experiment/link/anchor checks preserve the
boundary between local evidence and unperformed integrations. No new agent
instruction or framework was justified.

**Next Pass:** close D1-D3, type an inert two-input report and temporal basis,
then compare data/numeric/documentary adapters under DC1/DC5. Use an established
engine for a settled numeric/query slice. No new notation or sample until
independent value/error/authority/source-map fixtures and honest host profiles
agree; the map is a finite research frontier, not a promise to implement all
human knowledge simultaneously.

### Messaging Continuation (October 4)

**Evidence That Changed The Design:** selected primary architecture mechanisms
separate event identity from delivery attempts, queue receipts from partition
positions, acceptance from observation, and local atomic intent from external
effects. Replayable history is neither current execution authority nor automatic
business rollback. The synthesis now names those boundaries without admitting
new core grammar or an all-purpose reliable-delivery type.

**Workflow Friction:** some NATS documentation entrypoints redirected to an
unrelated index; the official documentation repository was used with a rolling
version fence instead. A simple consecutive-offset model would wrongly reject
real numeric gaps, so the finite frontier model uses delivered obligations.
Field matching and imposed atomic arbitration are explicitly not authentication,
crash-safe transactions or distributed fencing.

**Durable Improvement:** [the architecture dossier](../research/data_workflows/messaging_and_events.md)
routes six bounded forks, 24 edge cases, three target-only long forms and ten
original finite probes through the existing language-coherence packet. A new
capture-integrity/behavior/navigation test file and registered reproduction
commands make this evidence reproducible without changing runtime samples,
existing tests, browser inventory or accepted language contracts.

**Next Pass:** close D1-D3, type the messaging long forms, then choose one pinned
adapter under MSG1/MSG3 and independent crash/recovery/settlement vectors. Test
unknown publication, conflicting payload, retained dedup horizon and owner
fencing at the actual durable boundary. No broker, network, durable store,
asynchronous scheduler or authenticated authority was exercised by these probes.

**Verification:** 37 new messaging checks and 92 combined research/docs/packet
checks passed; the full suite passed 1,967 tests with 80 existing skips and ten
worker-repeated Jupyter path deprecation warnings. All five packets, the finite
capture comparison, Ruff and whitespace checks passed. Web manifest freshness
(123 runtime files, 11 samples) and WASM freshness (eight outputs) passed without
regeneration: this pass adds no runtime module or supported sample. Target
typing, broker integration and a new browser interaction trial remain unperformed.

## Research Gap Continuation, 2026-10-04

The accepted audit is documented across existing owners, with the
[research overview](../research/README.md#research-gap-continuation) providing
the full route. This bridge records research evidence, not implementation or
another live ordering. The synthesis packet now deepens
[memory publication](../research/features/concurrency.md#memory-visibility-and-publication),
[predicate consistency](../research/data_workflows/dependencies_and_time.md#predicate-consistency-beyond-snapshots-and-row-guards),
[package/module nominal identity](../research/features/modules_tooling.md#nominal-identity-across-package-instances),
[adaptive evaluation](../research/data_workflows/ai_ml.md#adaptive-evaluation-feedback-is-also-a-dependency),
[learned influence removal](../research/data_workflows/ai_ml.md#data-erasure-and-learned-influence-are-different-operations)
and [correlated uncertainty](../research/notation_atlas.md#correlated-uncertainty-shared-origin-is-part-of-the-model).
The function, resource and cognitive bridges retain their respective units.

**Evidence That Changed The Design:** tasks do not imply a memory model;
individually fresh rows do not protect a cross-row predicate; same-shaped
versioned declarations need not be the same nominal type. Selected primary
data/ML and measurement evidence also separates training reads from evaluation
feedback, data deletion from learned-state removal, and marginal summaries from
joint uncertainty. These sharpen existing research forks rather than select new
syntax, package identity rules, guarantees or engines.

**Workflow Friction:** already broad coverage can hide a missing composition
law. Each added unit therefore states both what the corpus already covers and
the narrower missing discriminator. Foreign specification guarantees, supplied
model assumptions and original thought experiments remain distinct. An
independent review additionally required the uncertainty averaging oracle to
state its measurand, independence and finite fixed-variance assumptions.
It also sharpened the generalization comparison: value eligibility cannot
quantify variables fixed by an outer shared slot. The memory counterexample
now says "store" rather than imply the publication edge it deliberately lacks.

**Durable Improvement:** existing DT4, ML1, ML4, DW4 and questions 8/9/13/15
now route to competing contracts, inspection obligations and three-level
experiments. Feature/data/interface indexes and registry discovery expose all
eleven detailed units from the ten audit findings. No separate packet, universal
IR, new experiment inventory, accepted target edit, generated web artifact,
code, test or runnable sample was added.

**Next Pass:** take one bounded unit through independent evidence: event- and
model-qualified memory observations, actual owner/adapter commit schedules,
resolved nominal declarations, declared holdout exposure, method-qualified
removal or a supported joint uncertainty procedure. Preserve unknowns and
unsupported profiles instead of widening the claim. Existing D1-D3 and the
canonical research-to-target admission process still gate language changes;
this documentation pass does not close any experiment.

**Completion Verification, 2026-10-05:** the resumed documentation pass passed
317 existing documentation/packet/target-fixture/research checks and all five
packet validations. Local links and heading anchors resolved across all 19
changed Markdown files. The existing generic-operation, interaction, domain
composition and messaging captures reproduced with `--check`; none captures the
new thought experiments or study protocols. The agent doctor passed all 18
checks after refreshing the ignored local RAG index. `git diff --check` passed.
Web manifest freshness (123 runtime files, 11 samples) and WASM freshness (eight
outputs) passed without regeneration: no runtime module or runnable sample
changed. No code/test/capture/target edits, full runtime suite, browser trial,
new foreign-system execution or human study belong to this research-only pass.
The dated source consultation notes remain October 4; registry review dates
record October 5 completion, and all four affected packets remain `designing`.
