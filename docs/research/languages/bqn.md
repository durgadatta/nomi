# BQN

> Status: comparative evidence; scope is mapping modifiers.

## Observe

BQN distinguishes Each, Table, Cells, and Rank rather than using one vague
"map" operation. Its two-input mapping rules specify shape agreement and
reject some mismatches instead of truncating silently.
[Primary reference: mapping modifiers](https://mlochbaum.github.io/BQN/doc/map.html).

## Judge And Pay

**Adopt** naming the domain of iteration and shape agreement. **Adapt** these
ideas to distinct Nomi array operations. **Reject** pretending one collection
verb has identical laws for Lists, arrays, and relational plans.

Nomi's familiar `map` may be too weak a vocabulary for array specialists. That
is a reason to extend a domain library coherently, not a reason to give the
pipeline operator implicit broadcasting. More operation names cost learning,
but may be necessary to expose genuinely different mathematical acts.

## Test

Compare zip-like element pairing, a Cartesian table, and mapping over cells.
Use unequal shapes and require explicit outcomes; record whether truncation is
ever intentional. Keep the List contract separate from array agreement.
See [numerics](../features/numerics.md), [collections](../features/collections.md),
and [collections.nomi](../../design/targets/collections.nomi).
