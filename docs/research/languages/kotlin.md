# Kotlin

> Status: comparative evidence; scope is sealed hierarchies.

## Observe

Kotlin sealed declarations constrain direct inheritance and support exhaustive
`when` handling. Indirect subclasses can still extend non-sealed members, so
the hierarchy is not universally recursively closed.
[Primary reference: sealed classes](https://kotlinlang.org/docs/sealed-classes.html).

## Judge And Pay

**Adopt** compiler-visible alternatives. **Adapt** them to Nomi's deliberately
closed variant declarations rather than a constrained inheritance tree.
**Reject** nullable members as the default way to encode unrelated states.

Nomi loses extensible object hierarchies and some familiar application patterns.
A public closed variant also creates a versioning obligation: adding a case
may break downstream exhaustive matches. The synthesis must therefore connect
pattern exhaustiveness to package compatibility, not treat it as a purely
local convenience.

## Test

Publish a package containing three states and a downstream exhaustive match.
Add a fourth state and require a compatibility report identifying the affected
match. Compare modelling a truly open plugin family through an explicit
interface proposal rather than pretending it is closed. See
[types/data](../features/types_data.md), [modules/tooling](../features/modules_tooling.md),
and [modules](../../design/targets/modules.nomi).
