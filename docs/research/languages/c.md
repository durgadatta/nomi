# C

> Status: comparative evidence; baseline is the C11 committee draft N1570.

## Observe

C exposes explicit object lifetimes, pointer operations, and integer behavior;
the draft specifies undefined behavior for some invalid operations, including
unrepresentable signed arithmetic results.
[Primary reference: N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf).

## Judge And Pay

**Adopt** taking representation and interop seriously. **Reject** undefined
arithmetic and unchecked pointer behavior as friendly Nomi defaults. **Defer**
low-level access to explicit host/profile contracts instead of contaminating
ordinary scripts with backend-dependent behavior.

GC, checking, and explicit conversions can cost time and memory; Nomi cannot
promise C's control or deployment footprint without evidence. Conversely, a
safe surface is not enough if a host adapter truncates numbers or retains
invalid memory behind it. FFI must validate ranges and state lifetime rules.

## Test

Round-trip minimum, maximum, and out-of-range host integers across CLI and
Wasm. Require the same deliberate conversion failures, never silent truncation.
Document whether native resource handles can cross a closed scope. See
[numerics](../features/numerics.md), [resources](../features/resources.md), and
[numerics.nomi](../../design/targets/numerics.nomi).
