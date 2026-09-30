# Ruby

> Status: comparative evidence; Nomi judgments are hypotheses.

## Observe

Ruby distinguishes lambdas from other Proc objects: arity handling and the
meaning of `return` differ. The common callable abstraction therefore carries
control-flow facts that a reader must recover from how it was created.
[Primary reference: Proc](https://ruby-doc.org/core/Proc.html).

## Judge And Pay

**Adopt** passing behavior as an ordinary value. **Adapt** ergonomic callbacks
to Nomi's single `(args) => expression` form. **Reject** multiple callback forms
with different nonlocal return rules, implicit receiver DSLs, and magical
argument names as core design directions. A Nomi callback should not make its
caller accidentally responsible for a distant return.

The cost is real: Ruby blocks can make resource and domain APIs exceptionally
fluid. Nomi's explicit parameters and ordinary calls may be longer, especially
for nested builders. Do not compensate with another lambda shorthand before a
whole builder program demonstrates the need.

## Test

Compare a three-level report builder against explicit functions in
[functions](../../design/targets/functions.nomi). Trace what returns from each
function and what can fail. If the proposed library needs statement callbacks,
record that missing contract rather than inventing a block syntax here.
See [functions](../features/functions.md) and
[metaprogramming](../features/metaprogramming.md).
