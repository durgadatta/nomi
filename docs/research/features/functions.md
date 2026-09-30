# Functions And Calls

> Status: comparative evidence; core accepted, generic callback contracts open.

Packet: `docs/design/function_contracts.md`,
`docs/design/function_contracts_target.nomi`,
`docs/review/2026-09-30-function-contracts.md`.

User pressure: know which arguments a transformation receives and where it
returns without reconstructing shorthand rules.

| Evidence | Mechanism | Nomi judgment |
| --- | --- | --- |
| [Ruby](../languages/ruby.md) | Callable variants differ in return and arity | One anonymous expression form. |
| [Haskell](../languages/haskell.md), [OCaml](../languages/ocaml.md) | Curried composition | Explicit lambdas instead of implicit partial application. |
| [Scheme](../languages/scheme.md) | Lexical first-class functions | Preserve lexical environments with explicit calls. |
| [Julia](../languages/julia.md) | Library-defined execution of callbacks | Admit callback contracts before optimizing their calls. |
| [Koka evidence](../design_frontiers.md#2-higher-order-effects-need-a-real-type-model) | Row-polymorphic callback effects | Compare effect propagation with pure-only strict transforms. |

```nomi
func add_tax(amount: Int, tax: Int) -> Int:
    return amount + tax

with_tax = (amount) => add_tax(amount, 2)
```

The long form gives behavior a name. The lambda only maps explicit inputs to
one expression; multi-step logic moves to a function. The pipeline inserts its
left value into an ordinary first argument and does not manufacture parameters.

Costs include extra lambdas and helpers, especially in builders. The accepted
surface does not yet settle generic declarations, function-value effect types,
statement callbacks, constructor values, or protocol resolution. Target demos
must not conceal these by passing a variant constructor directly to `map_error`.
Use `(error) => ErrorKind(error)` until that contract is admitted.

**Experiment:** format a beginner callback, a report builder, and an effectful
callback at 80/100 columns. Require input types, resolved effects, and return
targets to be inspectable. Compare a pure-only collection API with an explicitly
effect-propagating proposal. Keep signatures open rather than force fake purity.
The [focused proposal](../../design/function_contracts.md) now owns abstract
signatures, purity/capture distinctions, order, retention and admission gates.
Its initial pure-only recommendation remains unaccepted.
The manual derivation of invoice, submission and row-result calls is conditional
on proposed APIs. The resource and cold-task derivations deliberately stop at
region/error payload and authorization-timing gaps; no typechecker ran.

**User-facing gate:** hover and diagnostics must agree with actual calls and
show callback effects before supported playground promotion.
[Target](../../design/targets/functions.nomi).
