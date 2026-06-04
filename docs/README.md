# Nomi Docs

> Status: documentation entry point.
>
> This directory is moving toward a smaller syntax-centered spine: a few
> foundation and process docs, then concrete language syntax docs with
> examples, status, reductions, diagnostics, and implementation notes. Research,
> notes, drafts, and older planning scans are source material, not competing
> specs.

## Reading Order

Start here for most language design or implementation work:

1. [Language Foundation](language/language_foundation.md)
2. [Language Specification](language/language_spec.md)
3. [Spec Readiness Map](language/spec_readiness_map.md)
4. [Language Direction And Gap Map](language/language_direction_and_gap_map.md)
5. [Convenience Review And Roadmap](convenience/review_and_roadmap.md)
6. The focused syntax doc for the feature being changed.
7. [Artifacts And Usage](orientation/artifacts_and_usage.md), when runtime
   behavior or tooling is involved.

The default improvement path is to make an existing syntax doc clearer, not to
add another design note.

## Consolidation Direction

Most durable docs should be syntax-facing. A syntax-facing doc answers:

```text
What does the code look like?
What does it reduce to?
What is implemented now?
What diagnostics should users see?
What alternatives were rejected?
```

Keep only a few non-syntax foundations:

| Kind | Role |
| --- | --- |
| Foundation | Semantic anchors and normal forms. |
| Specification | Concrete syntax and behavior. |
| Direction map | Priorities, deduplication decisions, and docs cleanup policy. |
| Implementation plan | Ordered work and current TODOs. |
| Orientation | Runtime/tooling/process maps. |

When a research or planning doc produces a stable decision, fold that decision
into a foundation, spec, feature, or convenience syntax doc, then leave the
research file as a citation source.

### Canonical Ownership For Overlap

Use this ledger when two docs seem to say the same thing. Keep the left-hand
doc as the action surface; keep the right-hand docs as evidence, critique, or
background.

| Topic | Canonical action surface | Source or evidence docs |
| --- | --- | --- |
| Current backlog | [Implementation Todos](language/implementation_todos.md) | [Project Improvement Review 2026-06-03](orientation/project_improvement_review_2026_06_03.md), [Technical Implementation Improvement Notes](orientation/technical_implementation_improvement_notes.md), [Global Consistency Audit](orientation/global_consistency_audit.md) |
| Implementation gates | [Implementation Evolvability Gap Review](language/implementation_evolvability_gap_review.md) | [Implementation Codebase Audit](language/implementation_codebase_audit.md), [Adversarial Implementation Critique](language/adversarial_implementation_critique.md), [Adversarial Exploratory Implementation Critique](language/adversarial_exploratory_implementation_critique.md) |
| Python independence | [Python Independence And Compiler Backend Plan](language/python_independence_and_compiler_backend_plan.md) | [Backend Independence Roadmap](language/backend_independence_roadmap.md), [Core Runtime Backend Design](language/core_runtime_backend_design.md), [Core Runtime Backend Implementation Notes](language/core_runtime_backend_implementation_notes.md), [WASM-JS Runtime Architecture Review](orientation/wasm_js_runtime_review.md) |
| Syntax admission | [Spec Readiness Map](language/spec_readiness_map.md), [Design Proposal Template](language/design_proposal_template.md) | [Docs Eagle Eye Review](language/docs_eagle_eye_review.md), [Adversarial Design Critique](language/adversarial_design_critique.md), [Adversarial Language Design Enhancement Notes 2026-06-04](language/adversarial_language_design_enhancement_notes_2026_06_04.md) |
| Convenience syntax | [Convenience Review And Roadmap](convenience/review_and_roadmap.md) | [Syntax Synthesis Matrix](convenience/syntax_synthesis_matrix.md), [Design Lessons And Integration Critique](convenience/design_lessons_and_integration.md), per-feature convenience docs |
| Research coverage | [Language Family Coverage Map](research/language_family_coverage_map.md) | All `docs/research/*_deep_dive.md` and other research notes |
| Draft material | Active docs above | [Drafts](drafts/) |

If a duplicate claim is durable, move it into the canonical action surface and
leave a short citation or status note in the source document. Avoid creating a
new "final synthesis" file unless the old action surface is being retired.

## Orientation

Concrete project, process, and tooling docs.

- [Artifacts And Usage](orientation/artifacts_and_usage.md): current runtime
  pipeline and artifact map.
- [Implementation Guideline](orientation/implementation_guideline.md):
  implementation posture and AI tool history.
- [AI Collaboration](orientation/ai_collaboration.md): accepted AI use cases,
  critique workflow, and checkpoint doctrine.
- [Exploratory Implementation Doctrine](orientation/exploratory_implementation_doctrine.md):
  flexible, declarative, reversible implementation rules for early language
  design work.
- [Technical Implementation Improvement Notes](orientation/technical_implementation_improvement_notes.md):
  current high-impact scan across parser, runtime, web, contracts, host
  capabilities, and generated artifacts.
- [Global Consistency Audit](orientation/global_consistency_audit.md):
  high-impact follow-up notes from the 2026-05-24 consistency pass.
- [Project Improvement Review 2026-06-03](orientation/project_improvement_review_2026_06_03.md):
  dated evidence from the latest full-repo scan; durable action items are
  folded into [Implementation Todos](language/implementation_todos.md).
- [WASM-JS Runtime Architecture Review](orientation/wasm_js_runtime_review.md):
  implementation review notes for the browser Rust/WASM -> JS runtime path.
- [VS Code Extension](orientation/vscode_extension.md): local extension
  surface and roadmap.
- [RAG MCP Context](orientation/rag_mcp.md): local retrieval and MCP scaffold
  for codebase and programming-book context.
- [Performance Notes](orientation/performance_notes.md): parsing pipeline
  optimization log — attempts, findings, LALR status, and stage timings.

## Read By Task

Use these paths when entering the docs from a concrete job rather than from the
general reading order.

| Task | Read first |
| --- | --- |
| Add or change syntax | [Flexible Syntax Substrate Plan](language/flexible_syntax_substrate_plan.md), [Syntax Substrate TODO Audit](language/syntax_substrate_todo_audit.md), [Parser Frontend Decoupling Plan](language/parser_frontend_decoupling_plan.md), the relevant [Convenience](convenience/) note, [Design Proposal Template](language/design_proposal_template.md) |
| Audit implementation gaps | [Implementation Evolvability Gap Review](language/implementation_evolvability_gap_review.md), [Technical Implementation Improvement Notes](orientation/technical_implementation_improvement_notes.md), [Implementation Codebase Audit](language/implementation_codebase_audit.md), [Syntax Substrate TODO Audit](language/syntax_substrate_todo_audit.md), [Architecture Refactoring Plan](language/architecture_refactoring_plan.md) |
| Separate core/sugar/eval layers | [Core Layer Separation Plan](language/core_layer_separation_plan.md), [Language Degrees Of Freedom](language/language_degrees_of_freedom.md), [Architecture Refactoring Plan](language/architecture_refactoring_plan.md), [Flexible Syntax Substrate Plan](language/flexible_syntax_substrate_plan.md) |
| Critique implementation flexibility/performance | [Exploratory Implementation Doctrine](orientation/exploratory_implementation_doctrine.md), [Adversarial Exploratory Implementation Critique](language/adversarial_exploratory_implementation_critique.md), [Adversarial Implementation Critique](language/adversarial_implementation_critique.md), [Performance Notes](orientation/performance_notes.md), [Implementation Codebase Audit](language/implementation_codebase_audit.md), [Modern Language Implementation Artifacts](language/modern_language_implementation_artifacts.md) |
| Plan Python-independent backends | [Modern Language Implementation Artifacts](language/modern_language_implementation_artifacts.md), [Python Independence And Compiler Backend Plan](language/python_independence_and_compiler_backend_plan.md), [Parser Frontend Decoupling Plan](language/parser_frontend_decoupling_plan.md), [Architecture Refactoring Plan](language/architecture_refactoring_plan.md), [Flexible Syntax Substrate Plan](language/flexible_syntax_substrate_plan.md) |
| Restructure tests | [Test Suite Restructure Plan](language/test_suite_restructure_plan.md), [Syntax Substrate TODO Audit](language/syntax_substrate_todo_audit.md), [Forward Implementation Plan](language/forward_implementation_plan.md) |
| Design binding or decode | [Binding Constraints Feature](features/binding_constraints_feature.md), [Language Foundation](language/language_foundation.md), [Target Program Fixtures](language/target_program_fixtures.md) |
| Work on blocks/control | [Block Calls As Control Values](features/block_calls_feature.md), [Concurrency](convenience/concurrency.md) |
| Work on collections/query | [Structured Collections And Query Language](features/structured_collections_query_language.md), [Flow And Collections](convenience/flow_and_collections.md), [Syntax Synthesis Matrix](convenience/syntax_synthesis_matrix.md) |
| Work on symbolic/lazy computation | [Symbolic, Lazy, And Structural Computation](features/symbolic_structural_computation.md), [Flow And Collections](convenience/flow_and_collections.md), [Meta & Testing](convenience/meta_testing.md), [Python Independence And Compiler Backend Plan](language/python_independence_and_compiler_backend_plan.md) |
| Improve design docs | [Spec Readiness Map](language/spec_readiness_map.md), [Language Direction And Gap Map](language/language_direction_and_gap_map.md), [Docs Eagle Eye Review](language/docs_eagle_eye_review.md), [Language Family Coverage Map](research/language_family_coverage_map.md) |
| Critique design coherence | [Adversarial Design Critique](language/adversarial_design_critique.md), [Adversarial Language Design Enhancement Notes 2026-06-04](language/adversarial_language_design_enhancement_notes_2026_06_04.md), [Global Feature Interaction Map](convenience/interaction_map.md), [Spec Readiness Map](language/spec_readiness_map.md) |
| Make samples or demos | [Target Program Fixtures](language/target_program_fixtures.md), [Target Language Tour](language/target_language_tour.md), [Language Specification](language/language_spec.md) |

## Language

Canonical or near-canonical language direction. These are the decision surface
for implementation sequencing.

Core direction:

- [Language Foundation](language/language_foundation.md): canonical foundation
  and operational core.
- [Language Specification](language/language_spec.md): draft concrete spec.
- [Language Degrees Of Freedom](language/language_degrees_of_freedom.md):
  strict core, sugar, libraries, scoped extensions, future layers, and
  rejection framework.
- [Language Design Dimensions](language/language_design_dimensions.md):
  irreducible language-design axes and convergence points.
- [Delta On Python](language/delta_on_python.md): rationale for changes
  relative to Python.

Target programs:

- [Target Program Fixtures](language/target_program_fixtures.md):
  aspirational task-sized programs.
- [Target Demo Script](language/demo_target.nomi): compact target-only
  `.nomi` script for the future operational spec; not expected to parse today.
- [Target Language Tour](language/target_language_tour.md): large whole-program
  coherence target.
- [First-Hour Nomi](language/first_hour_nomi.md): smallest teaching path for
  values, names, calls, functions, constraints, and diagnostics.

Planning and process:

- [Language Direction And Gap Map](language/language_direction_and_gap_map.md):
  adoption-oriented steering note, core gap map, and docs consolidation policy.
- [Docs Eagle Eye Review](language/docs_eagle_eye_review.md): full-docs scan
  for hidden bridge gaps and next synthesis moves.
- [Adversarial Design Critique](language/adversarial_design_critique.md):
  hostile review of feature and global-language failure modes.
- [Adversarial Language Design Enhancement Notes 2026-06-04](language/adversarial_language_design_enhancement_notes_2026_06_04.md):
  sharp post-HCI critique, enhancement queue, and feature-admission gates.
- [Adversarial Enhancement Implementation Plan 2026-06-04](language/adversarial_enhancement_implementation_plan_2026_06_04.md):
  staged implementation route for the adversarial gates: events, capabilities,
  data boundary, command values, projections, agents, first-hour docs, and
  stdlib baseline.
- [Spec Readiness Map](language/spec_readiness_map.md): promotion workflow and
  coverage map for converting research, convenience notes, feature docs, and
  implementation plans into a future language specification.
- [Forward Implementation Plan](language/forward_implementation_plan.md):
  staged implementation sequence and gates.
- [Implementation Todos](language/implementation_todos.md): staged backlog.
- [Implementation Evolvability Gap Review](language/implementation_evolvability_gap_review.md):
  project-wide gate for feature ownership, explicit capability axes,
  Surface/Core authority, runtime result contracts, frontend parity, test
  matrices, and reversible implementation.
- [Current Capability Matrix](language/current_capability_matrix.md):
  live inspection route for parse, lower, run, reduce, explain, docs, tests,
  samples, web, and notebook capability axes.
- [Design Proposal Template](language/design_proposal_template.md): proposal
  process for new syntax, features, and promoted research ideas.
- [Architecture Refactoring Plan](language/architecture_refactoring_plan.md):
  high-level runtime API, pipeline, package, host, and frontend adapter plan.
- [Core Layer Separation Plan](language/core_layer_separation_plan.md):
  layer map for implementation core, semantic core, canonical surface, sugar,
  libraries, scoped extensions, eval separation, and backend targets.
- [Python Independence And Compiler Backend Plan](language/python_independence_and_compiler_backend_plan.md):
  staged path from Python-hosted prototype to Nomi Core IR, direct runtime,
  MLIR, LLVM/native, and Wasm/WASI backends.
- [Backend Independence Roadmap](language/backend_independence_roadmap.md):
  earlier concrete path sketch for reducing Python semantic authority.
- [Core Runtime Backend Design](language/core_runtime_backend_design.md):
  reference design for direct Core IR runtime backends.
- [Core Runtime Backend Implementation Notes](language/core_runtime_backend_implementation_notes.md):
  active implementation notes for the non-Python eval backend.
- [Modern Language Implementation Artifacts](language/modern_language_implementation_artifacts.md):
  concrete lessons from LLVM, MLIR, Tree-sitter, LSP, Rust, Swift, GHC,
  WebAssembly/WIT, Cranelift, Roslyn, and TypeScript for Nomi's artifact stack.
- [Prelude And Standard Library Plan](language/prelude_and_standard_library_plan.md):
  ordinary library surface for text, paths, files, JSON, CSV, HTTP, time,
  process, tables, tests, and secrets.
- [Standard Library Capability Baseline](language/stdlib_capability_baseline.md):
  capability honesty for world-touching standard-library functions.
- [Parser Frontend Decoupling Plan](language/parser_frontend_decoupling_plan.md):
  staged path from Lark-as-parser to parser frontends that produce Nomi-owned
  CST/Surface/Core artifacts before the Python AST backend.
- [Test Suite Restructure Plan](language/test_suite_restructure_plan.md):
  planning note for organizing unit, feature, contract, regression, smoke, and
  e2e tests into clearer run tiers.
- [Implementation Codebase Audit](language/implementation_codebase_audit.md):
  codebase scan tying implementation seams to stable TODO IDs.
- [Adversarial Implementation Critique](language/adversarial_implementation_critique.md):
  skeptical review of flexibility and performance risks in the current
  implementation.

Parser and syntax substrate:

- [Flexible Syntax Substrate Plan](language/flexible_syntax_substrate_plan.md):
  parser, grammar, lowering, and interpreter architecture.
- [Syntax Substrate TODO Audit](language/syntax_substrate_todo_audit.md):
  central TODO index and inline-code TODO map for easier syntax changes.

## Features

Focused feature designs. Active feature docs should be syntax-facing. Source
feature notes should be mined for decisions, then folded into the active syntax
spine.

| Doc | Role |
| --- | --- |
| [Binding Constraints Feature](features/binding_constraints_feature.md) | Active syntax/semantics for constrained bindings. |
| [Block Calls As Control Values](features/block_calls_feature.md) | Active syntax/semantics for caller-side blocks, `yield`, and policy blocks. |
| [Command Values Feature](features/command_values_feature.md) | Active feature packet for structured commands, previews, subprocess results, and agent/UI replay. |
| [Data Decode Boundary Feature](features/data_decode_boundary_feature.md) | Active feature packet for external data, config, provenance, defaults, redaction, and decode diagnostics. |
| [Failure Taxonomy Feature](features/failure_taxonomy_feature.md) | Active feature packet for absence, expected failure, exceptions, pattern non-match, constraint failure, decode failure, capability denial, and cancellation. |
| [Explanation And Trace Feature](features/explanation_trace_feature.md) | Active feature packet for shared semantic events, diagnostics, traces, examples, and `explain`. |
| [State And Capability Model](features/state_and_capability_model.md) | Active feature packet for world authority, capabilities, block policies, resources, command values, and traceable side effects. |
| [Declarative Implementation Plan](features/declarative_implementation_plan.md) | Source plan for declarative feature metadata and substrate-driven implementation. |
| [Structured Collections And Query Language](features/structured_collections_query_language.md) | Source feature note until collection/query syntax is reduced into the spec and `collections.md`. |
| [Symbolic, Lazy, And Structural Computation](features/symbolic_structural_computation.md) | Integration plan and source feature note for future `quote`, `describe`, `lazy`, rewrite, and plan work. |

## Convenience

Per-feature research on syntactic sugar and shortcuts found across languages.
Start with the convenience review: it consolidates candidates around shared
normal forms so Nomi grows by reduction instead of feature collection.

- [Convenience Index](convenience/README.md)
- [Convenience Review And Roadmap](convenience/review_and_roadmap.md) — normal
  forms, overlap critique, new candidates, implementation phases
- [Syntax Design Rules](convenience/syntax_design_rules.md) — concrete rules
  for primitive budget, axis coherence, eliminators, and promotion gates
- [Syntax And Special Forms Quality Review](convenience/syntax_special_forms_quality_review.md) —
  whole-language syntax/special-form audit and UX bar
- [Expression And Statement Orientation](convenience/expression_statement_orientation.md) —
  doctrine for value-producing and statement-friendly control surfaces
- [Design Lessons And Integration Critique](convenience/design_lessons_and_integration.md) —
  systemic cruft patterns, interaction rules, and synthesis method
- [Global Feature Interaction Map](convenience/interaction_map.md) —
  global/local feature interactions and promotion targets
- [Vertical Surface Pillars And Evolution Paths](convenience/vertical_pillars.md) —
  cross-cutting surfaces from simple programs to sophisticated programs
- [Syntax Synthesis Matrix](convenience/syntax_synthesis_matrix.md) —
  cross-language feature families, nuanced differences, and recommendations
  for combining syntax coherently
- [Language Family Coverage Map](research/language_family_coverage_map.md) —
  canonical index for detailed research notes and coverage status
- [Functions](convenience/functions.md) — equation, piecewise, hole lambda, where, operator sections
- [Flow And Collections](convenience/flow_and_collections.md) — map/filter/reduce, pipelines, ranges, spread
- [Patterns](convenience/patterns.md) — match, destructuring, if-let, guards
- [Absence And Result](convenience/absence_and_result.md) — `?.`, `??`, Result, try-as-expression, guard
- [Data And Types](convenience/data_and_types.md) — data classes, type aliases, strings, extension-method questions
- [Strings](convenience/strings.md) — literals, interpolation, typed wrappers,
  regex capture, and Unicode-view questions
- [Scope & Context](convenience/scope_context.md) — where clause, scope functions, builder DSL
- [Concurrency](convenience/concurrency.md) — async/await, channels, structured concurrency
- [Modules & Imports](convenience/modules_imports.md) — aliases, re-exports
- [Meta & Testing](convenience/meta_testing.md) — decorators, macros, inline tests
- [Implementation Learnings](convenience/implementation_learnings.md) —
  grammar interactions, AST bugs, and deferred special cases from prior work

## Research

Research docs are source material for future syntax work, not active
specification. Use them to recover rationale, compare language traditions, or
seed focused syntax sections. When a research idea becomes stable, fold it into
`language_spec.md`, a feature doc, or a convenience syntax doc.

| Source area | Use for | Fold stable decisions into |
| --- | --- | --- |
| [Cognitive Language Vision](research/cognitive_language_vision.md), [Language Foundation](language/language_foundation.md), [Spec Readiness Map](language/spec_readiness_map.md) | Philosophy and admission pressure. | [Language Foundation](language/language_foundation.md), [Language Direction And Gap Map](language/language_direction_and_gap_map.md) |
| [Research Notes Synthesis](research/research_notes_synthesis.md), [Spec Readiness Map](language/spec_readiness_map.md) | Layering and promotion history. | [Implementation Todos](language/implementation_todos.md), focused feature docs |
| [Language Family Coverage Map](research/language_family_coverage_map.md), [High-Level Language Usability Syntax Notes](research/high_level_language_usability_syntax_notes.md), [Python Syntax Stretch Feature Atlas](research/python_syntax_stretch_feature_atlas.md) | Cross-language comparison. | [Syntax Synthesis Matrix](convenience/syntax_synthesis_matrix.md), focused convenience docs |
| [Overlooked Language Design Dimensions](research/overlooked_language_design_dimensions.md) | Unicode/source text, accessibility, compatibility, migration, governance, localization. | [Language Specification](language/language_spec.md), [Design Proposal Template](language/design_proposal_template.md), explanation-event feature |
| [Orthogonal Language Feature Coverage](research/orthogonal_language_feature_coverage.md) | Cross-cutting design surfaces: formatting, diagnostics, accessibility, observability, packages, capabilities, secrets, interop, migration, governance, conformance, editor UX. | Feature-packet orthogonal impact rows, explanation-event feature, package/tooling docs |
| [Everyday Fallback Simplification Ideas](research/everyday_fallback_simplification_ideas.md), [Python Language Changes Deferred By Complexity](research/python_changes_deferred_by_complexity.md) | Rejected/deferred pressure and simplification ideas. | [Convenience Review And Roadmap](convenience/review_and_roadmap.md), [Language Direction And Gap Map](language/language_direction_and_gap_map.md) |

## Notes

Essays and detours that frame Nomi's philosophy, risk, or design context.

- [Positioning Ambition Risk](notes/positioning_ambition_risk.md)
- [Tractable Sophistication](notes/tractable_sophistication.md)
- [Category Theory Detour](notes/category_theory_detour.md)
- [Notes Meta](notes/meta.md)

## Drafts

Raw draft material. Treat these as scratch/reference input unless a task points
to them directly. Generated combined bundles should not be treated as canonical
docs; they duplicate the active spine and should be removed when no longer
needed.

- [Nomi Design Synthesis](drafts/combined_design_docs_synthesis.md)
- [From ADTs to Dependent Types](drafts/type_theory_design_guide.md)

## Complete Inventory

This inventory intentionally links every Markdown document under `docs/`.
Use the reading order and task routes above for normal work; use this section
when checking whether a document exists, finding source evidence, or pruning
duplicate material.

### Orientation

- [AI Collaboration](orientation/ai_collaboration.md)
- [Artifacts And Usage](orientation/artifacts_and_usage.md)
- [Exploratory Implementation Doctrine](orientation/exploratory_implementation_doctrine.md)
- [Global Consistency Audit](orientation/global_consistency_audit.md)
- [Implementation Guideline](orientation/implementation_guideline.md)
- [Performance Notes](orientation/performance_notes.md)
- [Project Improvement Review 2026-06-03](orientation/project_improvement_review_2026_06_03.md)
- [RAG MCP Context](orientation/rag_mcp.md)
- [Technical Implementation Improvement Notes](orientation/technical_implementation_improvement_notes.md)
- [VS Code Extension](orientation/vscode_extension.md)
- [WASM-JS Runtime Architecture Review](orientation/wasm_js_runtime_review.md)

### Language

- [Adversarial Design Critique](language/adversarial_design_critique.md)
- [Adversarial Enhancement Implementation Plan 2026-06-04](language/adversarial_enhancement_implementation_plan_2026_06_04.md)
- [Adversarial Exploratory Implementation Critique](language/adversarial_exploratory_implementation_critique.md)
- [Adversarial Implementation Critique](language/adversarial_implementation_critique.md)
- [Adversarial Language Design Enhancement Notes 2026-06-04](language/adversarial_language_design_enhancement_notes_2026_06_04.md)
- [Architecture Refactoring Plan](language/architecture_refactoring_plan.md)
- [Backend Independence Roadmap](language/backend_independence_roadmap.md)
- [Core Layer Separation Plan](language/core_layer_separation_plan.md)
- [Core Runtime Backend Design](language/core_runtime_backend_design.md)
- [Core Runtime Backend Implementation Notes](language/core_runtime_backend_implementation_notes.md)
- [Current Capability Matrix](language/current_capability_matrix.md)
- [Delta On Python](language/delta_on_python.md)
- [Design Proposal Template](language/design_proposal_template.md)
- [Docs Eagle Eye Review](language/docs_eagle_eye_review.md)
- [Flexible Syntax Substrate Plan](language/flexible_syntax_substrate_plan.md)
- [Forward Implementation Plan](language/forward_implementation_plan.md)
- [Implementation Codebase Audit](language/implementation_codebase_audit.md)
- [Implementation Evolvability Gap Review](language/implementation_evolvability_gap_review.md)
- [First-Hour Nomi](language/first_hour_nomi.md)
- [Language Feature Todos](language/implementation_todos.md)
- [Language Degrees Of Freedom](language/language_degrees_of_freedom.md)
- [Language Design Dimensions](language/language_design_dimensions.md)
- [Language Direction And Gap Map](language/language_direction_and_gap_map.md)
- [Nomi Language Foundation](language/language_foundation.md)
- [Nomi Language Specification](language/language_spec.md)
- [Modern Language Implementation Artifacts](language/modern_language_implementation_artifacts.md)
- [Parser Frontend Decoupling Plan](language/parser_frontend_decoupling_plan.md)
- [Prelude And Standard Library Plan](language/prelude_and_standard_library_plan.md)
- [Python Independence And Compiler Backend Plan](language/python_independence_and_compiler_backend_plan.md)
- [Spec Readiness Map](language/spec_readiness_map.md)
- [Standard Library Capability Baseline](language/stdlib_capability_baseline.md)
- [Syntax Substrate TODO Audit](language/syntax_substrate_todo_audit.md)
- [Target Language Tour](language/target_language_tour.md)
- [Target Program Fixtures](language/target_program_fixtures.md)
- [Test Suite Restructure Plan](language/test_suite_restructure_plan.md)

### Features

- [Binding Constraints Feature](features/binding_constraints_feature.md)
- [Block Calls As Control Values](features/block_calls_feature.md)
- [Command Values Feature](features/command_values_feature.md)
- [Data Decode Boundary Feature](features/data_decode_boundary_feature.md)
- [Declarative Implementation Plan](features/declarative_implementation_plan.md)
- [Explanation And Trace Feature](features/explanation_trace_feature.md)
- [Failure Taxonomy Feature](features/failure_taxonomy_feature.md)
- [State And Capability Model](features/state_and_capability_model.md)
- [Structured Collections And Query Language](features/structured_collections_query_language.md)
- [Symbolic, Lazy, And Structural Computation](features/symbolic_structural_computation.md)

### Convenience

- [Convenience Features](convenience/README.md)
- [Absence & Result Handling](convenience/absence_and_result.md)
- [Concurrency & Async Convenience](convenience/concurrency.md)
- [Data & Types](convenience/data_and_types.md)
- [Design Lessons & Integration Critique](convenience/design_lessons_and_integration.md)
- [Expression And Statement Orientation](convenience/expression_statement_orientation.md)
- [Flow & Collections](convenience/flow_and_collections.md)
- [Function Convenience](convenience/functions.md)
- [Implementation Learnings & Special Cases](convenience/implementation_learnings.md)
- [Global Feature Interaction Map](convenience/interaction_map.md)
- [Meta-Programming & Testing Convenience](convenience/meta_testing.md)
- [Modules & Imports Convenience](convenience/modules_imports.md)
- [Pattern Convenience](convenience/patterns.md)
- [Convenience Review, Normal Forms, And Roadmap](convenience/review_and_roadmap.md)
- [Scope & Context Convenience](convenience/scope_context.md)
- [Strings](convenience/strings.md)
- [Syntax Design Rules](convenience/syntax_design_rules.md)
- [Syntax And Special Forms Quality Review](convenience/syntax_special_forms_quality_review.md)
- [Syntax Synthesis Matrix](convenience/syntax_synthesis_matrix.md)
- [Vertical Surface Pillars And Evolution Paths](convenience/vertical_pillars.md)

### Research

- [AI-Readable Semantics: How Languages Expose Meaning to Machines](research/ai_readable_semantics_deep_dive.md)
- [Array Language Research (Deep Dive)](research/array_languages_deep_dive.md)
- [BEAM Languages: Erlang, Elixir, Gleam](research/beam_languages_erlang_elixir_gleam.md)
- [Cognitive Language Vision](research/cognitive_language_vision.md)
- [Concatenative Language Research](research/concatenative_languages.md)
- [Cross-Language Synthesis: The Capstone](research/cross_language_synthesis_master.md)
- [C#, Java, and Dart: Modern Feature Deep Dive](research/csharp_java_dart_modern_features.md)
- [Data Boundary Systems: Comprehensive Deep Dive](research/data_boundary_systems_deep_dive.md)
- [Deep Language Feature Survey](research/deep_language_feature_survey.md)
- [Deployment and Operations: Cross-Language Deep Dive](research/deployment_and_operations_deep_dive.md)
- [Diagnostics, Error Messages, and Explanation Design](research/diagnostics_and_explanations_comparative.md)
- [Error Handling, Defer, and Resource Cleanup: Research Notes](research/error_handling_defer_resource_cleanup_notes.md)
- [Everyday Fallback Simplification Ideas](research/everyday_fallback_simplification_ideas.md)
- [Everyday Interface Languages: Deep Dive](research/everyday_interface_languages_deep_dive.md)
- [First-Hour Pedagogy: A Cross-Language Deep Dive](research/first_hour_pedagogy_deep_dive.md)
- [Formatting and Style: Deep Dive](research/formatting_and_style_deep_dive.md)
- [Go Design Philosophy: Deep Dive](research/go_design_philosophy_deep_dive.md)
- [High-Level Language Usability Syntax Notes](research/high_level_language_usability_syntax_notes.md)
- [Human-Computer Interface Languages Deep Dive](research/human_computer_interface_languages_deep_dive.md)
- [Interactive Explanation Deep Dive](research/interactive_explanation_deep_dive.md)
- [Interpolation, Config, And Serialization Languages: Deep Dive](research/interpolation_config_serialization_deep_dive.md)
- [Language Family Coverage Map](research/language_family_coverage_map.md)
- [Modern Language Feature Survey](research/modern_language_feature_survey.md)
- [Orthogonal Language Feature Coverage](research/orthogonal_language_feature_coverage.md)
- [Overlooked Language Design Dimensions](research/overlooked_language_design_dimensions.md)
- [Package Docs & Examples: Cross-Language Deep Dive](research/package_docs_and_examples_deep_dive.md)
- [Packaging & Project Structure: Cross-Language Deep Dive](research/packaging_and_project_structure_deep_dive.md)
- [Pattern Matching: Cross-Language Synthesis](research/pattern_matching_synthesis.md)
- [Python Language Changes Deferred By Complexity](research/python_changes_deferred_by_complexity.md)
- [Python Syntax Stretch Feature Atlas](research/python_syntax_stretch_feature_atlas.md)
- [Remaining Language Feature Gap Survey](research/remaining_language_feature_gap_survey.md)
- [Research Notes Synthesis](research/research_notes_synthesis.md)
- [Scientific Language Research: MATLAB, R, Julia](research/scientific_languages_r_matlab_julia.md)
- [Security and Trust: A Deep Dive](research/security_and_trust_deep_dive.md)
- [Standard Library Design: Cross-Language Comparison](research/standard_library_design_comparative.md)
- [Table and Flow Systems: Deep Dive](research/table_and_flow_systems_deep_dive.md)
- [TypeScript Type System: Deep Dive](research/typescript_type_system_deep_dive.md)

### Notes

- [Category Theory Detour](notes/category_theory_detour.md)
- [Notes Meta](notes/meta.md)
- [Positioning within Ambition and Risk](notes/positioning_ambition_risk.md)
- [Design Note: On Building and Understanding Sophistication](notes/tractable_sophistication.md)

### Drafts

- [Nomi Design Synthesis](drafts/combined_design_docs_synthesis.md)
- [From ADTs to Dependent Types](drafts/type_theory_design_guide.md)

## Admission Rule

The current admission rule for new syntax remains:

> Add syntax only when it reduces to a small semantic primitive and makes a
> common programming pattern clearer at the call site, with diagnostics and
> tests that prove the intended semantics.
