# Racket

> Status: comparative evidence; Nomi judgments are hypotheses.

## Observe

Racket offers hygienic macros and tools for inspecting macro expansion. It
treats language extension as a substantive programming capability, not only
text substitution.
[Primary reference: macros](https://docs.racket-lang.org/guide/macros.html).

## Judge And Pay

**Adopt** inspectable expansion and preservation of source context as admission
requirements. **Defer** user syntax extension in Nomi's core. Begin with ordinary
values and calls; admit a scoped language only when a concrete domain program
cannot express its structure adequately that way.

The cost is less power for language-oriented libraries. Racket users can move
abstraction across the grammar boundary; Nomi initially makes that boundary
harder to cross. That is defensible only if a scoped extension eventually has
a workable package, formatter, diagnostic, and authority contract. Simply
prohibiting macros would duck the design problem rather than solve it.

## Test

Build one query as ordinary plan constructors and as a hypothetical scoped
form. Compare source-to-plan inspection, editor navigation, and error ranges.
Keep the call form if the notation saves only characters. See
[metaprogramming](../features/metaprogramming.md) and
[tooling](../../design/targets/tooling.nomi).
