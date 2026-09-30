# Haskell

> Status: comparative evidence; baseline is Haskell 2010, not all extensions.

## Observe

Haskell 2010 uses non-strict expression semantics and curried function
application, with pattern bindings and operator sections among its expression
forms. This is a coherent model, not a bag of independent conveniences.
[Primary reference: expressions](https://www.haskell.org/onlinereport/haskell2010/haskellch3.html).

## Judge And Pay

**Adopt** explicit algebraic alternatives and compositional pure functions.
**Reject** default non-strict evaluation, sections, and currying for Nomi's
eager model. Borrowing one of these surfaces without its evaluation discipline
would create misleading expectations about when work and failure happen.

Nomi loses elegant infinite structures and some compositional idioms. It must
offer explicit streams for bounded memory without claiming that eager lists
have become lazy just because they use a pipeline. Haskell's purity also
highlights a Nomi gap: effectful callback contracts must be explicit, not left
to an implementation's host call behavior.

## Test

Instrument a three-step transformation with an early error and a partial
consumer. Specify call counts separately for List and Stream. Compare a
partial application with Nomi's explicit lambda. See
[functions](../features/functions.md), [collections](../features/collections.md),
and [effects](../features/effects.md).
