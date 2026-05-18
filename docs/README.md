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

## Orientation

Concrete project, process, and tooling docs.

- [Artifacts And Usage](orientation/artifacts_and_usage.md): current runtime
  pipeline and artifact map.
- [Implementation Guideline](orientation/implementation_guideline.md):
  implementation posture and AI tool history.
- [AI Collaboration](orientation/ai_collaboration.md): accepted AI use cases,
  critique workflow, and checkpoint doctrine.
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
| Add or change syntax | [Flexible Syntax Substrate Plan](language/flexible_syntax_substrate_plan.md), [Syntax Substrate TODO Audit](language/syntax_substrate_todo_audit.md), the relevant [Convenience](convenience/) note, [Design Proposal Template](language/design_proposal_template.md) |
| Audit implementation gaps | [Implementation Codebase Audit](language/implementation_codebase_audit.md), [Syntax Substrate TODO Audit](language/syntax_substrate_todo_audit.md), [Architecture Refactoring Plan](language/architecture_refactoring_plan.md) |
| Critique implementation flexibility/performance | [Adversarial Implementation Critique](language/adversarial_implementation_critique.md), [Performance Notes](orientation/performance_notes.md), [Implementation Codebase Audit](language/implementation_codebase_audit.md) |
| Design binding or decode | [Binding Constraints Feature](features/binding_constraints_feature.md), [Language Foundation](language/language_foundation.md), [Target Program Fixtures](language/target_program_fixtures.md) |
| Work on blocks/control | [Block Calls As Control Values](features/block_calls_feature.md), [Concurrency](convenience/concurrency.md) |
| Work on collections/query | [Structured Collections And Query Language](features/structured_collections_query_language.md), [Flow And Collections](convenience/flow_and_collections.md), [Syntax Synthesis Matrix](convenience/syntax_synthesis_matrix.md) |
| Improve design docs | [Spec Readiness Map](language/spec_readiness_map.md), [Language Direction And Gap Map](language/language_direction_and_gap_map.md), [Docs Eagle Eye Review](language/docs_eagle_eye_review.md), [Language Family Coverage Map](research/language_family_coverage_map.md) |
| Critique design coherence | [Adversarial Design Critique](language/adversarial_design_critique.md), [Global Feature Interaction Map](convenience/interaction_map.md), [Spec Readiness Map](language/spec_readiness_map.md) |
| Make samples or demos | [Target Program Fixtures](language/target_program_fixtures.md), [Target Language Tour](language/target_language_tour.md), [Language Specification](language/language_spec.md) |

## Language

Canonical or near-canonical language direction. These are the decision surface
for the next implementation pass.

Core direction:

- [Language Foundation](language/language_foundation.md): canonical foundation
  and operational core.
- [Language Specification](language/language_spec.md): draft concrete spec.
- [Language Degrees Of Freedom](language/language_degrees_of_freedom.md):
  strict core, sugar, libraries, scoped extensions, future layers, and
  rejection framework.
- [Delta On Python](language/delta_on_python.md): rationale for changes
  relative to Python.

Target programs:

- [Target Program Fixtures](language/target_program_fixtures.md):
  aspirational task-sized programs.
- [Target Demo Script](language/demo_target.nomi): compact target-only
  `.nomi` script for the future operational spec; not expected to parse today.
- [Target Language Tour](language/target_language_tour.md): large whole-program
  coherence target.

Planning and process:

- [Language Direction And Gap Map](language/language_direction_and_gap_map.md):
  adoption-oriented steering note, core gap map, and docs consolidation policy.
- [Docs Eagle Eye Review](language/docs_eagle_eye_review.md): full-docs scan
  for hidden bridge gaps and next synthesis moves.
- [Adversarial Design Critique](language/adversarial_design_critique.md):
  hostile review of feature and global-language failure modes.
- [Spec Readiness Map](language/spec_readiness_map.md): promotion workflow and
  coverage map for converting research, convenience notes, feature docs, and
  implementation plans into a future language specification.
- [Forward Implementation Plan](language/forward_implementation_plan.md):
  staged implementation sequence and gates.
- [Implementation Todos](language/implementation_todos.md): staged backlog.
- [Design Proposal Template](language/design_proposal_template.md): proposal
  process for new syntax, features, and promoted research ideas.
- [Architecture Refactoring Plan](language/architecture_refactoring_plan.md):
  high-level runtime API, pipeline, package, host, and frontend adapter plan.
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
| [Structured Collections And Query Language](features/structured_collections_query_language.md) | Source feature note until collection/query syntax is reduced into the spec and `collections.md`. |
| [Symbolic And Structural Computation](features/symbolic_structural_computation.md) | Source feature note for future `quote`, rewrite, and plan work. |

## Convenience

Per-feature research on syntactic sugar and shortcuts found across languages.
Start with the convenience review: it consolidates candidates around shared
normal forms so Nomi grows by reduction instead of feature collection.

- [Convenience Index](convenience/README.md)
- [Convenience Review And Roadmap](convenience/review_and_roadmap.md) — normal
  forms, overlap critique, new candidates, implementation phases
- [Expanded Language Research](convenience/expanded_language_research.md) —
  newer languages, PL research ideas, consolidation decisions
- [Syntax Synthesis Matrix](convenience/syntax_synthesis_matrix.md) —
  cross-language feature families, nuanced differences, and recommendations
  for combining syntax coherently
- [Functions](convenience/functions.md) — equation, piecewise, hole lambda, where, operator sections
- [Flow And Collections](convenience/flow_and_collections.md) — map/filter/reduce, pipelines, ranges, spread
- [Patterns](convenience/patterns.md) — match, destructuring, if-let, guards
- [Absence And Result](convenience/absence_and_result.md) — `?.`, `??`, Result, try-as-expression, guard
- [Data And Types](convenience/data_and_types.md) — data classes, type aliases, strings, extension-method questions
- [Scope & Context](convenience/scope_context.md) — where clause, scope functions, builder DSL
- [Concurrency](convenience/concurrency.md) — async/await, channels, structured concurrency
- [Modules & Imports](convenience/modules_imports.md) — aliases, re-exports
- [Meta & Testing](convenience/meta_testing.md) — decorators, macros, inline tests

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

- [Drafts](drafts/)

## Admission Rule

The current admission rule for new syntax remains:

> Add syntax only when it reduces to a small semantic primitive and makes a
> common programming pattern clearer at the call site, with diagnostics and
> tests that prove the intended semantics.
