# Julia

> Status: comparative evidence, deepened 2026-10-10; living Julia 1.x manuals.
> Version-specific world-age binding changes are not assumed for older releases.

## Scope And Sources

Julia supplies evidence for numerical work, open generic functions, interactive
redefinition, and compilation driven by concrete program behavior. This is a
semantic comparison, not a claim that a Nomi prototype matches Julia's compiler
or ecosystem. No Julia benchmarks or comparative programs were executed.

## Multiple Dispatch And Open Extension

Julia selects methods from the types of multiple arguments. Two applicable
methods can be incomparable; the manual demonstrates an ambiguity error and an
explicit intersection method that resolves it.
[Primary reference: methods](https://docs.julialang.org/en/v1/manual/methods/).

**Nomi inference:** cross-product behavior is a real pressure for units, arrays,
encodings, and domain models. Compare ordinary explicit dispatch, operation
values, closed protocol families, and an open multimethod challenger. A decision
must cover ownership of extensions, dependency composition, overlap, and method
inspection. “Most specific” is insufficient when the order is partial.

A simple discriminator uses methods for `(Float, Any)` and `(Any, Float)` and
calls with `(Float, Float)`. A second adds these methods from separate packages.
Record whether ambiguity appears when linking, checking, or executing, and
whether importing a dependency can change existing calls. Closed nominal data
and open operations are independent decisions; neither logically implies the
other.

## Specialization And Representation

Julia's performance guidance uses function boundaries to isolate dynamic setup
from computation that can specialize on concrete argument types. Its advice
also discusses representation and allocation concerns.
[Primary reference: performance tips](https://docs.julialang.org/en/v1/manual/performance-tips/).

**Nomi inference:** local inference and explicit public contracts can coexist
with specialization. Compare erased generics, monomorphized generics, and a
bounded specialization profile using the same observable contract. Include
compilation latency, code size, debug inspection, and browser constraints in the
cost. A type annotation alone does not justify a performance claim or repair an
unclear data representation.

## Broadcast Plans And Observable Semantics

Dotted calls express broadcasting; nested dotted operations can fuse. Julia's
broadcast interface permits custom argument handling and result representations.
[Primary references: functions](https://docs.julialang.org/en/v1/manual/functions/),
[broadcast interfaces](https://docs.julialang.org/en/v1/manual/interfaces/).

The Nomi candidate is an explicit array execution contract with shape, element
type, ownership, and callback laws. Compare materialized passes with a fused
plan. Equal final numbers are insufficient if callbacks mutate, fail, consume
randomness, or inspect time. Specify evaluation counts and traversal order,
then restrict optimization to transformations justified by those laws.

Shape compatibility is also part of meaning. Compare scalar expansion, singleton
axis expansion, named axes, and explicit reshape. A fused expression still needs
an understandable diagnostic locating the incompatible operands.

## Interactive Redefinition Has A Visibility Model

Julia's world-age mechanism controls visibility of newer definitions to running
code. Tasks carry a world age, and `invokelatest` permits a call in the latest
world. The current manual separately identifies changes involving bindings in
Julia 1.12; those details are version-scoped.
[Primary reference: world age](https://docs.julialang.org/en/v1/manual/worldage/).

**Nomi inference:** editing a function while a notebook, stream, or task runs is
an evolution problem. Compare a frozen run revision, explicit adoption of a new
revision at a boundary, and live method lookup. Define which implementation an
old closure uses, how caches invalidate, and whether a restarted computation
retains its input/authority context. “Rerun” should not silently mix definitions
from different revisions. This links interactive use to package identity and
reproducible inspection.

## Integration Choices And Costs

| Pressure | Candidates | Cost or conflict |
| --- | --- | --- |
| Cross-type behavior | Explicit calls/dictionaries; protocols; multimethods | Verbosity versus overlap and dependency reasoning |
| Fast generic numerics | Erasure; monomorphization; bounded specialization | Runtime work versus latency and code size |
| Array composition | Materialized calls; inspectable fused plans | Allocation versus observable callback order |
| Interactive evolution | Frozen revision; explicit refresh; live lookup | Predictability versus immediate feedback |

## Prepared Discriminators

1. Exercise the intersecting two-argument method case above, including independently
   authored packages and a third method resolving their intersection.
2. Run a scalar kernel over several element types. Hold results/error behavior
   constant while measuring compilation, representation, and execution separately.
3. Evaluate two array passes and a fused candidate using a callback that records
   its arguments and fails at a chosen element. Compare complete traces.
4. Combine arrays with incompatible axes and require an operand-located shape
   diagnostic before publishing a result.
5. Start a task, redefine an operation, then invoke it through an old closure and
   a new call. Require each candidate to identify the definition revision used.
6. Repeat an inspected plan after changing one dependency. Explain invalidation
   and retained context instead of presenting a stale result as current.

Continue through [functions](../features/functions.md), [numerics](../features/numerics.md),
[collections](../features/collections.md), [modules/tooling](../features/modules_tooling.md),
and the [maintainer synthesis guide](../synthesis_guide.md).
