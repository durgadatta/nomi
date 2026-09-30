# Functions And Calls

> Status: comparative evidence; core accepted, generic callback contracts open.

User pressure: know which arguments a transformation receives and where it
returns without reconstructing shorthand rules.

| Evidence | Mechanism | Nomi judgment |
| --- | --- | --- |
| [Ruby](../languages/ruby.md) | Callable variants differ in return and arity | One anonymous expression form. |
| [Haskell](../languages/haskell.md), [OCaml](../languages/ocaml.md) | Curried composition | Explicit lambdas instead of implicit partial application. |
| [Scheme](../languages/scheme.md) | Lexical first-class functions | Preserve lexical environments with explicit calls. |
| [Julia](../languages/julia.md) | Library-defined execution of callbacks | Admit callback contracts before optimizing their calls. |

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

**User-facing gate:** hover and diagnostics must agree with actual calls and
show callback effects before supported playground promotion.
[Target](../../design/targets/functions.nomi).
