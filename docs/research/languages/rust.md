# Rust

> Status: comparative evidence; Nomi judgments are hypotheses.

## Observe

Rust's Result represents success or failure as data, with combinators and `?`
for propagation. Error values remain available for context and composition.
[Primary reference: Result](https://doc.rust-lang.org/std/result/).

## Judge And Pay

**Adopt** explicit expected failure and **adapt** propagation to Nomi's
Result/Option distinction. **Defer** any inference that importing `?` also
imports Rust's ownership or lifetime guarantees. Nomi's GC profile and resource
scopes require their own escape and cleanup rules.

Typed error plumbing can become repetitive when a workflow crosses several
libraries. Nomi should keep explicit mapping to domain variants but measure
whether diagnostics make the boilerplate understandable. Automatic conversion
must not become an invisible catch-all. Distinguishing panic from Result also
means the result type does not enumerate every abnormal exit.

## Test

Trace two failures through [failure](../../design/targets/failure.nomi): an
expected parse error and an internal constraint violation. Require different
channels and preservation of the original cause. Attempt to return a live
reader from a resource scope; record the missing lifetime rule rather than
assuming the Rust answer. See [failure](../features/failure.md) and
[resources](../features/resources.md).
