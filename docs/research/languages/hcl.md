# HCL

> Status: comparative evidence; scope is Terraform expressions, not all HCL hosts.

## Observe

Terraform's expression dialect provides references, collection expressions,
conditionals, and dynamic blocks within a host-defined configuration model.
The host gives these expressions their deployment meaning.
[Primary reference: expressions](https://developer.hashicorp.com/terraform/language/expressions).

## Judge And Pay

**Adopt** the distinction between data description and operational execution.
**Adapt** deployment descriptions to typed Nomi plan values. **Reject** letting
ordinary constructors execute deployment effects or assuming every host of HCL
shares Terraform's semantics.

Nomi's general-purpose functions may make authoring more flexible but also less
predictable than a restricted domain language. A plan needs unknown-value,
sensitivity, dependency, validation, and execution-phase contracts. Those are
not solved by adding a `resource` keyword to the grammar.

## Test

Build a plan containing an unresolved output and a secret. Require an inspectable
dependency graph, redacted output, and zero deployment effects during plan
construction. Execute only with explicit grants. See
[metaprogramming](../features/metaprogramming.md), [effects](../features/effects.md),
and [modules/tooling](../features/modules_tooling.md).
