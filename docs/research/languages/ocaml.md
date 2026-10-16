# OCaml

> Status: comparative evidence; Nomi judgments are hypotheses.

## Observe

OCaml combines inference with records, variants, pattern matching, and modules.
These mechanisms allow substantial domain structure without repeating every
local type annotation.
[Primary reference: language tour](https://ocaml.org/docs/tour-of-ocaml).

## Judge And Pay

**Adopt** inferred local types and closed alternatives. **Adapt** product and
variant declarations into Nomi's one `data` family. **Reject** automatic curried
application as the default call model; named Nomi functions remain explicit
argument lists, and choice remains in `match` rather than equation clauses.

This trades elegant partial application for a more uniform call site. Modules
also show that a simple surface must eventually support substantial abstraction
boundaries. Nomi's generic and protocol design is not settled merely because
examples use `List[T]`; module signatures and abstraction leaks need their own
admission packet.

## Test

Model a ticket workflow, add a new state, and measure exactly which matches and
public interfaces must change. Compare reusable higher-order functions with
explicit lambdas. See [types/data](../features/types_data.md),
[functions](../features/functions.md), and [data](../../design/targets/data.nomi).

## Effect-Handler Comparison

The OCaml 5.3 manual describes handlers and captured one-shot continuations.
Repeated resumption is checked dynamically; eventual resumption/discontinuation
is a programmer responsibility, so suspended computation can retain resources.
[Primary reference: effect handlers](https://ocaml.org/manual/5.3/effects.html).

For Nomi, compare direct callbacks, explicit suspended
state, and a one-shot handler challenger. Hold a scoped reader during suspension,
then resume once, resume twice, abandon, and cancel with a release error. Require
an owner and complete cause/cleanup observations. The continuation mechanism
does not itself supply a world grant or the accepted exactly-once scope law.

The [effect owner](../features/effects.md#control-effects-and-continuation-ownership)
contains the unperformed comparison; the
[maintainer guide](../synthesis_guide.md) connects it to questions 4/5/7. No OCaml
execution, Nomi continuation implementation, or scheduler study is claimed.
