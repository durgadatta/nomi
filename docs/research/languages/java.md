# Java

> Status: comparative evidence; scope is the historical Java 16 records design.

## Observe

Java records express transparent data carriers with declared components and
generated members. Component finality does not make objects reachable through
components deeply immutable.
[Primary reference: record specification changes](https://cr.openjdk.org/~gbierman/jep395/jep395-20201204/specs/records-jls.html).

## Judge And Pay

**Adopt** reducing boilerplate for explicit domain products. **Adapt** this to
Nomi's immutable `data` contract and constrained fields. **Reject** saying
"immutable" without specifying what happens to nested collections and host
references.

Nomi's stronger immutable-value ambition may require copies or restricted
interop. Record-like generated equality and decoding also need inspectable
rules; an easy declaration should not hide expensive traversal or accidental
secret disclosure. Generated behavior must be a specified projection, not
whatever the current backend happens to synthesize.

## Test

Construct a Ticket with a collection field, retain the source collection, and
attempt to mutate it through each alias. Specify the result before choosing
a runtime representation. Inspect generated equality and decoder metadata.
See [types/data](../features/types_data.md), [decoding](../features/decoding.md),
and [data](../../design/targets/data.nomi).
