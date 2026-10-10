# Mojo

> Status: comparative evidence added 2026-10-10; official documentation labelled
> Mojo 1.1.0 when consulted. Mechanisms are version-scoped, not Nomi guarantees.

## Scope And Sources

Mojo studies a Python-familiar surface with explicit value conventions,
compile-time parameters, native compilation, and Python interoperability.
Historical descriptions of `fn`/`def` should not be used as the current contract:
the consulted documentation describes function declarations with `def`.
This review did not run a Mojo compiler, GPU kernel, or interoperability benchmark.

## Arguments Carry Access And Ownership Facts

Mojo's argument conventions distinguish read access, mutable access, and owned
values. Ownership transfer and reference exclusivity constrain legal aliasing.
Its origin model tracks lifetime and mutability relationships of references,
including relationships carried by captured values.
[Primary references: ownership](https://mojolang.org/docs/manual/values/ownership/),
[lifetimes and origins](https://mojolang.org/docs/manual/values/lifetimes/).

**Nomi inference:** efficient arrays and foreign buffers may need more precise
access contracts than ordinary GC values. Compare copied immutable owned data,
explicit scoped buffer handles, and a borrowing profile. Do not make every
ordinary beginner function expose lifetime machinery before these pressures
justify it. A reference's lifetime does not establish permission to use the
foreign system or the outcome of fallible cleanup.

Test a buffer view escaping in a closure or an error value, and a mutable argument
aliased with another argument. A friendly call syntax must still expose what a
caller retains after transfer and which accesses become invalid.

## Protocol Shape And Compile-Time Parameters

Mojo traits express declared requirements; structs explicitly declare conformance.
Matching method names alone does not establish conformance.
[Primary reference: traits](https://mojolang.org/docs/manual/traits/).

Compile-time parameters can be types or values and are distinguished from
runtime arguments. They support specialization of generic functions and types.
[Primary reference: parameters](https://mojolang.org/docs/manual/parameters/).

**Nomi inference:** compare ordinary generics, explicit value parameters, and
shape/dtype metadata. State which information is required at checking time,
which remains dynamic, and what happens when a user only knows a shape at runtime.
A static array dimension is a useful constraint, but not evidence that a floating
reassociation is mathematically valid. Trait conformance proves interface shape
only to the extent checked; algebraic laws need separate evidence.

Parameterization also costs compiler work and generated code. Include latency,
cache identity, diagnostics, and code size alongside runtime execution. Reject
an API that quietly requires a runtime value to be available at an earlier phase.

## Compile-Time Execution Is A Restricted Phase

Mojo's compile-time evaluation supports a broad subset of computation while
restricting operations including file I/O, foreign function execution, and
raising errors; the documentation also discusses materialization limits.
[Primary reference: compile-time evaluation](https://mojolang.org/docs/manual/metaprogramming/comptime-evaluation/).

**Nomi inference:** compare ordinary constants, bounded static parameters, derived
metadata, and explicit compiler execution. The inputs and stage must be inspectable.
A build cannot secretly acquire runtime credentials, perform a device operation,
or replace a future failure with an unexplained compiler crash. Compilation
budgets and reproducibility belong in the contract before syntax convenience.

## Typed Raising And Callback Composition

The consulted function/error documentation distinguishes non-raising functions,
raising functions, and typed or parameterized error declarations. `raises Never`
expresses a non-raising contract; bare `raises` loses static error specificity.
[Primary references: functions](https://mojolang.org/docs/manual/functions/),
[errors](https://mojolang.org/docs/manual/errors/).

**Nomi inference:** compare typed exception effects with Result-returning functions
and explicit mapping. This is a real alternative to study, not a reason to rename
Nomi's already distinct Result/panic/cancellation channels. For callbacks,
propagate the actual expected failure contract without an implicit universal
error. Compare readability, generic signatures, cleanup, and debugging. Keep
uncaptured function pointers and captured closures separate when studying the
examples; one cannot establish the other's lifetime contract.

## Python Access Is A Host Boundary

Mojo's Python interoperability uses the CPython runtime and a Python shared
library; calling compiled Mojo from Python uses explicit bindings. Mojo's own
execution does not inherently require Python.
[Primary reference: Python interoperability](https://mojolang.org/docs/manual/python/).

**Nomi inference:** ecosystem access and backend independence are distinct goals.
A foreign Python object is not automatically immutable owned Nomi data. An adapter
must name conversion, aliasing, exceptions, capability use, resource validity,
and interpreter requirements. Keep host-dependent interop outside a portable
browser claim. Record transfer/copy costs separately from the native computation.

## Integration Choices And Costs

| Pressure | Nomi candidates | Cost or conflict |
| --- | --- | --- |
| Efficient native buffers | GC data; scoped handles; borrowing profile | Copies versus explicit access/escape restrictions |
| Shape-aware generic code | Type parameters; static values; dynamic checks | Compile-time demands versus runtime flexibility |
| Reusable native operations | Explicit dictionaries; declared protocols | Plumbing versus implementation coherence |
| Failure-polymorphic callbacks | Result/error parameters; typed raising challenger | Signature complexity and channel compatibility |
| Python ecosystem | Pinned host adapters; copied owned conversions | Installation, runtime coupling, transfer overhead |

## Prepared Discriminators

1. Pass overlapping views as mutable/read arguments, then transfer the buffer.
   Specify legal accesses, rejection location, and retained aliases.
2. Instantiate one operation with a static dimension and a runtime-only dimension.
   Require an explicit dynamic path or a phase-located rejection.
3. Attempt compile-time filesystem access and foreign execution. Specify the
   restriction and diagnostic without treating compiler execution as a sandbox proof.
4. Compose a callback that fails with two declared domain errors. Compare typed
   raising and Result mapping, including cause preservation and release failure.
5. Import a mutable Python object, make an owned candidate, and mutate the original.
   Require declared copy/isolation or visible sharing, with no implicit validation.
6. Run the same scalar contract on native and browser candidates. Refuse a CPython
   dependency where the backend does not provide it; do not fake portable success.

Continue through [functions](../features/functions.md), [resources](../features/resources.md),
[numerics](../features/numerics.md), [metaprogramming](../features/metaprogramming.md),
and the [maintainer synthesis guide](../synthesis_guide.md).
