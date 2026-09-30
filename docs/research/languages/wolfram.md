# Wolfram Language

> Status: comparative evidence; scope is expression evaluation.

## Observe

Wolfram Language evaluates symbolic expressions through transformation rules;
evaluation control and attributes determine when parts evaluate. Symbolic
structure is fundamental rather than an ordinary eager-value afterthought.
[Primary reference: evaluation of expressions](https://reference.wolfram.com/language/tutorial/EvaluationOfExpressions.html).

## Judge And Pay

**Adopt** symbolic expressions as inspectable values for appropriate domains.
**Defer** a scoped symbolic tool. **Reject** default symbolic rewriting or
implicit held evaluation in ordinary Nomi function calls.

Nomi loses direct symbolic convenience and should not pretend eagerly calling
`differentiate` on a number can recover source expressions. A symbolic library
needs explicit expression constructors or an admitted quoted surface, with
source mapping and controlled authority. Evaluation strategy is part of the
data contract, not an implementation optimization.

## Test

Represent a small polynomial as an explicit expression value, differentiate
it, and inspect the transformed tree. Compare a hypothetical scoped quote
only after variable binding, substitution, and effects are specified.
See [metaprogramming](../features/metaprogramming.md),
[numerics](../features/numerics.md), and [tooling](../../design/targets/tooling.nomi).
