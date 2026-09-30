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
| Types | Progressive checking versus stronger whole-program inference | Complete public signatures; no implicit Any; principality/annotation costs | semantics, questions 2/3/10 |
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
The first D0 implementation checkpoint adds target-direction metadata to the
existing feature registry and shared inspection API. It does not change
prototype coverage or select a new grammar. Three entries remain explicitly
unreviewed; see [current inspection](../orientation/artifacts_and_usage.md#target-direction-inspection).
The existing pattern contract is a bounded accepted slice and can continue its
registered migration without waiting for all 29 dimensions. Do not implement
open notation merely to keep the repository busy.

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

## Research Stop Rule

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

Continue breadth only when it exposes a missing concept or credible competing
representation. Close a thread when an experiment distinguishes its candidates,
promote the result into its owner, and retain the thread as cited rationale.
Do not describe this agenda as a complete next-generation language. The next
exact semantic step is D1: type map/fold, decoder derivation, and resource
callbacks together; otherwise every richer interface would rest on an unresolved
function contract.
