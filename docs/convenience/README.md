# Convenience Features

Per-feature research docs on syntactic sugar and semantic shortcuts
found across languages — candidates for selective, progressive
implementation in Nomi.

Each doc covers: what the feature is, examples in source languages,
current Nomi status, and implementation notes.

| Doc | Feature | Status |
|-----|---------|--------|
| [functions.md](functions.md) | Equation, piecewise, hole lambda, where, operator sections | **mostly implemented** |
| [implicit_functions_nuance.md](implicit_functions_nuance.md) | Nuance comparison of `_`, `$1`, `$name`, `(+)`, `=>` | living reference |
| [collections.md](collections.md) | map/filter/reduce, pipelines, ranges, spread, broadcasting | partial |
| [patterns.md](patterns.md) | match/destructuring, if-let, guards, match-as-expression | partial |
| [null_handling.md](null_handling.md) | optional chaining `?.`, null coalesce `??`, Option/Result | not started |
| [error_handling.md](error_handling.md) | try-as-expression, `?` propagate, guard, let-else | not started |
| [strings.md](strings.md) | interpolation, multi-line, heredocs, regex literals | f-strings partial |
| [types.md](types.md) | data classes, type aliases, extension methods, operator overloading | not started |
| [scope_context.md](scope_context.md) | scope functions (let/apply/also), implicit params, builder DSL | where clause done |
| [concurrency.md](concurrency.md) | async/await, structured concurrency, channels, actors | async/await |
| [modules_imports.md](modules_imports.md) | import aliases, re-exports, wildcard, multi-import | basic imports |
| [meta_testing.md](meta_testing.md) | decorators, macros, inline tests, doctests | decorators done |
| [array_languages.md](array_languages.md) | APL/J/K/Q: adverbs, broadcasting, qSQL, forks, til | not started |
| [others.md](others.md) | Go, Rust, Ruby, TS, Swift, Elixir, SQL, PS, R, Pascal, C#, academic | mixed |

For philosophical / design research, see `../research/`.
