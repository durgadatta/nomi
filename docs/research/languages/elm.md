# Elm

> Status: comparative evidence; Nomi judgments are hypotheses.

## Observe

Elm's custom types model alternatives with distinct constructors and payloads.
The design makes states explicit rather than encoding them as unrelated flags.
[Primary reference: custom types](https://guide.elm-lang.org/types/custom_types).

## Judge And Pay

**Adopt** explicit state modelling and **adapt** it to Nomi's nominal closed
variants and exhaustive `match`. **Reject** replacing a meaningful state with
an unvalidated string because that looks friendlier in a notebook.

Closed states cost more during experimentation and constrain downstream
extension. Nomi should distinguish a stable package-owned variant from an
external service whose future tags are outside that package's control. A
decoder may reject an unknown tag or preserve a deliberately modelled unknown
state; the compiler cannot promise external exhaustiveness.

## Test

Extend TicketState with a paused state and require all non-exhaustive matches
to be diagnosed. Separately decode an unknown external tag with an exact path.
Compare the two messages so users can distinguish a source migration from bad
input. See [types/data](../features/types_data.md), [patterns](../features/patterns.md),
and [data](../../design/targets/data.nomi).
