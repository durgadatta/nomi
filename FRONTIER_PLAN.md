# Nomi frontier strategy and staged plan

> Active, user-requested strategy, started 2026-10-08 from 7db4ed5.
> This consumes the direction in [ASTRA_HANDOFF.md](ASTRA_HANDOFF.md).
> Canonical language decisions remain in [docs/design/](docs/design/README.md);
> the [roadmap](docs/orientation/project_roadmap.md) owns project-wide delivery.
> This is a temporary planning and continuity surface, not another specification.

> Planning reviewed 2026-10-09. Preservation commit: **6aec9f3**. The remaining
> work is prepared below for a fresh implementation session; this session does
> not begin it. Start with [planning disposition](#planning-disposition) and
> [the fresh-session sequence](#fresh-implementation-session-sequence).

## Current scope: planning only

The latest user direction is to focus on **plan and strategy**, with hints of
potential implementation, before proceeding with implementation. This overrides
the earlier instruction to keep implementing after each plan commit. Finish and
commit the strategy; do not automatically begin or repair an implementation.

Partial implementation is preserved in the 2026-10-09 checkpoint. Treat it as
unfinished experimental evidence, not an accepted architecture or a completed
milestone. The [current checkpoint](docs/orientation/frontier_checkpoint_2026-10-08.md)
records its inventory, known failures and checks. The user's latest request
explicitly includes committing the previously uncommitted work. The preservation
commit includes code, tests, product documentation and generated inventory;
subsequent work in this session is planning only.
A future implementation phase must first reconcile that work with the selected
contract; its existence is not a reason to select its architecture.

## Big picture

Build a humane computational language that starts with useful ordinary code,
admits progressively stronger contracts, and grows through domain libraries,
tools and independently replaceable engines. Optimize coherent complete
workflows rather than feature count. Preserve an operational CLI and playground
during deliberate migration.

The first audience is someone creating a script, notebook or small automation
who later needs to share, inspect and depend on it. The next audience is the
library author who must make that reuse trustworthy. Both should be able to
understand source, boundaries, errors and proposed changes without learning a
backend's machinery.

The canonical direction now admits exploratory code and inferred-or-declared
checked public contracts (fcc0b2d). This settles the direction, not a general
inference algorithm, generic interface rules or dynamic package adapters.
Explicit mutation remains the current target. Compare simple reassignment
against var/set separately; a checking switch cannot change capture, evaluation
or mutation meaning.

Keep four dimensions independent: source semantics, selected checking policy,
runtime authority and execution engine. A stricter check must neither invent
proof nor grant permissions. Choosing an engine must not change source meaning.
An unknown fact is useful diagnostic information, never Any inferred as proof.

The broader ambition includes shell, data, tables, documents, web, design,
automation and AI/ML. Shared foundations should connect those domains while
retaining their distinct laws for ordering, transactions, layout, timing and
learning. A universal graph or a large common object hierarchy is not a
prerequisite. Current Python AST, Lark, Rust/WASM, JavaScript and Core IR are
replaceable laboratory tools.

## Product strategy and success criteria

The first product bet is a small program that can grow into a reusable,
checked, explainable workflow without being rewritten in a second language.
The invoice is the entry point, not sufficient evidence for that promise.
Carry three existing pressure programs through design together:

| Journey | What the person should accomplish | Required design evidence |
| --- | --- | --- |
| Beginner invoice | Create, inspect and revise a calculation; select a restriction; reuse a function | Before/after source, facts versus unknowns, one useful error and repair, stable meaning |
| Import and report | Decode imperfect external data, reuse a library, produce a table or document | Path errors, public contract, dependency evidence, effects/authority, explainable output |
| Resource-heavy job | Use a file/service, start dependent work, handle failure or cancellation | Ownership, exit/cause order, bounded lifetime, stale-result behavior, understandable recovery |

Reuse the [target suite](docs/design/targets/README.md) and focused packet fixtures.
For each journey, compare create → inspect → revise → restrict → reuse → repair.
Include text plus a table/form or notebook view where useful. Show what survives
a revision: names, identities, comments, contracts and pending effects.

Table, document, shell and AI-assisted variants can challenge composition now
at the design level. They need not wait for every compiler feature. A scheduling
or collaborative-editing case is a challenger when the three journeys miss a
fundamental distinction. Do not turn every challenger into a simultaneous
implementation project.

Judge candidates in this order:

1. Coherent observable meaning and honest guarantees.
2. Understandable creation, review and repair.
3. Composition, interoperability and cost of changing the design.
4. Portability and inspectability across supported profiles.
5. Measured startup, memory and execution cost for a supported workload.

A hard semantic failure cannot be averaged away by syntax convenience or a speed
estimate. Record concepts introduced, required annotations, facts a reader must
find elsewhere, repair steps and unsupported cases. These are design observations
until real user trials measure learnability; agent agreement is critique, not
usability evidence. Keep novice and library-author experience visible separately.

## Strategic strands and dependencies

| Strand | Near-term design deliverable | Later runnable outcome |
| --- | --- | --- |
| Humane authoring and representations | Three growth journeys; text/structured-document comparison; diagnostic and repair sketches | Coherent CLI, notebook and selected projections with inspectable edits |
| Semantic assurance and interoperability | Composed callable/boundary/effect/lifetime contracts; honest evidence and policy rules | Reusable checked interfaces, controlled dynamic boundaries and portable artifacts |
| Dependable execution and engines | Independent value/effect/completion expectations; supported-operation boundaries | Reliable hosted execution, equivalent alternative engines and measured specialization |

These strands inform one another. Human interaction and domain comparisons can
begin with paper examples and supplied facts. Executable guarantees still require
their specific semantic prerequisites. A hosted generator repair does not gate
target function/resource or representation design. A scalar checker does not
close the generic callable contract.

Keep one leading product question per iteration and, during a future
implementation phase, at most one independent maintenance slice alongside it.
Reassess priorities after each checkpoint. Convenient tests and accumulated code
must not displace the selected user pressure.

## Design-only checkpoints

| Checkpoint | Work and existing owner | Finished when |
| --- | --- | --- |
| P0: strategy and state | This plan, roadmap routing and current checkpoint | Vision, priorities, unresolved forks, deferred implementation and dirty work are explicit; docs committed |
| P1: growth journeys | Language-coherence and cognitive-interfaces packets; existing target suite | Beginner, reusable and failure-heavy forms include diagnostics, formatting and review/repair; unfamiliar APIs are labeled proposed |
| P2: composed contracts | Function-contracts and resource-lifetime packets; D1/D2 | Credible alternatives face map/fold, decode and scoped-resource calls; independent type judgments, effect obligations, capture/escape and completion traces distinguish them |
| P3: representation challenge | Cognitive-interfaces packet and existing domain research | Text-primary and structured-document-primary candidates face the same task, including unsupported source, stale edits and effects; table/document laws retain owners |
| P4: architecture and migration | Implementation-layer map, roadmap owners and canonical decision ledger where needed | A bounded contract has producer/consumer boundaries, refusal behavior, inspection, migration/removal cost and one proposed implementation slice |
| P5: reviewed planning checkpoint | Existing bridge retrospective and this plan | Independent critique is resolved or named, changed judgments are recorded, next exact task is scoped, documents committed |

P1 supplies the shared programs for P2/P3, which can proceed independently.
P4 incorporates both. A broad question may stay open if it does not affect the
bounded contract under consideration. P5 may conclude that more design is needed.
Finishing a plan does not restart implementation under the current request.

### Planning Disposition

| Checkpoint | October 9 result | Evidence still required later |
| --- | --- | --- |
| P0 | All pending work committed at 6aec9f3; fresh failure/pass counts recorded | The known continuation failures remain unresolved. |
| P1 | [Three growth journeys](docs/design/synthesis.md#growth-journeys-and-boundary-evidence), policy matrix, boundary/error/repair expectations and target fragments prepared | Actual target execution and novice/library-author experience. |
| P2 | [Closed contract/call-shape/generalization comparisons](docs/design/function_contracts.md#bounded-contract-comparison-for-implementation) and [remaining completion schedules](docs/design/resource_lifetime.md#remaining-completion-experiments) prepared | Source-derived typing, host-controlled async traces and a coherent D1/D2 rule; no new syntax accepted. |
| P3 | [Paired text/structured trial](docs/design/interaction_model.md#paired-representation-and-revision-trial), revision/binding distinction and table/document challengers prepared | Comparable prototypes and human/assistive-technology trials. |
| P4 | [Producer/consumer, invalidation and migration boundaries](docs/orientation/implementation_layers.md#planned-assurance-and-representation-boundaries) and ordered work units below | A bounded implementation comparison that establishes, rather than supplies, facts. |
| P5 | Adversarial self-review and planning stop gate below; packet/handoff routes updated | Independent review remains a later gate; this session did not use a separate reviewer. |

These checkpoints finish **planning preparation**, not D1-D7 design acceptance,
language conformance or product readiness. The four designing packets remain
designing. Broad alternatives are not all decided by a larger amount of prose.

### What This Pass Chose

Choices here are experiment order and starting candidates, not new language laws:

- Lead with reusable, inspectable boundary evidence across the invoice and import
  journeys. A scalar call check is useful groundwork but cannot be the endpoint.
- Start the next contract experiment with a closed monomorphic export; require
  explicit refusal of unknown dependencies. Keep dynamic adapters separate until
  their precise runtime guarantees can be stated.
- Compare exact positional callback contracts before richer subtyping; test
  pure-only strict collection callbacks while permitting resource callbacks to
  declare effects under their separate invocation/lifetime contract.
- Compare conservative generic generalization with justified relaxation using
  shared-storage witnesses. Do not choose a generic spelling before call shape,
  shared state and public evidence are coherent.
- Use text-primary read-only views as the first reversible product trial, with
  equally specified structured-document tasks and a concrete replacement trigger.
- Keep hosted continuation repair as bounded maintenance. It cannot decide target
  cleanup semantics or absorb the main authoring/reuse agenda.

No fresh language survey, universal IR, agent framework or new implementation
tool is justified by the remaining questions.

## Fresh Implementation Session Sequence

This is a decomposition of existing A05/A08/A11/A14/A19-A24 owners and D1-D7,
not another project-wide queue. Apply it only when the fresh session starts
implementation. Each row ends in a reviewable result; a failed gate narrows or
replaces the candidate instead of automatically opening the next row.

| Order / owner | Exact work unit and likely files | Independent completion evidence | Stop or replacement condition |
| --- | --- | --- | --- |
| 1. Baseline, A11/A24 | Read 6aec9f3 and current checkpoint; reproduce the protocol-review families only if code/environment changed; inspect generator state and continuation adapter | Current failure families agree with the recorded source; prior operand/cleanup fixes remain visible | Unexpected unrelated failures change the baseline before any readiness claim. |
| 2. Contract experiment, A05/A08/A19 | Passive monomorphic contract cases beside `prototype/analysis/model.py`; new contract test file; two consumers for judgments and inspection | Constant export, directed scalar function, absent private implementation, unknown dependency and version/identity negatives agree with prepared judgments | Supplied metadata is mistaken for inferred evidence, or an unknown needs to be treated as Any. |
| 3. Source producer, A04/A05 | One target-profile adapter feeding those same contracts; analysis/source and frontend capability owner as required | Source-derived facts match the independent cases; import/default/annotation bodies never execute; actual or explicitly unavailable spans | Hosted constraint annotations are assumed to be target static types; pub support is claimed without a producer. |
| 4. Product explanation, A19/A20 | Public check facade, CLI scope display and installed-workflow fixture | Beginner can inspect invoice, see a public-contract blocker and repair it; report states exact scope/provenance and preserves preview behavior | Version-1 `ok` silently changes meaning, a private API is needed, or checking performs user effects. |
| 5. D1 composition, A08/A12 | Function packet cases for map/fold, explicit defaults, decode and shared storage; compare source candidates and formatter shapes | Complete positive/negative type/effect/capture judgments without private consumer facts; decoder errors preserve row paths | Arity/effect/region ambiguities survive behind pretty generic notation; retain explicit adapters and narrow scope. |
| 6. D2 completion, A11/A14/A15 | Resource packet and new event-controlled lifetime/cleanup fixtures; first synchronous, then bounded async | Binding failure release, all causes, heterogeneous errors, whole-completion non-escape, cancellation/join and incomplete cleanup are explicit | Host exception suppression or worker termination is presented as target completion; return to the contract. |
| 7. D3/D4 integration, A03/A09/A12/A26 | A bounded invoice/import segment; scalar/codec/profile and dependency-interface vectors | Values, strict decode, nominal identity, dependency changes and expected/abnormal failures agree across chosen routes | A row-count bound substitutes for byte/work bounds, or a public type name substitutes for owner identity. |
| 8. D5 representation, A21-A23 | Same invoice facts and prepared HX8 tasks; read-only text/table first, structured challenger when triggered | Same evidence/commands, epoch and unsupported-source handling; separate human correctness/repair results | Needs a second evaluator, lossy round trips or automatic effectful refresh. |
| 9. D6/D7 promotion, A02/A06/A24/A28 | One accepted contract through supported frontend/Core/runtime/formatter, CLI/browser and sample inventory | Capability matrix for parse/check/lower/run/diagnose/format; installed and actual browser checks; exact generated artifacts | Any route silently accepts unsupported target meaning or claims a full packet from one sample. |

Rows 5/6 **co-design** callable regions, effects and completion; they are not
cyclic prerequisites requiring each whole packet to finish first. Use explicitly
supplied region/call facts to compare consumers, then require real producers
before admission. Representation paper trials can proceed now, and a supplied-
fact study can proceed alongside contract implementation if clearly labeled.
A production editable view depends only on the actual contracts it consumes,
not completion of every Nomi research topic.

The known-broken continuation adapter must be reconciled before new claims of
reliable hosted execution. At most one maintenance slice accompanies the leading
contract/product question. This does not require all target D2 work to wait for
Python compatibility, or permit shipping the known failures as completed work.

### First Product Experiment: Work Order

**Pressure:** publish a tiny reusable calculation without converting the first
client's observed arguments into a public promise. **Layer:** analysis and
module/tooling contracts; no new source notation. **Owners:** function-contracts
and language-coherence; A05/A08/A19. **Starting source:** `maximum_batch_size()`
in the overall fixture, followed by the directed `subtotal(Int, Int)` boundary.

1. Write independent expected records for a complete constant export, a directed
   scalar function, an unknown provider, a changed dependency, an incompatible
   result and a missing/unsupported artifact version. Record supplied facts as
   supplied. No AST traversal or inference in this step.
2. Make the call-obligation consumer and an explanation consumer agree on those
   cases. Expected explanations name scope, inferred/declared/verified/unknown
   evidence, the public promise and a concrete repair. A well-formed record with
   unverifiable claims remains insufficient evidence.
3. Review the contract boundary before a source producer: compare source digest,
   contract compatibility and implementation verification identity. Recheck
   policy combinations and an unchanged consumer with a changed dependency.
4. Implement only the agreed producer slice in the next bounded increment.
   If supported target annotations/pub cannot be produced honestly, keep the
   contract lab separate rather than using hosted annotation evaluation as proof.
5. Integrate a user-visible explanation only once the origin/scope is accurate.
   Add broader inference or package persistence only after this workflow exposes
   the missing requirement. A passing passive-consumer test is not an exported
   source-interface capability.

Proposed files: a small `prototype/analysis/contracts.py`, a new
`prototype/tests/unit/analysis/test_interface_contracts.py`, then the existing
analysis/facade and frontend metadata owners if the experiment succeeds. Names
are handoff suggestions, not files created in this planning session. Keep the
v1 module-execution report distinct if the experiment needs a new contract scope.

**Exit:** two consumers agree with independent cases; the supported source
producer establishes the same facts; the CLI exposes a useful boundary/repair;
unsupported dependencies remain refused. **Remove:** consumer model or producer
can be withdrawn without changing ordinary program execution. Do not claim
general generics, a secure package verifier, lifetimes or browser support.

### Continuation Maintenance: Work Order

Compare three mechanisms on the **same existing oracle**, not three rewrites:

| Candidate | Minimum experiment | Rejection signal |
| --- | --- | --- |
| Bounded host adapter with explicit source-exception transport | Source StopIteration reaches source handler/exit before the public generator boundary; thrown GeneratorExit subclass reaches a yielding handler | Provenance is guessed from exception text/cause, or special handling keeps multiplying across protocol layers. |
| Explicit interpreter continuation frames | Retain one binary left operand and a waiting try/cleanup frame; deliver value/error once | Duplicates state machines per AST operator instead of exposing a small shared completion protocol. |
| Narrow pre-effect support fence | Refuse every unsupported suspended path before body effects, including definition-time expressions in nested declarations | Rejects useful required samples indiscriminately or allows a supported-looking prefix to execute first. |

First inspect the unmodified native/hosted fixtures in
`test_generator_protocol_review.py` and `test_generator_completion_ownership.py`.
Keep send(None), delegation, active exception identity, repeated close and
attached Nomi blocks in the neighboring regression surface. Preserve source
exception provenance without recognizing it by message. The clean checkpoint
makes replacement reviewable; it is not an instruction to reset or discard work.
An explicitly reduced support boundary must be reflected in capabilities and
diagnostics before effects. Target generators and fallible resource scope remain
separate design gates whatever wins this maintenance comparison.

### Verification Ladder For The Fresh Session

| Change | Required fresh check | What it does not establish |
| --- | --- | --- |
| Contract model/consumer | New positive/negative independent case tests; packet integrity | Source inference or execution support. |
| Source producer | Accepted/refused frontend cases, no-user-execution adversaries, evidence invalidation and span checks | General public polymorphism or every frontend. |
| Hosted continuation | Both focused new generator files, neighboring generator/context-manager/defer suites in all three modes, then relevant regression/full suite | Target D2 or browser worker cleanup. |
| Facade/CLI | New API/CLI tests plus existing source-check suite and installed-wheel check | Browser support or strict run admission. |
| Browser-exposed behavior | Runtime contract/freshness checks and actual browser checker, including legacy route when affected | Assistive-technology usability or every untested interaction. |
| Sample/inventory change | Regression snapshots as authorized, `make_web.py --check`, WASM freshness when relevant | A runnable target feature merely from manifest inclusion. |

Use the current repository commands, not historical pass totals. Preserve the
existing test-edit rules and add new tests for new behavior. No new runtime,
browser or performance evidence was produced by the planning changes themselves.

## Planning Stop Gate And Unresolved Decisions

Further prose is useful only if it exposes a new counterexample, changes an
owner/dependency or makes an experiment executable. The following questions now
have enough preparation to require another kind of evidence:

| Remaining decision | Smallest discriminating evidence | Reopen/choose when |
| --- | --- | --- |
| Public inference and dynamic adapters | Separate-consumer judgments, unknown provider and changed dependency cases | A complete guarantee can be established locally or enforced by an explicitly scoped adapter. |
| Callable spelling/subtyping/generalization | Exact/default/tuple cases plus shared-slot/fresh-factory judgments and reader repair | One rule remains sound for the cases with lower documented complexity/repair cost. |
| Resource carrier, cause precedence and defer timing | Prepared body/bind/release schedules, heterogeneous mappings and event-controlled async | All causes, destinations, lifetime and incomplete outcomes remain explainable. |
| Binding and notebook revision | Old closure/task across mutation, shadowing, rerun and reset | Same-source meaning stays stable; representation/session choice does not quietly update old captures. |
| Primary representation | Paired task results including unsupported export/merge and accessibility | A measured repair benefit survives preservation and authority constraints. |
| Numeric, codec and nominal identity | Profile vectors, strict indexed decode and duplicate-package cases | Two actual producers/consumers agree; display equality is insufficient. |
| Backend optimization | Fixed workload, equal results/order/failures, cold/warm time and peak memory | Measured end-to-end benefit justifies replacement and a rollback remains available. |
| Domain extension | One useful report/table/document journey with explicit domain laws | Ordinary functions demonstrably fail; only then compare scoped notation. |

No time estimate is a performance result, no successful example is a general
type proof, and no agent review is a usability study. These are bounded remaining
questions, not reasons to keep extending the bibliography or add more planning
machinery. Other domain/release/package work stays with the roadmap until a
selected journey or measured bottleneck reaches its trigger.

### Adversarial Self-Review

| Challenge | Planning correction or surviving limit |
| --- | --- |
| Does preservation imply a green baseline? | No: 24 protocol failures are committed and repeated explicitly in the handoff. |
| Did the scalar checker become the whole product strategy? | No: three growth journeys and early representation/domain trials remain the acceptance pressure. |
| Can uncalled unknown code pass and then be exported as checked? | Module-execution scope and complete callable evidence are separate obligations. |
| Can a private edit leave an apparently fresh proof because the API is unchanged? | Contract compatibility, implementation verification and build/run identity are separate. |
| Does pure-only map ban effectful resource callbacks? | Each higher-order API owns its invocation/effect contract; resource body effects remain explicit. |
| Does a wrapper make shared storage polymorphic? | Environment-fixed variables and retained regions survive wrapping; fresh allocation is a changed program. |
| Does zero body execution prove cold-task purity or authority? | Construction/latent requirements remain open and are not inferred from coldness alone. |
| Is a row limit a byte or queue-memory limit? | No; file/response bytes, nesting, queue and diagnostic work have separate gates. |
| Does text-first decide the representation fork? | No; structured-primary export/merge tasks and a replacement trigger remain. |
| Is P5 an independent review? | No; this is explicit self-review against prepared counterexamples. Obtain independent critique during the next executable comparison. |

The planning pass stops at this evidence boundary. The exact next work is the
monomorphic contract experiment above, with bounded continuation reconciliation
before relying on hosted execution. A new implementation session can begin from
the committed plan without another global survey. It must not mistake prepared
judgments for implemented guarantees or unfinished experimental code for approval
of its architecture.

## Decisions that could invalidate substantial work

These are comparisons to make, not newly accepted language choices. Record
positive and negative examples before choosing a mechanism; update the named
canonical owner when evidence actually settles a target decision.

| Priority / question | Credible candidates | Discriminating case and consequence | Owner / present disposition |
| --- | --- | --- | --- |
| First: dynamic/checked boundaries | Reject unresolved dependencies at a checked boundary; admit an explicit runtime adapter with limited guarantees | A library with an unknown host dependency changes without its consumer changing; what evidence is invalidated? | Language-coherence, industrial; checked contracts accepted in principle, adapter/export rules open |
| First: policy composition | Independent restrictions with explicit prerequisite closure; named profiles expanding to the same obligations | Same source under no restriction, types, purity and both; unsupported evidence must remain visible and policy order must not alter meaning | Semantics/industrial; dimensions separated, public policy surface open |
| First: generic callable contracts | Inferred public schemes within stated limits; required annotations at ambiguous/higher-order boundaries | Map/fold, decoder callback and captured resource type consistently; one scalar call cannot prove a generic interface | Function-contracts D1; designing |
| First: binding and revision | Existing explicit mutation with value/cell capture rules; simpler reassignment with equally explicit binding identity | Rename/re-execute a notebook cell while a closure or task holds an older binding; what does it observe? | Semantics/cognitive-interfaces; current var/set target, alternative unresolved |
| First: lifetime and completion | Static non-escape; scoped dynamic revocation; candidate cause/completion rules already in resource packet | Body failure plus release failure plus cancellation; escaped callback or task; reader can predict ownership and cause order | Resource-lifetime D2; symbolic evidence, type/runtime admission open |
| Early and parallel: representation | Text-primary with projections; structured-document-primary with equally usable text | Edit a table/document, preserve comments and unsupported source, merge stale edits, inspect a proposed effect | Cognitive-interfaces D5; genuine fork, existing editor does not decide it |
| After bounded contract: artifact boundaries | Frontend adapters to owned versioned facts/Core; temporary host-AST adapter behind the same declared scope | Two producers disagree on source positions or scalar meaning; consumer refuses incompatible evidence | Implementation layers / D3-D6; current substrates replaceable |
| Parallel challenger: domain extension | Ordinary libraries/protocols; scoped notation where long form fails real work | A table transform and document change share identity/outcomes but retain ordering/layout/transaction laws | Existing domain research and synthesis; no universal executor selected |
| After workload: optimization | Improve current interpretation; bytecode/native/specialized candidate | Same workload, cold and warm cost, failure/order/cleanup equivalence, inspection overhead | Roadmap runtime/profile owners; no performance winner assumed |

Compare alternatives on the same source and expected observations. Mark a claim
as proposed, deduced under assumptions, observed in a prototype, or measured with
users. Keep the smallest unresolved question when evidence cannot choose.
Research further only when a missing fact could change that choice; do not
repeat the bibliography to postpone a decision.

## Eventual delivery map

F0-F6 below are **frontier outcome labels**, not the roadmap's M1/M2 milestones.
The roadmap remains the scheduling authority; D0-D7 remain design-closure gates.
P0-P5 above are the current planning sequence. S0-S3 below retain names from
earlier granular plans solely to identify parked experiments.

| Outcome | Deliverable | Dependency for promotion | Completion evidence |
| --- | --- | --- | --- |
| F0: useful feedback | Existing retrospective plus justified evidence tooling | An actual recurring process failure | A changed judgment or corrected behavior, durable evidence, less repeated friction |
| F1: exploratory checking | Bounded source facts, independent restrictions, CLI/API and installed workflow | Settled scope and evidence contract for that slice | Independent policy matrix; no user execution or false proof; useful repair; supported boundary documented |
| F2: reliable hosted execution | Operand/phase retention and lexical cleanup in the compatibility lane | Native/hosted value and event oracles | Once-only effects, sent values, failure/cleanup traces; unsupported paths fenced; neighboring behavior preserved |
| F3: composed typed foundation | Function/generic/effect interfaces and resource/task contracts | Closed D1/D2 slice, informed by F1 and pressure examples | Map/fold, decode and resource programs agree; negative capture/failure cases reject for the right reason |
| F4: portable product slice | Versioned source/fact/Core/value/diagnostic boundaries and CLI/browser experience | One F3 slice plus its D3 scalar/codec laws and representation decision | Independent values/order/failures/spans across routes; invalid artifacts refused; installed/browser workflow evidence |
| F5: domain composition | One complete file/report, table/data or document/change workflow at a time | Shared identity/outcomes/authority/lifetime plus that domain's laws | Useful creation-to-repair workflow, bounded resources, explicit external effects, inspectable extensions |
| F6: performance/deployment | Measured engine candidates, package closure, supported profiles | Stable bounded artifacts and workload/host evidence | Equivalent behavior, end-to-end benefit, exact artifact identity and rollback |

F1 and F2 can advance independently in a later implementation phase; F0 supports
every outcome. F5 design probes begin early, while F5 executable guarantees depend
on the contracts they actually use. No outcome requires implementing every domain.
Publishing, licensing and support commitments remain separate owner decisions.

## Implementation hints, not instructions to begin

The earlier S0-S3 implementation plans are preserved in Git (903aa97, 6f97222).
They are hypotheses to reassess after P1-P4, not commitments created by partial
implementation. Keep each future hint to a boundary, minimal experiment,
independent expected result and replacement trigger.

| Candidate | Boundary and likely owner | Small experiment / independent expectation | Replacement or stop trigger |
| --- | --- | --- | --- |
| S0: feedback evidence | Explicit command → local receipt; existing agent workflow and tools owner | Successful, failing and interrupted checks retain status, source identity and output | Tooling creates more maintenance than avoided friction, or receipts are mistaken for attestation |
| S1: conservative checking | Source adapter → scoped versioned facts → selected obligations; runtime facade and analysis owner | Invoice facts, latent effects and unknown call; changing restrictions changes admission, not facts or execution | Host-AST assumptions leak into language law; stale facts or a declaration pass as proof; widening needs unresolved generic rules |
| S2: hosted continuation | Suspended evaluation → retained state/completion → lexical handler/cleanup; hosted interpreter owner | Native/hosted operand, send, failure and cleanup traces; unsupported suspension refused before effects | Protocol support requires unbounded patches, source exception identity/order changes, or compatibility begins deciding target D2 |
| S3: product integration | Public check/run facade → CLI/installed workflow; product and packaging owners | Same source can run and be inspected; actionable unknown dependency; malformed policy refused | Demo needs private APIs, hidden execution or claims beyond the producer's scope |
| Later domain projection | Owned values/revisions/change descriptions → domain renderer/executor | One table and one document example can be inspected, edited and repaired | Common layer erases domain laws or makes every edit depend on global evaluator changes |

For S2, compare explicit interpreter frames, a bounded host-generator adapter and
a narrower supported-shape fence. The current adapter has unresolved exception
and definition-time-expression defects (checkpoint). A source-exception carrier
is one possible experiment, not an accepted fix; an accumulating series of
protocol patches is evidence to reconsider the mechanism.

Prefer declarative capability/operation metadata where independent consumers
justify it. Keep the imperative implementation behind that contract. Avoid
building a universal framework before two real consumers expose a shared need.

## Self-improving feedback cycle

Use the existing [design-pass workflow](docs/orientation/design_pass_workflow.md)
and its four-part retrospective. The cycle applies during planning without
writing code:

1. Choose one user pressure and the smallest example that distinguishes choices.
2. State the candidates, expected judgments and unknowns before preferring a
   mechanism. Identify which observation could reverse the preference.
3. Seek independent critique of the same examples, including a negative case and
   a representation/domain challenger. Record disagreements rather than voting.
4. Revise the contract or narrow its claim. State what changed and why; rejected
   alternatives count as progress.
5. Check document coherence and authority, then commit the planning result.
6. Record the exact next task and ask whether convenient implementation displaced
   the selected user pressure. Remove or consolidate guidance made obsolete.

During a later implementation phase, add failing reproductions, bounded changes,
adversarial review, relevant verification and coherent implementation commits.
Command receipts identify what ran on which source; they do not prove soundness,
usability or architectural merit.

Promote repeated reasoning needs to a skill/prompt and deterministic repeated
failures to a check. Leave one-off observations in the existing bridge.
A process addition must name the friction it removes and when it should be
deleted. Do not add automation solely because a feedback cycle was requested.

This pass already exercised the planning loop: review exposed conflicting
milestone labels, a stale annotation premise and implementation-led priorities.
This revision corrects those, introduces early human/domain comparisons and
makes the user's phase boundary explicit. It adds no new automation.

## Evidence, continuity and gates

Earlier planning commits: 581b549, 903aa97 and 6f97222.
Canonical exploration/checked-contract direction: fcc0b2d.
The prior high-level dependency plan: 8d80f34.
The current checkpoint distinguishes completed documentation, partial code,
historical passing checks and newly exposed failures. Do not use an older green
suite as proof the latest worktree is ready.

For this planning phase, review links, authority, terminology, dependencies and
unresolved choices; validate registered packet integrity and staged whitespace.
No implementation is admitted, no packet becomes validated merely from this
plan, and no runtime/browser test is needed for these prose-only changes.

A later implementation plan must name pressure, owner, alternatives, independent
expectations, files, verification surface and removal criteria before editing.
Preserve existing tests unless their scoped modification is authorized; add
focused reproductions without weakening expectations. Verify the affected
installed/CLI/browser routes, refresh generated manifests when their inventory
changes, and distinguish actual checks from intended checks.

Commit only the current owned slice after inspecting the staged diff. Keep
generated reports, caches and screenshots out of Git. Preserve unfinished edits
and their inventory when work stops; report explicitly when a clean checkout
cannot reconstruct them.
