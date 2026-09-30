# C#

> Status: comparative evidence; scope is LINQ execution models.

## Observe

LINQ separates a query's source, construction, and execution. Query behavior
depends on its target, including in-memory enumeration versus provider-backed
queries; query syntax alone does not determine all execution semantics.
[Primary reference: introduction to LINQ](https://learn.microsoft.com/en-us/dotnet/csharp/linq/get-started/introduction-to-linq-queries).

## Judge And Pay

**Adopt** common collection verbs and inspectable query composition. **Adapt**
these to explicit Nomi List, Stream, and TablePlan types. **Defer** query
comprehension syntax and provider quotation until ordinary plan construction
demonstrates a concrete readability failure.

Nomi loses familiar declarative query notation and must write some joins more
verbosely. Its promised benefit is predictable execution mode, not fewer
capabilities. A table plan cannot accept an arbitrary effectful closure and
silently decide whether to translate it or execute it locally.

## Test

Express filtering, joining, grouping, and ordering as calls. Require a plan
inspection artifact before execution and reject unsupported callbacks at the
source range. Compare with the eager
[collection fixture](../../design/targets/collections.nomi).
See [collections](../features/collections.md) and [effects](../features/effects.md).
