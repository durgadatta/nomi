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

The [language-feature matrix](../language_feature_matrix.md) includes Excel and
keyboard commands beside the 44 language columns, using these thread reviews
as their evidence links. The other threads retain this separate interface map.

## Thread Map

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

Do not interpret breadth as an obligation to implement 18 products. Begin with
the invoice target, pure transformation inspection, or Run/Stop. Compare two
representations under a deliberately invalid input, stale revision, and denied
capability. Keep a new notation only when the long form has a demonstrated
failure that tooling cannot repair adequately.

Historical sources generate questions; they do not prove that an interface is
easy. Documentation checks establish inventory and packet integrity, not
syntax conformance, semantic laws, accessibility, or performance.
