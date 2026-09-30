# APL

> Status: comparative evidence; scope is Dyalog APL, not every dialect.

## Observe

Dyalog arrays have rank, shape, and depth. Its rank operator applies functions
to selected subarrays with explicit frame-compatibility rules.
[Primary references: arrays](https://docs.dyalog.com/21.0/programming-reference-guide/introduction/arrays/arrays/),
[rank operator](https://mastering.dyalog.com/Operators.html).

## Judge And Pay

**Adopt** shape and rank as semantic concepts. **Defer** an array-focused scoped
surface; **reject** a global glyph vocabulary in the everyday Nomi core.
Array algebra is the useful contribution, not a set of visually compact
spellings detached from that algebra.

Nomi's named calls cost density and can obscure an expert's mathematical
composition. ASCII alone is not proof of accessibility; the right experiment
must measure novices and experienced array users separately. A general-purpose
List is also not a rectangular array, so rank must not silently appear on every
collection.

## Test

Apply one reduction to cells of rank zero, one, and two. Show input shape,
frame, result shape, and mismatch diagnostics in a proposed inspection view.
Compare named operations before considering scoped notation. See
[numerics](../features/numerics.md) and [metaprogramming](../features/metaprogramming.md).
