# Nomi Documentation

> Status: current documentation entry point.

Start with [DIGEST.md](../DIGEST.md) for a self-contained repository story or
[open the playground](https://durgadatta.github.io/nomi/web/) to try calculation
and report repair/export. The published and local playgrounds share committed
samples and runtime assets.

## Choose A Route

| Goal | Start here | What it owns |
| --- | --- | --- |
| Learn and run Nomi | [User guide](guide/README.md), [getting started](guide/getting_started.md), [examples](guide/examples.md) | Supported workflows and their boundaries. |
| Understand current support | [Status](guide/status.md), [artifact map](orientation/artifacts_and_usage.md) | Working prototypes, profiles and implementation limits. |
| Understand purpose and meaning | [Vision](design/vision.md), [target design](design/README.md), [syntax](design/syntax.md), [semantics](design/semantics.md), [decisions](design/decisions.md) | Accepted laws and clearly marked design candidates. |
| Grow the language | [Synthesis](design/synthesis.md), [industrial contracts](design/industrial.md), [pattern contract](design/pattern_matching.md), [target suite](design/targets/README.md) | Whole-program coherence and admission obligations. |
| Study alternatives | [Research guide](research/synthesis_guide.md), [families](research/families.md), [convergences](research/convergences.md), [open questions](research/open_questions.md) | Comparative evidence and bounded experiments. |
| Implement or maintain | [Development](orientation/development.md), [implementation layers](orientation/implementation_layers.md), [roadmap](orientation/project_roadmap.md) | Setup, current owners and dependency-ordered delivery. |
| Resume a focused question | [Packet workflow](orientation/design_pass_workflow.md), [registry](../config/design_passes.json), current bridges below | Evidence, open gaps, checks and next actions. |

## Authority

Current user decisions can revise the target. `design/` owns intended meaning;
`research/` supplies evidence; `orientation/` maps current implementation and
work. Tests establish supported prototype behavior, not the final language.
Target-only code stays under `design/`; runnable product examples live in
`samples/` and require parser/runtime/diagnostic agreement on advertised paths.

Update live records in place. Current bridges under `review/` describe present
evidence and gaps. Project evolution is concise and isolated in
[HISTORY.md](../HISTORY.md); detailed old artifacts remain in Git.

## Complete Markdown Inventory

<details>
<summary>Browse current documents by area</summary>

### Guide

- [Learn And Use Nomi](guide/README.md)
- [Choose An Example](guide/examples.md)
- [Getting Started With Nomi](guide/getting_started.md)
- [Language Basics](guide/language_basics.md)
- [Explore Learning And Reasoning](guide/reasoning_lab.md)
- [Current Support And Growth](guide/status.md)
- [Using Nomi's Tools](guide/tools.md)

### Design

- [Nomi Target Design](design/README.md)
- [Learning, Inference And Intelligent Programs](design/ai_frameworks.md)
- [Nomi Decision Ledger](design/decisions.md)
- [Function And Callback Contracts](design/function_contracts.md)
- [Nomi Industrial Model](design/industrial.md)
- [Nomi Interaction Model](design/interaction_model.md)
- [Engine-Free Objects](design/object_framework.md)
- [Pattern Matching](design/pattern_matching.md)
- [Primitives And Their Compositions](design/primitive_composition.md)
- [A Minimal Algebra Of Scientific Reasoning](design/reasoning_algebra.md)
- [Design-First Redesign Agenda](design/redesign_agenda.md)
- [Resource Completion Proposal](design/resource_lifetime.md)
- [Scientific Models And Discovery](design/scientific_discovery.md)
- [Nomi Semantics](design/semantics.md)
- [Statistical Data Interface](design/statistical_data.md)
- [Nomi Syntax](design/syntax.md)
- [Nomi Language Synthesis](design/synthesis.md)
- [Target Program Suite](design/targets/README.md)
- [Research Pressure Programs](design/targets/research/README.md)
- [Nomi As A Computational Medium](design/vision.md)

### Research

- [Nomi Research](research/README.md)
- [Computation As A Cognitive Instrument](research/cognition.md)
- [Cross-Language Design Convergences](research/convergences.md)
- [Data And Workflow Languages](research/data_workflows/README.md)
- [AI, Learning And Knowledge: Conceptual Foundations](research/data_workflows/ai_ml.md)
- [Local Composition Experiments](research/data_workflows/composition_experiments.md)
- [Dependencies, Change And Time](research/data_workflows/dependencies_and_time.md)
- [Execution And Workflow Models](research/data_workflows/execution_models.md)
- [Messaging And Event-Driven Architectures](research/data_workflows/messaging_and_events.md)
- [Nomi Synthesis And Experiments](research/data_workflows/nomi_candidates.md)
- [Data Source Forms](research/data_workflows/source_forms.md)
- [Statistical Objects Before Observations](research/data_workflows/statistical_objects.md)
- [Language Redesign Frontiers](research/design_frontiers.md)
- [Coherent Domain Layers](research/domain_composition.md)
- [DSLs And Strings: Research Dossier](research/dsls/README.md)
- [Composing Orthogonal DSLs](research/dsls/composition_boundaries.md)
- [DSL Domain Atlas](research/dsls/domain_atlas.md)
- [Executed DSL Boundary Probes](research/dsls/experiments.md)
- [Layered Configuration Is A Stack Of Languages](research/dsls/layered_configuration.md)
- [Nomi DSL Candidates And Discriminating Experiments](research/dsls/nomi_candidates.md)
- [Orthogonal DSL Models](research/dsls/orthogonal_models.md)
- [Strings, Embedded Languages And Boundary Preservation](research/dsls/strings_and_embedding.md)
- [Text As A Computational Interface](research/dsls/text_as_interface.md)
- [Language Family Findings](research/families.md)
- [Feature-Language Synthesis Matrix (Transposed)](research/feature_language_matrix.md)
- [Cross-Language Feature Comparisons](research/features/README.md)
- [Bindings And State](research/features/binding.md)
- [Collections And Plans](research/features/collections.md)
- [Concurrency](research/features/concurrency.md)
- [Decoding And Constraints](research/features/decoding.md)
- [Effects And Authority](research/features/effects.md)
- [Failure And Absence](research/features/failure.md)
- [Functions And Calls](research/features/functions.md)
- [Metaprogramming](research/features/metaprogramming.md)
- [Modules And Tooling](research/features/modules_tooling.md)
- [Numerics And Shape](research/features/numerics.md)
- [Patterns And Choice](research/features/patterns.md)
- [Resource Lifetime](research/features/resources.md)
- [Types And Owned Data](research/features/types_data.md)
- [Generic Operations And Compositional Properties](research/generic_operations.md)
- [Human-Computer Languages](research/interfaces/README.md)
- [Shells: Invocation Is A Boundary](research/interfaces/command_shells.md)
- [Interaction Composition And Implementation Experiments](research/interfaces/composition_cases.md)
- [Dialogue: Negotiate Intent Before Execution](research/interfaces/conversational_agents.md)
- [Direct Manipulation: Make The Change Explicit](research/interfaces/direct_manipulation.md)
- [Collaboration: Agreement Is Not Correctness](research/interfaces/distributed_collaboration.md)
- [Human Computation At The Edges](research/interfaces/edge_cases.md)
- [Executed Interaction Boundary Probes](research/interfaces/experiments.md)
- [Games And Turtles: An Executable Mental Model](research/interfaces/games_turtles.md)
- [Keyboard Commands: Meaning Before Gesture](research/interfaces/keyboard_commands.md)
- [Music And Timing: Choose The Clock](research/interfaces/music_timing.md)
- [Natural Language As A Design Resource](research/interfaces/natural_language.md)
- [Planning: Ask For A Witness](research/interfaces/planning_optimization.md)
- [Query And Search: Evidence Has A Domain](research/interfaces/query_search.md)
- [Reactive Interfaces: Recalculation Is Not Repetition](research/interfaces/reactive_temporal.md)
- [Spreadsheets: Name The Dependency](research/interfaces/spreadsheets.md)
- [State And Protocols: Validity Over Time](research/interfaces/state_protocols.md)
- [Structured Documents: Preserve The Draft](research/interfaces/structured_documents.md)
- [Stack And Tacit Forms: Where Did The Argument Go?](research/interfaces/tacit_stack.md)
- [Patterns And Selectors: Describe A Set](research/interfaces/text_patterns.md)
- [History: Undo Which World?](research/interfaces/transactions_versions.md)
- [Units And Constraints: Meaning Is More Than A Number](research/interfaces/types_units_constraints.md)
- [Visual Programs: An Edge Needs A Meaning](research/interfaces/visual_programming.md)
- [General Knowledge Representation And Processing](research/knowledge_frameworks.md)
- [Language-Feature Synthesis Matrix](research/language_feature_matrix.md)
- [Critical Language Reviews](research/languages/README.md)
- [APL](research/languages/apl.md)
- [Bash](research/languages/bash.md)
- [BQN](research/languages/bqn.md)
- [C](research/languages/c.md)
- [Clojure](research/languages/clojure.md)
- [C++](research/languages/cpp.md)
- [C#](research/languages/csharp.md)
- [CUE](research/languages/cue.md)
- [Dart](research/languages/dart.md)
- [Dhall](research/languages/dhall.md)
- [Elixir](research/languages/elixir.md)
- [Elm](research/languages/elm.md)
- [Erlang](research/languages/erlang.md)
- [F#](research/languages/fsharp.md)
- [Gleam](research/languages/gleam.md)
- [Go](research/languages/go.md)
- [Haskell](research/languages/haskell.md)
- [HCL](research/languages/hcl.md)
- [J](research/languages/j.md)
- [Java](research/languages/java.md)
- [JavaScript](research/languages/javascript.md)
- [Julia](research/languages/julia.md)
- [Kotlin](research/languages/kotlin.md)
- [MATLAB](research/languages/matlab.md)
- [Mojo](research/languages/mojo.md)
- [Nickel](research/languages/nickel.md)
- [Nix](research/languages/nix.md)
- [OCaml](research/languages/ocaml.md)
- [Pkl](research/languages/pkl.md)
- [PowerShell](research/languages/powershell.md)
- [Python](research/languages/python.md)
- [R](research/languages/r.md)
- [Racket](research/languages/racket.md)
- [Roc](research/languages/roc.md)
- [Ruby](research/languages/ruby.md)
- [Rust](research/languages/rust.md)
- [Scala](research/languages/scala.md)
- [Scheme](research/languages/scheme.md)
- [SQL](research/languages/sql.md)
- [Swift](research/languages/swift.md)
- [Tcl](research/languages/tcl.md)
- [TypeScript](research/languages/typescript.md)
- [Uiua](research/languages/uiua.md)
- [Mathematica And Wolfram Language](research/languages/wolfram.md)
- [Zig](research/languages/zig.md)
- [Notation Beyond Programming](research/notation_atlas.md)
- [Open Research Questions](research/open_questions.md)
- [Pattern Matching Research](research/pattern_matching.md)
- [Resource Outcome And Escape Experiment](research/resource_lifetime.md)
- [Scientific Models As Instruments For Thinking](research/scientific_models.md)
- [Syntax Forms: Recognition Before Compression](research/syntax_forms.md)
- [Syntax Matrix: The Forms People Read And Write](research/syntax_matrix.md)
- [Researching And Integrating One Coherent Language](research/synthesis_guide.md)

### Orientation

- [AI Collaboration](orientation/ai_collaboration.md)
- [Artifacts And Usage](orientation/artifacts_and_usage.md)
- [Design Pass Workflow](orientation/design_pass_workflow.md)
- [Developing Nomi](orientation/development.md)
- [Exploratory Implementation Doctrine](orientation/exploratory_implementation_doctrine.md)
- [Implementation Guideline](orientation/implementation_guideline.md)
- [Implementation Layers](orientation/implementation_layers.md)
- [Performance And Profiling](orientation/performance_notes.md)
- [Project Action Notes](orientation/project_action_notes.md)
- [Project Roadmap](orientation/project_roadmap.md)
- [RAG MCP Context](orientation/rag_mcp.md)
- [VS Code Extension](orientation/vscode_extension.md)
- [Browser Runtime Architecture](orientation/wasm_js_runtime_review.md)

### Review

- [Cognitive Interfaces Implementation Bridge](review/cognitive_interfaces.md)
- [Function Contracts Implementation Bridge](review/function_contracts.md)
- [Language Coherence Implementation Bridge](review/language_coherence.md)
- [Pattern Matching Implementation Bridge](review/pattern_matching.md)
- [Resource Lifetime Implementation Bridge](review/resource_lifetime.md)

</details>
