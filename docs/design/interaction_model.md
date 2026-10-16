# Nomi Interaction Model

> Status: designing proposal; no new grammar or public library APIs accepted.

Packet: `docs/research/interfaces/README.md`,
`docs/design/interaction_model_target.nomi`,
`docs/review/cognitive_interfaces.md`.

Evidence starts at [cognitive foundations](../research/cognition.md) and the
[18 interface threads](../research/interfaces/README.md). This proposal extends
the [language synthesis](synthesis.md); it does not replace [syntax](syntax.md),
[semantics](semantics.md), or [industrial contracts](industrial.md). The
[redesign agenda](redesign_agenda.md) owns broader unresolved design work.
The [computational-medium vision](vision.md) supplies the guiding purpose. Its
broader discovery loop can challenge these candidates, the current primary
representation and the assumption that every useful interaction fits this model.

Further evidence: [data/workflow layers](../research/data_workflows/README.md)
and [cross-disciplinary notation](../research/notation_atlas.md) test whether
sets, axes, model references and evidence relations fit this proposal. Their
[research targets](targets/research/README.md) admit no new grammar or exports.

The [human-computation edge atlas](../research/interfaces/edge_cases.md) adds
96 pressure cases across 24 families, with
[twelve composition cases and HX1-HX8](../research/interfaces/composition_cases.md)
and [executed local probes](../research/interfaces/experiments.md).
The [philosophical translation](../research/cognition.md) now distinguishes
representation, interpretation, assumptions, all-path obligations, progress,
situated repair, and agency. These sharpen this proposal; they accept no new
syntax or production API and do not establish usability or conformance.

The [text-interface research](../research/dsls/text_as_interface.md) expands the
working text-primary direction. It separates display, inspection, formatting,
rendering, encoding, parsing and execution; compares language and PowerShell
naming; and supplies T1-T10 plus a
[target-only pressure program](targets/research/text_boundaries.nomi). These are
candidate contracts, not accepted standard-library names.

The [natural-language continuation](../research/interfaces/natural_language.md)
and [target challenger](targets/research/natural_language.nomi) extend this
proposal with roles, segmentation, scope, context, dialogue and localization.
NL1-NL6 and prepared N01-N10 facts refine T1/T9/T10 and HX3/HX8; no natural-language
evaluator, grammatical naming rule or measured usability result is accepted.

The [domain-layer proposal](synthesis.md#domain-layer-proposal) extends the
shared context/evidence/projection boundary across data/time, learning and
documentary domains. Each payload retains its domain owner; graph layout and
common diagnostics do not erase relation, temporal or numeric laws.

## Thesis And A Real Fork

Nomi could be a checked computational medium whose meaning remains inspectable
through text, values, tables, diagrams, commands, and traces. This is broader
than an editor with decorations and narrower than a universal language of
thought. The unit of coherence is a person's reasoning activity, supported by
explicit computations and contracts. The [thinking direction](vision.md#thinking-is-the-shared-design-goal)
asks whether people can form an idea, expose its assumptions, follow consequences,
compare alternatives and revise understanding across representations. The
[scientific continuation](scientific_discovery.md) supplies a demanding pressure
case; neither a common view nor a common graph erases domain-specific laws.

Two credible directions remain:

| Candidate | Strength | Cost |
| --- | --- | --- |
| Text-primary source with derived views and explicit edits | Reviewable files, Git compatibility, readable fallback, one formatter | Some spatial/domain tasks remain awkward; inverse edits may be unavailable. |
| Structured document as primary program with equally editable projections | Stable structure/identity and domain editing without reparsing text | Storage, merge, interoperability, accessibility, and exporting arbitrary source become first-order problems. |

**Working delivery recommendation:** start text-primary and read-only projections.
Compare structured and mixed authoring directly on selected domain tasks; they
need not wait for a text implementation to fail. Source-synchronization costs
are one pressure to investigate, alongside creation, incomplete work and handoff.
The recommendation is reversible and does not choose the winner of that comparison.

Text-primary means exact authored source plus explicit interpretation stages,
not bare strings at every boundary. Bytes decoding, Unicode coordinates,
localized display, machine encoding, trusted templates, source construction and
process invocation remain different operations. A readable fallback is required
in this text-primary candidate even when a richer projection exists. The
structured candidate must expose saved meaning, access and supported export
limits; it need not silently promise arbitrary text round trips. Display output
is never the persistence or execution contract by implication.

## Small Semantic Model

| Concept | Owned fact | Not interchangeable with |
| --- | --- | --- |
| Source revision | Exact checked text/document and edition | Whatever is currently visible in an editor. |
| Binding identity | Resolved declaration/reference relationship | A name string or screen position. |
| Model incarnation | A particular object/history in which revisions have meaning | A revision counter reused after reset or a rendered label. |
| Owned value | Nominal concept after validation | Raw form text, host object, or diagram coordinates. |
| View | Projection of source/value/trace plus presentation state | Another independently authoritative program. |
| Candidate change | Proposed operation against a known revision/target | A committed mutation or capability grant. |
| Evaluation epoch | Source, input snapshot, profile, observations and run identity | Latest edit time or a sequence number alone. |
| Execution action | Explicit authorized effectful work | Re-rendering, invalidation, or replaying a preview. |
| Evidence record | Provenance-tagged static fact, test, observation, or suggestion | A universal proof or model-generated assurance. |

Different identities serve different purposes. A domain row ID is not a source
binding ID; a run ID is not a revision hash. Source-only edits do not necessarily
change domain data, and a form input transaction does not necessarily rewrite
the program. Every command must declare which object it changes.

## Context And Evidence Pressure

The extended invoice target gives Model and Edit an explicit incarnation value
so a reset revision cannot revive a candidate from an old history. These Text
values are fixture tokens, not accepted identity-generation or grant APIs.
Domain identity, model incarnation, source revision, and run epoch remain
different facts. A sorted row keeps its domain identity; restarting a model
does not keep the old edit's validity merely because its revision number recurs.

Two candidates remain open in [HX1](../research/interfaces/composition_cases.md):
invalidate a proposal whenever its context changes, or selectively reprepare
pure checked facts while revalidating all mutable preconditions. Name the actual
read set and semantic owner rather than attach every possible context field to
every command. No cached artifact contains replayable execution permission.
Concrete capability enforcement, including revocation timing for running tasks,
belongs to the effect/task owner.

The target's pure `apply_edit` validates one immutable snapshot and returns a
candidate. It is not a shared-state publication protocol. A serialized owner or
guarded publication must enforce the committed base at the operation boundary;
P19 exposes the race when preparation and unconditional publication are separate.
Forks cannot share the same incarnation/counter as if they were one committed
history. Identity generation, branch identity, crashes, and remote effects are
not settled by that local model.

P21 challenges counter reuse under undo and copied forks; the unchanged-context
case remains valid. Restore values under a new committed context or explicitly
identify a branch. Do not infer global identity from a copied snapshot or impose
a blanket prohibition on pure-result reuse. P22 similarly separates observation
freshness from timestamp comparability: unrelated clocks/boots need a declared
mapping before subtraction, and incomparable evidence is not known stale.

Where policy requires human review, the review scope and current grant are
independent facts. P20 changes a payload/recipient/model while keeping a broad
grant, and revokes a grant while retaining matching review. Exact-proposal review
and explicitly bounded automatic-action policies remain candidates. A digest or
supplied review record establishes neither human understanding nor authenticity.

Evidence also has a context. A candidate record may distinguish source/inputs,
analysis assumptions, observed host outcome, completeness, redaction scope,
and truncation. Unknown external outcome is separate from local cancellation;
partial inspection is separate from incomplete execution. Schema projection
must identify omitted rules and cannot replace actual decoding. These are
proposed envelope obligations, not a new universal evidence type in Core.

Start [HX2](../research/interfaces/composition_cases.md) with captured read-only
results. If a domain needs fresh inspection with effects, expose that as an
explicit action. Opening a view cannot silently refresh host objects, queries,
or live handles. P14 only tests an imposed snapshot policy; real adapters and
privacy guarantees still need their own evidence.

## Knowledge Contexts And Qualified Explanations

The [historical knowledge-framework synthesis](../research/knowledge_frameworks.md)
extends this proposal beyond program traces. The person needs to distinguish a
statement being discussed, a premise being endorsed, a consequence being checked
and an observation being reported. These distinctions refine existing Model,
View and Evidence concepts; they do not introduce one global truth object or
universal ontology.

Keep reasoning context separate from source revision, model incarnation and
execution authority. A context may identify a theory/signature, parameters,
premises, interpretation and method. Bind only the facets the question needs.
Every displayed answer must retain its applicable scope and profile-specific
result; ordinary Bool expressions keep their language meaning.

An explanation view should expose:

- the exact question and interpretation, including identity, negation and any
  completeness assumptions;
- endorsed premises separately from quoted reports, hypotheses and retrieved
  material;
- derivation or observation support and independently supported alternatives;
- unresolved obligations, omitted evidence and the method's resource limits;
- which source, premise or model revision changed the applicability of the answer.

Displaying a statement does not assert it. Opening a captured explanation does
not run its method again. A theory import does not transfer actual permissions.
Replaying a proof requires the matching checker/context; rendering provenance is
not proof replay. A model bridge must retain what it preserves, approximates or
loses, rather than show all translated answers as equivalent.

| Open design fork | Benefit | Cost and discriminator |
| --- | --- | --- |
| One canonical ontology versus context-owned vocabularies | Canonical terms simplify some cross-domain lookups; local vocabularies preserve domain commitments. | Global reconciliation can impose false identity. Compare same labels/different owners and different labels/possibly same entity. |
| Global answer/status envelope versus profile-specific judgments with shared navigation | A common envelope simplifies rendering; typed payloads preserve meaning. | A single status can erase unknown/conflict/search limits. Compare a proof, a closed-snapshot query and an empirical estimate. |
| Monotonic derivation history versus revision-aware current support | History is stable and replayable; current support reflects corrected premises. | A revision needs an explicit policy and all relevant support paths. Withdraw one of two justifications and preserve the other. |
| Automatic model alignment versus explicitly checked correspondence | Automation reduces authoring effort; explicit obligations expose limits. | A plausible match can overclaim equivalence. Require refusal of an unqualified exact-to-float or one-way-to-two-way transfer. |

Prefer context-owned vocabularies, profile-specific payloads and explicit
correspondence for the bounded comparison. This remains a designing candidate;
do not burden a simple program with ontology metadata or claim the remaining
alternatives have been empirically rejected.

Extend HX2/HX8 and SP0 with the dossier's fading-oscillation investigation,
missing-invoice question, conflicting reports and exact-to-numerical conversion.
Match facts across text, structured and mixed views. Score correct scope,
missing-premise diagnosis, alternative comparison, revision and handoff. Show
“no match in this complete snapshot” separately from “not established in this
knowledge context.” No participant trial or general knowledge UI has run.

The [reasoning algebra](reasoning_algebra.md#contexts-interpretations-and-reasoning-methods)
owns R1/R2's binder, premise and bridge experiments. This packet owns whether their
qualified explanations support the person's work. Finite artifact oracles can
check support and context handling; they cannot establish human understanding.

## Candidate Architecture, Not Mandatory Core IR

```text
text or structured draft
  -> lossless recovery -> checked Surface -> Core -> completed result/events
                           |                         |
                      source views              value/trace views
                           |                         |
                    candidate source edit      candidate input/model change
                           |                         |
                       check/commit             decode/validate/commit
```

Existing versioned Surface, diagnostics, and host-capability contracts are
extraction points. Do not make editor layout part of Core, or include a model's
private state in an exported source artifact. A semantic command adapter may
remain tool-owned without becoming a runtime function type.

## Shared Normal Form

The [primitive synthesis](synthesis.md#candidate-primitive-synthesis-and-integration-path)
maps commands/views to explicit candidate values, validation, and owner-controlled
publication. Its next data-platform case requires stable references to lazy
intermediates and passive inspection of contracts/proof obligations. A shared
interface does not erase table grain, missingness, numeric or statistical laws;
each domain retains its semantic owner. No new interaction API is accepted here.

[The invoice target](interaction_model_target.nomi) uses ordinary functions,
nominal data, explicit Result, and proposed collection/decoder APIs. Its three
pressures are a beginner calculation, a production immutable change, and a
failure-heavy submission. The same semantic model could appear as:

- text defining line totals and an explicit fold;
- a grid with input columns and read-only derived totals;
- a dependency diagram with labelled eager data edges;
- a form storing invalid drafts until decode succeeds;
- a command palette applying a quantity change against a revision;
- an explanation tracing a total back to validated inputs.

These views do not require spreadsheet coordinates, global reactive bindings,
graph scheduling, or natural-language evaluation in ordinary source. They may
require better binding identity, source maps, typed metadata, and command
contracts. Those are real language/toolchain obligations, not free UI features.

## Interaction Laws To Falsify

1. Opening or navigating a view never repeats an external action.
2. View reordering preserves selected domain identity.
3. A valid draft becomes owned data only through the declared boundary.
4. A change commits entirely or not at all; stale revisions are explicit errors.
5. A supported projection round trip preserves resolved meaning and comments
   under separate semantic and lossless contracts.
6. Unsupported source remains visible; a view cannot silently delete it.
7. Results retain their epoch; late responses cannot replace a newer run.
8. Keyboard, pointer, palette, and agent adapters invoke the same checked command.
9. Inspection and semantic diff disclose uncertainty and omitted information.
10. No serialization, replay, or source rewrite creates authority.

These laws need counterexamples, not decorative checkmarks. Reformatting can
change source offsets; remapping must preserve references. Arbitrary programs
may have no useful editable diagram. Undo may restore a model snapshot but
cannot guarantee reversal of external effects. Execution budgets may truncate
a trace while leaving the program's result valid; the explanation must say so.

## Command Vocabulary

### Linguistic Roles And Negotiated Intent

Designing hypothesis: keep resolved binding/command identity separate from
lexical sense, semantic role and audience label. Function signatures and named
arguments can expose roles without treating ordinary calls as English phrases.
Domain glossaries may guide optional lint/discovery; they cannot infer types,
effects or authorization from parts of speech. Localized labels and search
aliases route to the same checked command and may require disambiguation.

A dialogue can retain an authored draft and propose an interpretation, but
ambiguous references, quantifier scope and query-versus-request intent remain
explicit missing facts until resolved. A supplied interpretation is untrusted
input, not checked meaning. Explanation/readback is neither authenticated review
nor execution authority. Recheck mutable context at the semantic owner, preserve
unsupported/ambiguous drafts, and never turn a confident paraphrase into action.

Use NL2's same-type role swap and NL4's changed referent as HX8 pressure tasks
after D1-D3 close the actual command contract. Boolean scope/empty-domain facts
remain unchanged; unknown domain evidence is not default false. The prepared
language cases are facilitator facts, not NLP parsing or comprehension tests.

### Stable Commands

Proposed stable command IDs, not implemented exports or shortcut defaults:

| ID | Target/precondition | Completion | Authority |
| --- | --- | --- | --- |
| `nomi.run` | Supported source revision and host profile | Run ID and typed result/diagnostics | Explicit profile grants. |
| `nomi.stop` | A particular active run | Cancellation requested, then joined/stopped or failed | Run ownership, not arbitrary process access. |
| `nomi.inspect` | Artifact/value/trace identity | Bounded redacted projection | Read existing evidence; no reexecution. |
| `nomi.apply_source_edit` | Revision plus resolved target and edit | New checked revision or diagnostic | Document edit authority. |
| `nomi.apply_input_change` | Model/input revision and decoded command | New owned model or expected error | Model edit authority. |
| `nomi.reset_session` | Named session | Explicit reset report | Session ownership; no claim of external undo. |

Toolbars use familiar icons with names; palettes and menus expose command names.
Keybindings are remappable contextual adapters. Do not impose arbitrary chords
before Monaco, browser, OS, keyboard-layout, IME, and accessibility testing.
Commands which cannot run must report why without losing focus or draft input.

## Type, Failure, Effect, And Time Interactions

| Existing contract | Interaction obligation |
| --- | --- |
| Immutable bindings and `var`/`set` | A view distinguishes program binding edits from runtime cell mutation. |
| Nominal data and decode | Input widgets preserve raw drafts; commit uses the actual decoder, not just exported schema. |
| `match` and constraints | Pattern witness views use the checked closed domain; invalid input remains a decode error. |
| Result/panic/cancellation | Source-edit conflict, invalid quantity, runtime panic, and Stop are different outcomes. |
| Effects/capabilities | Pure preview is separate from execution; approvals bind to the exact program/action. |
| Resources/tasks | Inspection does not revive leases; run completion includes cleanup/join obligations. |
| Collections/plans | A diagram labels eager data flow versus a lazy plan; opening it never executes a query. |
| Numeric/text semantics | Views preserve precision and identity; pretty output is not a lossy input codec. |
| Modules/editions | Binding IDs and resolved interface facts are edition/profile-aware. |

Callback typing, derived decoder signatures, region types, and numeric overflow
remain open elsewhere. This packet does not claim to typecheck its target.

## Diagnostics And Formatting

Illustrative diagnostic payload, not a new schema accepted by this pass:

```json
{
  "code": "EDIT_STALE_REVISION",
  "phase": "interaction",
  "message": "This change was prepared for an older invoice.",
  "expected_revision": 7,
  "actual_revision": 8,
  "target": {"kind": "line", "id": "tea"},
  "repair": "Refresh the preview before applying the change."
}
```

Source-related diagnostics additionally need real source spans and binding IDs;
input diagnostics need data paths. Host exception strings are not the primary
explanation. Values and evidence honor existing redaction. The formatter renders
ordinary Nomi, never a hidden diagram serialization inside comments. Narrow
views may wrap labels but cannot change the represented expression.

## Paired Representation And Revision Trial

October 9 planning specification. No interface, user trial or new semantic law
is implemented by this section. Reuse HX8 and its U01-U07 fixtures; the rows
below specify how to compare candidates on the growth journeys without creating
a competing study inventory. D1-D3 still gate claims of checked target behavior.
Paper comparisons and explicitly supplied-fact mockups can proceed earlier.

Candidate T keeps lossless source primary and derives views. Candidate S keeps
a structured document primary with equally usable text import/export. Both get
the same model, diagnostics, command preconditions and available evidence.
Neither gets permission to execute from rendering a view. A read-only fallback
is a legitimate result; an unsupported inverse edit must not be guessed.

| Task and fixed stimulus | Observable outcome in both candidates | Cost to record separately |
| --- | --- | --- |
| Create Tea quantity 2 at 400 and Cup quantity 1 at 700 | Total 1500; explain both contributions | Concepts, setup actions, source/view navigation; no learnability claim from agent judgment. |
| Sort rows, change Tea quantity to 3 | Tea ID changes, Cup remains 1; total 1900 | Target discovery and whether sorting confused identity. |
| Enter quantity text `three` | Preserve draft; explain decode path; committed model unchanged | Recovery actions and whether source/data editing were confused. |
| Request only `make the total 2000` | Expose underdetermined inputs; no invented quantity/price mutation | Clarification and explicit-input selection costs. |
| Apply a revision-7 edit after revision 8 commits | Conflict at publication owner; retain recoverable draft | Explanation, reprepare effort and accidental duplicate actions. |
| Open an unsupported source construct with comments | Preserve exact source or an opaque lossless segment; indicate read-only region | Escape hatches, export/merge failure and comment movement. |
| Inspect old report after an edit; older run finishes late | Old epoch stays visible and never masquerades as current | Reader's prediction of what actually ran and what evidence is missing. |
| Stop after remote publication loses acknowledgment | Local state and unknown remote outcome remain distinct | Whether the reader incorrectly predicts rollback or safe blind retry. |
| Repeat with keyboard, screen reader and active IME draft | Same target/command meaning; composition/cancellation retains input | Blocked tasks, focus loss and assisted versus unassisted completion. |

For S, export/import and a stale concurrent text edit are mandatory tasks, not
optional infrastructure deferred until after a favorable demonstration. A
structured document needs a declared merge owner and durable identity story.
For T, lossless parsing and editable-literal selection are mandatory before
claiming inverse source edits; syntax offsets alone are not stable identity.
Neither candidate may count replacing unsupported code with a generated stub
as a successful round trip.

Predictions are made before showing outcomes. Record correctness of target,
value, effects, epoch and repair; then record time/actions and qualitative
confusion. Unsupported tasks remain in the results, not removed as outliers.
Use the existing counterbalanced HX8 protocol; this paper pass has no participants
and establishes no empirical winner. Continue T as the cheaper reversible first
implementation trial. Trigger S if T repeatedly needs lossy/ambiguous rewrites
for the selected useful task, and compare both before adopting a storage format.

### Binding Syntax And Notebook Re-execution

Keep the current target `var`/`set` while comparing simpler reassignment under
the same closure and revision questions. This is an open experiment, not a
policy toggle that changes source meaning.

```nomi
var quantity = 2
read_quantity = () => quantity
set quantity = 3
```

Under accepted mutable-cell capture, calling read_quantity now observes 3.
Contrast immutable `quantity = 2` followed by a nested scope's new quantity:
the existing closure retains the original binding and observes 2. The simpler
candidate `quantity = 2; ...; quantity = 3` must say whether it updates one cell
or creates a new binding before its syntax can be compared fairly. Keep it in
metalanguage until such a rule is selected; checking policy cannot choose it.

Notebook revision is a separate axis. Compare whole-cell re-execution creating
a fresh evaluation epoch with explicit updates of persistent session cells.
An old closure/task does not silently acquire the new binding merely because
the name is unchanged. Dependency invalidation must say which results are
historical and whether recomputation is requested. Never rerun effectful cells
merely to make a projection current. Record rename, shadowing, reset, an old
closure held by a task, and an invalid new draft as the minimum counterexamples.
Prefer fresh-epoch re-execution for the first trial; persistent mutation remains
an explicitly different session operation, pending a notebook contract.

### Domain Challengers With Owned Payloads

Use the same import/report data for a table and a rendered document. The table
owns schema, row identity, ordering and null/duplicate policy. The document owns
layout, escaping, reference/version identity and exported form. Share source/
value epochs and change descriptions only where they mean the same thing.
A cell reordering is not a document rewrite or a database transaction. A
document's display string is not its machine codec.

One shell variant consumes an explicit argument vector and one AI-assisted
variant proposes an input/source change. Both retain preview versus execution,
current grants and unknown external outcome. Neither needs a new language
keyword or a universal graph executor. Add scheduling or collaborative editing
only if this pair fails to expose a specific ownership/time distinction.

## Ordered Playground Experiments

This order is the reversible delivery baseline. Matched authoring comparisons
can run alongside it; their preparation does not require delivery steps to fail.
Promotion into a supported playground still needs the selected source and
execution contracts.

| Order | Deliverable/owner | Acceptance evidence | Stop or removal condition |
| --- | --- | --- | --- |
| 1 | Language/tool design: selected invoice model and explicit view contract | Beginner/change/submission fixtures; invalid/stale/duplicate-ID cases; law counterexamples | Inconsistent core contracts: return to typing/decode before promoting execution. |
| 2 | Tooling: read-only value/dependency projection | Existing artifact IDs; no reexecution; redaction and unsupported fallback | Needs a second evaluator: keep plain inspection. |
| 3 | Frontend: shared Run/Stop/Inspect command adapter | Same operation from button/palette/keyboard; late-response and repeated-Stop tests | Changes current execution semantics accidentally: remove adapter. |
| 4 | Design study: text versus grid/form/diagram | Counterbalanced tasks, error categories, novice/expert/accessibility evidence | Faster only by hiding invalidity or authority: reject. |
| 5 | Tooling spike: one editable literal/input projection | Atomic/stale checks, undo distinction, comments/identity preservation | Arbitrary inverse guessing: remain read-only. |
| 6 | Structured/mixed authoring comparison alongside delivery | Compare primary representations on matched model/tasks and declared export limits | No measurable reasoning benefit for added storage/merge cost. |
| 7 | Promotion after settled contract | CLI/browser conformance, sample regression, fresh manifest and browser smoke | Any unsupported target fixture presented as runnable. |

The [HX1-HX8 detail](../research/interfaces/composition_cases.md#prioritized-discriminators)
refines these experiments with explicit candidate forks and stop conditions.
The [real-file handoff](../research/interfaces/composition_cases.md#implementation-handoff)
maps source artifacts, worker generations, result/event records, decode paths,
host declarations, and editor/notebook adapters. The atlas and local probes
do not justify a new evaluator or waiting for every research family to close;
promote one settled executable contract at a time under the existing D0-D7 gates.
Those gates govern the promise being promoted, rather than admitting discovery.

Use the current [playground roadmap](../orientation/project_roadmap.md).
The runtime UI does not establish these proposed interaction laws or human benefit. A trial of six to eight varied users
could identify failure mechanisms, but would not establish universal usability.
Pre-register tasks, counterbalance presentation order, retain qualitative repair
accounts, and include assistive-technology testing rather than claiming it from
an automated DOM check.

The [HX8 preparation protocol](../research/interfaces/composition_cases.md#hx8-minimal-study-protocol)
now specifies seven tasks, supplied answer facts, counterbalancing, prediction
and repair scoring, incident categories, and blocked-task reporting. It remains
unperformed. Maintained research tests and capture verification establish the
integrity of those documents and finite models, not empirical success.

The [creative timing continuation](../research/interfaces/music_timing.md#bounded-model-experiment)
executes a separate supplied-model profile. Identical initial schedules diverge
under beat versus absolute-time rules; retained runs keep their old model basis;
local Stop may leave an unmatched note-on. These observations motivate explicit
model/revision/delivery explanations. They do not implement shared adapters,
acknowledged release, source/timeline authoring or any HX human comparison.

The [U01-U07 fixture set](../research/interfaces/study_cases.json) keeps supplied
facts, hidden controls, and answer keys distinct. P23's identical observations
with different hidden action outcomes guard against grading unknown as either
definite success or definite non-action. Blocked tasks, assisted trials, and
unassisted timings need separate reporting; no automatic grader is accepted.
