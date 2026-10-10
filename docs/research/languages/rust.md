# Rust

> Status: comparative evidence, deepened 2026-10-10; living stable reference
> mechanisms, with Nomi ownership/borrowing choices still research questions.

## Scope And Sources

Study Rust as an integrated contract among values, borrowing, traits, failure,
and compiler-enforced restrictions. Similar punctuation cannot transfer those
guarantees to a GC-hosted interpreter. This pass consulted primary documentation;
it did not run Rust cases, prove a Nomi borrow checker, or measure performance.

## Ownership Is More Than Cleanup Syntax

Rust references permit access without transferring ownership. Shared references
and exclusive mutable references are constrained to prevent conflicting access;
references must remain valid. The restrictions affect which APIs and program
shapes can be expressed directly.
[Primary reference: references and borrowing](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html).

**Nomi inference:** compare GC values with scoped resource regions against a
borrowed-buffer profile before designing ownership syntax. Memory lifetime,
resource validity, aliasing, and thread transfer are separate obligations.
A GC root can keep an object alive after its file or device buffer is invalid.
Borrow checking can protect access while still requiring explicit operational
rules for fallible close, cancellation, and external authority.

Destruction follows Rust's drop scopes and field/local ordering, but safe code
can suppress destruction, and abort/exit paths can bypass it. Rust does not
promise that every value's destructor runs in every possible execution.
[Primary reference: destructors](https://doc.rust-lang.org/reference/destructors.html).

Nomi's resource proposal therefore needs its own exactly-once scope contract and
its stated interruption limits. Do not turn a memory-safety argument into an
unconditional external-cleanup guarantee. If release fails during another
failure, specify which cause is primary and how the second remains inspectable.

## Traits, Coherence, And Separate Packages

Rust checks trait implementation coherence: overlapping implementations are
restricted, and orphan rules constrain where implementations can be declared.
The detailed rule accounts for local types and uncovered type parameters.
[Primary reference: implementations](https://doc.rust-lang.org/reference/items/implementations.html).

**Nomi inference:** a protocol system needs a package ownership rule before it
needs convenient method syntax. Compare globally coherent implementations,
explicit operation dictionaries, and scoped implementation selection. Test a
foreign protocol on a foreign type supplied by two adapters. Global coherence
limits independently authored retrofits; explicit dictionaries cost call-site
plumbing. Both costs belong in the language decision.

A trait signature also does not prove ordering, associativity, or serialization
round-trip laws. Keep verified interface shape separate from declared laws,
property tests, and stronger proof-carrying proposals.

## Expected Failure And Propagation

Result carries success or failure as values, and `?` supports propagation.
Combinators preserve error values for mapping and context.
[Primary reference: Result](https://doc.rust-lang.org/std/result/).

The accepted Nomi target has distinct Result, Option, panic, and cancellation.
Compare explicit domain-error mapping against convenience conversion without
inventing an invisible catch-all. A Result type is a contract for expected
failure; it does not enumerate every abnormal termination. Typed propagation
must preserve the original cause and resource ownership across function exits.

## Address Stability And Compile-Time Execution

Pinning constrains movement of a pointee through the permitted interface when
address-sensitive invariants require it; it does not make every pointer value
immovable or replace all ownership reasoning. The `Unpin` distinction matters.
[Primary reference: pinning](https://doc.rust-lang.org/std/pin/).

Treat this as evidence that async state machines can impose representation
constraints. Nomi should expose a user-level suspend/escape contract before
choosing a representation or copying Pin syntax. Ask whether a borrowed handle
can survive suspension and who owns it if the task is cancelled.

Rust permits constant evaluation in specified contexts with restrictions on
available operations. This is a distinct phase from ordinary runtime calls.
[Primary reference: constant evaluation](https://doc.rust-lang.org/reference/const_eval.html).

For Nomi, compare declared compile-time parameters, ordinary constant folding,
and generated metadata. Compiler execution needs bounded work, reproducible
inputs, and phase-specific diagnostics. Optimization must not create authority
or change the observable failure timing of an ordinary call.

## Integration Choices And Costs

| Pressure | Nomi candidates | Cost or conflict |
| --- | --- | --- |
| Valid access to buffers/handles | Scoped GC regions; explicit borrowing profile | Restricted escapes versus broad shared-value convenience |
| Package-safe abstraction | Coherent protocols; explicit dictionaries | Retrofit limits versus visible plumbing |
| Recoverable failure | Typed Result mapping | Boilerplate and cross-library error composition |
| Safe suspension | Region/capture rules; restricted borrowed suspension | Expressiveness versus representation complexity |
| Compile-time specialization | Constants; typed parameters; restricted evaluation | Compile time, code size, reproducibility |

## Prepared Discriminators

1. Alias a mutable buffer, retain a slice, and attempt resizing. State which
   candidate rejects the operation and which lifetime is tracked.
2. Return a reader in a closure, container, error payload, and child task.
   Require the same resource escape law through every carrier.
3. Compose two packages implementing one foreign protocol for one foreign type.
   Require deterministic refusal or explicitly selected behavior.
4. Propagate an expected parse error while release also fails. Preserve both
   causes and exactly the admitted cleanup attempts.
5. Suspend with a borrowed handle, then cancel before resumption. Record validity,
   child ownership, and release under the candidate's stated interruption model.
6. Compare a constant computation and runtime computation with an invalid
   operand. Specify diagnostic stage; do not silently shift ordinary semantics.

Continue through [resources](../features/resources.md), [functions](../features/functions.md),
[failure](../features/failure.md), [metaprogramming](../features/metaprogramming.md),
and the [maintainer synthesis guide](../synthesis_guide.md).
