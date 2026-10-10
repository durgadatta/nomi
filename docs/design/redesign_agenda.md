# Design-First Redesign Agenda

> Status: active design agenda; recommendations and unresolved forks, not acceptance.

This is the live cross-cutting agenda following the
[language synthesis](synthesis.md), [cognitive research](../research/cognition.md),
and [interface proposal](interaction_model.md). It asks what matters when
designing a language now, without assuming contemporary tools are the answer.
The [redesign frontier research](../research/design_frontiers.md) checks typed
holes, higher-order effects, bidirectional laws, incremental artifacts,
coordination, synthesis, Unicode, and runtime budgets against primary evidence.
Existing accepted contracts remain in [syntax](syntax.md),
[semantics](semantics.md), [industrial](industrial.md), and [decisions](decisions.md).
The [dated audit](../review/2026-09-30-cognitive-interfaces.md) is evidence, not
a second live backlog.
The [Project Enhancement Roadmap](../orientation/project_roadmap.md) schedules
language closure alongside runtime, product, verification and maintenance work.
This agenda continues to own D0-D7 and the semantic questions below.

## Vision Sets The Agenda

The [computational-medium vision](vision.md) guides the language and environment
together. D0-D7, the current research taxonomy and the first-product milestones
are working organization. They must change when broader evidence exposes a
missing concept or a better route. They do not restrict exploration to ideas
that fit the current code, report workflow or small-core preference.

Run discovery alongside delivery. Observe how people create, explain, negotiate,
delegate and maintain computational work; investigate unfamiliar activities and
competing representations before all compiler contracts close. A useful research
lead may begin with a question rather than an already failing target program.
Record the lead's limits, then develop concrete comparisons before promoting it.
Admission of executable meaning remains a separate obligation.

The following questions extend the existing dimensions rather than assume
their present decomposition is complete:

| Broader question | Consequence to investigate | Current routes, subject to revision |
| --- | --- | --- |
| How does a person discover the model before they know its vocabulary? | Examples, demonstrations, domain objects and alternative starting representations; cost of premature abstraction | Human intent, partial programs, interaction; cognitive research |
| What is being claimed about the world, and what evidence supports it? | Navigable assumptions, measurements, derived facts and uncertainty; correctness within a model versus fitness of the model | Proof/evidence, numbers, data identity; domain composition |
| Which computational model exposes this activity's useful structure? | Functional, relational, constraint, temporal and stochastic candidates; domain laws and composition costs | Meaning, logic/search, time, scoped tools |
| How does understanding survive handoff and changed requirements? | Decision context, competing goals, semantic conflicts and explicit responsibility | Change/history, governance, AI collaboration; team cognition |
| How can a learner invent something beyond the supplied examples? | Diverse outcomes, concrete-to-abstract transitions, discoverable concepts and independently created work | Human intent, accessibility, interaction; construction and learning |
| Which assumptions about source, core and tools should be replaced? | Text/structured/mixed authoring, library/scoped/core placement and architecture comparisons | D4-D6; no candidate protected by implementation investment |

## Design Before Implementation

Do not equate a large bibliography with a settled design. "Reasonably designed"
means a bounded vertical program can be explained consistently across source,
types, constraints, effects, time, failure, formatting, diagnostics, and host
profile. Implementation can then challenge that contract without defining it.
The whole next-generation language is not settled by this pass.

Use three recurring programs: a beginner invoice, a boundary-heavy import/report,
and a cancellation/resource-heavy job. Add a symbolic scheduling model and
multiplayer/editing scenario as challenger programs when the ordinary language
fails them. The [target suite](targets/README.md) is the source pressure set,
not a claim all proposed APIs typecheck.

## What A Language Must Decide

The table is an agenda of questions, not a feature wish list. "Owner" points to
the single live contract/question family; detail should move there rather than
be copied into this document. Challenger topics extend those families unless
three real programs justify a new registered packet.

| Dimension | Question and credible fork | Evidence/deliverable | Owner |
| --- | --- | --- | --- |
| Human intent | General-purpose script-first versus domain/projection-first entry | Compare invoice creation/revision/review; name audience and exclusion costs | interaction model |
| Meaning | Operational core alone versus additional inspectable denotational/plan models | Laws with purity, termination and numeric side conditions; no hidden alternate evaluator | semantics |
| Binding | Value/cell capture, shadowing, symbol identity across edits | Closure and rename cases; tentative/commit trace | semantics, open question 1 |
| Types | Dynamic exploration and selected restrictions versus stronger whole-program inference | Checked public contracts inferred or declared; honest unknowns; generalization/annotation costs | semantics, questions 2/3/10 |
| Polymorphism | Nominal protocols, generic bounds, effect variables versus broad dispatch | Type three collection/codec/resource callbacks and conflicting extensions | function contracts, questions 3/10 |
| Proof and evidence | Runtime contracts/tests versus optional proof-carrying refinements | Distinguish proof, witness, test and assumption; annotate what was actually checked | constraints and tooling |
| Failure | Ordinary typed errors versus abnormal completion; conversion/composition | Failure-heavy target, all causes, accumulated versus fail-fast outcomes | question 6, resource packet |
| Effects/authority | Declared effect taxonomy versus precise capability parameterization | Three host profiles, pure callbacks, authority attenuation, denied capability | question 4, industrial |
| Lifetime | Static non-escape versus dynamic revocation; cleanup carrier | Actual type and scheduler validation after symbolic comparison | question 5, resource packet |
| Time/concurrency | Cold tasks, group failure policy, epochs and observation order | Controlled cancellation/late-response traces, queue bound and join proof | synthesis gate 3, interaction model |
| Data identity | Nominal internal data versus structural interoperability | Equality/hash, cycles, serialization identity, duplicate domain IDs | semantics, question 11 |
| Evolution | Closed decode versus forward compatibility; stored versus source editions | Rolling version cases, unknown fields, explicit migrations | questions 11/14 |
| Numbers | Exact/scientific defaults versus profile-specific widths/performance | Overflow, rounding, NaN, negative zero, big integer golden vectors | question 9 |
| Text and names | Unicode identity versus display; human language versus source vocabulary | Normalization, confusables, graphemes, sorting and IME cases | scalar/tooling contracts |
| Collections | Strict/stream/table/array distinction versus generic abstraction | Empty, ordered, single-pass, shape/rank and lazy-plan programs | questions 7/8/9 |
| Logic/search | Predicate execution versus relation/solver models | Multiple/no/incomplete solutions; budgets and witnesses | scoped tools, question 12 |
| Change/history | Source edit, model transaction, external compensation | Stale revision, merge, undo and unknown remote outcome | interaction model |
| Partial programs | Non-executable recovery versus formally typed partial evaluation | Incomplete editing, stuck/unknown results, effect isolation; never execute recovery guesses | industrial tooling, frontier 1 |
| Interaction | Text-primary versus structured-document primary | Supported round trips, fallback, identity, comments and semantic diff | interaction model |
| Accessibility | Fast expert gestures versus learnable multimodal commands | Keyboard/layout/IME/screen-reader trials, not automated claims | industrial tooling |
| AI collaboration | Proposal assistance versus model-dependent semantics | Provenance, malicious input, reviewable changes, no authority creation | interaction model, industrial security |
| Privacy | Rich traces versus bounded redacted evidence | Secret flow through diagnostics, caches, exports and agents | industrial security |
| Cost model | Friendly abstraction versus predictable allocation/latency | Resource budgets, startup, memory, sustained streams, inspection overhead | runtime profiles |
| Modern hardware | Portable semantics versus specialized acceleration | Explicit data movement/device plans, precision and fallback contracts | FFI/profiles, not core syntax |
| Interop | Convenient host objects versus typed/reviewable adapters | Exception/sentinel/ownership translation; no host reflection as language law | industrial FFI |
| Packages/builds | Federated identity versus location; determinism versus extension | Offline/mirror/key-compromise cases, pure fetch, locked inputs | question 13, industrial |
| Metaprogramming | Protocol/code generation versus staged hygienic transformations | Budgets, maps, expansion, ambiguity and removal criteria | question 12 |
| Portability | One meaning versus honest unsupported profile capability | Frontend-neutral fixtures and differential results/diagnostics | question 15, industrial conformance |
| Governance | Research freedom versus long-term stability | Decision provenance, edition policy, removal gates and support profile | questions 14/15, decisions |

Numbers refer to [existing open questions](../research/open_questions.md), not
new duplicate questions. Some scalar/tooling details currently have no complete
packet: that is a gap to close, not a decision silently made by this table.

## Novel Hypotheses Worth Trying

These are original Nomi design hypotheses, not claims of historical novelty:

1. **Evidence-aware explanations:** distinguish compiler facts, supplied data,
   observed host events, and agent suggestions in one bounded inspectable view.
2. **Semantic commands:** share a checked operation across pointer, keyboard,
   palette, macro, and agent, while keeping gesture state out of grammar.
3. **Typed change sets:** treat proposed changes as reviewable values with target,
   base revision and validity, but keep authority in the executor.
4. **Epoch-explicit exploration:** retain pure live feedback without confusing
   it with repeated effects or replacing a newer result with old completion.
5. **Relation values:** support checking, searching and explaining through
   explicit models, rather than changing eager calls into universal inversion.
6. **Projected notation:** let a domain reveal useful geometry or tabular shape
   while preserving a readable long form and unsupported-source fallback.
7. **Semantic migration receipts:** show what type/effect/boundary contract a
   migration changed, including uncertainty, not just a textual rewrite.

Each can fail. Metadata may become expensive; representation conversion may be
lossy; a shared command abstraction may be too broad; proofs may be unusable;
library-first may produce more concepts than a well-scoped notation. Measure
that cost instead of defending a small core as a goal independent of users.

## Ordered Design Closure

The October 9 [first-product contract](synthesis.md#first-product-contract)
selects calculation, local JSON report/repair and local reuse. Apply these gates
to the guarantees that profile promises. D1 needs closed calls and the selected
library callbacks; D3 needs portable scalars and strict codecs. General public
generics, fallible resources and structured tasks remain later design work.
D2 is not a global prerequisite for a pure report with host-owned transport.
D5 starts with text and read-only results; its richer alternatives remain
challengers. The table inventories owners, not mandatory completion of every
research topic before one useful product can ship.

| Gate | Deliverable | Acceptance and visible outcome |
| --- | --- | --- |
| D0 | Accurate authority map and prototype/target dispositions | No supported feature falsely presented as an accepted target form. |
| D1 | Callback/generic/protocol/effect sketch tied to three programs | Every call resolves; hover can name actual inputs, results and authority. |
| D2 | Error/resource/task completion contracts | All exit traces and cause ordering; Run/Stop and failed import are explainable. |
| D3 | Scalar/codec/identity golden contract | Portable numbers/text, strict path errors, stable targets, explicit wire format. |
| D4 | One whole vertical program review | Source/type/effect/lowering/format/diagnostic contracts agree; no unexplained placeholder API. |
| D5 | Competing representation experiment | Creation, review and repair evidence; stale/invalid/effectful counterexamples. |
| D6 | Smallest backend-neutral migration | Capability-gated frontend/Core slice and differential fixtures; current samples kept honest. |
| D7 | One supported GitHub playground sample | CLI/browser conformance, regressions, fresh generated assets, browser evidence. |

The resource comparison already supplies symbolic evidence for D2, not closure.
The [function contract proposal](function_contracts.md) narrows D1 with explicit
callback metadata and pure-only/effect-polymorphic candidates, but does not yet
admit function-type or generic declaration syntax.
The [generic-operation continuation](../research/generic_operations.md)
adds GA1-GA8 to that same packet: invocation/demand, state history, merge laws,
observation failure, cache dependencies and conditional equality/hash/codecs.
Its ordinary-call targets admit no new syntax or universal method hierarchy;
the first typed checks remain inside D1-D3 rather than a new global design gate.
The first D0 implementation checkpoint adds target-direction metadata to the
existing feature registry and shared inspection API. It does not change
prototype coverage or select a new grammar. Three entries remain explicitly
unreviewed; see [current inspection](../orientation/artifacts_and_usage.md#target-direction-inspection).
The [text-interface extension](../research/dsls/text_as_interface.md) sharpens
D3: close Text/Bytes validity and strict decode, source/public offset units,
display versus inspection versus encoding, interpolation conversion, line
ending/normalization policy, and redaction/provenance golden vectors across
Python and browser hosts. T1-T3 are the first discriminators; T4-T10 remain
conditional library/tool experiments. This accepts no codec API or new syntax.
The existing pattern contract is a bounded accepted slice and can continue its
registered migration without waiting for all 29 dimensions. Do not implement
open notation merely to keep the repository busy.

The [domain-layer proposal](synthesis.md#domain-layer-proposal) adds data/time,
AI/ML and documentary challengers to D1-D4. DT1-DT5/ML1-ML6/DC1-DC6 extend
existing questions; they do not add another global gate or require implementing
every domain. First type inert descriptions and contextual references, preserve
domain payload laws, then review one composed report/train/review/publication
program. A shared envelope is a candidate protocol, not a universal Core IR.

## Reversible Implementation Policy

Use the [exploratory doctrine](../orientation/exploratory_implementation_doctrine.md).
Prefer declarations in existing feature/frontend/backend registries, versioned
schemas, adapters, and feature capabilities. Keep experimental execution off by
default. Distinguish **implemented today** from **accepted in the target**;
rejected prototype features may continue running during an explicit migration.

Migrate one semantic owner per checkpoint: golden contract, producer, validator,
consumer, diagnostics, then user sample. Avoid a replacement framework for the
entire language. Preserve artifacts that let a different parser/runtime replace
the experiment. Removal criteria and cost of changing the choice are part of
the design review, not cleanup work left for later.

## Research And Promotion

Exploratory breadth can originate in real activity, a primary research mechanism,
an unfamiliar discipline or a speculative comparison. The current table is not
an admission filter for those investigations. Distinguish a discovered question,
a proposed mechanism, a discriminating experiment and an accepted contract.
When an investigation only repeats known examples, summarize its consequence
and move on; when it reveals a missing dimension, revise the agenda itself.

### Qualified Guarantees

Tool output must say what a guarantee covers. These labels are not synonyms:

| Label | Evidence required | Does not establish |
| --- | --- | --- |
| Parsed | Valid syntax under a named profile | Types, authority, intent or termination. |
| Typechecked | A resolved contract under declared rules | All runtime constraints or absence of panic. |
| Exhaustive | Coverage of a checked subject domain | Completeness of external-world modelling. |
| Pure | Defined observation/mutation discipline | Termination, low cost or numeric exactness. |
| Tested | Particular cases/fixtures and their observations | A universal behavioral theorem. |
| Model-checked | A bounded model and declared assumptions | Arbitrary programs or omitted host behavior. |
| Solved | Witness/certificate and solver theory/budget | Intent correctness or always a global optimum. |
| Merged | Document reconciliation under its rules | A valid combined public contract. |
| Approved | Exact proposed action under current authority | Static safety or permission for a changed revision. |

Use this vocabulary in diagnostics and future playground views. No compiler
or UI produces all these guarantee records yet.

Use breadth to discover missing concepts and credible competing representations.
Close a focused thread when an experiment distinguishes its candidates,
promote the result into its owner, and retain the thread as cited rationale.
Do not describe this agenda as a complete next-generation language. The next
target delivery work includes D1: type map/fold, decoder derivation and resource
callbacks coherently. Broader representation, learning and domain investigations
can proceed with explicitly supplied facts while that work advances. Their
results can change these contracts and the schedule. Actual product claims need
actual semantic and host evidence; a supplied-fact comparison has a different scope.
