# TypeScript

> Status: comparative evidence; Nomi judgments are hypotheses.

## Observe

TypeScript narrows union types through control flow, discriminants, and type
predicates. This supports explicit state modelling without requiring a class
hierarchy at every boundary.
[Primary reference: narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html).

## Judge And Pay

**Adopt** narrowing as useful diagnostic reasoning and **adapt** tagged states
to closed nominal Nomi variants. **Reject** treating a static annotation or
assertion as evidence that untrusted runtime data was validated. Nomi needs a
visible `Value -> Result[Owned, DecodeErrors]` transition.

Nominality loses convenient structural interoperability and requires adapters
between independently defined but similarly shaped products. That cost must
buy better boundary messages and package reasoning, not merely more wrappers.
Type predicates also suggest a useful capability Nomi currently limits: a
pure reusable domain test should remain an ordinary function even though it
does not become a user-defined pattern extractor.

## Test

Send a string where an integer is required, an extra property, and an unknown
variant tag through [boundaries](../../design/targets/boundaries.nomi). Require
three stable paths and no constructed owned value. Compare adapter verbosity
for two nominal products. See [types/data](../features/types_data.md) and
[decoding](../features/decoding.md).
