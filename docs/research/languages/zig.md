# Zig

> Status: comparative evidence; cited master documentation is moving.

## Observe

Zig separates error sets and error unions, and supplies both `defer` and
error-path `errdefer`. These make different cleanup intentions visible.
[Primary reference: language reference](https://ziglang.org/documentation/master/).

## Judge And Pay

**Adopt** explicit failure paths and conditional cleanup as a design pressure.
**Defer** an additional Nomi error-only cleanup keyword. Ordinary state and
unconditional lexical defer should first demonstrate whether rollback intent
can remain clear without a second scope-exit mechanism.

Nomi pays with more explicit bookkeeping for staged acquisition. Conversely,
a new keyword would need to define whether cancellation, panic, or an ordinary
returned Err qualifies as its trigger. Zig's systems context does not settle
that taxonomy for a GC language with async resource scopes.

## Test

Specify acquire A, acquire B, commit, then fail each stage independently.
Require exactly one cleanup per acquired resource and no rollback after a
successful commit. Compare an explicit committed flag with a proposed library
transaction object before considering syntax. See [resources](../features/resources.md)
and [failure](../features/failure.md).
