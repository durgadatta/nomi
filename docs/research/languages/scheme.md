# Scheme

> Status: comparative evidence; scope is lexical binding in TSPL.

## Observe

Scheme's lambda and local binding forms make lexical environment construction
explicit. Different binding forms encode different initialization visibility.
[Primary reference: binding](https://www.scheme.com/tspl4/binding.html).

## Judge And Pay

**Adopt** lexical scope and first-class functions. **Adapt** them to Nomi's
indentation and explicit parenthesized calls. **Reject** multiplying local
binding forms merely because their reductions are elegant. Nomi still must
specify initializer visibility, shadowing, and closure capture; one spelling
does not remove those semantic obligations. Nomi already specifies immutable
value captures and mutable cell captures; the concurrency implications remain
a separate gate.

Scheme's uniform expression model enables concise composition and small
interpreters. Nomi's separate statement suites and expression lambdas lose
some of that uniformity. The gain must be easier recognition of state changes
and control transfer, not an argument that prefix notation is inherently bad.

## Test

Write nested shadowing, a self-referential initializer, and a closure capturing
a mutable binding. Document exact accepted/rejected cases and evaluation order
in [binding](../../design/targets/binding.nomi). If initialization needs a new
form, first show why an explicit named function cannot solve the user problem.
See [bindings](../features/binding.md) and [functions](../features/functions.md).
