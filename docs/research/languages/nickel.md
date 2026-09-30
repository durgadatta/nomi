# Nickel

> Status: comparative evidence; scope is contracts.

## Observe

Nickel uses contracts to validate values, including higher-order values, and
reports blame at contract boundaries. Contract checking can have evaluation
and timing implications beyond a static type annotation.
[Primary reference: contracts](https://nickel-lang.org/user-manual/contracts/).

## Judge And Pay

**Adopt** contextual explanations of violated expectations. **Adapt** this to
Nomi's declared constraints and path-bearing decode errors. **Reject** allowing
ordinary constraint predicates to acquire authority or silently postpone
checking until unrelated later use.

Nomi's eager boundary validation may perform more work than a lazy contract
system for fields never used. It also currently has no settled higher-order
contract surface. These costs should remain visible rather than being hidden
behind a claim that all contracts are just `where`.

## Test

Decode a nested list with several invalid fields. Require independent errors
at the boundary and no delayed exception on later field access. For an invalid
internal constructor, require declaration and use-site locations instead.
See [decoding](../features/decoding.md), [failure](../features/failure.md), and
[boundaries.nomi](../../design/targets/boundaries.nomi).
