# Julia

> Status: comparative evidence; scope is explicit broadcasting and fusion.

## Observe

Julia's dotted calls express broadcasting, and nested dotted operations can
fuse. The broadcast interface also permits library customization of arguments
and result representations.
[Primary references: functions](https://docs.julialang.org/en/v1/manual/functions/),
[broadcast interfaces](https://docs.julialang.org/en/v1/manual/interfaces/).

## Judge And Pay

**Adopt** explicit array execution and inspectable optimization. **Adapt** the
idea to a Nomi array library with stated shapes, evaluation order, and callback
effects. **Defer** dotted-call syntax and open dispatch mechanisms until a
protocol coherence proposal exists.

Nomi may lose performance and elegant interoperability if it refuses extensible
array execution entirely. Conversely, fusion is not harmless when callbacks
can observe time, mutate state, or fail. A rewrite must preserve admitted
semantics, not just produce the same final numbers in a pure benchmark.

## Test

Compare two explicit passes with a fused pure plan and an effectful callback.
Require identical pure values and a deliberate rejection or documented trace
for effects. Inspect the chosen plan and output shape. See
[numerics](../features/numerics.md), [effects](../features/effects.md), and
[collections](../features/collections.md).
