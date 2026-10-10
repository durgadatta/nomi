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

## Frontier Planning Continuation, 2026-10-09

### Evidence That Changed The Design

The pending scalar checker, CLI, feedback tooling and continuation candidate are
preserved at 6aec9f3. The [checkpoint](../orientation/frontier_checkpoint_2026-10-08.md)
records 146 passing focused checks and 24 failing/15 passing protocol-review
cases. The scalar experiment supplies module-execution facts, not checked public
interfaces. Reviewing the invoice/import/job journey exposed the next missing
boundary: public compatibility, source verification and executable identity
must remain distinct, including when private changes leave a signature unchanged.

### Workflow Friction

The old next action still requested the now-preserved scalar experiment, while
the handoff described its code as unreconstructible local work. A high-level
growth promise also lacked explicit transitions, policy scopes and repair cases.

### Durable Improvement

The [canonical growth journeys](../design/synthesis.md#growth-journeys-and-boundary-evidence)
now own those comparisons and the typed/unknown/effect expectations. Existing
target fixtures, research routes, registry and boundary map were updated. The
frontier plan decomposes implementation with removal and verification gates.
No new language law, runtime change or process automation belongs to this pass.

### Next Pass

When the fresh implementation session begins, compare the closed monomorphic
contract with an independent client consumer, unknown-dependency refusal and
changed-source/dependency cases. Reconcile the known continuation failures before
relying on hosted execution. Keep all three journeys visible. This pass is
self-reviewed planning; no independent reviewer, target typechecker or human
study was run. Final document checks are recorded in the current checkpoint.

## Bounded Scalar Continuation, 2026-10-09

The strategy committed at `bc8f0c8` authorizes iterative calculation, report and
reuse work. This bounded pass accepts scalar meaning in
[semantics](../design/semantics.md#first-product-scalar-contract), records the
[decision](../design/decisions.md#first-product-scalars-october-9-acceptance), and
updates the [synthesis closure](../design/synthesis.md#bounded-closure-before-coding-the-target-slice).
The packet remains `designing`: callable, codec and host-run contracts are still
open. Target acceptance here is not a claim that the active overall fixture
parses, typechecks or executes.

### Evidence That Changed The Design

Independent read-only probes of the continuation baseline found more than an
invoice-specific failure. JS Core produced `"12"` for `1 + "2"`, `5` for
`7 - "2"`, `3` for `7 // "2"`, `1` for `7 % "2"` and `49` for `7 ** "2"`;
unary `+"2"` produced Int `2`. Public Python execution refused those operands.
Both routes already support `7 * "2"` as Text repetition; the repair must not
erase that separate compatibility operation through a blanket numeric guard.
Core nil plus Int also fell through to host coercion on JS.

Python and JS disagree on Bool/numeric equality and on Text ordering: Python
places U+1F600 after U+E000, while JS's UTF-16 comparison places it before.
Public Python checking admitted this Text comparison and `not 1`. These are
bounded type facts over host execution, not evidence of canonical portable
meaning. Initial target `true` and `none` sources parsed as names then failed
Python lookup; prototype Bool fixtures require explicit `True`/`False` labels.
JS exposes `.strip()` using host trim rather than the target `.trim()` contract.

The selected target is exact mathematical Int, distinct Bool, and Unicode scalar
Text with code-point units, exact equality and scalar lexicographic ordering.
The [golden vectors](../design/semantics.md#independent-scalar-vectors) separately
pin invoice edits, zero/negative arithmetic, integers beyond 53 and signed
64 bits, mixed operands, supplementary characters and invalid text. Checked
fixed width would add an arbitrary default overflow boundary while still needing
an exact browser representation beyond 53 bits. Exact Int therefore wins this
bounded product comparison; no speed, allocation or numeric-tower claim follows.

### Workflow Friction

The old closure table treated all scalar questions as one open comparison,
while implemented range refusal could be mistaken for the target's numeric law.
A JS-only fix could also wrongly remove valid Text repetition or advertise
typed Int boundaries that Python still executes using Bool arithmetic.
`known-types` records establish result types on normal completion, not exact
values, runtime capacity or an accepted public callable contract. Source
spelling and coordinate units need their own evidence rather than an inferred
claim from a passing Core vector.

### Durable Improvement

The existing semantic owner now has an explicit primitive table and independent
oracles. Target decision, runtime observation and remaining admission work are
separate. No new document, framework, syntax or test rewrite was required. The
following map identifies migration ownership; scheduling and actual check
receipts remain in the frontier plan and current checkpoint.

| Boundary | Current owner and migration obligation |
| --- | --- |
| Source and checking | `prototype/parser/` and `prototype/analysis/source.py`: accept canonical scalar spellings; align primitive/Bool facts without treating declarations or observed calls as proof. |
| Python execution | `prototype/runtime/backends/core_runtime.py` and the hosted interpreter layers: replace reliance on Bool's host numeric subtype, preserve exact Int and diagnose invalid operands at the semantic boundary. |
| JS evaluation and lowering | `prototype/runtime/js/core_runtime.js` and `lower_to_core_ir.js`: first remove reproduced coercion; then implement exact Int capacity, scalar text validity/order and Bool-only boundaries. |
| Internal wire | `prototype/syntax/core_json.py`, `prototype/runtime/backends/js_core.py`, JS lowering and result envelopes: introduce a planned versioned tagged decimal Int transport, validate payloads recursively and refuse unknown major versions before effects. No new version is currently specified or implemented. |
| External codecs | The forthcoming supported `std.json`/declared-data slice and `prototype/runtime/api.py`: preserve accepted integer values exactly, distinguish external JSON shape from internal tags/display, and settle integral decimal/exponent tokens with independent decode/encode vectors. |
| Source and run evidence | Runtime diagnostics, `prototype/runtime/js/worker.js` and the web host: preserve UTF-8 byte spans/source revision and convert explicitly to code-point or UTF-16 columns; record measured profile limits and capacity/budget refusals. |

Current Core JSON numbers and JS safe-integer refusal remain explicitly bounded
migration support. Planned recursive tagged Int transport is not yet a schema
contract or measured implementation. Common byte/depth/work/integer/output
limits, trim whitespace, strict JSON shapes and typed-call/source-surface
agreement remain pending. No budget number is invented to close this pass.

### Next Pass

Verify the reproduced coercion repair against public Python, Python-produced
Core/Node and committed WASM-produced Core with independent expected outcomes.
Then admit exact transport/execution, Bool/text/source boundaries and measured
capacity before claiming calculation target conformance. The report separately
needs explicit trim and strict codec closure. Existing Text repetition,
compatibility Bool behavior and unsupported scalar operations must remain
honestly classified during migration. Document/packet checks verify these edits;
they do not supply the missing runtime, browser, benchmark or human evidence.

## Report Planning And Gap Review, 2026-10-09

This continuation starts at `52deae4` and fulfills the request to deepen and
commit plans and gaps. The calculation delivery at `9d2f87d` is historical
bounded evidence; no new runtime or browser execution is attributed to this
pass. Existing uncommitted continuation changes remain outside its commit.
The packet stays `designing`.

The [report decision](../design/decisions.md#first-report-boundary-october-9-planning-decision)
and [semantic owner](../design/semantics.md#first-report-boundary-contract)
select the closed data rules. The [library proposal and admission gaps](../design/synthesis.md#report-library-experiment)
separate the lab's structural records from target nominal data and Result.
The active [overall target](../design/targets/overall.nomi) now calls the explicit
finite `trim_text` library operation instead of leaving host-like `.trim()`
ambiguous. The proposed `std.text` export is target-only.

### Evidence That Changed The Design

Reading the actual `prototype/runtime/decode.py` confirms that it contains
passive error records, not decoding. Its path renderer also lacks the proposed
`$` root and escaping, so reuse needs an adapter rather than relabeling existing
output. The provider inventory describes current callback-first collection
calls and supplied effect facts. Core value records alone do not establish
target immutable nominal ownership, distinct Unit/Option, or a checked library.

Reviewing the proposed report records exposes missing outer outcome and input
identity rules: the same `$` can refer to batch or options input. Parse-first
failure and bounded accumulated decode errors also need different completeness
explanations. Node/byte limits need accounting for supplied trees, shared
children, repeated calls and escaped output; row count cannot bound a run.
These findings add concrete admission gaps, not invented executed failures.

### Workflow Friction

The active queue still requested calculation implementation after its delivery,
and historical “next” instructions disagreed with the report handoff. A working
compatibility report could also have been mistaken for target completion because
the missing data/Result/callback/module steps were listed without delivery order.

### Durable Improvement

The existing roadmap now owns explicit report-to-target dependency gates; the
frontier plan has a current resume point and commit boundaries. Synthesis owns
the remaining decisions and literal prepared oracles, including exact report
JSON. The registry and numeric research route point to the same state. Manual
schema/outcome adapters have replacement triggers before they grow into a
parallel type system. No new planning document, agent rule or automation was
needed. The checkpoint records actual documentation validation separately.

### Next Pass

Close failure classification/completeness, path rendering, parser/encoder
lexical details and local budget accounting; materialize independent records
before implementing the closed libraries. Then settle two-input/outer-outcome
identity, adapt ordinary providers and deliver the source report. Target data,
Result, checked callbacks and local modules follow the roadmap gates; prepare
the scalar reuse producer/consumer comparison independently where possible.
Continuation compatibility still needs separate review and tests. Measured
capacity, full-suite health, human trials and hosted distribution remain open.

## Planning Closure Toward Synthesis, 2026-10-09

The follow-up instruction is to finish this planning line through synthesis.
The eight gap comparisons now have selected dispositions in
[synthesis](../design/synthesis.md#report-admission-gaps), with exact lab records,
lexical/encoding rules and capacity accounting. The
[literal handoff](../../prototype/tests/data/report_boundary/v1.json) contains
prepared expected results, not captured implementation output. The
[synthesis conclusion](../design/synthesis.md#october-9-planning-synthesis)
states what is ready to implement and the concrete triggers for reopening it.
The language-coherence packet remains `designing`; planning completion is a
bounded deliverable, not the packet's conformance status.

### Evidence That Changed The Design

Local probes on Python 3.14.0rc3 and Node 25.9.0 show why host JSON defaults
cannot supply the contract. Python's ordinary parse of duplicate `age` fields
keeps only the second value; its token/pair hooks preserve both entries and
their `9007199254740993` / `20.0` spellings. Node's ordinary parser rounds
`9007199254740993` to `9007199254740992`, keeps only the last duplicate field,
and turns `20.0` into Number 20. A bounded scanner is selected to preserve these
facts and enforce early limits consistently; a hook adapter remains replaceable
if it later supplies the same evidence and limits. No scanner was implemented
or benchmarked by these probes.

Record review selected stage-scoped completeness and options-first entry
validation. Lossless paths can themselves exceed output budgets, so the plan
now specifies explicit diagnostic refusal rather than truncating authoritative
paths. A single run-owned boundary allowance closes resettable-call and shared-
graph loopholes; this is still distinct from general source-execution limits.
The limits are unmeasured settings, with a concrete measurement protocol.

The earlier pending continuation work was separately completed at `e4209c8`.
Its 258 focused and 3,392 full-suite passes plus real default/legacy browser
checks refresh implementation health; they do not validate report libraries.

### Workflow Friction

The previous plan named the right questions but still required the next agent
to invent failure/completeness, options identity and accounting while coding.
Repeated “commit the plan, then decide” instructions also obscured the fact
that the requested planning deliverable could itself reach completion.

### Durable Improvement

Existing canonical owners now contain selected decisions and rejected
alternatives. Literal JSON fixtures make the handoff inspectable without
requiring a prototype decoder. The roadmap, frontier brief, registry and
checkpoint distinguish completed planning, verified compatibility and pending
target implementation. No new agent process or parallel planning document was
needed. Final planning checks are recorded in the checkpoint.

### Next Pass

Implement the two closed boundary libraries and consume the literal expectations
in real conformance tests; extend them with the listed limit, graph and adapter
cases. Then integrate ordinary providers and the options-first source report,
followed by real repair/export, target extraction and checked local reuse.
Measure capacities before publishing support limits. Human and hosted release
evidence remain separately scheduled. Further global planning is not a
prerequisite; reopen only against the stated concrete counterexamples.

### Boundary Library Checkpoint, 2026-10-09

The first executable library slice now exists in
`prototype/runtime/report_boundary.py` and
`prototype/runtime/js/report_boundary.js`, registered as ordinary Core host
calls and included in the browser worker's runtime load order. Both sides ran
the standalone applicable vectors from the prepared literal fixture: 20 Python
cases and 21 JavaScript cases, with the JS safe-integer profile applied only to
JavaScript. This verifies that this small set of recorded examples agrees with
the fixture; it does not establish full library conformance.

The slice preserves JSON number tokens in the value tree, rejects decoded
duplicate keys, keeps options default provenance, validates the two closed
descriptors, emits sorted deterministic JSON, and shares an evaluator-owned
input/work/output allowance across calls. Python retains arbitrary-precision
integer decoding; the JavaScript descriptor refuses integers beyond its exact
safe range. The generated web manifest now includes the added modules.

The experiment remains incomplete. The fixture's `build_report` cases are not
implemented; public Python execution and the options-first source report are
not connected. Nested duplicate-key diagnostics currently need path fidelity,
and the complete target accounting still needs enforcement for diagnostic
serialization bytes, diagnostic byte fallback, all shared graph/resource
edges, and precisely counted validation work. Cross-runtime tests cover the
prepared standalone vectors only; add malformed supplied-tree, depth/node/work
boundaries, 64/65-error, alias/cycle adapter, and repeated-call budget probes.
The actual browser worker quick tour and legacy Pyodide quick tour, pipeline and
call-boundary smoke checks pass. Measure pinned hosts against the provisional
capacities and record any unsupported route as refused. The next step is to
finish those boundary cases and gaps before wiring the ordinary source report
and its explicit encode/save stages.

## Report Compatibility Completion, 2026-10-10

The continuation instruction advances the selected planning handoff to the
bounded implementation at `8081e93`. This supersedes the incomplete October 9 library
checkpoint: the closed libraries, ordinary providers, source-owned report and
actual default-browser repair/JSON download now have independent evidence.
The canonical laws remain unchanged; no syntax or whole-report builtin was
admitted. Exact counts, pinned measurements and route limits are in the
[completion receipt](../orientation/frontier_checkpoint_2026-10-08.md#report-compatibility-completion-receipt-2026-10-10).

### Evidence That Changed The Implementation

Independent negative probes first exposed nested duplicate paths, null/missing
confusion, depth/node/work accounting, truncation/completeness and numeric
conversion leaks. Token-preserving scanners, strict supplied-tree validation
and bounded writers now meet the selected records. A 129-row batch is a
cardinality constraint with suppressed child validation; an observed 65th
error instead makes the first 64 incomplete. Resource/numeric refusals discard
earlier schema errors and stop, while diagnostic overflow becomes an explicit
root refusal. Shared acyclic occurrences charge again and decode independently.

Ordinary source exposed two integration defects: Python's lazy callback-first
collections require explicit strict materialization, and WASM branch conditions
need balanced, quote-aware raw accessor lowering. The source and producer
contracts cover those cases without changing the target data-first library
contract. Explicit boundary boxing also prevents an outcome's ordinary `kind`
field from being mistaken for a runtime tag. Final adapter probes reject
foreign tag-shaped objects, getters, symbolic fields and malformed storage.
They do not establish a sandbox for arbitrary native proxies.

Real browser scenarios verify two-field repair, current revision identity,
exact downloaded bytes and report preservation on encoder/download-initiation
failure. Local capacity probes identify Python/Node/Chromium versions and source
digests; counters and different memory measures are explicit. Browser peak
memory and representative supported-capacity validation remain unavailable.

### Workflow Friction And Durable Improvement

The first committed library checkpoint passed a small set of prepared examples
while leaving the public source path disconnected. Running independent edge,
graph, adapter and producer tests before broader checks made its remaining gaps
concrete. The new report sample is the single runnable source owner, reused by
contracts, CLI, regressions and actual browser scenarios. Existing runtime
checks and the design-pass registry now include those durable surfaces; no
parallel specification or new agent process was needed.

### Next Pass

The October 10 user direction now selects the
[user-facing readiness pass](../orientation/project_roadmap.md#user-facing-readiness-audit):
start with documentation, then audit browser, CLI, editor/notebook, and
distribution. The integrated guide and actual host/artifact probes now expose
an older published playground and specific onboarding, presentation, engine,
and packaging gaps. Record them before the
[next fixing pass](../orientation/project_roadmap.md#next-fixing-pass-order).
The bounded report completion closes this compatibility continuation; it does
not close the target-language packet.

For target-language implementation, follow the roadmap's target scalar, nominal
construction/derived decoder, Result/match and checked callback gates. Prepare the closed source-derived
`maximum_batch_size`/subtotal evidence comparison with two passive consumers;
checking must not run bodies, imports, defaults or annotations. Keep unknown
facts unknown and source/contract/verification identities separate.
The compatibility sample still edits JSON inside source; separate input/options
revision/persistence/navigation controls, checked local module reuse, user
trials and exact release validation remain open. The packet stays `designing`.

## Broader Vision Revision, 2026-10-10

**Evidence That Changed The Design:** the user's broader direction establishes
the [computational-medium vision](../design/vision.md) as the guiding purpose.
The first-product profile is an experiment toward it, not a boundary on research.
Creation, explanation, evolving models, multiple representations, collaboration
and delegation can challenge current source/core/library assumptions.

**Workflow Friction:** interpreting a closed implementation dependency as a ban
on earlier discovery would make the current prototype determine the target.
Conversely, broader ambition alone supplies no scalar, callback or module proof.

**Durable Improvement:** the existing agenda, research method and roadmap now
distinguish discovery from semantic promotion and delivery. The vision records
current gaps and contrasting pressure activities without creating another
implementation queue. Existing report laws, literal fixtures and packet statuses
are unchanged; no target-only source was moved into runnable samples.

**Next Pass:** advance actual target meaning and checked reuse while investigating
the growing model's creation/revision/handoff and a contrasting creative or
scientific activity. Allow the evidence to revise the model and schedule. Use
the cognitive packet's [direction retrospective](2026-09-30-cognitive-interfaces.md#whole-system-vision-continuation-2026-10-10)
for discovery scope and the roadmap's existing target gates for implemented claims.

## Maintainer Language Research Continuation, 2026-10-10

### Pass Retrospective

#### Evidence That Changed The Design

The user's next direction is a research/synthesis pass for the developer,
maintainer, and designer before deeper language choices. Primary documentation
now expands Wolfram, Haskell, Scala, Kotlin, Rust, Julia, and TypeScript across
several composing mechanisms; Mojo fills a genuinely missing review. The
[maintainer synthesis guide](../research/synthesis_guide.md) brings those routes,
a candidate worksheet, whole-program cases, depth gaps, and integration rules
into one entry point. Python/Cython/Codon/PyPy and OCaml/Lean provide bounded
adjacent leads without adding unreviewed full matrix columns.

The evidence sharpens the existing owners for operation selection, representation
and aliases, stages/binding, numeric transformation laws, and definition visibility.
No new target feature was accepted. The exact default Int closure was reconciled
with stale numeric research; the representation question now permits a direct
text/structured comparison in line with the broader vision.

#### Workflow Friction

One-mechanism language summaries made deeper integration questions hard to find.
Mixing compiler checking, library conventions, runtime behavior, and unexecuted
experiments would make the synthesis overclaim. Moving documentation also needs
version scope: Haskell 2010 and GHC 9.12.2 are distinct, Mojo evidence is from
consulted 1.1.0 docs, Scala capture/separation checking is experimental, and
Julia's version-specific world-age binding changes are fenced.

#### Durable Improvement

The new guide consolidates the repeatable research loop instead of introducing
a separate backlog. Five existing feature owners carry the new comparisons.
Language indexes, the exact semantic transpose, syntax matrix, complete document
inventory, open questions, and registry routes agree on 45 language reviews and
13 feature categories. Existing checks enforce that coverage; no new validation
framework or agent instructions were needed.

Verification at this checkpoint: 130 focused matrix/document/packet/target checks
passed; all five registered packets passed integrity validation; 2,094 local file
links across 164 documents resolved; `git diff --check` passed. These are
repository coherence checks. The new foreign-language cases and user activities
remain prepared, and no compiler comparison, benchmark, Nomi semantic checker,
or human study was executed by this pass.

The second review makes the guide's evidence surfaces explicitly independent,
adds literal evaluation and behavior-selection pilots, deepens Wolfram's delayed
rules/live expressions and Haskell's carrier laws, and routes OCaml's one-shot
handler lead through the existing effect owner. The callback pilot preserves
different complete traces even when both candidates fail with the same error.
This strengthens the prepared oracle; it is not a newly executed experiment.

Final documentation verification: 137 focused checks passed; 2,103 local file
links across 164 documents resolved; all nine heading links in the maintainer
guide resolved; the registered packet remained coherent; `git diff --check`
passed. The local retrieval index was rebuilt for discovery of the new guide
and comparisons; a search located the guide and all 18 agent-doctor checks passed
after the rebuild. None of these
checks establishes the proposed dispatch, type, stage, or resource semantics.

#### Next Pass

Review the guide's interaction matrix and select one concrete synthesis
comparison after the user considers the alternatives. Start from its explicit
value/call baseline and independent expected observations. Operation-value versus
protocol/multimethod selection is a bounded first option; symbolic theory/staging
or scientific buffer ownership are independent alternatives. Preserve existing
question and packet ownership. Promote only the settled contract through design,
ledger, whole-program target, and a reversible implementation bridge. The packet
remains `designing`; broader target implementation and distribution work retain
their existing readiness gates.

## Primitive Composition And Gap Path, 2026-10-10

### Evidence That Changed The Design

The user requests broader coverage and a concrete coherent integration path,
then a data-platform focus. The synthesis now compares six semantic families:
Value, Bind, Apply, Choose, Perform, and Scope. Its feature composition map retains
checks for lifetimes, control completion, scheduling, authority, and numeric theory.
The maintainer guide adds eighteen corner cases and fresh primary leads for
variance, erased trait interfaces, equality/hash coherence, and cooperative
cancellation. These are proposed cases and a designing model, not accepted IR.

### Workflow Friction

A tiny encoding can hide required laws, and a broad feature taxonomy can avoid
answering which contract to close next. Calling everything a function would not
establish resource release, lawful fusion, or observational equivalence. A source
schema can support a statistical plan without providing actual observations;
that does not establish the observations' validity or every numeric identity.

### Durable Improvement

The canonical synthesis now owns the primitive model, feature reductions, gap
receipts and ordered path through D0-D7. The guide owns prepared counterexamples;
the agenda and interaction proposal route to the same path. Existing packet
owners and release scheduling remain intact. Repository coherence validation
covers the changed documents; no source grammar or runtime behavior was changed.

### Next Pass

Focus on the user's statistical/data-platform interface: typed lazy plans,
referable intermediates, schema-only checking, explicit statistical-object
families, and exact mean decomposition with stated missingness, empty-input,
weight and representation laws. Start with a removable interface/checking model,
then compare pinned engine adapters. Preserve conditional/unknown proof results,
and do not introduce a dataframe engine or claim universal statistical proofs.

## Statistical Interface Fragment, 2026-10-10

### Evidence That Changed The Design

The selected continuation now has an executable engine-free interface rather
than only aspirational dataframe calls. Its schema-only example names a filter,
nullable difference, sum, valid count, row count, mean, expansion and alias.
The exact mean expansion is established by a closed definitional rule; row-count
and Float64 variants remain unknown. Primary Polars evidence shows schema
resolution can perform I/O; Ibis provides unbound descriptions as an existing
precedent. R/dplyr and Substrait expose policy and state boundaries to retain.

### Workflow Friction

Schema-only correctness, definitional equality, physical backend conformance and
scientific validity are different questions. A catalog cannot imply distribution
or fitting support. A numeric countermodel initially assumed Python `sum` was
a naive float fold; Python 3.14.0rc3's result disproved that assumption. The test
now explicitly contrasts a left fold with `math.fsum`, without making an engine
claim. Named references should survive fusion without forcing materialization.

### Durable Improvement

`statistical_data.md` owns the designing contract and data-only closure path;
`statistical_objects.md` owns primary evidence and discriminators. The catalog
distinguishes seven implemented fragments from eighteen catalog-only families.
The isolated tool checks graph/schema/domain contracts, passively inspects every
node, emits a context-qualified mean-law receipt and refuses forged or stale
receipts. It neither binds data nor executes an adapter. Thirty-six new tests
include 85 finite exact sequences as an independent soundness discriminator.
Combined focused validation passed 173 tests; 2136 local links across 166
documents and all five design packets were coherent; Ruff passed.

### Next Pass

Expose a normalized expression/theory artifact for independent replay, then
extend the exact paired-moment theory with units and denominator policies. The
broader catalog contracts still need typed specialized ports and scientific
obligations before their operators can be admitted. Backend execution and Nomi
source/package admission remain separate. The packet stays `designing`.

## Independent Replay And Statistical Descriptors, 2026-10-10

### Evidence That Changed The Design

A second consumer now reconstructs the exact graph and verifies the mean-law
receipt without importing the planner or its type inference. Its equality test
uses structurally interned terms, not matching supplied hashes. Both consumers
refuse numeric-definition changes without a supported theory revision. The
descriptor catalog now has 35 families, typed reference ports and inert
parameter shapes. A named Normal model/fit description remains unbound with
unresolved scale and population assumptions.

### Workflow Friction

Descriptor shape, expression typing and scientific validity need different
success statuses. Captured finite countermodels show invalid matrix-wide
correlation despite valid local pairs, wrong weighted domains, positional versus
labeled alignment and join-induced double counting. The descriptor context
addition briefly reused a loop variable for catalog metadata; focused checks
caught and corrected that implementation error before checkpointing. The current
wire receipt still conservatively invalidates on manifest-order/catalog changes;
semantic revision identity needs a later narrower dependency contract.

### Durable Improvement

The canonical statistical proposal owns one extension route through catalog
ports, specialized validators, closed laws, independent evidence and adapter
admission. The research dossier adds deeper primary R formula/distribution/
matrix and pandas/Polars context evidence. User-facing navigation routes to the
research tool with an explicit source-checkout boundary. All 35 families can
name and inspect descriptions; catalog-only objects still cannot execute.
Combined focused validation passed 210 tests, including 73 new data-interface,
replay, descriptor and finite-countermodel cases. Ruff, five packet checks and
2142 local links across 166 documents passed. No language grammar, interpreter,
browser runtime or real statistical execution engine was changed.

### Next Pass

Keep the next work solely within the data path: specialized semantic validators,
units, paired-valid exact moments and denominator policies. Then close group/
window/alignment/cardinality contracts and richer model/inference obligations
before selecting one pinned backend. Independent exact replay is delivered;
formal verification, arbitrary laws, floating guarantees, fitting and scientific
assumption validation remain open. The current descriptor and proof artifacts
are removable research surfaces, not accepted Nomi public package contracts.

## Engine-Free Foundation Correction — 2026-10-10

This continuation supersedes the preceding data-only next action. The user
clarified that objects themselves should be independent of engines and that
data/statistics should adapt a generic framework. Laziness alone does not
provide description, contract, identity or realization independence.

### Evidence That Changed The Design

The unfinished units/moments branch would have specialized the object model
before establishing the common boundary. Its two untracked local draft modules
were removed; no committed statistical behavior was changed. The new
[framework](../design/object_framework.md) and `tools/object_interface/` implement
nominal families, typed named ports, abstract inputs, literals, aliases, pure
closed definitions and inert descriptions. Arithmetic and text execute through
an explicitly chosen adapter; document descriptions remain useful without a
renderer. References identify graph revisions, and results do not mutate objects.

The statistical adapter derives 35 description families and preserves all
example IDs, ports and parameters after the existing domain validator. It
does not pretend that generic composition checking validates scientific
assumptions or replaces the specialized computation/proof checker.

### Workflow Friction

The prior navigation and registered next actions directed every continuation
straight into statistics. They now start with the generic foundation. Testing
also identified a domain leak: repeated references in a many port are valid
generic composition, while the statistical descriptor validator retains its
own stricter distinct-reference checks.

### Durable Improvement

The new canonical owner, top-level navigation and registry distinguish object
description, checking, comparison, compilation, binding and execution. Structural
term interning and memoized definitions keep diamond expansions bounded. Backend
callbacks run only during explicit execution; data and result snapshots remain
detached. Effectful objects retain identity and are refused by the pure executor.
Validation passed 139 focused tests: 62 new framework/adapter cases, 73 existing
statistical cases and four documentation lifecycle checks. Ruff and 2152 local
file links across 167 documents passed. No parser/interpreter/browser change or
statistical engine installation was made.

### Next Pass

Compare a domain refinement/obligation protocol and an independent generic
consumer before broadening the envelope. Then adapt a statistical computation
fragment while preserving grain, missingness, exact theory and independent
v1 replay. General algebra, effectful realization, parameterized type checking,
scientific validity and Nomi source admission remain distinct gates.

## Independent Object Replay Continuation — 2026-10-10

### Evidence That Changed The Design

`Graph.verify` is a useful self-check, but it imports the same rules as the
producer. `tools/object_replay.py` now independently reconstructs the pinned
lab vocabulary's nominal types, aliases, square/double definitions, structural
terms and full graph context. It imports only the standard library and succeeds
when planner construction/comparison are replaced with failing functions.
Changed definitions require new independent admission rather than being trusted
as supplied claims. This is a separate consumer, not formal verification.

### Workflow Friction

The domain-neutral framework needs separate admission scopes just as the
statistical checker does. Replaying an arbitrary vocabulary would otherwise
let unreviewed metadata choose the consumer's trusted theory. The new consumer
pins one complete vocabulary and refuses unsupported revisions. It validates
disconnected nodes too, so an unrelated malformed description cannot ride
along with an apparently valid comparison.

### Durable Improvement

Twenty-six new replay cases exercise independent imports, planner-free replay,
identity/alias/definition evidence, forged receipts, altered source/type/port
records, changed vocabulary and the CLI JSON boundary. The framework owner
and packet checks now include the independent consumer and export/replay route.
Backend correctness remains separate from composition equivalence.
Five additional edge cases cover unnamed lowered-operation origins,
mid-operation cancellation, backend mapping isolation, undeclared algebra and
expanded-term capacity. Construction and binding now validate their detached
snapshots. Combined framework/statistical/packet validation passed 293 cases;
Ruff, the five packet checks and 2161 local links passed.

### Next Pass

Establish a domain refinement/obligation protocol with one numeric and one
non-numeric witness. Then adapt statistical computation contracts while
preserving existing independent mean-law replay. Broader vocabulary admission,
general parameterized types, effectful realization and user-facing Nomi package
integration remain open; no data engine is needed to investigate the next step.

## Engine-Free Obligation Protocol — 2026-10-10

### Evidence That Changed The Design

Nominal composition alone cannot say whether an input satisfies a domain
precondition. The new `Requirements` artifact gives named obligations their
own owner/revision, graph context and satisfied/refuted/pending evidence.
Positive ExactInt and nonempty Text supply numeric and non-numeric witnesses.
Only literals, literal aliases and explicitly supplied input snapshots can
discharge these two predicates. Computed expressions remain pending rather
than invoking an engine during checking.

### Workflow Friction

Treating a supplied status as proof would weaken the boundary; accepting a
pending computed precondition before execution would claim an unenforced
contract. Both are refused. Conditions attach explicitly to a compiled
realization, and invalid input stops binding before backend callbacks run.
An unrelated or stale obligation cannot be attached to another graph/result.

### Durable Improvement

The framework now preserves static and binding evidence separately in a
realization receipt. Diagnostics name failed condition IDs. A pending receipt
can be replayed as pending; replay never changes its verdict to satisfied.
The CLI supports passive obligation checks and explicit required execution.
Nineteen new cases exercise both domains, literal/alias evidence, pending
computed subjects, callback-free refusal, scope, tampering, type boundaries
and the CLI. These are closed representation predicates, not scientific
assumptions, a general solver or accepted Nomi constraint syntax.
Combined framework, existing statistical and packet/documentation validation
passed 312 cases. Ruff, all five packet checks and 2163 local file links across
167 documents passed. The guarded CLI example returns the same exact/text
values with separate static and binding evidence; no data engine was added.

### Next Pass

Preserve richer domain payloads through the common envelope and admit separate
refinement consumers. A statistical computation adapter should reuse graph
identity/inspection while retaining domain masks, schemas, numeric theory and
the existing independent v1 proof boundary. A documentary witness should test
requirements beyond text length before the shared protocol is generalized.

## Independent Obligation Evidence — 2026-10-10

### Evidence That Changed The Design

The object consumer now independently admits the two initial predicates as
well as composition definitions. It reconstructs source types, alias/literal
evidence, supplied input slots, rule identity, graph/requirement contexts and
the actual verdict without importing `Graph` or `Requirements`. Verifying
pending or refuted evidence preserves that verdict; it cannot authorize a
required realization that lacks satisfied input conditions.

### Workflow Friction

Source validation was duplicated when adding a second receipt kind. The
independent consumer now shares its own source reconstruction between
composition and predicate replay, while remaining independent of producer code.
Binding evidence requires an explicit requirement artifact, preventing CLI
flags from being silently ignored or interpreted as computation results.

### Durable Improvement

Twenty-four new cases cover all three verdicts, planner-free replay, forged
truth/status/phase/binding claims, changed rules, invalid nominal bindings,
literal aliases, unresolved computed subjects and the independent CLI.
The canonical owner and registered checks include the separate evidence route.
No predicate execution or data discovery was added to object inspection.
Final combined validation passed 336 focused cases; Ruff, all five design
packets and 2163 local file links passed. The original statistical tests remain
unchanged and passing. The broader interpreter/browser suites were not needed
for this isolated, source-checkout artifact framework.

### Next Pass

Test a richer documentary or schema refinement through this protocol before
admitting another generic predicate. Preserve specialized domain contracts and
their independent consumers when adapting statistical computation. The current
generic foundation is runnable and remains a removable library/artifact
experiment rather than a source-language semantic commitment.

## Composable Structural Object Contracts — 2026-10-10

### Evidence That Changed The Design

A shallow record codec could accept a document-shaped dictionary while missing
every section/paragraph contract. Closed record fields and array item codecs
now compose within the generic envelope without a data or rendering engine.
Binding, literal and output boundaries accumulate independent original paths
instead of stopping at the first nested mismatch. Missing/null/empty and
nominal family distinctions remain separate.

### Workflow Friction

The CLI discarded structural details when presenting a contract exception.
It now returns stable path/code/expected errors and completeness. Bare record
and array codecs keep their existing meanings, avoiding a silent change to
statistical description metadata or the independently pinned v1 vocabulary.

### Durable Improvement

Twelve new cases cover nested composition, exact failure paths, no defaults,
detached error reports, invalid/cyclic schemas, 128-error capacity, shallow
compatibility and codec/nominal round trips. The structural codec owner and
registered checks make its limited promises explicit; no predicate or host
callback is run during shape validation.

### Next Pass

Add obligations on declared nested parts, then use a document specification
with an explicit render request to challenge nominal boundaries and independent
consumer admission. Keep schemas separate from meaningful domain constraints.

## Documentary Composition And Nested Obligations — 2026-10-10

### Evidence That Changed The Design

A document specification now composes required fields and ordered items without
an engine. A version-2 obligation selects a declared path and checks a closed
predicate. Empty structured drafts stay valid while explicit publication
conditions can remain pending or be refuted. Rendering is a distinct typed
request, followed by an explicit conversion to Text.

### Workflow Friction

Every intermediate was referable in Python but the CLI could execute only the
default outputs. Repeatable `--output` now makes selected realization available
without editing an artifact. Path conditions remain deliberately limited: an
indexed condition is not an all-items assertion, and computed subjects cannot
be made static evidence by supplying their inputs.

### Durable Improvement

Twenty-two new cases challenge nested paths, absence, nominal conversions,
pre-callback gates, detached evidence and two renderer profiles against expected
outputs including Unicode, embedded newlines and empty parts. All 65 selected
new/obligation cases and Ruff passed; original v1 receipts and tests are intact.
The domain profile is separate from the original vocabulary fingerprint.

### Next Pass

Independently admit the document vocabulary and version-2 path evidence before
claiming replay for this richer domain. Then distill the documented language
into a dependency hierarchy, naming reductions, operational laws and unclosed
gates instead of treating the framework's six roles as language primitives.

## Independent Documentary Admission — 2026-10-10

### Evidence That Changed The Design

The independent consumer now separately pins the documentary vocabulary and
owns its nominal port and nested-value checks. Version-2 evidence reconstructs
declared paths, missing indexed values and closed predicates, retaining each
original verdict. This proves the bounded protocol can carry a richer domain
without assuming a renderer or reusing producer inference.

### Workflow Friction

The first consumer inferred every port family from its result family, which
fails for document projections and explicit rendered-text conversion. Reviewed
per-operation port requirements now preserve those distinct domain meanings.
Editing a supplied vocabulary still cannot install new trusted rules.

### Durable Improvement

Nineteen new cases cover all three verdicts, forged scope/phase/path evidence,
changed codecs, invalid unselected nodes, deep binding rejection, nominal
aliases and pending computed subjects. A fresh isolated process rejects every
producer import while replaying a documentary receipt. All 69 selected replay
cases and Ruff passed; original consumer receipts remain unchanged.

### Next Pass

Use this evidence to separate reusable framework mechanisms from semantic
language primitives. Build the requested composition hierarchy with owners,
operational laws and explicit residual gaps; do not infer a universal IR or
source-language acceptance from successful library experiments.

## Primitive Composition Hierarchy — 2026-10-10

### Evidence That Changed The Design

The user asked to approach the coherent language from its primitives upward.
The canonical hierarchy now connects six candidate semantic families to 56
compositions spanning source constructs, operational boundaries, domains and
interaction tools. Every composition retains a law and an unclosed gate.
Worked reductions expose evaluation order, lexical return targets, accumulated
errors, completion policy, domain-qualified equality and owner-checked edits.

### Workflow Friction

A compact formula could hide exactly the facts it was meant to explain.
The hierarchy separates semantic families from machine opcodes, contracts from
runtime branching, navigation from proof, and domain laws from representation.
The catalog includes validation/tooling ingredients; its closure cannot be used
to infer the effect set of the subject program.

### Durable Improvement

A declarative catalog and passive inspector expose dependencies by DAG depth.
Validation rejects cycles, unknown dependencies, missing/escaped owners,
unmapped target files, candidate-root acceptance claims and stale documentation.
All 25 current target-suite programs have declared routes; that does not prove
construct or semantic completeness. Nineteen validator cases and 127 existing
documentation/packet/target cases passed, alongside Ruff, five packets and
2250 local links across 168 documents. Entry points now route to one hierarchy.

### Next Pass

Use the hierarchy to implement a parameterized multi-output engine-free
workflow, instantiated twice with explicit reference arguments. Preserve
nominal families, source identities, conditions and independent replay while
avoiding a new execution primitive or implicit sharing. Source-derived report
contracts and later operational/domain gates retain their existing owners.

## Reusable Engine-Free Graph Workflows — 2026-10-10

### Evidence That Changed The Design

The primitive hierarchy exposed reuse as reference substitution, retained
identity and contract composition rather than another executor primitive.
A multi-output workflow now declares its complete abstract interface and
expands into an existing checked graph. Namespaced intermediate objects remain
referable. Explicitly repeated reference arguments share inputs; separate input
identities do not become equal through type or name similarity.

### Workflow Friction

Reusing the graph alone would discard separately carried conditions. Composing
the previous instance now transfers its conditions into the appended graph's
context and adds the new namespaced conditions. Component inspection retains
the original requirement owner/revision/context; the combined artifact has an
explicit composition owner. Compilation through the instance attaches all
conditions and refuses a selection that drops a required subject.

### Durable Improvement

Twenty-six new cases cover two instances, explicit sharing, foreign revisions,
wrong nominal arguments, collisions, conditions from both instances, deep
documentary paths, independent expanded-graph replay, literal refutation,
pending computed arguments, ordered repeated ports, parameter-free templates
and aggregate graph limits. All three documented Python examples execute.
The catalog now includes a dedicated graph-workflow composition; durable
workflow/persistence semantics remain a separate open domain.

### Next Pass

Independently replay template substitution and carried-condition composition
itself, rather than using expanded-graph validation to claim that proof. Then
compare authoring and repair against inline graphs, and select one cross-object
relation with an owned rule before broader quantified domain validation.

## Independent Workflow Substitution — 2026-10-10

### Evidence That Changed The Design

An expanded graph can be valid yet contain the wrong reference substitution.
The independent consumer now reconstructs every supplied workflow instance from
the original base graph, explicit definitions and checked reference arguments.
It compares the exact expanded graph, selected outputs, namespace identities,
source condition provenance and combined conditions. This closes a different
claim from graph typing or predicate replay; it neither infers user intent nor
executes an implementation.

### Workflow Friction

Raw JSON definition files and canonicalized producer documents exposed an
output-order disagreement that in-process round trips missed. Export ports now
have explicit canonical name order in the consumer and documentation. Expanded
bundles also enforce the aggregate artifact byte limit instead of relying on
separate graph/inspection limits.

### Durable Improvement

Twenty-three new cases challenge lost conditions, forged satisfied/realized
states, stale provenance, wrong but type-correct substitution, nominal argument
errors, namespace collisions, unchecked definitions and ambiguous CLI modes.
A fresh isolated process refuses producer imports and verifies two instances
with pending conditions. The original scalar/documentary consumers still use
their independently owned inference; no shared producer normalizer was added.
Final combined validation passed 457 focused cases, including the original
statistical contracts and all documentation/packet/target checks. Ruff, five
design packets, the 63-node hierarchy and 2253 local links across 168 documents
passed. All four documented Python examples and the independent workflow CLI
replay executed. Parser, interpreter and browser semantics were not changed;
their broader suites were not needed for these isolated artifact/tooling changes.

### Next Pass

Compare inline and reusable authoring/repair using the same contract and task.
Select a bounded cross-object relation only after identifying its owner and
independent rule; fixed paths cannot stand in for quantification. The generic
framework is ahead of the statistical adapter, while source-language admission,
operational scopes, physical engines and human outcomes remain open.
