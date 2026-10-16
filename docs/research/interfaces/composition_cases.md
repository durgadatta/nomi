# Interaction Composition And Implementation Experiments

> Status: designing research experiments and implementation handoff; illustrative
> APIs are unaccepted and unexecuted. Updated 2026-10-04.

This is the experiment detail for the [edge atlas](edge_cases.md), within the
existing [interaction proposal](../../design/interaction_model.md) and
[current-to-target bridge](../../review/cognitive_interfaces.md#current-evidence).
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
| C01 | Sort + collaboration + source-directed repair | H01, H22, H23, H45, H77 | P01, P12, P15, P19 |
| C02 | Reset + cached artifact + changed authority | H06, H47, H70, H71, H90 | P02, P10, P20, P21 |
| C03 | Incomplete draft + IME + accessible command | H09, H13, H41, H73, H76, H79 | P03, P16 |
| C04 | Inverse view + rounding + omitted constraint | H15, H16, H38, H40, H44 | P04, P13 |
| C05 | Stop + lost response + changed retry | H29, H54, H69, H71, H72, H87 | P09, P11, P23 |
| C06 | Algebraic rewrite + evidence domain + progress | H25, H49, H52, H66, H68 | P05, P06, P07, P08 |
| C07 | Converged draft + domain invariant + reviewed proposal | H14, H30, H40, H45, H46, H47, H48, H63 | P02, P10, P12, P19, P20, P21 |
| C08 | Reactive result + notebook history + late completion | H04, H33, H34, H35, H36 | P09, P14 |
| C09 | Observation + privacy + bounded explanation | H24, H64, H74, H89, H91 | P14, P23 |
| C10 | Internationalized input + source mapping + rename | H09, H42, H77, H78, H80 | P15, P16 |
| C11 | Spatial projection + frame reset + stale control | H53, H55, H81, H82, H83, H85, H86, H88 | P17, P18, P22 |
| C12 | Beginner success + interrupted work + model revision | H60, H62, H93, H94, H95, H96 | Human study required; P23 checks one supplied control |

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

Where application policy requires review, retain its actual scope: action,
recipient, payload, and relevant model facts. A current `publish` grant does
not establish that the person reviewed a changed recipient or payload. Compare
exact-proposal review with an explicitly bounded automatic-action policy;
neither can turn review into a capability. P20 only imposes the first policy.
Approval authenticity, expiration/consumption, delegation, and in-flight
revocation remain separate dependencies, not properties of a digest or button.

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

P23 supplies a missing epistemic control: a request lost before delivery and
an acknowledgment lost after action have identical visible unknown/Stop-requested
records but different hidden action counts. The capture exposes both worlds for
research review; a study interface must not reveal the hidden count as evidence.
Neither "nothing happened" nor "it definitely happened" follows. New provider
evidence can refine that outcome; no universal reconciliation API is assumed.

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

There is also a publication race before any merge. Two calls to the invoice's
pure `apply_edit` can return valid revision-8 candidates from revision 7.
Returning `Ok` does not publish either one to shared state. In P19, four of six
prepare/publish orders accept both candidates if publication is unconditional.
An imposed atomic revision check at publication accepts one in all six orders.

Compare a serialized model owner with version-guarded publication. Specify the
operation boundary, target incarnation, read set, response, and unchanged state
on rejection. A strict-freshness owner must not acknowledge two successors of
the same committed base as if both were the current revision. Forked histories
need distinct branch/commit identity; copying the incarnation and revision
counter alone does not distinguish them. No locks, storage, or identity service
are implemented here.

P21 supplies those two missing examples: undo restores the old quantity and
counter under a different commit, and a copied branch shares incarnation/counter
but contains another successor. Keep publication history distinct from value
history; one candidate restores values through a new commit, another names a
distinct branch/commit context. Unchanged context must still be accepted.
Selective reuse of a pure result is not reuse of execution/review permission.

Herlihy and Wing supply a primary treatment of concurrent histories and
linearizability, not a proof of this candidate. The paper's operation-history
boundary is the distinction needed beyond a sequential pre/postcondition.
[Primary paper, introduction and section 2](https://www.cs.cmu.edu/~wing/publications/HerlihyWing90.pdf).
MITRE also describes the broader
[time-of-check/time-of-use failure pattern](https://cwe.mitre.org/data/definitions/367.html).
This is a research counterexample, not a discovered vulnerability in Nomi.
Local publication does not atomically commit a remote action or settle grant
revocation timing; those still belong to the executor/resource contracts.

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

P22 adds a timestamp-domain challenger: equal-looking ticks from another clock
or previous boot are incomparable without a declared mapping. Distinguish stale,
incomparable, and invalid-future evidence; do not report all denied observations
as old. Compare same-clock-only intervention with a mapping carrying offset/skew
bounds and provenance. Uncertainty can prevent intervention without claiming the
sample is definitely stale. Physical freshness still needs real host evidence.

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

### HX8 Minimal Study Protocol

Status: proposed formative protocol; no participants, interface trial, or
statistical result. This closes a preparation gap, not HX8's empirical question.
The tasks and scoring below are original Nomi study design. W3C recommends
involving people with disabilities while retaining standards-based evaluation;
individual user results do not establish general accessibility.
[W3C evaluation guidance](https://www.w3.org/WAI/test-evaluate/involving-users/).

**Conditions and prerequisites:** compare A, text plus plain result/diagnostic
records, with B, the same source/results plus a read-only named-input table.
Both expose identical semantic facts and use the same commands and evidence.
An editable projection is a later condition only after its supported subset
and commit contract exist. A mockup may study interpretation of supplied facts;
it cannot establish execution or adapter conformance. Do not run an ambiguous
or inconsistent fixture and score the resulting confusion as a participant bug.

Use fresh snapshots for each task. The baseline invoice has tea quantity 2 at
400 minor units and cup quantity 1 at 700, total 1500. Currency is fixed outside
this toy model. Pre-register parallel fixtures and check their answers before
using them to reduce repetition/learning effects.

The [machine-readable stimuli and answer facts](study_cases.json) provide one
versioned original U01-U07 set. They are preparation fixtures, not Nomi syntax,
a public result schema, a human grader, or an executed study. Tests check their
arithmetic, identity/draft/context controls, references, and evidence scope.
Only each task's `provided` record is participant-visible: prompts and answer
keys must not accidentally disclose `facilitator_only` or `expected` facts.
Both conditions must receive the same supplied facts, not a richer explanation
in the projected condition. Record any extra help as a treatment difference.

U05 has two hidden-world controls with the same visible unknown observation:
zero actions after lost delivery, one action after lost acknowledgment. P23
checks that equivalence in the supplied model. Grade the uncertain answer, not
the hidden truth. U06 has partial and complete trace controls; the full trace
contains a handled failure hidden by the three-event projection. This prevents
teaching that every shortened trace necessarily implies a failure, or that a
completed execution necessarily supplies complete inspection.

| Task | Prompt or perturbation | Answer facts required by the supplied model | Error to retain |
| --- | --- | --- | --- |
| U01: prediction | Change tea quantity to 3; predict before running | Tea becomes 1200, cup stays 700, total becomes 1900 | Wrong dependency or accidental cup change |
| U02: draft repair | Enter blank, minus sign, `3x`, then valid 3 | Raw drafts survive; committed quantity stays 2 until explicit valid commit | Lost draft, invalid owned value, unintended execution |
| U03: identity | Display cup before tea, then edit tea | Same tea ID changes; cup quantity stays 1 | Positional retargeting |
| U04: context | Apply a revision-1 edit from invoice-a to revision-1 invoice-b | Different history rejects; invoice-b remains unchanged | Number-only freshness or partial commit |
| U05: responsibility | Review a publication, lose its acknowledgment, then change recipient/payload | Previous external outcome remains unknown; current grant alone cannot satisfy the imposed exact-review policy | False no-action/undo claim or reused endorsement |
| U06: evidence | Show three of five trace events beside a completed result | Two events are omitted; partial explanation alone proves neither absent failures nor incomplete execution | Complete-proof claim from the shortened trace |
| U07: transfer | Interrupt work, then request a second currency/domain | Recover the target/context; expose the fixed-currency assumption and revise the model before combining unlike amounts | Correct arithmetic used as evidence of the wrong domain |

**Procedure:** record prior programming/domain experience and the participant's
chosen input/assistive setup, using voluntary self-description. Also record prior
exposure to this public fixture/answer set; pre-register how exposed trials enter
the analysis instead of quietly excluding them. Obtain agreement
to the tasks and recording, allow stopping or declining a task, and use only
fictional local data and fake publication events. Pre-register retention and
access to study notes; avoid collecting client code, secrets, or unnecessary
personal data. This is a method proposal, not an ethics/compliance certification.

Allocate AB and BA presentation order deliberately. Use matched parallel tasks,
record the allocation, assistance, interruptions, and deviations; counterbalancing
does not eliminate learning or recruitment bias. Ask for a prediction and reason
before Run/Commit, then ask what evidence would change the answer. Preserve the
person's initial interpretation and subsequent repair rather than only the final
successful state. Include creation, review, and repair; do not treat experienced
users as a substitute for novice or assistive-technology workflows.

**Scoring and records:** pre-register examples for each score and incident type,
then independently code a subset and retain disagreements before reconciling
them. Do not silently rewrite the rubric after discovering a preferred view.
For each answer record 2 for the required facts plus a
supported explanation, 1 for a correct answer with incomplete reasoning, and 0
for an incorrect claim. Appropriate uncertainty counts as correct on U05/U06;
confidence alone is not evidence. Separately record wrong-target, wrong-context,
implicit-action, lost-draft, false-evidence, and wrong-domain incidents, along
with completion time, assistance, input path, and recovery steps. Do not average
a critical incident away in a speed score.

Each study row needs an anonymous session ID, task/fixture version, condition,
order, supplied source/model/run context, initial answer, cited evidence,
observed command/state changes, assistance, incident category, repair, and any
blocked step. Keep a task blocked by focus/input/accessibility failure as a
design outcome in that setup, not silently as an excluded participant. Publish
pre-registered exclusions and limitations alongside results. Quotes/transcripts
need the participant's agreed recording scope.

Mark blocked/unattempted answers separately from incorrect answers; report
both attempted and assigned denominators and the blocking reason. Do not infer
that a blocker is caused by the representation alone: browser, assistive setup,
content, training, and task framing are competing explanations. Check known
barriers before recruitment and include baseline input/setup checks. Facilitated
think-aloud observations and unassisted timing trials are different evidence;
do not pool their task times into a speed claim. These controls refine the
W3C-linked method limits, not an executed conformance assessment.

**Decision gate:** retain B only if its new relationships are understood without
losing identity, context, uncertainty, or agency; otherwise revise it or keep A.
Report task-level qualitative mechanisms and observed differences. A small
convenience pilot cannot support population-wide superiority, broad causal
claims, or accessibility certification. If all conditions support the wrong
domain model, revise the model rather than choosing the faster interface.

### C12 Advisory Reliability And Calibrated Reliance

Status: additional HX8 research protocol, not an executed study or another
prepared fixture set. U01-U07 remain the only supplied HX8 answer fixtures.
The sequences below are hypothetical stimuli that need independent answer
review and piloting before recruitment. They do not establish the accuracy of
an agent, compiler, linter, or Nomi interface.

The current protocol separates confidence from evidence on an individual task.
The additional question is whether repeated useful advice changes what a person
checks later. **Linguistic certainty**, **a person's reported confidence**,
**a tool's measured reliability on a stated population**, and **appropriate
reliance on this task** are different facts. A confident label or numerical
score cannot substitute for any of the others. Missing advice is not a complete
negative check; advice that conflicts with an independent observation cannot
be treated as authoritative merely because earlier advice was correct.

Skitka's primary NASA report describes five studies of automated decision aids,
including a student simulation comparing monitoring with and without an aid and
one-/two-person conditions. It distinguishes missed events when an aid supplies
no cue from following an erroneous recommendation. This motivates separate
omission and commission controls; it neither measures programming tools nor
establishes Nomi's error rates or an inevitable decline in human skill.
[Primary report, methods and results](https://ntrs.nasa.gov/api/citations/19980048379/downloads/19980048379.pdf).
The report's populations, task workload, supplied instrument accuracy and
experimental reliability matter. Do not copy their quantitative results into
a claim about contemporary agents or this study.

| Scenario | Same ordinary computation | Additional research pressure |
| --- | --- | --- |
| Beginner | Predict the invoice total before changing tea quantity | A useful hint becomes a habit; later a hint names cup instead of tea while the original request remains visible. |
| Production | Review a prepared publication with explicit recipient, payload and revision | After several correct summaries, the advice says the recipient is unchanged although the supplied candidate differs. |
| Failure-heavy | Repair invalid input and inspect a bounded result before a new action | A warning is absent despite a supplied invalidity, or advice says to retry while the retained remote outcome is unknown. |

Counterexamples to a successful-looking design:

- Nineteen accurate suggested edits precede one wrong-target edit. The change
  is typed, fresh and authorized; the reviewer stops comparing it with the
  authored request. Formal correctness and current permission do not settle
  whether the person checked or intended the target.
- A linter emits no warning on a case outside its supported check set. The
  person treats silence as evidence that every relevant condition was checked.
  Disclosure of unsupported coverage must not resemble a successful check.
- Advice and its explanation both come from the same analysis. Presenting them
  as two corroborating sources can encourage false confidence. Shared origin
  does not make either false, but it does not provide independent confirmation.
- A cautious user rejects correct advice because the interface advertises every
  suggestion as uncertain. Avoiding all automation is not the success criterion;
  correct acceptance and justified rejection must both remain possible.

**Alternatives:** no advice with the same underlying facts; advice plus its
stated basis; or advice plus a task-specific evidence comparison before review.
An imposed comparison is a candidate, not a requirement to add a confirmation
dialog to every reversible edit. Its time, attention and habituation costs must
be measured. Warning density and forced clicks are not evidence of verification.

**Bounded method:** select one scenario and one comparison, rather than combine
all three with every representation. Prepare disjoint matched sequences of
fictional local tasks. For example, a pilot sequence may contain twenty-four
reviews, including two suggestions contradicted by supplied evidence and one
omitted warning. Those counts are an original stimulus proposal, not observed
error rates, a sufficient sample size or a recommended production reliability.
Vary advice availability while holding the task facts and commands fixed;
counterbalance error position/order and record training, workload, interruption
and prior exposure. Disclose to participants that advice can be fallible and
use the study's agreed recording/debriefing protocol. An ethics review, if
required for the chosen setting, is not replaced by this paragraph.

Record advice accepted/rejected, the task decision, which independently supplied
facts were consulted, reported confidence, wrong-target/action incidents, missed
anomalies and repair. Distinguish justified reliance from lucky correctness.
Report critical error opportunities and their denominators separately from
routine successes; average accuracy can hide a rare consequential error. An
absent cue with a complete negative check and an absent cue with an unsupported
check are paired controls, not equivalent meanings. If the experiment varies
both reliability and presentation, identify that confound rather than attribute
every difference to language. Small pilots reveal mechanisms, not population
calibration curves or proof that automation degrades expertise. Longer-term
skill retention requires a separately justified longitudinal design.

**Candidate normal form and layer:** retain authored intent and source/input
context; attach advisory origin, analysis scope and evidence basis where the
owner can establish them; compare or request missing facts; form an ordinary
typed candidate; then use the existing review/current-authority/commit boundary.
Advice remains tool-owned input, not Core truth or a new source operator. A
source-linked explanation may name `ADVICE_EVIDENCE_CONFLICT` or
`CHECK_COVERAGE_UNKNOWN` as illustrative diagnostic facts; these are not accepted
stable codes. Inspecting an old suggestion must reveal its basis without
rerunning the program. Never label an unmeasured model score a calibrated
probability or manufacture a history of checks from an approval click.

**Falsifiers/removal:** reject the candidate presentation if it raises unjustified
acceptance, conceals omitted coverage, encourages treating correlated claims as
independent evidence, or makes valid repair inaccessible. Remove a forced-check
step that adds clicks without improving verification or that blocks ordinary
low-risk work without a stated policy. Retain contrary evidence: a plain view
may support better review, and more explanation may increase reliance without
increasing correct understanding. These outcomes refine HX8 and the
[linguistic confidence boundary](natural_language.md#grounding-reliance-and-shared-understanding).

### C12 Team Handoff And Distributed Understanding

Status: unperformed HX8 extension. A reviewed/converged document and an
authentic approval do not establish who knows which assumption, which check
someone performed, or which unresolved work a successor owns. This is distinct
from C07's merge validity and publication race, and from current capability
enforcement. Communication acknowledgment, comprehension, assigned work,
completed checking and execution permission must remain separate claims.

Hollan, Hutchins and Kirsh's primary distributed-cognition article proposes
studying cognition across people, artifacts and their environment rather than
only an isolated desktop user. The author-hosted search extraction exposed the
abstract/introduction; the full PDF fetch failed in this pass. It supports a
framework-level research lead, not a checked account of every case or a measured
handoff benefit. [Primary article](https://interactivity.ucsd.edu/articles/DCog/DCog.pdf),
[author publication index](https://pages.ucsd.edu/~ehutchins/vitae/pubs.htm).
Clark and Brennan's grounding source in the
[natural-language dossier](natural_language.md#selected-evidence-and-limits)
provides a neighboring communication lens. Neither source makes a signed
receipt proof that the recipient understood all relevant assumptions.

| Scenario | Split knowledge or ownership | Required research distinction |
| --- | --- | --- |
| Beginner | One person changes quantities; another checks prices and resumes the calculation | A visible total does not disclose which inputs each person checked or who owns an unresolved price. |
| Production | A preparer knows the currency policy; a reviewer receives the invoice and publication candidate | Source/approval convergence differs from transfer of the fixed-currency assumption and relevant check scope. |
| Failure-heavy | A new operator inherits completed, blocked and remotely uncertain work after interruption | Assignment of recovery differs from knowledge of the old outcome, authority to retry and actual completed checks. |

Counterexamples:

- Both reviewers assume the other verified the recipient or currency. Both
  approvals are genuine and current; nobody performed that domain check.
- A handoff says "validated" without naming the schema, revision or omitted
  cross-field rule. The successor correctly reads the document but attributes
  a stronger guarantee than the completed check supports.
- A checklist says a check is assigned to a colleague; a summary presents it
  as completed. The record has lost a responsibility state, not merely a label.
- A recipient acknowledges a summary but cannot see a redacted input or query
  result needed to assess it. Receipt is observable; comprehension of the hidden
  fact is not. Clarification must not leak that fact to prove shared awareness.
- A successor repeats a publication because the earlier operator is unavailable
  and the local task has ended. Neither team membership nor handoff receipt
  resolves the retained unknown remote outcome.

**Alternatives:** ordinary source/result records; a revision-bound handoff
summary that names checked, pending, disputed and unknown facts; or that summary
plus explicit acknowledgment of assigned next work. These are competing tool/
application protocols, not a universal mandated checklist. A useful short
handoff may disclose only the assumptions the next task needs. Duplicating every
trace into every person's view can impose cost and violate disclosure policy.

**Bounded method:** recruit pairs for one fictional scenario, record relevant
experience and communication/input setup, and assign disjoint task information
deliberately. Do not withhold a fact then grade its unknowable answer as an error.
Use separate cases where the missing fact can be requested, remains unavailable,
or is intentionally outside the recipient's disclosure scope. Compare matched
plain-record and scoped-handoff conditions; counterbalance role/order and permit
clarification or refusal. A tabletop supplied-fact mockup can investigate
interpretation now; it cannot establish a real collaboration adapter's behavior.

Before any proposed action, ask each person what was checked, what remains
unknown, what they believe the partner checked, and who owns the next step.
Use the facilitator's actual supplied check history to score those different
claims. Record unsupported beliefs about another person's knowledge, duplicated
work, unperformed required checks, changed assumptions, requests for information
and repair. Keep timing, communication volume, assistance and social pressure
separate from correctness. Dyads are linked observations, not two independent
samples; participant- and pair-level analyses need a justified design. Think-aloud
or explicit questioning can itself improve handoff, so do not pool it with
unassisted performance or claim that a prompted finding arose spontaneously.

**Candidate normal form and layer:** a library/tool record refers to an artifact
revision and a named check/question; it can distinguish a supplied assertion,
observed completed check, pending assignment, contested result and unavailable
evidence. Its owner and intended recipient are task facts, not implicit access
rights. A recipient may accept assigned work or request clarification; only
the owning domain protocol can establish completion and current authority.
Immutable data and ordinary functions suffice for the research long form; no
new source syntax, common-knowledge type or global "understood" bit is proposed.
Illustrative diagnostic facts are `HANDOFF_CHECK_SCOPE_STALE` and
`REQUIRED_CHECK_UNASSIGNED`, with the exact artifact, scope and missing fact.
Use C09/HX2's bounded/redacted inspection; preserve contested and historical
records rather than rewrite a disagreement as unanimous approval.

**Falsifiers/removal:** reject a handoff representation that encourages false
beliefs about completed checks, silently assigns work, retargets approval,
discloses protected evidence, or treats acknowledgment as comprehension. Remove
metadata that costs more coordination than it saves on the selected task.
Acknowledge a negative result where partners with plain artifacts detect the
gap more reliably. Social incentives, hierarchy, workload and language context
are competing explanations; authentic records cannot certify shared intent.
This extends HX8 under the existing packet and
[collaboration thread](distributed_collaboration.md), not a new distributed
runtime or second task backlog.

## Implementation Handoff

These are read current extraction points, not claims that the proposed contract
is implemented. Keep experimental metadata out of Core until a semantic owner
needs it; no second universal IR or evaluator follows from this research.

| Existing surface | Observed current fact | Small reversible next slice | Conformance evidence before promotion |
| --- | --- | --- | --- |
| [web/app.js](../../../web/app.js) | Request IDs, pending replies, worker generations; Stop terminates/restarts worker | Explicit run/result context and state adapter after C02/C05/C08 rules settle | Old-worker replies, repeated Stop, timeout/restart, result retention; no claim of resource join from worker termination |
| [web/runtime.js](../../../web/runtime.js), [cells.js](../../../web/cells.js) | Result tabs, run/reset/cancel UI and cell model | Read-only captured projection using existing result contract | Navigation emits zero execution actions; C03/C09 focus/draft/truncation tests and manual accessibility trials |
| [runtime/api.py](../../../prototype/runtime/api.py) | ExecutionResult and InspectionResult facades | Tool-owned evidence/epoch envelope around completed results | CLI/browser serialize the same evidence facts; unknown-version behavior |
| [runtime/session.py](../../../prototype/runtime/session.py) | Persistent bindings and lowered-AST cache keys | Keep parse cache identity separate from session/run/input observation identity; name a model publication owner separately | C02 reset/incarnation, C07 same-base publication and C08 notebook-history fixtures; a pure candidate is not a shared-state commit |
| [runtime/diagnostics.py](../../../prototype/runtime/diagnostics.py) | Passive diagnostics/events, IDs, parent IDs, redaction metadata | Define one bounded observation envelope in the owning protocol | C09 zero extra effects, explicit truncation, export redaction; fixture results do not imply full information-flow security |
| [runtime/decode.py](../../../prototype/runtime/decode.py) | Decode error/path records | Draft/raw-value adapter plus actual decoder commit boundary after codec design | C03/C04 invalid drafts, omitted projected rules, unchanged committed state |
| [runtime/host_capabilities.py](../../../prototype/runtime/host_capabilities.py) | Declared host-call names/manifest checks | Separate declared support, current concrete grants, and application-required review scope | C02/C07/C11 denied/revoked/narrowed authority and changed review target/payload; today's manifest is not that grant system |
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
| HX1 | Full proposal invalidation versus selective repreparation | Context/read-set/review-scope rules and owner-enforced publication with C02/C07 negative fixtures | Interaction; D1/D3 prerequisite for typed public APIs | Reuse or check-then-publish can hide changed authority/meaning |
| HX2 | Captured snapshot versus explicitly refreshed inspection | Evidence/truncation/disclosure envelope and C08/C09 fixtures | Interaction/runtime results; D2/D3 | Requires implicit effects or claims unsupported confidentiality |
| HX3 | Draft-plus-commit versus restrictive control | C03 shared-command event fixtures and manual input/accessibility trial | Interaction/tooling; D5 | Valid entry/repair or an accessible path is lost |
| HX4 | Read-only derived values versus bounded inverse adapter | C04 supported subset, alternatives, fallback and preservation contract | Interaction/scoped library; D4/D5 | Must guess source/input intent or invent solver semantics |
| HX5 | Request-only Stop versus request plus observed completion states | C05/C08 state table with local/remote outcomes and cleanup blockers | Resource/task and interaction; D2 | Completion/rollback claim exceeds host evidence |
| HX6 | Exact-span conversion versus structural target plus spans | C01/C10 revision-aware offset/binding mapping fixture | Scalar/parser/tooling; D3 | Text mapping rewrites meaning or guesses a target |
| HX7 | Fail-on-context-change versus explicit reproject/replan | C11 frame/mode/freshness data contract and fake-device traces | Library/host profile; after D3, not a core feature | Physical guarantees inferred from the toy model |
| HX8 | Text versus projected work on interrupted/transfer tasks | Execute the C12 protocol with U01-U07 answer facts, incident/blocked-task records and qualitative repair evidence | Interaction; D5 | Speed wins only by hiding facts, removing agency, or excluding blocked input paths |

HX1-HX8 are the live experiment details for this extension, not a competing
cross-project delivery queue. Each must close or refine an existing owner;
repeat philosophical reasoning only when new evidence changes a choice.
