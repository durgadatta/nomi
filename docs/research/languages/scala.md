# Scala

> Status: comparative evidence; scope is Scala 3 pattern matching.

## Observe

Scala 3 supports extractor-based matching through mechanisms such as `unapply`.
Pattern abstraction can therefore invoke library-defined behavior rather than
only inspect a fixed representation.
[Primary reference: pattern matching](https://docs.scala-lang.org/scala3/reference/changed-features/pattern-matching.html).

## Judge And Pay

**Adopt** powerful domain decomposition as a use case. **Adapt** it to an
ordinary classifier call followed by Nomi's structural match. **Reject**
extractors in the accepted core pattern vocabulary, keeping evaluation and
coverage analysis bounded by the language contract.

That loses concise composition of virtual views and can expose intermediates
that Scala hides elegantly. Nomi's alternative is credible only if naming
those values improves debugging and avoids repeated expensive work. A pure
classifier can still be slow or partial; it needs a visible result type.

## Test

Classify the same domain value in several branches, compare once-before-match
with extractor-style repeated computation, and inspect evaluation counts and
missing-case diagnostics. Reconsider only with a complete extractor purity,
termination, caching, and coverage proposal. See [patterns](../features/patterns.md)
and [metaprogramming](../features/metaprogramming.md).
