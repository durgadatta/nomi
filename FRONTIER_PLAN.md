# Nomi frontier strategy and staged plan

> Active, user-requested strategy, started 2026-10-08 from 7db4ed5.
> This consumes the direction in [ASTRA_HANDOFF.md](ASTRA_HANDOFF.md).
> Canonical language decisions remain in [docs/design/](docs/design/README.md);
> the [roadmap](docs/orientation/project_roadmap.md) owns project-wide delivery.
> This is a temporary planning and continuity surface, not another specification.

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

**Next exact planning task:** start P1 with the existing invoice and import/report
targets. Show their exploratory, reusable and checked-boundary forms; identify
the first place where a public callable contract or representation choice becomes
necessary. Sketch one failure and repair in each. No new checker, runtime, editor
or process tool is needed to write that comparison.

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
