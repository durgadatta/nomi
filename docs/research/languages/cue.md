# CUE

> Status: comparative evidence; scope is CUE's value lattice.

## Observe

CUE puts values, types, and constraints in a common lattice and combines
information through unification. This supports order-independent constraint
composition rather than ordinary imperative assignment.
[Primary reference: the logic of CUE](https://cuelang.org/docs/concept/the-logic-of-cue/).

## Judge And Pay

**Adopt** constraints as reusable schema information. **Adapt** them to pure
Nomi predicates evaluated at explicit construction and decoding boundaries.
**Reject** importing general unification into binding semantics.

Nomi loses declarative multi-source merging and some schema reasoning.
Arbitrary predicates cannot automatically support CUE-like compatibility
proofs; a generated schema may only project the portable subset. Claiming all
`where` clauses can become JSON Schema would overstate the target.

## Test

Define a range predicate, a cross-field predicate, and a pure function predicate.
Inspect which can be exported and require an explicit unsupported-projection
message for the rest. Keep runtime validation complete even when projection
is partial. See [decoding](../features/decoding.md),
[types/data](../features/types_data.md), and [boundaries](../../design/targets/boundaries.nomi).
