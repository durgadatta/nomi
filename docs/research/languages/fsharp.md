# F#

> Status: comparative evidence; scope is active patterns.

## Observe

F# active patterns let named functions participate in pattern decomposition,
including partial classifications. They extend matching beyond fixed data
constructors.
[Primary reference: active patterns](https://learn.microsoft.com/en-us/dotnet/fsharp/language-reference/active-patterns).

## Judge And Pay

**Adopt** reusable domain classification. **Adapt** it to an ordinary function
returning a closed variant or Option, followed by structural Nomi `match`.
**Reject** user-defined extractors in the accepted pattern grammar. A matching
arm should not hide arbitrary computation, effects, or repeated work.

The price is an extra named intermediate and less compositional matching of
domain views. F# makes that abstraction pleasant; Nomi must demonstrate that
its long form preserves readability rather than simply forbidding power.
Purity alone would not settle termination, repeated evaluation, or coverage
reasoning for extensible extractors.

## Test

Classify an email once with an ordinary function, then match on the result.
Count evaluations and compare diagnostic ranges to a hypothetical extractor
form. Keep the structural form unless the alternative has a complete coverage
and evaluation contract. See [patterns](../features/patterns.md) and
[the pattern fixture](../../design/targets/patterns.nomi).
