# Convenience Features

Per-feature syntax docs for Nomi convenience forms, backed by comparative
research. This folder should now consolidate more than it expands: prefer
enhancing an existing syntax doc over adding a new one.

Start with
[review_and_roadmap.md](review_and_roadmap.md). It consolidates the folder
around Nomi normal forms: binding, function, pattern, flow, block,
absence/result, data boundary, and explanation. Individual docs should use the
status labels from that review:

```text
implemented
prototype-ready
design-needed
library-first
research-only
rejected-for-now
```

Each durable doc should be syntax-facing. It should cover: Nomi examples,
everyday need, normal-form reduction, current implementation status,
diagnostics, rejected alternatives, and implementation notes. Source-language
examples belong only where they change a concrete Nomi decision.

## Consolidation Rules

- Do not add a new convenience doc when an existing syntax family can absorb
  the idea.
- Keep `functions.md`, `patterns.md`, `collections.md`, `error_handling.md`,
  `null_handling.md`, `types.md`, `strings.md`, `scope_context.md`,
  `modules_imports.md`, `concurrency.md`, and `meta_testing.md` as the main
  syntax homes.
- Keep `review_and_roadmap.md` as the normal-form and status spine.
- Keep `syntax_synthesis_matrix.md` and `expanded_language_research.md` as
  source research, not day-to-day specs.
- When a focused companion note becomes stable, fold its decision back into the
  main syntax doc and leave the companion as edge-case history.

Use the overview/detail split to keep the folder from growing sideways:

- put synthesis, admission decisions, and teaching order in the main feature
  docs such as `functions.md`, `patterns.md`, `collections.md`, and
  `error_handling.md`;
- keep parser caveats, scoping edge cases, and implementation scars in focused
  companion notes such as `implicit_functions_nuance.md`,
  `if_let_detail.md`, and `challenges_match_as_expression.md`;
- move broad source-language catalogues into `expanded_language_research.md`,
  `syntax_synthesis_matrix.md`, or `others.md` unless they change a concrete
  Nomi recommendation.

| Doc | Normal form | Status |
|-----|-------------|--------|
| [review_and_roadmap.md](review_and_roadmap.md) | Cross-doc critique, normal forms, new feature candidates, roadmap | active spine |
| [design_lessons_and_integration.md](design_lessons_and_integration.md) | Systemic cruft patterns, feature interaction analysis, community praise/regret, integration rules | active synthesis |
| [syntax_synthesis_matrix.md](syntax_synthesis_matrix.md) | Cross-language feature families, nuanced differences, and Nomi combination recommendations | research source |
| [expanded_language_research.md](expanded_language_research.md) | Newer languages (Roc, Gleam, Zig, Unison, CUE, etc.) and PL research, overlap consolidation | research source |
| [functions.md](functions.md) | Function: equations, piecewise, holes, sections, composition, where | implemented (func, =>, equations, holes, sections, compose, where) |
| [implicit_functions_nuance.md](implicit_functions_nuance.md) | Function (companion): scoping reference for `_`, `$1`, `$name`, `(+)` | focused detail |
| [patterns.md](patterns.md) | Pattern: match, if-let, while-let, guard-let, destructuring, future captures | implemented (match, if-let, while-let, guard-let); destructuring partial |
| [if_let_detail.md](if_let_detail.md) | Pattern (companion): if-let vs `if`, edge cases, desugaring | focused detail |
| [challenges_match_as_expression.md](challenges_match_as_expression.md) | Pattern (companion): match-as-expression parser caveats, full-suite challenge | focused detail |
| [collections.md](collections.md) | Flow: pipelines, map/filter/reduce, ranges, spread, comprehensions | implemented (pipeline, ranges, range-step, spread, comprehensions) |
| [error_handling.md](error_handling.md) | Absence/result + Block: try-expression, `?` propagate, guard, defer | implemented (try-expr, guard-let, defer); propagate design-needed |
| [null_handling.md](null_handling.md) | Absence/result: `?.`, `??`, Option/Result types | implemented (`?.`, `??`); Option/Result design-needed |
| [scope_context.md](scope_context.md) | Binding + Function: where clauses, scope functions, implicit params, builder DSL | implemented (where, block-call DSL); implicit params design-needed |
| [types.md](types.md) | Data boundary: type aliases, data classes, sum types, extension methods | type aliases implemented; data classes design-needed |
| [strings.md](strings.md) | Data boundary: interpolation, multi-line, heredocs, regex | f-strings + triple-quote implemented; regex library-first |
| [concurrency.md](concurrency.md) | Block + Flow: async/await, structured concurrency, channels, actors | async/await implemented; structured concurrency design-needed |
| [modules_imports.md](modules_imports.md) | Binding: import aliases, re-exports, wildcard, multi-import | basic Python-compatible imports implemented |
| [meta_testing.md](meta_testing.md) | Explanation + Block: decorators, inline tests, assert diagnostics, macros | decorators implemented; inline tests design-needed |
| [array_languages.md](array_languages.md) | Flow (research): APL/J/K/Q adverbs, broadcasting, forks, array rank | research-only |
| [others.md](others.md) | Misc catalogue: Go, Rust, Ruby, TS, Swift, Elixir, SQL, PS, R, Pascal, C#, academic | mixed; candidate for folding into per-feature docs |
| [implementation_learnings.md](implementation_learnings.md) | Grammar interactions, AST bugs, deferred features | living reference |

For philosophical / design research, see `../research/`.

## Sample Discipline

When a convenience feature is later implemented, add runnable examples only
after focused tests pass. The full guided example belongs in
`samples/demo.nomi`; the compressed memory-refresh version belongs in
`samples/demo_terse.nomi`. If the feature is also part of interpreter
regression coverage, update the relevant file under
`prototype/tests/data/sample_sources/`.
