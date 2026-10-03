# Human Computation At The Edges

> Status: research coverage and original counterexamples; no new language forms
> or interaction APIs accepted. Expanded 2026-10-02.

This atlas extends the [18 interface threads](README.md), the
[cognitive foundations](../cognition.md), and the
[orthogonal DSL models](../dsls/orthogonal_models.md). It belongs to the existing
[interaction packet](../../design/interaction_model.md), whose
[invoice target](../../design/interaction_model_target.nomi) supplies a shared
normal form. The [composition experiments](composition_cases.md) turn selected
combinations into implementation questions; [local probes](experiments.md)
provide bounded counterexamples.

## Coverage And Evidence

"All human interaction with computation" is a direction for discovery, not a
completeness claim. Here are 96 pressure cases across 24 families. The first 18
reuse their linked thread's evidence; six additional families bring selected
standards and papers. Every numbered case is an original Nomi hypothesis, not
an observation that the cited system has that bug. Standards establish specific
mechanisms; they do not establish usability or certify a Nomi implementation.

The family boundaries overlap deliberately. A voice-controlled spreadsheet is
both a grid and a multimodal interface. A paper form scanned by a camera is a
document, an uncertain measurement, and an authority boundary. Copying the same
case into three independent backlogs would obscure that composition.

Use this sampling frame before claiming coverage:

| Axis | Cases to vary |
| --- | --- |
| Person | Novice, expert, returning user, reviewer, collaborator, person using assistive technology, person under interruption |
| Act | Name, transform, model, choose, repeat, fail, touch the world, understand |
| Medium | Text, table, form, diagram, timeline, dialogue, gesture, audio, physical object, spatial scene |
| Phase | Draft, recovered, checked, proposed, committed, scheduled, running, observed, compensated |
| Knowledge | Known, absent, invalid, incomplete, contradictory, inferred, measured, assumed |
| Time | Immediate, delayed, reordered, duplicated, concurrent, expired, offline, restarted |
| Authority | None, narrowed, granted, revoked, delegated, contested, profile-unsupported |
| Scale | Empty, singleton, duplicate, large, unbounded, cyclic, lossy, version-mismatched |
| Repair | Correct input, choose a model, refresh evidence, reconcile, retry, compensate, stop, retain uncertainty |

Pairwise sampling is an economical starting point, not proof that higher-order
interactions are safe. Start with the invoice, import/report, and cancellation
job. Add a spatial/control model only when it reveals a missing distinction.

## 1. Spreadsheets And Grids

Evidence owner: [spreadsheets](spreadsheets.md) and
[data source forms](../data_workflows/source_forms.md). Destination: collection
contracts and editor projections, not coordinate variables in core.

| ID | Trigger | Fact to preserve | Candidate outcome or falsifier |
| --- | --- | --- | --- |
| H01 | Sort/filter rows after selecting a quantity | Domain identity differs from displayed position | The command still targets the same line ID; positional retargeting falsifies the view. |
| H02 | Copy a formula across a hidden subtotal row | Dependency and selection scope are explicit | Preview names selected domain fields; accidental subtotal inclusion is an error. |
| H03 | Two imported rows share an ID but display different labels | Duplicate identity is invalid, not a layout collision | Decode reports both paths before any model commit. |
| H04 | A derived cell shows an old result while inputs are edited | Result belongs to an input/source epoch | Mark the old epoch; never present it as a result of the new draft. |

## 2. Shells And Invocation

Evidence owner: [command shells](command_shells.md). Destination: structured
process values and explicit stream adapters.

| ID | Trigger | Fact to preserve | Candidate outcome or falsifier |
| --- | --- | --- | --- |
| H05 | Argument contains a newline, wildcard, or leading dash | Data, argv, and command syntax differ | Keep the argument intact; the tool's own option grammar still needs an explicit policy. |
| H06 | History is replayed after working directory/environment change | Invocation context belongs to the action | Show current context and recheck authority; a saved command is not a saved grant. |
| H07 | Consumer exits while producer continues writing | Stream lifetime and exit success are distinct | Report producer/consumer outcomes and bounded teardown; no silent hanging pipe. |
| H08 | A displayed object is piped to a bytes-only process | Display is not serialization | Require a named codec and limit; reject an implicit pretty-text conversion. |

## 3. Keyboard, Modal Commands, And Macros

Evidence owner: [keyboard commands](keyboard_commands.md). Destination: contextual
command adapters; input modality remains outside source grammar.

| ID | Trigger | Fact to preserve | Candidate outcome or falsifier |
| --- | --- | --- | --- |
| H09 | Enter is pressed while an IME is composing | Composition completion differs from Run | No execution from a composition key; retain the draft and focus. |
| H10 | A held key produces repeated command events | Repeatable navigation differs from effectful execution | The command's repeat policy prevents accidental duplicate actions. |
| H11 | A macro recorded in one focus context is replayed in another | Target and preconditions differ from raw gestures | Resolve or reject the target; do not type into an unintended control. |
| H12 | A chord's second key arrives after the context changes | Pending gesture state is not authority | Cancel/re-resolve the command rather than using an old selection. |

## 4. Direct Manipulation

Evidence owner: [direct manipulation](direct_manipulation.md). Pointer cancellation
and capture have a separate [event contract](https://www.w3.org/TR/pointerevents3/).
Destination: preview/change tooling and domain libraries.

| ID | Trigger | Fact to preserve | Candidate outcome or falsifier |
| --- | --- | --- | --- |
| H13 | Pointer capture is lost during a drag | Preview differs from commit | Cancel the candidate; a partial drag never becomes an unexplained edit. |
| H14 | A collaborator changes the value before pointer release | Candidate has a base revision | Revalidate/reject stale commit; do not silently overwrite. |
| H15 | Dragging a total could change either price or quantity | A projection need not have a unique inverse | Offer explicit alternatives or keep it read-only. |
| H16 | Snapping changes a value outside the visible scale | Presentation tolerance differs from semantic precision | Preview the exact proposed value and constraint; hidden rounding falsifies the control. |

## 5. Visual Graphs And Blocks

Evidence owner: [visual programming](visual_programming.md) and
[composition boundaries](../dsls/composition_boundaries.md). Destination:
source-mapped views before another frontend.

| ID | Trigger | Fact to preserve | Candidate outcome or falsifier |
| --- | --- | --- | --- |
| H17 | One output fans out to two effectful consumers | Data reuse differs from repeated invocation | Show call multiplicity and ordering; opening a graph changes neither. |
| H18 | A connection creates a cycle | Eager dependency, feedback, and fixed point differ | Reject or name the domain's explicit cycle semantics. |
| H19 | A node represents generated/scoped code | Source and expansion identities differ | Preserve origin/expansion links and unsupported source. |
| H20 | A node is deleted while holding a resource | Layout deletion differs from lifetime completion | Propose a checked source change; do not destroy an active lease by rendering policy. |

## 6. Patterns, Selectors, And Refactoring

Evidence owner: [text patterns](text_patterns.md). Destination: bounded selection
libraries and resolved source tools; core match retains its own contract.

| ID | Trigger | Fact to preserve | Candidate outcome or falsifier |
| --- | --- | --- | --- |
| H21 | Empty match, invalid selector, and missing target look alike | These are distinct outcomes | Report which happened, with a repair suited to it. |
| H22 | Rename crosses a shadowed scope | Binding identity differs from text equality | Change only resolved references and preserve the shadowed declaration. |
| H23 | Replacements overlap or alter later source offsets | Match set belongs to one source revision | Construct a conflict-checked transaction; avoid sequential offset drift. |
| H24 | Search exceeds a budget before finding a match | Incomplete search differs from empty complete search | Retain coverage/budget status instead of reporting "not found" as a fact. |

## 7. Query, Retrieval, And Exploration

Evidence owner: [query/search](query_search.md),
[SQL](../languages/sql.md), and [orthogonal models](../dsls/orthogonal_models.md).
Destination: explicit plan/evidence values.

| ID | Trigger | Fact to preserve | Candidate outcome or falsifier |
| --- | --- | --- | --- |
| H25 | No results arrive from a partially indexed corpus | World absence differs from missing evidence | State searched coverage and snapshot, not universal nonexistence. |
| H26 | Pagination is traversed while remote rows change | Page order differs from snapshot identity | Declare consistency and duplicates/omissions; stable IDs alone are insufficient. |
| H27 | Null, malformed input, and false predicate are grouped together | Absence, decode failure, and Bool differ | Preserve variants and error paths before filtering. |
| H28 | A query plan is inspected with no database capability | Description differs from execution | Static explain succeeds where supported; no hidden remote statistics fetch. |

## 8. State, Protocols, And Legal Actions

Evidence owner: [state/protocols](state_protocols.md). Destination: ordinary
state/event data plus transition and executor contracts.

| ID | Trigger | Fact to preserve | Candidate outcome or falsifier |
| --- | --- | --- | --- |
| H29 | Stop arrives twice, then an old completion arrives | State transition, run identity, and request differ | Idempotent stop request; no new completion for the wrong run. |
| H30 | Event handler synchronously causes another event | Reentrancy differs from queued delivery | Name dispatch order; preserve invariants at observable boundaries. |
| H31 | A button is enabled from yesterday's protocol state | Affordance differs from current eligibility | Executor rechecks preconditions; an enabled-looking button is not proof. |
| H32 | A transition is valid locally but loses its resource token | Dependency readiness differs from consumable availability | Recheck/tokenize acquisition atomically; no double allocation. |

## 9. Reactive Cells And Time

Evidence owner: [reactive time](reactive_temporal.md). Destination: explicit
reactive libraries or tooling, not alternate ordinary binding semantics.

| ID | Trigger | Fact to preserve | Candidate outcome or falsifier |
| --- | --- | --- | --- |
| H33 | Old run completes after a newer run | Completion order differs from intended current epoch | Archive it with its identity; never replace the current result. |
| H34 | Pure-looking cache depends on a clock or mutable capture | Dependency set differs from visible arguments | Reject the purity claim or include the explicit observation/capture contract. |
| H35 | Invalidation reaches a node that sent a request | Recompute differs from retry | Mark it invalid; external execution needs its declared action policy. |
| H36 | Observer/debugger changes scheduling or consumes a stream | Observation itself has cost and possible effects | Use captured bounded evidence; disclose perturbation or single-pass consumption. |

## 10. Quantities, Units, And Constraints

Evidence owner: [units/constraints](types_units_constraints.md). Destination:
nominal quantities, explicit conversions, decode, and separate solver tools.

| ID | Trigger | Fact to preserve | Candidate outcome or falsifier |
| --- | --- | --- | --- |
| H37 | Absolute temperature is added as if it were a difference | Affine point differs from vector/duration | Diagnose the concept mismatch, not merely a numeric type mismatch. |
| H38 | Equal-looking amounts have different currencies | Number differs from quantity and exchange epoch | Require explicit currency/conversion/rounding policy. |
| H39 | A measurement interval intersects a validity boundary | Estimate differs from certainty | Return uncertainty/policy evidence; do not quietly choose the midpoint. |
| H40 | A schema exports field ranges but omits a cross-field predicate | Projection differs from enforcement | Report the omitted rule; commit runs the actual decoder. |

## 11. Forms, Documents, And Drafts

Evidence owner: [structured documents](structured_documents.md). Destination:
lossless draft storage and checked commits.

| ID | Trigger | Fact to preserve | Candidate outcome or falsifier |
| --- | --- | --- | --- |
| H41 | Quantity passes through blank, minus sign, invalid text, integer | Draft differs from owned input | Keep each draft; only valid commit changes the invoice. |
| H42 | Locale displays `1,234` with a different separator convention | Presentation differs from codec | Use an explicit locale input policy; source literals keep language semantics. |
| H43 | Hidden/read-only form field is altered through imported JSON | Widget policy differs from trusted validation | Decode/authorize at the real boundary. |
| H44 | Rendered/exported document omits comments or unknown constructs | Semantic and lossless round trips differ | Preserve fallback and identify export loss; no silent deletion. |

## 12. Collaboration And Organizational Work

Evidence owner: [collaboration](distributed_collaboration.md). Destination:
versioned drafts, semantic validation, and application policy.

| ID | Trigger | Fact to preserve | Candidate outcome or falsifier |
| --- | --- | --- | --- |
| H45 | Two individually valid edits combine into an invalid range | Merge convergence differs from validity | Revalidate the merged draft; do not inherit either checked result. |
| H46 | Concurrent rename/delete targets the same entity | Identity lifetime differs from spelling | Preserve an explicit conflict; avoid recreating a deleted object accidentally. |
| H47 | Someone reviewed source but another person changed host policy | Review and authority have different owners | Identify both contexts and recheck the executor's current policy. |
| H48 | Offline command arrives after ownership changed | Causal intent differs from current permission | Retain the proposal, diagnose the invalid precondition, and reconcile explicitly. |

## 13. Planning, Solving, And Proof

Evidence owner: [planning](planning_optimization.md) and
[DSL evidence kinds](../dsls/orthogonal_models.md). Destination: bounded scoped
models/libraries, not magic inversion of eager functions.

| ID | Trigger | Fact to preserve | Candidate outcome or falsifier |
| --- | --- | --- | --- |
| H49 | Budget expires after exploring only failing assignments | Unknown differs from unsatisfiable | Report remaining search and assumptions; no false impossibility claim. |
| H50 | Feasible schedule is found before optimization completes | Witness differs from certified optimum | Label objective/bound/optimality status separately. |
| H51 | Two equally valid solutions are shown as one answer | Relation differs from unique function | Expose choice/enumeration policy and reproducibility. |
| H52 | Proof uses an assumption that a newer model changes | Theorem/evidence belongs to a theory and revision | Invalidate the applicable guarantee; retain the historical proof record. |

## 14. Music, Audio, And Timelines

Evidence owner: [music/timing](music_timing.md). Destination: event/signal and
clock-domain libraries under an honest host profile.

| ID | Trigger | Fact to preserve | Candidate outcome or falsifier |
| --- | --- | --- | --- |
| H53 | Tempo changes while events are queued | Musical position differs from wall-clock schedule | Declare whether queued timestamps are recomputed and from which epoch. |
| H54 | Stop is requested after an audio buffer was submitted | Requested stop differs from already committed output | Explain the bounded pending output; no impossible instantaneous-reversal claim. |
| H55 | Equal-time events arrive in a different order | Timestamp equality differs from ordering policy | Use declared tie/causal ordering, not accidental host iteration. |
| H56 | Feedback loop has zero versus one-sample delay | Dependency cycle differs from temporal recurrence | Make the delay/initial condition explicit in the model. |

## 15. Games, Turtles, And Simulations

Evidence owner: [games/turtles](games_turtles.md). Destination: pure step models
and effectful rendering/device boundaries.

| ID | Trigger | Fact to preserve | Candidate outcome or falsifier |
| --- | --- | --- | --- |
| H57 | Display frame rate changes | Simulation step differs from rendering frequency | Same declared input/step sequence yields the same model trace. |
| H58 | Contact/turn events coincide | Collision/order policy differs from animation | Diagnose/predict using model rules, not screen position alone. |
| H59 | Replaying a simulation uses a different random seed | Recording inputs differs from reproducing observations | Name random capability/seed/profile and disclose replay differences. |
| H60 | User learns sequence from animation but cannot inspect state | Perception differs from an explainable model | Provide pose/state evidence and test prediction without playback. |

## 16. Dialogue, Agents, And Mixed Initiative

Evidence owner: [conversational agents](conversational_agents.md). Destination:
proposals and explicit effectful model APIs, outside core evaluation.

| ID | Trigger | Fact to preserve | Candidate outcome or falsifier |
| --- | --- | --- | --- |
| H61 | "Increase it" has two plausible referents | Intent differs from a resolved command | Preserve unresolved alternatives; no silent target guess. |
| H62 | User corrects a plan after part of it ran | New intent differs from past world action | Show completed/uncertain work and a new proposal; do not rewrite history. |
| H63 | Imported text instructs the agent to change permissions | Task data differs from instruction/authority | Preserve provenance; source/data transformations create no grant. |
| H64 | Fluent explanation contradicts the captured trace | Suggestion differs from observation | Link claims to evidence and disclose absent support. |

## 17. Stack, Tacit, And Symbolic Compression

Evidence owner: [tacit/stack forms](tacit_stack.md) and [Iverson](../cognition.md).
Destination: explicit ordinary calls first, bounded domain tools if justified.

| ID | Trigger | Fact to preserve | Candidate outcome or falsifier |
| --- | --- | --- | --- |
| H65 | Insert a diagnostic into a tacit chain | Hidden argument/stack state differs from local named values | Show stack/shape effects or use the inspectable long form. |
| H66 | Reorder two logically equivalent effectful predicates | Value law differs from evaluation trace | Preserve short circuit, invocation count, and authority. |
| H67 | Empty array loses its intended rank or element type | Empty data differs from missing shape information | Retain explicit shape/type; reject guessed rank semantics. |
| H68 | Reassociate a floating-point fold | Mathematical real law differs from numeric profile | Require numeric side conditions; compare result and diagnostics. |

## 18. History, Transactions, Retry, And Compensation

Evidence owner: [transactions/history](transactions_versions.md). Destination:
application changes and executor-owned remote recovery.

| ID | Trigger | Fact to preserve | Candidate outcome or falsifier |
| --- | --- | --- | --- |
| H69 | Publication succeeds but its response is lost | Unknown outcome differs from failed action | Reconcile by stable operation identity under the provider's contract. |
| H70 | Session reset reuses revision number 1 | Numeric revision differs from history/session identity | Reject an old change from the previous incarnation. |
| H71 | Undo follows an acknowledged external action | Model reversal differs from compensation | Restore source/model only; name separate external recovery. |
| H72 | Retry reuses an idempotency key for different payload | Same operation identity differs from changed intent | Reject or create an explicitly new operation; never conceal the mismatch. |

## 19. Accessibility, Perception, And Attention

New evidence: [WCAG 2.2](https://www.w3.org/TR/2024/REC-WCAG22-20241212/)
covers keyboard access, focus, dragging alternatives, and status messages;
[ARIA keyboard guidance](https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/)
distinguishes focus from selection. These are selected requirements and design
guidance, not evidence that a particular interface is accessible. Destination:
equivalent command paths and faithful alternative projections.

| ID | Trigger | Fact to preserve | Candidate outcome or falsifier |
| --- | --- | --- | --- |
| H73 | Grid virtualization removes the focused item | Focus, selection, and domain identity differ | Keep/recover focus predictably and identify the same selected entity. |
| H74 | Pure recalculation floods live announcements | Semantic events differ from announcement frequency | Coalesce presentation while preserving navigable result/epoch evidence. |
| H75 | Error/edge type is encoded only by color or motion | Perceptual channel differs from semantic information | Supply named/textual structure and reduced-motion alternatives. |
| H76 | A drag has no keyboard/switch-access equivalent | Gesture differs from the computation | Invoke the same typed change from an accessible command; verify manually. |

## 20. Multilingual And Multimodal Input

New evidence: [UI Events](https://www.w3.org/TR/uievents/) exposes composition
state and distinguishes keyboard events from text input.
[UAX 9](https://www.unicode.org/reports/tr9/),
[UAX 29](https://www.unicode.org/reports/tr29/), and
[UTS 39](https://www.unicode.org/reports/tr39/) separate visual order,
segmentation, and confusability. Pin versions in a future implementation;
these references do not determine Nomi's identifier policy. Destination:
input adapters, scalar contracts, source maps, and diagnostics.

| ID | Trigger | Fact to preserve | Candidate outcome or falsifier |
| --- | --- | --- | --- |
| H77 | Diagnostic uses byte offsets in a UTF-16 editor | Bytes, scalars, code units, and graphemes differ | Convert against the exact source revision and declare the offset unit. |
| H78 | Bidi controls/confusable letters alter visible reading | Logical identity differs from appearance | Reveal suspicious structure without treating all non-Latin names as invalid. |
| H79 | Speech/handwriting recognizer revises a partial hypothesis | Observation confidence differs from final command | Keep draft/provenance and resolve target before commit. |
| H80 | Localized labels change while a command remains selected | Human label differs from command/binding identity | Preserve the semantic target; translation cannot retarget an action. |

## 21. Spatial, Tangible, And Embodied Computation

New evidence: [WebXR reference spaces](https://www.w3.org/TR/webxr/) define
spatial tracking and reference-space resets. [Sketchpad](../cognition.md)
grounds graphical constraints. Tangible token recognition and robot calibration
below are challenger hypotheses, not researched hardware protocols.
Destination: versioned spatial models and typed device adapters.

| ID | Trigger | Fact to preserve | Candidate outcome or falsifier |
| --- | --- | --- | --- |
| H81 | Tracking origin resets after a spatial edit was prepared | Coordinate differs from reference-frame identity/epoch | Reproject or reject the old candidate; never apply its numbers in a new frame. |
| H82 | Physical tokens are occluded, duplicated, or misrecognized | Recognized observation differs from owned entity | Retain ambiguity/confidence; do not manufacture a unique identity. |
| H83 | Simulation command is exported to a real device | Model possibility differs from hardware authority | Cross an explicit calibrated, capability-checked adapter. |
| H84 | A coordinate is valid but outside an actual reachable region | Numeric/shape validity differs from domain feasibility | Return model-specific evidence; ordinary typechecking proves neither reach nor safety. |

## 22. Supervision And Physical Automation

New evidence: Leveson and Thomas's
[STPA Handbook](https://psas.scripts.mit.edu/home/get_file.php?name=STPA_handbook.pdf),
chapter 2, examines control actions, feedback, timing, and controller process
models. It is a hazard-analysis method, not a device runtime or certification
standard. Destination: library/host control models and observable execution.

| ID | Trigger | Fact to preserve | Candidate outcome or falsifier |
| --- | --- | --- | --- |
| H85 | Sensor value is in range but old | Value validity differs from observation freshness | Check sensor/frame/clock evidence, not merely the numeric range. |
| H86 | Automation mode changes while a human command is pending | Action meaning depends on current mode/context | Revalidate the mode precondition; expose the changed meaning. |
| H87 | Stop acknowledgment is lost or actuator remains active | Requested, accepted, and physically achieved differ | Retain explicit unknown/active status and feedback requirements. |
| H88 | Manual override changes a plan but scheduled actions remain | Intention/history differs from queued authority | Reconcile outstanding actions and explain what can still occur. |

## 23. Privacy, Security, And Evidence Boundaries

Evidence owner: [industrial security](../../design/industrial.md) and
[agent research](conversational_agents.md). WebXR's own privacy discussion
also shows that spatial observations can reveal information beyond the
intended operation. Cases below are threat hypotheses, not a security audit.
Destination: capability enforcement and redaction-aware evidence adapters.

| ID | Trigger | Fact to preserve | Candidate outcome or falsifier |
| --- | --- | --- | --- |
| H89 | Masked value is exported through trace payload or clipboard | Pretty redaction differs from data-flow protection | Apply retention/export policy to every channel; a masked widget proves little. |
| H90 | Cached checked artifact outlives revoked permission | Static possibility differs from current authority | Executor rechecks current policy; cache hits grant nothing. |
| H91 | Diagnostic leaks secret through length, equality, or timing | Content hiding differs from all information-flow guarantees | Name the actual redaction scope; avoid an unsupported confidentiality claim. |
| H92 | A helper/delegate receives broader rights than its task needs | Effect category differs from narrow concrete capability | Attenuate authority at the boundary and retain delegation provenance. |

## 24. Learning, Repair, And End-User Appropriation

Evidence: [Suchman's situated-action chapter](https://www.cambridge.org/core/books/abs/humanmachine-reconfigurations/situated-actions/F4AA82303887FF0875BD656977661875)
questions equating plans with actual situated work;
[Ko and colleagues](https://faculty.washington.edu/ajko/papers/Ko2011EndUserSoftwareEngineering.pdf)
survey end-user engineering and attention investment. The latter is synthesis,
not a newly replicated study. Destination: examples, repair tools, and user
studies; no separate beginner semantics follows.

| ID | Trigger | Fact to preserve | Candidate outcome or falsifier |
| --- | --- | --- | --- |
| H93 | User copies an example into a different domain/host | Working example differs from universal recipe | Expose assumptions, required effects, and edge fixtures alongside the example. |
| H94 | A hole/recovered draft has a plausible partial result | Editing assistance differs from executable checked source | Preserve missing structure; effectful recovery guesses never execute. |
| H95 | Explanation fixes syntax while preserving the wrong model | Compiler correctness differs from intent correctness | Compare a contrasting domain example and let the user revise the model. |
| H96 | Faster task completion conceals poor review/repair performance | Throughput differs from understanding and retained agency | Measure prediction, diagnosis, revision, and transfer separately. |

## Non-Obvious Composition Rules

Single-family success is weak evidence. Exercise H01 + H45 + H77: sort a shared
grid, merge a rename, then apply a diagnostic-directed edit whose source offsets
belong to the old revision. Exercise H33 + H69 + H87: Stop and a late response
cannot establish whether an action happened. Exercise H40 + H79 + H89: a
recognizer, schema, and masked form can each appear trustworthy while jointly
discarding constraints and leaking evidence.

The [twelve composition cases](composition_cases.md) define forks, long forms,
diagnostic facts, and removal gates for these combinations. A family appearing
here does not earn an engine, a keyword, or a graphical editor.

## Gaps And Next Discovery Triggers

Not independently researched here: brain/computer interfaces, haptic protocols,
clinical decision interfaces, jurisdiction-specific legal workflows, detailed
robot safety standards, gesture recognition accuracy, tactile mathematics,
cross-cultural field studies, adversarial usability studies, and long-term
organizational adoption. Paper, abaci, slide rules, and physical manipulatives
remain useful competing representations; no historical survey of them is
claimed. Offline/intermittent connectivity and team handoff are cases in the
matrix, not tested distributed products.

Open one of those areas when a concrete Nomi program/view loses a fact that the
current model cannot express, two credible repairs remain, and a bounded study
can distinguish them. Record exclusions and affected people. A passing local
probe does not close an accessibility, privacy, or physical-control question.
