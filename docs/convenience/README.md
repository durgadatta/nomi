# Convenience Features

Per-feature research docs on syntactic sugar and semantic shortcuts found
across languages. These are candidates for selective, progressive
implementation in Nomi only when they reduce to a small, shared normal form.

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

Each doc should cover: the everyday need, examples in source languages, Nomi's
normal-form reduction, current status, critique, and implementation notes.

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

| Doc | Feature | Status |
|-----|---------|--------|
| [review_and_roadmap.md](review_and_roadmap.md) | Cross-doc critique, normal forms, new feature candidates, roadmap | active roadmap |
| [expanded_language_research.md](expanded_language_research.md) | Newer language and PL research pass, overlap consolidation, extra candidates | active research |
| [syntax_synthesis_matrix.md](syntax_synthesis_matrix.md) | Cross-language feature families, nuanced differences, and Nomi combination recommendations | active synthesis |
| [functions.md](functions.md) | Function normal form, equations, piecewise clauses, holes, sections, composition, where | active synthesis; many surfaces implemented |
| [implicit_functions_nuance.md](implicit_functions_nuance.md) | Scoping reference for `_`, `$1`, `$name`, `(+)`, `=>` | focused detail |
| [implementation_learnings.md](implementation_learnings.md) | Tricky grammar interactions, AST bugs, deferred features | living reference |
| [challenges_match_as_expression.md](challenges_match_as_expression.md) | Match-as-expression parser caveats and remaining full-suite challenge | focused detail |
| [if_let_detail.md](if_let_detail.md) | If-let difference from `if`, pattern edge cases, desugaring | focused detail |
| [collections.md](collections.md) | map/filter/reduce, pipelines, ranges, spread, broadcasting | partial; pipeline/ranges/range-step/spread done |
| [patterns.md](patterns.md) | Pattern normal form, match, if-let, while-let, guard-let, piecewise dispatch, future captures | active synthesis; partial prototype |
| [null_handling.md](null_handling.md) | optional chaining `?.`, null coalesce `??`, Option/Result | partial; `??` and safe attr/call/subscript done |
| [error_handling.md](error_handling.md) | try-as-expression, `?` propagate, guard, let-else | partial; try-expr, guard-let, defer done |
| [strings.md](strings.md) | interpolation, multi-line, heredocs, regex literals | partial; simple f-strings+triple-quote done |
| [types.md](types.md) | data classes, type aliases, extension methods, operator overloading | type aliases done |
| [scope_context.md](scope_context.md) | scope functions (let/apply/also), implicit params, builder DSL | where+defer done |
| [concurrency.md](concurrency.md) | async/await, structured concurrency, channels, actors | async/await |
| [modules_imports.md](modules_imports.md) | import aliases, re-exports, wildcard, multi-import | basic imports |
| [meta_testing.md](meta_testing.md) | decorators, macros, inline tests, doctests | decorators done |
| [array_languages.md](array_languages.md) | APL/J/K/Q: adverbs, broadcasting, qSQL, forks, til | research-only |
| [others.md](others.md) | Go, Rust, Ruby, TS, Swift, Elixir, SQL, PS, R, Pascal, C#, academic | mixed |

For philosophical / design research, see `../research/`.

## Sample Discipline

When a convenience feature is later implemented, add runnable examples only
after focused tests pass. The full guided example belongs in
`samples/demo.nomi`; the compressed memory-refresh version belongs in
`samples/demo_terse.nomi`. If the feature is also part of interpreter
regression coverage, update the relevant file under
`prototype/tests/data/sample_sources/`.
