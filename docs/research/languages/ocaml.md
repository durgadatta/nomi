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
