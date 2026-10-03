# Human-Computer Languages

> Status: selected interface research; proposals and experiments, not specification.

Packet: `docs/design/interaction_model.md`,
`docs/design/interaction_model_target.nomi`,
`docs/review/2026-09-30-cognitive-interfaces.md`.

Start with [the cognitive foundations](../cognition.md). This third dimension
extends the [44 language reviews](../languages/README.md) and
[13 feature comparisons](../features/README.md): interfaces are studied as
representations of human computational acts, not as candidate syntax libraries.
Sources were consulted on 2026-09-29/30. No usability trial was conducted.

The 2026-10-02 continuation adds [96 edge cases across 24 families](edge_cases.md),
[twelve composition cases and HX1-HX8 comparisons](composition_cases.md), and
[20 executed local research probes](experiments.md). It deepens the philosophical
readings in [cognition](../cognition.md) and maps hypotheses to current files.
The added standards/papers have their own bounded evidence notes. This remains
one packet; no human trial, production command adapter, or new evaluator is
claimed.

The follow-up gap review adds maintained capture/link/reference checks,
same-base publication and exact-review counterexamples, and an
[HX8 task/scoring protocol](composition_cases.md#hx8-minimal-study-protocol).
A valid immutable candidate is not a shared-state commit; current authority
is not evidence of the person's endorsement of a changed action.

The [language-feature matrix](../language_feature_matrix.md) includes Excel and
keyboard commands beside the 44 language columns, using these thread reviews
as their evidence links. The other threads retain this separate interface map.

## Thread Map

The [data/workflow extension](../data_workflows/README.md) and
[cross-disciplinary notation atlas](../notation_atlas.md) deepen these existing
threads with primary evidence and shared pressure programs. They are consolidated
comparisons, not additional independent syntax authorities. The
[DW experiment order](../data_workflows/nomi_candidates.md) owns their next steps.

| Thread | Representations considered | Pressure on Nomi |
| --- | --- | --- |
| [Spreadsheets](spreadsheets.md) | Excel, grids, fill, named columns, pivots | Value/dependency views without coordinate-bound semantics. |
| [Command Shells](command_shells.md) | Bash, PowerShell, prompts, history | Typed invocation, explicit streams and process boundaries. |
| [Keyboard Commands](keyboard_commands.md) | Chords, modal operators, macros, palettes | Semantic commands independent of their input gestures. |
| [Direct Manipulation](direct_manipulation.md) | Sketchpad, CAD, sliders, drag/drop | Candidate changes with validation, identity, and source maps. |
| [Visual Programming](visual_programming.md) | Blockly, Node-RED, block/port graphs | Separate data, event, and control edges. |
| [Text Patterns](text_patterns.md) | Regex, glob, CSS, tree selectors | Selection versus transformation; explicit costs and ambiguity. |
| [Query And Search](query_search.md) | SQL, facets, pivots, retrieval | Explicit relation/plan values; missing evidence is not false. |
| [State And Protocols](state_protocols.md) | Statecharts, Petri-net/BPMN candidates | Temporal validity, transitions, bounded model inspection. |
| [Reactive Time](reactive_temporal.md) | Notebooks, cells, event graphs, watches | Explicit epochs and effects; no accidental reruns. |
| [Units And Constraints](types_units_constraints.md) | Physical measures, forms, geometric relations | Checking versus solving; exact quantity semantics. |
| [Structured Documents](structured_documents.md) | Forms, markup, rendered mathematics | Draft versus checked data; presentation is a projection. |
| [Collaboration](distributed_collaboration.md) | Git, CRDT documents, semantic diffs | Merge convergence is not program correctness. |
| [Planning And Optimization](planning_optimization.md) | Logic relations, constraint models, SAT candidates | Solver budgets, witnesses, multiple/no solutions. |
| [Music And Timing](music_timing.md) | Pure Data, scores, sequencers, signal graphs | Clock domains and explicit event/signal conversion. |
| [Games And Turtles](games_turtles.md) | Logo, simulations, spatial grids | Embodied traces with a pure, inspectable model. |
| [Conversational Agents](conversational_agents.md) | Dialogue, proposed edits, tool approvals | Intent negotiation separate from authority and execution. |
| [Stack And Tacit Forms](tacit_stack.md) | Forth, RPN, point-free/array notation | Compression versus hidden arguments and shape. |
| [Transactions And History](transactions_versions.md) | Undo, replay, retry, compensation | Explicit state change; external effects are not reversible edits. |

Named neighboring systems are a coverage map, not a claim that all their
implementations were examined. Each thread bounds its checked evidence and
marks extrapolation. Unverified neighbors remain experiment candidates.

## Edge And Composition Dossier

| Artifact | Owns | Does not establish |
| --- | --- | --- |
| [Edge atlas](edge_cases.md) | 96 numbered triggers, distinctions, falsifiers, six additional families and explicit gaps | Exhaustive human coverage or observed bugs in cited systems |
| [Composition cases](composition_cases.md) | Twelve combined pressures, ordinary-call candidates, diagnostics, real-file handoff and HX1-HX8 | Accepted APIs, another project backlog, or an implemented interface |
| [Executed probes](experiments.md) | Inputs, results, limits, reproduction and promotion rules | Nomi/browser/solver/device conformance or human comprehension |
| [Probe script](probe_interactions.py) and [capture](probe_results.json) | Original finite models and named host observations with explicit execution flags | A shared runtime or universal interaction IR |

Obvious entry cases include invalid quantity, stale revision, and row sorting.
Less obvious compositions include incarnation reuse after reset, complete-looking
schema projections with omitted constraints, observation that itself runs code,
lost acknowledgments after Stop, changed coordinate frames, and valid values
with stale control context. Philosophical readings connect those cases to
discoverability, interpretation, preconditions, progress, evidence, and agency.

## Shared Extraction Method

For each interface ask: what does the person know, select, combine, change,
observe, or authorize? Then write:

```text
human act -> relation -> representation -> explicit Nomi long form
         -> law and counterexample -> failure -> destination -> experiment
```

Destinations are core, reducible convenience, library/protocol, scoped tool, or
editor/view with no source-language addition. A view is not a fifth syntax
extension layer: it projects a contract from one of the existing four layers.
The [interaction synthesis](../../design/interaction_model.md) compares the
threads and orders playground experiments. The
[redesign agenda](../../design/redesign_agenda.md) covers wider language gaps.

## Research Admission And Stop Rules

Do not interpret breadth as an obligation to implement one product per family.
Begin with the invoice target, pure transformation inspection, or Run/Stop. Compare two
representations under a deliberately invalid input, stale revision, and denied
capability. Keep a new notation only when the long form has a demonstrated
failure that tooling cannot repair adequately.

Historical sources generate questions; they do not prove that an interface is
easy. Documentation checks establish inventory and packet integrity, not
syntax conformance, semantic laws, accessibility, or performance.
