# Nomi Documentation

> Status: canonical documentation entry point.
>
> Nomi keeps one target-language authority, one consolidated research set, and
> a separate implementation orientation. Current prototypes are evidence and
> migration vehicles; they do not define the future language.

## Start Here

For language design, read:

1. [Target Design](design/README.md)
2. [Syntax](design/syntax.md)
3. [Semantics](design/semantics.md)
4. [Pattern Matching](design/pattern_matching.md)
5. [Industrial Model](design/industrial.md)
6. [Decision Ledger](design/decisions.md)
7. [Target Suite](design/targets/README.md) and [Overall Program](design/targets/overall.nomi)
8. [Pattern Target](design/pattern_matching_target.nomi)
9. [Language Synthesis](design/synthesis.md)
10. [Interaction Proposal](design/interaction_model.md) and
    [Design-First Agenda](design/redesign_agenda.md)

For the evidence and unresolved forks behind those choices, read:

1. [Research Overview](research/README.md)
2. [Language Families](research/families.md)
3. [Design Convergences](research/convergences.md)
4. [Pattern Matching Research](research/pattern_matching.md)
5. [Open Questions](research/open_questions.md)
6. [Language-Feature Matrix](research/language_feature_matrix.md),
   [Transpose](research/feature_language_matrix.md),
   [Syntax Matrix](research/syntax_matrix.md), and [Syntax Forms](research/syntax_forms.md)
   alongside [Language Reviews](research/languages/README.md) and [Feature Comparisons](research/features/README.md)
7. [Cognitive Foundations](research/cognition.md) and
   [Human-Computer Languages](research/interfaces/README.md)
   with the [human computation edge atlas](research/interfaces/edge_cases.md),
   [composition experiments](research/interfaces/composition_cases.md), and
   [executed local probes](research/interfaces/experiments.md): philosophical
   ideas translated to contracts, counterexamples, and implementation handoffs.
8. [Data And Workflow Languages](research/data_workflows/README.md) and
   [Cross-Disciplinary Notation](research/notation_atlas.md): source forms,
   layered execution models, critical comparisons and bounded Nomi experiments.
9. [DSLs And Strings](research/dsls/README.md): configuration/string boundaries
   plus text API vocabulary, 50 DSL families and 24 orthogonal semantic models;
   primary evidence, composition fixtures, local probes and bounded candidates.

For the current repository and runtime, read:

1. [Artifacts And Usage](orientation/artifacts_and_usage.md)
2. [Implementation Guideline](orientation/implementation_guideline.md)
3. [Exploratory Implementation Doctrine](orientation/exploratory_implementation_doctrine.md)
4. [Design Pass Workflow](orientation/design_pass_workflow.md)
5. [Implementation Layers](orientation/implementation_layers.md)

The [2026-07-16 Language Design Review](review/2026-07-16.md) records why the
old design corpus was consolidated and gives the concrete action sequence.
The [Pattern Matching Design Pass](review/2026-07-16-pattern-matching.md) is the
first registered research-to-target-to-bridge packet.

## Authority

When artifacts disagree, use this order:

```text
current user decision
-> docs/design target
-> docs/research evidence
-> docs/orientation current implementation map
-> executable prototypes and tests
-> Git history
```

Tests remain authoritative for what a supported implementation does today.
They are not a veto over a new target-language decision.

Target-only source belongs under `docs/design/targets/` or a registered focused
target. `design/target.nomi` is a superseded predecessor retained for historical
links. Files under `samples/` are runnable product fixtures
and must remain aligned with parser, runtime, tests, generated web manifest,
and browser execution.

## Documentation Types

| Location | Purpose | May decide target semantics? |
| --- | --- | --- |
| `docs/design/` | Canonical target language and industrial contracts | Yes |
| `docs/research/` | Consolidated evidence and bounded open questions | No; informs decisions |
| `docs/orientation/` | Current implementation, tooling, and collaboration | No |
| `docs/review/` | Dated judgments and evidence snapshots | No; decisions must be promoted |

New design notes should normally update an existing canonical file. Add a new
document only when it owns a durable information type that the current set
cannot hold cleanly.

## Design Change Workflow

For a registered cross-cutting feature, use the complete
[Design Pass Workflow](orientation/design_pass_workflow.md) and update
`config/design_passes.json`.

1. Start with a failing or awkward program, not a borrowed feature.
2. Check [Open Questions](research/open_questions.md) and existing research
   convergence before doing new broad research.
3. Compare at least two Nomi surfaces and the explicit long form.
4. Specify semantics, formatting, diagnostics, effects, and interactions.
5. Update the [Target Suite](design/targets/README.md) and [Overall Program](design/targets/overall.nomi).
6. Record the decision or experiment in the [Decision Ledger](design/decisions.md).
7. Only then map the change onto parser, Surface/Core, runtimes, tests, and web.

## Implementation Orientation

- [Project Enhancement Roadmap](orientation/project_roadmap.md): project-wide
  audit, priorities, dependencies, detailed workstreams and delivery gates;
  semantic decisions remain with the existing design owners.
- [AI Collaboration](orientation/ai_collaboration.md): repository doctrine for
  AI-assisted design, implementation, critique, and checkpoints.
- [Design Pass Workflow](orientation/design_pass_workflow.md): linked research,
  target, bridge, validation, retrospective, and topic-routing contract.
- [Artifacts And Usage](orientation/artifacts_and_usage.md): current execution
  pipelines, runtime artifacts, samples, and validation commands.
- [Exploratory Implementation Doctrine](orientation/exploratory_implementation_doctrine.md):
  reversible implementation while semantics are still moving.
- [Implementation Guideline](orientation/implementation_guideline.md): current
  engineering posture and project history.
- [Implementation Layers](orientation/implementation_layers.md): readable
  orchestration, replaceable engines, packaging, and bounded migration gates.
- [Performance Notes](orientation/performance_notes.md): parser/runtime
  performance experiments and measurements.
- [RAG MCP Context](orientation/rag_mcp.md): local code/document retrieval
  setup.
- [VS Code Extension](orientation/vscode_extension.md): local editor tooling.
- [WASM-JS Runtime Review](orientation/wasm_js_runtime_review.md): browser
  parser/runtime architecture evidence.

## Reviews

- [Language Design Review 2026-07-16](review/2026-07-16.md): syntax-first reset,
  research consolidation, target language, and ordered actions.
- [Pattern Matching Design Pass 2026-07-16](review/2026-07-16-pattern-matching.md):
  focused research, accepted target, implementation delta, and bridge.
- [GitHub Playground Plan 2026-09-29](review/2026-09-29-github-playground-agentic-plan.md):
  user-facing playground and VS Code agent workflow.
- [Language Synthesis Review 2026-09-29](review/2026-09-29-language-synthesis.md):
  cross-language evidence, target corrections, and registered continuation.
- [Implementation Boundary Review 2026-09-30](review/2026-09-30-implementation-boundaries.md):
  discovery/fix checkpoint preserving the current runtime and playground.
- [Deferred Test Review 2026-09-30](review/2026-09-30-test-issues.md):
  test-maintenance findings reserved for a separate pass.

## Complete Markdown Inventory

This list is intentionally complete and is checked by tests.

### Design

- [Target Design](design/README.md)
- [Syntax](design/syntax.md)
- [Semantics](design/semantics.md)
- [Pattern Matching](design/pattern_matching.md)
- [Industrial Model](design/industrial.md)
- [Decision Ledger](design/decisions.md)
- [Language Synthesis](design/synthesis.md)
- [Target Suite](design/targets/README.md)
- [Resource Completion Proposal](design/resource_lifetime.md)
- [Interaction Proposal](design/interaction_model.md)
- [Design-First Agenda](design/redesign_agenda.md)
- [Function Contracts](design/function_contracts.md)

### Research

- [Research Overview](research/README.md)
- [Language Families](research/families.md)
- [Design Convergences](research/convergences.md)
- [Pattern Matching Research](research/pattern_matching.md)
- [Open Questions](research/open_questions.md)
- [Resource Outcome And Escape Experiment](research/resource_lifetime.md)
- [Cognitive Foundations](research/cognition.md)
- [Natural Language As A Design Resource](research/interfaces/natural_language.md)
- [Language Redesign Frontiers](research/design_frontiers.md)
- [Language-Feature Synthesis Matrix](research/language_feature_matrix.md)
- [Feature-Language Transpose](research/feature_language_matrix.md)
- [Syntax Matrix](research/syntax_matrix.md)
- [Syntax Forms](research/syntax_forms.md)
- [Data And Workflow Research](research/data_workflows/README.md)
- [Data Source Forms](research/data_workflows/source_forms.md)
- [Workflow Execution Models](research/data_workflows/execution_models.md)
- [Dependencies, Change And Time](research/data_workflows/dependencies_and_time.md)
- [AI/ML Transformations, State And Evidence](research/data_workflows/ai_ml.md)
- [Messaging And Event-Driven Architectures](research/data_workflows/messaging_and_events.md)
- [Coherent Domain Layers](research/domain_composition.md)
- [Generic Operations And Compositional Properties](research/generic_operations.md)
- [Local Domain Composition Experiments](research/data_workflows/composition_experiments.md)
- [Data/Notation Synthesis And Experiments](research/data_workflows/nomi_candidates.md)
- [DSL And String Research](research/dsls/README.md)
- [Layered Configuration Languages](research/dsls/layered_configuration.md)
- [Strings And Embedded Languages](research/dsls/strings_and_embedding.md)
- [Text As A Computational Interface](research/dsls/text_as_interface.md)
- [DSL Domain Atlas](research/dsls/domain_atlas.md)
- [Orthogonal DSL Models](research/dsls/orthogonal_models.md)
- [Composing Orthogonal DSLs](research/dsls/composition_boundaries.md)
- [Nomi DSL Candidates And Experiments](research/dsls/nomi_candidates.md)
- [Executed DSL Boundary Probes](research/dsls/experiments.md)
- [Cross-Disciplinary Notation Atlas](research/notation_atlas.md)
- [Research Pressure Targets](design/targets/research/README.md)

### Interface Threads

- [Human-Computer Language Index](research/interfaces/README.md)
- [Human Computation Edge Atlas](research/interfaces/edge_cases.md)
- [Interaction Composition And Implementation Experiments](research/interfaces/composition_cases.md)
- [Executed Interaction Boundary Probes](research/interfaces/experiments.md)
- [Spreadsheets](research/interfaces/spreadsheets.md)
- [Command Shells](research/interfaces/command_shells.md)
- [Keyboard Commands](research/interfaces/keyboard_commands.md)
- [Direct Manipulation](research/interfaces/direct_manipulation.md)
- [Visual Programming](research/interfaces/visual_programming.md)
- [Text Patterns](research/interfaces/text_patterns.md)
- [Query And Search](research/interfaces/query_search.md)
- [State And Protocols](research/interfaces/state_protocols.md)
- [Reactive Time](research/interfaces/reactive_temporal.md)
- [Units And Constraints](research/interfaces/types_units_constraints.md)
- [Structured Documents](research/interfaces/structured_documents.md)
- [Collaboration](research/interfaces/distributed_collaboration.md)
- [Planning And Optimization](research/interfaces/planning_optimization.md)
- [Music And Timing](research/interfaces/music_timing.md)
- [Games And Turtles](research/interfaces/games_turtles.md)
- [Conversational Agents](research/interfaces/conversational_agents.md)
- [Stack And Tacit Forms](research/interfaces/tacit_stack.md)
- [Transactions And History](research/interfaces/transactions_versions.md)

### Language Reviews

- [Language Review Index](research/languages/README.md)
- [Python](research/languages/python.md)
- [Ruby](research/languages/ruby.md)
- [JavaScript](research/languages/javascript.md)
- [TypeScript](research/languages/typescript.md)
- [Bash](research/languages/bash.md)
- [PowerShell](research/languages/powershell.md)
- [Tcl](research/languages/tcl.md)
- [Scheme](research/languages/scheme.md)
- [Racket](research/languages/racket.md)
- [Clojure](research/languages/clojure.md)
- [OCaml](research/languages/ocaml.md)
- [F#](research/languages/fsharp.md)
- [Haskell](research/languages/haskell.md)
- [Elm](research/languages/elm.md)
- [Gleam](research/languages/gleam.md)
- [Roc](research/languages/roc.md)
- [Rust](research/languages/rust.md)
- [Go](research/languages/go.md)
- [Zig](research/languages/zig.md)
- [Swift](research/languages/swift.md)
- [Kotlin](research/languages/kotlin.md)
- [Scala](research/languages/scala.md)
- [Java](research/languages/java.md)
- [C#](research/languages/csharp.md)
- [Dart](research/languages/dart.md)
- [C](research/languages/c.md)
- [C++](research/languages/cpp.md)
- [Erlang](research/languages/erlang.md)
- [Elixir](research/languages/elixir.md)
- [SQL](research/languages/sql.md)
- [R](research/languages/r.md)
- [MATLAB](research/languages/matlab.md)
- [Julia](research/languages/julia.md)
- [APL](research/languages/apl.md)
- [J](research/languages/j.md)
- [BQN](research/languages/bqn.md)
- [Uiua](research/languages/uiua.md)
- [Wolfram Language](research/languages/wolfram.md)
- [CUE](research/languages/cue.md)
- [Nickel](research/languages/nickel.md)
- [Dhall](research/languages/dhall.md)
- [Pkl](research/languages/pkl.md)
- [Nix](research/languages/nix.md)
- [HCL](research/languages/hcl.md)

### Feature Comparisons

- [Feature Index](research/features/README.md)
- [Bindings](research/features/binding.md)
- [Functions](research/features/functions.md)
- [Types And Data](research/features/types_data.md)
- [Patterns](research/features/patterns.md)
- [Failure](research/features/failure.md)
- [Effects](research/features/effects.md)
- [Resources](research/features/resources.md)
- [Concurrency](research/features/concurrency.md)
- [Collections](research/features/collections.md)
- [Decoding](research/features/decoding.md)
- [Numerics](research/features/numerics.md)
- [Modules And Tooling](research/features/modules_tooling.md)
- [Metaprogramming](research/features/metaprogramming.md)

### Orientation

- [Project Enhancement Roadmap](orientation/project_roadmap.md)
- [Project Action Notes](orientation/project_action_notes.md)
- [AI Collaboration](orientation/ai_collaboration.md)
- [Design Pass Workflow](orientation/design_pass_workflow.md)
- [Artifacts And Usage](orientation/artifacts_and_usage.md)
- [Exploratory Implementation Doctrine](orientation/exploratory_implementation_doctrine.md)
- [Implementation Guideline](orientation/implementation_guideline.md)
- [Implementation Layers](orientation/implementation_layers.md)
- [Performance Notes](orientation/performance_notes.md)
- [RAG MCP Context](orientation/rag_mcp.md)
- [VS Code Extension](orientation/vscode_extension.md)
- [WASM-JS Runtime Review](orientation/wasm_js_runtime_review.md)

### Reviews

- [Language Design Review 2026-07-16](review/2026-07-16.md)
- [Pattern Matching Design Pass 2026-07-16](review/2026-07-16-pattern-matching.md)
- [GitHub Playground Plan 2026-09-29](review/2026-09-29-github-playground-agentic-plan.md)
- [Language Synthesis Review 2026-09-29](review/2026-09-29-language-synthesis.md)
- [Resource Lifetime Experiment 2026-09-29](review/2026-09-29-resource-lifetime.md)
- [Cognitive And Interface Review 2026-09-30](review/2026-09-30-cognitive-interfaces.md)
- [Function Contract Checkpoint 2026-09-30](review/2026-09-30-function-contracts.md)
- [Implementation Boundary Review 2026-09-30](review/2026-09-30-implementation-boundaries.md)
- [Deferred Test Review 2026-09-30](review/2026-09-30-test-issues.md)
