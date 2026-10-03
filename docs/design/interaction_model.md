# Nomi Interaction Model

> Status: designing proposal; no new grammar or public library APIs accepted.

Packet: `docs/research/interfaces/README.md`,
`docs/design/interaction_model_target.nomi`,
`docs/review/2026-09-30-cognitive-interfaces.md`.

Evidence starts at [cognitive foundations](../research/cognition.md) and the
[18 interface threads](../research/interfaces/README.md). This proposal extends
the [language synthesis](synthesis.md); it does not replace [syntax](syntax.md),
[semantics](semantics.md), or [industrial contracts](industrial.md). The
[redesign agenda](redesign_agenda.md) owns broader unresolved design work.

Further evidence: [data/workflow layers](../research/data_workflows/README.md)
and [cross-disciplinary notation](../research/notation_atlas.md) test whether
sets, axes, model references and evidence relations fit this proposal. Their
[research targets](targets/research/README.md) admit no new grammar or exports.

The [human-computation edge atlas](../research/interfaces/edge_cases.md) adds
96 pressure cases across 24 families, with
[twelve composition cases and HX1-HX8](../research/interfaces/composition_cases.md)
and [22 executed local probes](../research/interfaces/experiments.md).
The [philosophical translation](../research/cognition.md) now distinguishes
representation, interpretation, assumptions, all-path obligations, progress,
situated repair, and agency. These sharpen this proposal; they accept no new
syntax or production API and do not establish usability or conformance.

## Thesis And A Real Fork

Nomi could be a checked computational medium whose meaning remains inspectable
through text, values, tables, diagrams, commands, and traces. This is broader
than an editor with decorations and narrower than a universal language of
thought. The unit of coherence is the computation and its contracts, not the
number of interfaces surrounding it.

Two credible directions remain:

| Candidate | Strength | Cost |
| --- | --- | --- |
| Text-primary source with derived views and explicit edits | Reviewable files, Git compatibility, readable fallback, one formatter | Some spatial/domain tasks remain awkward; inverse edits may be unavailable. |
| Structured document as primary program with equally editable projections | Stable structure/identity and domain editing without reparsing text | Storage, merge, interoperability, accessibility, and exporting arbitrary source become first-order problems. |

**Working recommendation:** start text-primary and read-only projections. This
is a reversible experiment, not proof the second direction is inferior. If
source synchronization repeatedly defeats useful domain edits, run a fenced
structured-document experiment instead of forcing every interaction into text.

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

## Ordered Playground Experiments

| Order | Deliverable/owner | Acceptance evidence | Stop or removal condition |
| --- | --- | --- | --- |
| 1 | Language/tool design: invoice model and explicit view contract | Three programs; invalid/stale/duplicate-ID cases; law counterexamples | Inconsistent core contracts: return to typing/decode first. |
| 2 | Tooling: read-only value/dependency projection | Existing artifact IDs; no reexecution; redaction and unsupported fallback | Needs a second evaluator: keep plain inspection. |
| 3 | Frontend: shared Run/Stop/Inspect command adapter | Same operation from button/palette/keyboard; late-response and repeated-Stop tests | Changes current execution semantics accidentally: remove adapter. |
| 4 | Design study: text versus grid/form/diagram | Counterbalanced tasks, error categories, novice/expert/accessibility evidence | Faster only by hiding invalidity or authority: reject. |
| 5 | Tooling spike: one editable literal/input projection | Atomic/stale checks, undo distinction, comments/identity preservation | Arbitrary inverse guessing: remain read-only. |
| 6 | Alternative-design spike if needed | Compare structured primary document on the same tasks and export requirements | No measurable reasoning benefit for added storage/merge cost. |
| 7 | Promotion after settled contract | CLI/browser conformance, sample regression, fresh manifest and browser smoke | Any unsupported target fixture presented as runnable. |

The [HX1-HX8 detail](../research/interfaces/composition_cases.md#prioritized-discriminators)
refines these experiments with explicit candidate forks and stop conditions.
The [real-file handoff](../research/interfaces/composition_cases.md#implementation-handoff)
maps source artifacts, worker generations, result/event records, decode paths,
host declarations, and editor/notebook adapters. The atlas and 22 local probes
do not justify a new evaluator or waiting for every research family to close;
promote one settled contract at a time under the existing D0-D7 gates.

Use the existing [playground plan](../review/2026-09-29-github-playground-agentic-plan.md).
No UI was built and no study was run here. A trial of six to eight varied users
could identify failure mechanisms, but would not establish universal usability.
Pre-register tasks, counterbalance presentation order, retain qualitative repair
accounts, and include assistive-technology testing rather than claiming it from
an automated DOM check.

The [HX8 preparation protocol](../research/interfaces/composition_cases.md#hx8-minimal-study-protocol)
now specifies seven tasks, supplied answer facts, counterbalancing, prediction
and repair scoring, incident categories, and blocked-task reporting. It remains
unperformed. Maintained research tests and capture verification establish the
integrity of those documents and finite models, not empirical success.
