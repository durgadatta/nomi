# Nomi Docs

> Status: documentation entry point.
>
> This directory is organized by conceptual category and rough concreteness:
> orientation and project-process docs first, current language direction next,
> focused feature designs after that, then broader research notes, essays,
> archive material, and drafts.

## Reading Order

Start here for most design or implementation work:

1. [Language Foundation](language/language_foundation.md)
2. [Language Direction And Gap Map](language/language_direction_and_gap_map.md)
3. [Language Specification](language/language_spec.md)
4. [Implementation Todos](language/implementation_todos.md)
5. [Artifacts And Usage](orientation/artifacts_and_usage.md)
6. [AI Collaboration](orientation/ai_collaboration.md)

For feature work, read the relevant focused design under
[features](features/) after the foundation.

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

## Language

Canonical or near-canonical language direction. These are the decision surface
for the next implementation pass.

- [Language Foundation](language/language_foundation.md): current design
  foundation and operational core.
- [Language Direction And Gap Map](language/language_direction_and_gap_map.md):
  adoption-oriented steering note, coherence gaps, caveats, and next design
  artifacts.
- [Language Degrees Of Freedom](language/language_degrees_of_freedom.md):
  framework for deciding what belongs in the strict core, surface sugar,
  libraries, scoped extensions, future layers, or rejection.
- [Language Specification](language/language_spec.md): draft concrete spec.
- [Implementation Todos](language/implementation_todos.md): staged backlog.
- [Delta On Python](language/delta_on_python.md): rationale for changes
  relative to Python.

## Features

Focused feature designs. These are more concrete than research notes but may
still contain open design questions.

- [Binding Constraints Feature](features/binding_constraints_feature.md):
  constrained binding syntax, semantics, and diagnostics.
- [Block Calls As Control Values](features/block_calls_feature.md): caller-side
  blocks, `yield`, and policy blocks.
- [Yield To Block](features/yield_to_block.md): historical and delicate
  resumable-control notes.
- [Structured Collections And Query Language](features/structured_collections_query_language.md):
  collection/table/query API and syntax design.
- [Symbolic And Structural Computation](features/symbolic_structural_computation.md):
  computation descriptions, plans, rewrites, and backend lowering.

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
- [Collections](convenience/collections.md) — map/filter/reduce, pipelines, ranges, spread
- [Patterns](convenience/patterns.md) — match, destructuring, if-let, guards
- [Null Handling](convenience/null_handling.md) — `?.`, `??`, Option/Result types
- [Error Handling](convenience/error_handling.md) — `?`, try-as-expression, guard
- [Strings](convenience/strings.md) — interpolation, multi-line, regex
- [Types](convenience/types.md) — data classes, type aliases, extension methods
- [Scope & Context](convenience/scope_context.md) — where clause, scope functions, builder DSL
- [Concurrency](convenience/concurrency.md) — async/await, channels, structured concurrency
- [Modules & Imports](convenience/modules_imports.md) — aliases, re-exports
- [Meta & Testing](convenience/meta_testing.md) — decorators, macros, inline tests

## Research

Source notes and speculative synthesis. Use these to recover rationale, compare
language traditions, or seed future focused specs.

- [Cognitive Language Vision](research/cognitive_language_vision.md)
- [First-Principles Programming Model](research/first_principles_programming_model.md)
- [Hierarchical Language Research Plan](research/hierarchical_language_research_plan.md)
- [Research Notes Synthesis](research/research_notes_synthesis.md)
- [Language Coherence Model](research/language_coherence_model.md)
- [Language Family Coverage Map](research/language_family_coverage_map.md)
- [Everyday Fallback Simplification Ideas](research/everyday_fallback_simplification_ideas.md)
- [High-Level Language Usability Syntax Notes](research/high_level_language_usability_syntax_notes.md)
- [Python Language Changes Deferred By Complexity](research/python_changes_deferred_by_complexity.md)
- [Python Syntax Stretch Feature Atlas](research/python_syntax_stretch_feature_atlas.md)

## Notes

Essays and detours that frame Nomi's philosophy, risk, or design context.

- [Positioning Ambition Risk](notes/positioning_ambition_risk.md)
- [Tractable Sophistication](notes/tractable_sophistication.md)
- [Category Theory Detour](notes/category_theory_detour.md)
- [Notes Meta](notes/meta.md)

## Archive

Historical design material. These files are source material, not active
specification.

- [Archived Design Review](archive/design_review/README.md)

## Drafts

Raw draft material and large combined synthesis artifacts. Treat these as
scratch/reference input unless a task points to them directly.

- [Drafts](drafts/)

## Admission Rule

The current admission rule for new syntax remains:

> Add syntax only when it reduces to a small semantic primitive and makes a
> common programming pattern clearer at the call site, with diagnostics and
> tests that prove the intended semantics.
