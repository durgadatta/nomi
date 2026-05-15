# Convenience Features

Per-feature syntax docs for Nomi convenience forms, backed by comparative
research.  This folder consolidates more than it expands — prefer enhancing
an existing doc over adding a new one.

Start with [design_lessons_and_integration.md](design_lessons_and_integration.md)
for the critical synthesis.  Then use the per-feature docs below.

## Normal Forms

Every accepted convenience reduces to one of eight normal forms:

- **Binding** — receive value, tentatively bind, check constraints, commit or diagnose
- **Function** — parameters are bindings, body evaluates, result may be checked
- **Pattern** — test structure, bind captures, check constraints, choose body
- **Flow** — pass a value through calls, functions, collection transforms, or plans
- **Block** — ordinary call plus attached caller-side code invoked by `yield`
- **Absence/result** — distinguish missing value, expected failure, and unexpected error
- **Data boundary** — external value explicitly decoded into owned data with diagnostics
- **Explanation** — semantic events become traces, examples, diagnostics, or `explain` views

## Documents

### Synthesis & Planning

| Doc | Purpose |
|-----|---------|
| [design_lessons_and_integration.md](design_lessons_and_integration.md) | Systemic cruft patterns, feature interactions, community praise/regret, designer quotes, integration rules |
| [review_and_roadmap.md](review_and_roadmap.md) | Normal-form status spine, cross-doc critique, implementation roadmap |
| [syntax_synthesis_matrix.md](syntax_synthesis_matrix.md) | Cross-language feature families with nuanced differences and Nomi recommendations |
| [expanded_language_research.md](expanded_language_research.md) | Index to detailed research notes in `docs/research/` |

### Per-Feature Docs

| Doc | Normal form | Status |
|-----|-------------|--------|
| [functions.md](functions.md) | Function | implemented (func, `=>`, equations, holes, sections, compose, where) |
| [patterns.md](patterns.md) | Pattern | implemented (match, if-let, while-let, guard-let); includes companion detail appendices |
| [flow_and_collections.md](flow_and_collections.md) | Flow | implemented (pipeline, ranges, range-step, spread) |
| [absence_and_result.md](absence_and_result.md) | Absence/result + Block | implemented (`?.`, `??`, try-expr, guard-let, defer); Result/Option design-needed |
| [data_and_types.md](data_and_types.md) | Data boundary | type aliases + strings implemented; data classes design-needed |
| [scope_context.md](scope_context.md) | Binding + Function | where + block-call DSL implemented; implicit params design-needed |
| [concurrency.md](concurrency.md) | Block + Flow | async/await implemented; structured concurrency design-needed |
| [modules_imports.md](modules_imports.md) | Binding | Python-compatible imports implemented |
| [meta_testing.md](meta_testing.md) | Explanation + Block | decorators implemented; inline tests design-needed |

### Reference

| Doc | Purpose |
|-----|---------|
| [implementation_learnings.md](implementation_learnings.md) | Grammar interactions, AST bugs, deferred features — living reference |

## Research Sources

Deep language surveys live in `../research/`.  See
[expanded_language_research.md](expanded_language_research.md) for the
index, or start with:

- [error_handling_defer_resource_cleanup_notes.md](../research/error_handling_defer_resource_cleanup_notes.md)
- [deep_language_feature_survey.md](../research/deep_language_feature_survey.md)
- [modern_language_feature_survey.md](../research/modern_language_feature_survey.md)

## Consolidation Rules

- Do not add a new doc when an existing doc can absorb the idea.
- Keep companion notes as appendices in the parent doc once stable.
- Source-language catalogues belong in `docs/research/`, not here.
- Implemented features should have runnable examples in `samples/demo.nomi`
  and `samples/demo_terse.nomi` after tests pass.
