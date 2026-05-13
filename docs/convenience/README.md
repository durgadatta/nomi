# Convenience Features

Per-feature research docs on syntactic sugar and semantic shortcuts
found across languages — candidates for selective, progressive
implementation in Nomi.

Each doc covers: what the feature is, examples in source languages,
current Nomi status, and implementation notes.

| Doc | Feature | Status |
|-----|---------|--------|
| [review_and_roadmap.md](review_and_roadmap.md) | Cross-doc critique, stale-status audit, implementation queue | active roadmap |
| [functions.md](functions.md) | Equation, piecewise, hole lambda, where, operator sections | **mostly implemented; doc partly stale** |
| [implicit_functions_nuance.md](implicit_functions_nuance.md) | Nuance comparison of `_`, `$1`, `$name`, `(+)`, `=>` | living reference |
| [implementation_learnings.md](implementation_learnings.md) | Tricky grammar interactions, AST bugs, deferred features | living reference |
| [challenges_match_as_expression.md](challenges_match_as_expression.md) | Match-as-expression: implemented forms and remaining full-suite challenge | partial |
| [if_let_detail.md](if_let_detail.md) | If-let: difference from `if`, patterns, edge cases, cross-lang ref | implemented |
| [collections.md](collections.md) | map/filter/reduce, pipelines, ranges, spread, broadcasting | partial; pipeline/ranges/spread done |
| [patterns.md](patterns.md) | match/destructuring, if-let, guards, match-as-expression | partial; match expressions now work in expression-valued forms |
| [null_handling.md](null_handling.md) | optional chaining `?.`, null coalesce `??`, Option/Result | partial; `??` and safe attr/call/subscript done |
| [error_handling.md](error_handling.md) | try-as-expression, `?` propagate, guard, let-else | partial; try-expr and defer done |
| [strings.md](strings.md) | interpolation, multi-line, heredocs, regex literals | partial; simple f-strings+triple-quote done |
| [types.md](types.md) | data classes, type aliases, extension methods, operator overloading | type aliases done |
| [scope_context.md](scope_context.md) | scope functions (let/apply/also), implicit params, builder DSL | where+defer done |
| [concurrency.md](concurrency.md) | async/await, structured concurrency, channels, actors | async/await |
| [modules_imports.md](modules_imports.md) | import aliases, re-exports, wildcard, multi-import | basic imports |
| [meta_testing.md](meta_testing.md) | decorators, macros, inline tests, doctests | decorators done |
| [array_languages.md](array_languages.md) | APL/J/K/Q: adverbs, broadcasting, qSQL, forks, til | not started |
| [others.md](others.md) | Go, Rust, Ruby, TS, Swift, Elixir, SQL, PS, R, Pascal, C#, academic | mixed |

For philosophical / design research, see `../research/`.
