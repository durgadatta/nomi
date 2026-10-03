# Interaction Composition And Implementation Experiments

> Status: designing research experiments and implementation handoff; illustrative
> APIs are unaccepted and unexecuted. Updated 2026-10-02.

This is the experiment detail for the [edge atlas](edge_cases.md), within the
existing [interaction proposal](../../design/interaction_model.md) and
[current-to-target bridge](../../review/2026-09-30-cognitive-interfaces.md).
The [philosophical translation](../cognition.md) generates discriminating
questions; it does not settle the candidates. The
[local probes](experiments.md) test original finite models, not these Nomi APIs.

## Shared Programs And Method

Use the [invoice target](../../design/interaction_model_target.nomi) for a
beginner's quantity/total change, its checked immutable production edit for
identity/revision, and its raw submission boundary for failure-heavy input.
The [overall import](../../design/targets/overall.nomi) challenges effects and
data boundaries; the [resource target](../../design/resource_lifetime_target.nomi)
challenges cancellation and completion. Frame/control cases use a separate
small library model, not a real device or new ordinary-language semantics.

For each comparison hold the intended computation fixed. Compare observable
values, errors, effects, ordering, source preservation, and evidence, not only
rendered text. The ordinary-call sketches below are fictional tool/library APIs;
they establish pressures before naming signatures. The function-contract packet
still owns generic/callback/effect typing. No helper here can create authority.

| Case | Main composition | Atlas cases | Local motivating probes |
| --- | --- | --- | --- |
| C01 | Sort + collaboration + source-directed repair | H01, H22, H23, H45, H77 | P01, P12, P15 |
| C02 | Reset + cached artifact + changed authority | H06, H47, H70, H90 | P02, P10 |
| C03 | Incomplete draft + IME + accessible command | H09, H13, H41, H73, H76, H79 | P03, P16 |
| C04 | Inverse view + rounding + omitted constraint | H15, H16, H38, H40, H44 | P04, P13 |
| C05 | Stop + lost response + changed retry | H29, H54, H69, H71, H72, H87 | P09, P11 |
| C06 | Algebraic rewrite + evidence domain + progress | H25, H49, H52, H66, H68 | P05, P06, P07, P08 |
| C07 | Converged draft + domain invariant + reviewed proposal | H40, H45, H46, H48, H63 | P02, P10, P12 |
| C08 | Reactive result + notebook history + late completion | H04, H33, H34, H35, H36 | P09, P14 |
| C09 | Observation + privacy + bounded explanation | H24, H64, H74, H89, H91 | P14 |
| C10 | Internationalized input + source mapping + rename | H09, H42, H77, H78, H80 | P15, P16 |
| C11 | Spatial projection + frame reset + stale control | H81, H82, H83, H85, H86, H88 | P17, P18 |
| C12 | Beginner success + interrupted work + model revision | H60, H62, H93, H94, H95, H96 | Human study required |

## C01. The Row Is The Same; The Source Is Not

Sort an invoice view, merge a teammate's label change, then apply a repair
prepared from an old source diagnostic. Two identity problems coexist: row
positions have changed and source offsets are no longer valid.

```nomi
# Illustrative long form; tool APIs not accepted.
candidate = changes.set_quantity(
    model_identity=current.identity,
    base_revision=current.revision,
    line_id=selected_line.id,
    quantity=3,
)
outcome = changes.commit(current, candidate)
```

Compare resolved identity plus strict revision rejection with an explicit
rebase that resolves/checks again before presenting a new candidate. Rebase is
not reuse of old offsets or authorization. Keep source edits separate from
input/model changes; use binding IDs for the former and domain IDs for the latter.

Record target identity, expected/actual revisions, source digest, offset unit,
and unchanged state on rejection. Proposed diagnostic facts: `EDIT_STALE_SOURCE`
versus `EDIT_UNKNOWN_TARGET`, with refresh/rebase versus target-selection repairs.
Neither code is an implemented stable export. Remove the editable projection
if it requires guessing which declaration or row the person meant.

## C02. Revision One In Which History?

A session resets to revision 1 while an old edit and checked artifact remain in
a queue. A host grant used during the old preview is also revoked. A number-only
revision check and a cached "allowed" bit can each pass incorrectly.

```nomi
# Incarnation/epoch are proposed value metadata, not opaque runtime addresses.
context = proposals.context(
    source_digest=checked.source_digest,
    model_identity=model.identity,
    model_incarnation=model.incarnation,
    model_revision=model.revision,
    input_digest=inputs.digest,
    host_profile=profile.id,
)
proposal = proposals.prepare(context, requested_change)
outcome = executor.apply(proposal, current_context, current_capabilities)
```

Compare invalidating the complete proposal on any context change with selectively
repreparing pure description/checking facts and rechecking mutable execution
preconditions. The context fields need a typed ownership contract; not every
command reads all fields. Do not impose one giant envelope on every library call.

The decisive case is identical revision numbers in different incarnations.
Record changed object/context and current authority; never serialize capability
handles into history. Prepared, checked, authorized, and executed are distinct
evidence claims. An artifact hash is identity, not proof of permission.
Removal gate: a cache or macro can restore authority without the executor's
current enforcement. Runtime revocation timing remains with the effect/task
contracts; this experiment does not select a new grant syntax.

## C03. The Invalid Draft Is Useful Information

Enter blank, minus sign, malformed quantity, then a valid integer through text,
IME, speech hypothesis, and form. Lose pointer capture during a second edit.
Move focus to a result view without changing the selected line.

```nomi
draft = drafts.replace_text(previous_draft, new_text)
checked = quantity_decoder.decode(draft.raw_value)
candidate = changes.from_decoded(checked, selected_id, base_revision)
# Only an explicit complete candidate can reach commit.
```

Compare permissive draft storage plus commit validation with control-level input
filtering. The latter can win only if it preserves valid construction paths,
composition, repair information, and equivalent accessible commands. Previewing
an invalid draft must not construct an invalid owned Line or erase a valid model.

Capture raw draft, decode path, commit state, focus, selected identity, and command
count. Test a duplicate Enter/held-key event and a composition-completion Enter.
Use keyboard/switch/palette paths to request the same change. Proposed failures:
decode error, missing target, stale model, cancelled gesture, and unavailable
command; do not collapse them into a generic runtime error. Manual IME and
assistive-technology trials remain required even if a finite event model passes.

## C04. A Display Has No General Inverse

An invoice total can be changed by quantity or price. Zero quantity admits many
prices for the same total. Rounding hides precision, and an exported schema
omits a cross-field constraint. The attractive drag/form is underdetermined.

```nomi
alternatives = projections.propose_input_changes(
    model=model,
    requested_total=1200,
    editable_fields=selected_fields,
    numeric_policy=policy,
)
preview = projections.describe(alternatives)
```

Compare a read-only derived value plus explicit input editing with a bounded
inverse adapter that returns no solution, one candidate, or alternatives. This
does not turn arbitrary functions into relations or make `where` a solver.
Report units, exact value, rounding, edited fields, and rules not represented
by the schema. Commit must still use the real decoder/constraints.

An unsupported/lossy projection returns a reason and textual fallback. Preserve
comments separately from resolved meaning. Removal gate: it silently chooses an
inverse, uses pretty output as its input codec, or claims an omitted rule is
enforced. A total-only comparison cannot prove a source transformation equivalent.

## C05. Stop Cannot Tell You Whether The World Changed

Publishing succeeds remotely, but its acknowledgment is lost. The user requests
Stop, edits the payload, and presses Retry. Local cancellation and remote outcome
are independent dimensions.

```nomi
# Fictional recovery API; provider guarantees must be explicit.
observation = publication.outcome(operation_id)
recovery = recovery_policy.plan(
    operation_id=operation_id,
    original_payload_digest=original_digest,
    current_payload_digest=current_digest,
    observation=observation,
)
```

Compare fail-closed reconciliation with explicit resend under a provider-supported
stable operation key and payload contract. A retry with a changed payload is a
new action or an explicit conflict; no universal exactly-once guarantee follows.
Retain requested cancellation, local join/cleanup, remote acknowledgment, and
compensation as separate facts. Completion may mean the local task ended while
the remote result remains unknown.

Proposed diagnostic: `ACTION_OUTCOME_UNKNOWN`, with operation identity and
available recovery, not "nothing happened." Removal gate: Stop/Undo or a retry
wrapper implies external reversal. The local fake ledger in P11 imposes its own
idempotency rule; it is not evidence any provider offers that rule.

## C06. Valid Algebra Can Be Invalid Execution

Boolean conjunction is commutative as a pure value law. Swapping a false operand
and an effectful predicate changes whether an action happens. Complement changes
when the universe changes. A bounded failing search establishes neither
unsatisfiability nor termination; a maintained invariant can coexist with stutter.

```nomi
description = analysis.compare(
    original=original_expression,
    candidate=rewritten_expression,
    domain=declared_domain,
    numeric_profile=numeric_profile,
    admitted_observations=observation_policy,
)
```

Compare conservative rewrites backed by explicit resolved facts with an optional
law-bearing scoped model. Require evaluation order, invocation count, failure,
purity/capture facts, numeric theory, and progress assumptions as appropriate.
No live arbitrary-code equivalence oracle is proposed.

Dijkstra's nondeterministic guards are not Nomi's ordered match; Boole's algebra
does not make bag/list operations idempotent. Analysis must distinguish witness,
complete finite check, bounded counterexample, unknown, and unsupported.
Removal gate: a pretty identity omits an effect/numeric/termination condition or
claims the external world has the same closed domain as the model.

## C07. Convergence Can Publish An Invalid Model

Start with range [0, 10]. One collaborator changes the lower bound to 8; another
changes the upper bound to 5. Each edit is valid against the original state.
A property-wise merge converges to [8, 5], which violates the domain invariant.
An agent's independently prepared "fix" can also belong to an older revision.

```nomi
merged_draft = collaboration.merge(left_draft, right_draft)
checked_model = Range.decode(merged_draft.raw_value)
review = proposals.describe(checked_model, current_context)
```

Compare retaining an invalid merged draft for human repair with domain-aware
conflict detection before merge. Both must preserve alternatives and provenance;
neither may inherit the old valid model or execution review automatically.
Do not describe P12's simple property merge as an Automerge/CRDT conformance test.

Record both source proposals, merged values, failing predicate/path, and the last
valid committed model. Removal gate: a green merge/check indicator conflates
transport convergence with domain validity. Intent/priority arbitration remains
application policy, not a rule silently embedded in the editor or language.

## C08. A Notebook Is A History, Not Only A Graph

Change a pure invoice input while an import is running. Restart the worker, then
receive an old reply. Open the result and dependency view repeatedly. Persistent
notebook bindings and run history must not be confused with a clean all-cells run.

```nomi
run = runs.start(checked_source, input_snapshot, profile, capabilities)
snapshot = runs.completed_snapshot(run.id)
view = inspection.project(snapshot, inspection_budget)
```

Compare explicit Run with pure-only automatic recomputation. Store source/input
identity, worker/session incarnation, run ID, causal links, and host observation
identity. Different displayed tabs cannot become different evaluators.
Results of old runs remain inspectable as historical evidence; current result
selection cannot be determined by whichever reply arrived last.

The browser already uses request IDs and worker generations; this is useful
existing structure, not the complete epoch contract. Notebook caches already
have parser/profile/source keys; those are not result histories or grants.
Removal gate: view navigation repeats effects or clears provenance accidentally.

## C09. Explain Without Repeating Or Leaking

A completed result has five events including a secret-bearing input. The view
budget allows three. A host object's display getter would touch the world; a
naive export copies the raw event payload despite masking the visible label.

```nomi
projection = inspection.project(
    completed_snapshot,
    budget=inspection_budget,
    disclosure=disclosure_policy,
)
```

Compare captured redacted snapshots with an explicit effectful inspection
adapter only for domains where refreshing is necessary. The latter is a new
authorized action, not passive inspection. Summary generation must not invoke
arbitrary host getters. Record total/shown/omitted events and their epoch;
bounded explanation does not mean incomplete program execution.

Candidate evidence fields: claim kind, source/model revision, assumptions,
observation origin, redaction scope, retention, and truncation reason. Redacting
content is not automatically noninterference for timing, length, equality, or
metadata. Removal gate: UI masking is advertised as comprehensive confidentiality
or a truncated trace is presented as complete proof.

## C10. A Character Has Several Coordinate Systems

An emoji before a diagnostic spans four UTF-8 bytes and two UTF-16 units.
A combining sequence can render as one grapheme. IME composition, bidi display,
translated labels, and resolved rename all interact with that source map.

```nomi
target = source_maps.resolve(
    source_revision=diagnostic.source_revision,
    offset=diagnostic.offset,
    offset_unit=diagnostic.offset_unit,
)
candidate = refactoring.rename_resolved(target, proposed_name)
```

Compare exact revision-aware conversion with stable structure/binding references
plus mapped spans. Both need diagnostic rendering in logical source order and
safe presentation of bidi/confusable structure. Neither may normalize or rewrite
identifiers merely to make a display look similar.

Pin Unicode rules when implementing; byte, scalar, code-unit, and grapheme counts
are not interchangeable. P15 reports host units and canonical normalization only;
it does not implement grapheme segmentation or the bidi algorithm. Removal gate:
a repair edits the wrong source or the interface excludes multilingual input to
avoid fixing its mapping/input contract.

## C11. A Coordinate Or Sensor Number Is Not A Situation

Prepare a spatial edit, reset tracking origin, and switch automation mode before
commit. A sensor is numerically plausible but stale. The same coordinate/action
numbers no longer mean the same intervention.

```nomi
proposal = spatial.prepare_move(entity_id, frame_snapshot, target_pose)
transition = control.check(
    proposal,
    current_frame,
    current_mode,
    latest_observation,
    freshness_policy,
)
```

Compare rejecting stale frame/mode proposals with explicit reproject/replan and
revalidation. Frames need identity, transform, units, uncertainty, and calibration
epoch; observations need clock/source/freshness contracts. Actual capability
execution remains a typed device boundary.

STPA adds questions about missing, wrong, mistimed, and overlong actions; it does
not certify Nomi. P17/P18 are imposed finite models with a fixed freshness rule,
no device or physics. Removal gate: a simulation/view silently gains device
authority or type validity is marketed as physical safety/reachability.

## C12. Success On The Happy Path Can Hide A Learning Failure

Let participants create an invoice, predict a modified result, repair invalid
input, review a teammate's change, resume after interruption, and transfer the
model to another currency/domain. Include novice/expert and assistive-technology
workflows. The same tasks compare text, read-only table/form/diagram, and one
bounded editable projection.

Compare task completion with prediction/repair evidence. Pre-register which
facts each representation exposes and which mistakes count: wrong identity,
wrong epoch, implicit action, false evidence claim, lost draft, and misunderstood
domain. Counterbalance presentation order; retain qualitative explanations and
participant exclusions. A small formative study can reveal mechanisms, not
universal usability or an accessibility certification.

No human study is executed here. If a representation gains speed by concealing
uncertainty or removing user choice, return to its contract. If all views expose
the wrong domain assumptions, revise the model first. Philosophy motivates the
question; participants and domain facts can falsify the design recommendation.

## Implementation Handoff

These are read current extraction points, not claims that the proposed contract
is implemented. Keep experimental metadata out of Core until a semantic owner
needs it; no second universal IR or evaluator follows from this research.

| Existing surface | Observed current fact | Small reversible next slice | Conformance evidence before promotion |
| --- | --- | --- | --- |
| [web/app.js](../../../web/app.js) | Request IDs, pending replies, worker generations; Stop terminates/restarts worker | Explicit run/result context and state adapter after C02/C05/C08 rules settle | Old-worker replies, repeated Stop, timeout/restart, result retention; no claim of resource join from worker termination |
| [web/runtime.js](../../../web/runtime.js), [cells.js](../../../web/cells.js) | Result tabs, run/reset/cancel UI and cell model | Read-only captured projection using existing result contract | Navigation emits zero execution actions; C03/C09 focus/draft/truncation tests and manual accessibility trials |
| [runtime/api.py](../../../prototype/runtime/api.py) | ExecutionResult and InspectionResult facades | Tool-owned evidence/epoch envelope around completed results | CLI/browser serialize the same evidence facts; unknown-version behavior |
| [runtime/session.py](../../../prototype/runtime/session.py) | Persistent bindings and lowered-AST cache keys | Keep parse cache identity separate from session/run/input observation identity | C02 reset/incarnation and C08 notebook-history fixtures |
| [runtime/diagnostics.py](../../../prototype/runtime/diagnostics.py) | Passive diagnostics/events, IDs, parent IDs, redaction metadata | Define one bounded observation envelope in the owning protocol | C09 zero extra effects, explicit truncation, export redaction; fixture results do not imply full information-flow security |
| [runtime/decode.py](../../../prototype/runtime/decode.py) | Decode error/path records | Draft/raw-value adapter plus actual decoder commit boundary after codec design | C03/C04 invalid drafts, omitted projected rules, unchanged committed state |
| [runtime/host_capabilities.py](../../../prototype/runtime/host_capabilities.py) | Declared host-call names/manifest checks | Separate declared support from current concrete grant enforcement | C02/C07/C11 denied/revoked/narrowed authority; today's manifest is not that grant system |
| [pattern_surface.py](../../../prototype/syntax/pattern_surface.py) | Versioned pattern document and UTF-8 byte spans | Reuse explicit source/unit/version discipline in future lossless/typed artifacts | C01/C10 conversion and stale-span failures across frontends; binding identity still needs design |
| [VS Code run commands](../../../tools/vscode/nomi/src/run_commands.js), [Jupyter kernel](../../../tools/jupyter/nomi_kernel.py) | Run ownership and persistent session/reset adapters | Consume the same settled semantic command/result contract | Equivalent target/context across adapters; old context cannot revive grants |

The runtime facade contains prototypes, and callback/decoder/task contracts are
still open. This handoff deliberately distinguishes a missing contract from a
bug in supported behavior. The existing [D0-D7 order](../../design/redesign_agenda.md)
owns dependencies; the interaction proposal owns promotion order. Research
probes can run now, while production migration waits for the relevant contract.

## Prioritized Discriminators

| Experiment | Compare | Deliverable | Owner/gate | Stop condition |
| --- | --- | --- | --- | --- |
| HX1 | Full proposal invalidation versus selective repreparation | Context/read-set rules and C02/C07 negative fixtures | Interaction; D1/D3 prerequisite for typed public APIs | Reuse can hide changed authority/meaning |
| HX2 | Captured snapshot versus explicitly refreshed inspection | Evidence/truncation/disclosure envelope and C08/C09 fixtures | Interaction/runtime results; D2/D3 | Requires implicit effects or claims unsupported confidentiality |
| HX3 | Draft-plus-commit versus restrictive control | C03 shared-command event fixtures and manual input/accessibility trial | Interaction/tooling; D5 | Valid entry/repair or an accessible path is lost |
| HX4 | Read-only derived values versus bounded inverse adapter | C04 supported subset, alternatives, fallback and preservation contract | Interaction/scoped library; D4/D5 | Must guess source/input intent or invent solver semantics |
| HX5 | Request-only Stop versus request plus observed completion states | C05/C08 state table with local/remote outcomes and cleanup blockers | Resource/task and interaction; D2 | Completion/rollback claim exceeds host evidence |
| HX6 | Exact-span conversion versus structural target plus spans | C01/C10 revision-aware offset/binding mapping fixture | Scalar/parser/tooling; D3 | Text mapping rewrites meaning or guesses a target |
| HX7 | Fail-on-context-change versus explicit reproject/replan | C11 frame/mode/freshness data contract and fake-device traces | Library/host profile; after D3, not a core feature | Physical guarantees inferred from the toy model |
| HX8 | Text versus projected work on interrupted/transfer tasks | C12 pre-registered task protocol and qualitative error evidence | Interaction; D5 | Speed wins only by hiding facts or removing agency |

HX1-HX8 are the live experiment details for this extension, not a competing
cross-project delivery queue. Each must close or refine an existing owner;
repeat philosophical reasoning only when new evidence changes a choice.
