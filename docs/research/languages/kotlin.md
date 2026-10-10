# Kotlin

> Status: comparative evidence, deepened 2026-10-10; living Kotlin and
> kotlinx.coroutines references, with experimental contract APIs scoped explicitly.

## Scope And Sources

Kotlin is useful here as an application language that connects concise ordinary
code to JVM/host ecosystems, type refinement, higher-order functions, and
structured concurrent libraries. This review separates language rules from
library conventions. No Kotlin program or comparative usability study was run.

## States, Nullability, And Refinement

Sealed declarations restrict direct inheritance and support exhaustive `when`
handling; non-sealed descendants can introduce further subtypes. Smart casts
refine a value after checks when the compiler can rely on its stability. Mutable
properties and some captured or externally visible bindings cannot be refined
under the same conditions as stable local values.
[Primary references: sealed classes](https://kotlinlang.org/docs/sealed-classes.html),
[type checks and casts](https://kotlinlang.org/docs/typecasts.html).

**Nomi inference:** closed nominal variants and Option give states a deliberate
vocabulary. Flow analysis can improve diagnostics without changing what data
exists. Refinement needs a mutation/alias rule: observing a field once cannot
justify a later read after a callback changes it. Snapshot the relevant value,
prove stability, or require another check. Publicly adding a variant case is a
package compatibility event for downstream exhaustive matches.

## Friendly Calls Still Need Exact Resolution And Control Rules

Extension functions are resolved statically from the declared receiver type;
they do not add virtual members to that type.
[Primary reference: extensions](https://kotlinlang.org/docs/extensions.html).

The Nomi question is whether receiver-style convenience reduces reading effort
while leaving the function's origin and implementation visible. Compare an
ordinary function call, pipeline insertion, and a scoped extension proposal.
Two imported helpers with the same friendly name need deterministic lookup and
an actionable diagnostic. Do not infer open multimethod dispatch from receiver
syntax.

Inline function parameters can permit non-local returns, while `crossinline`
constrains that behavior; reified type parameters are tied to inlining.
[Primary reference: inline functions](https://kotlinlang.org/docs/inline-functions.html).

Nomi's accepted `return` targets the nearest function. Preserve that law in
higher-order APIs and optimization. A library's retry, iteration, or resource
callback should not acquire hidden control transfer just because an optimizer
inlines it. Compare explicit outcome values against any proposed non-local
control mechanism, including failure and cleanup paths.

## Compiler Knowledge Versus Verified Behavior

Kotlin's contract API describes facts such as invocation frequency and
relationships between return outcomes and arguments. The API contains
experimental declarations, including the CallsInPlace vocabulary.
[Primary reference: contracts](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.contracts/).

**Nomi inference:** once-only callback facts are useful for initialization,
borrowing, effects, and resources, but a declaration alone is insufficient
proof of implementation. Research separately: compiler-checked contract bodies,
trusted library declarations, and contracts expressed through restricted
constructs. An API claiming to call once must be tested when it calls zero,
twice, after return, or on an error path. Optimization should consume verified
facts and preserve the same runtime meaning.

## Suspension, Ownership, And Stream Consumption

Kotlin coroutines support structured parent/child work through scopes and jobs.
Cancellation is cooperative; non-suspending computation may need an explicit
cancellation check.
[Primary references: coroutine basics](https://kotlinlang.org/docs/coroutines-basics.html),
[ensureActive](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/ensure-active.html).

The Flow interface can represent cold or hot streams; its reference describes
sequential execution by default and operators that introduce concurrency.
[Primary reference: Flow](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-flow/).

**Nomi inference:** distinguish creating a description, starting work, observing
completion, and consuming a stream. A stream API needs explicit answers for
repeat collection, buffering, producer lifetime, cancellation, and capability
capture. A task count bound does not establish a queue capacity bound. A parent
scope must define what happens to sibling work when one child fails, and what
cleanup remains observable after cancellation.

## Integration Choices And Costs

| Pressure | Candidates | Cost or conflict |
| --- | --- | --- |
| Readable state handling | Closed variants and Option; stable-value refinement | Exhaustiveness obligations and alias analysis |
| Fluent APIs | Ordinary calls/pipelines; scoped extensions | Explicit origin versus concise receiver vocabulary |
| Higher-order performance | Semantics-preserving inlining | Code size and debugging; no hidden return target |
| Reliable callbacks | Checked invocation contracts; fenced trusted contracts | Verification burden and API expressiveness |
| Concurrent streams | Explicit Stream plus scoped jobs | More visible lifecycle terms; fewer accidental starts |

## Prepared Discriminators

1. Publish three closed states, then add a fourth. Identify the downstream match
   and the package compatibility consequence.
2. Check a mutable field's type, invoke a callback that changes it, then use it.
   Require another check, a stable snapshot, or a proof that mutation is impossible.
3. Resolve two imported receiver helpers and an ordinary call to the same operation.
   Compare origin inspection and ambiguity repair.
4. Inline a callback containing a return. Its target must remain the nearest
   function under the accepted Nomi contract.
5. Supply implementations claiming once-only invocation that actually call zero,
   twice, and after return. Identify rejection or the explicit trust boundary.
6. Consume the same stream twice, then cancel a long-running producer with a
   bounded buffer. Record start count, retained values, termination, and cleanup.

Continue through [types/data](../features/types_data.md), [functions](../features/functions.md),
[concurrency](../features/concurrency.md), [collections](../features/collections.md),
and the [maintainer synthesis guide](../synthesis_guide.md).
