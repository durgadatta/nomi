# TypeScript

> Status: comparative evidence, deepened 2026-10-10; living handbook plus
> historical TypeScript 4.9 evidence for the introduction of `satisfies`.

## Scope And Sources

TypeScript is studied as a typed layer over a dynamic host and a large ecosystem,
not as a Python runtime replacement. Its compromises are useful evidence for
Nomi's browser, foreign-value, tooling, and public-contract boundaries. This
pass did not execute a TypeScript compiler or test Nomi interoperability.

## Structural Convenience And Its Boundary

Type compatibility is substantially structural, with deliberately unsound
allowances documented for JavaScript practice.
[Primary reference: type compatibility](https://www.typescriptlang.org/docs/handbook/type-compatibility).

**Nomi inference:** convenient interoperability has a cost as well as a benefit.
Compare structural internal products, nominal owned concepts, and explicit
adapters between structurally similar nominal products. Nominality must earn
its extra work through boundary diagnostics, package identity, and invariants.
Structural shape alone cannot express whether a value has been validated,
which package owns its meaning, or which authority it carries.

## Flow Refinement Is Useful Evidence, Not Data Validation

TypeScript narrows unions using control flow, discriminants, and predicates.
[Primary reference: narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html).

Nomi can use refinement to explain alternatives eliminated by a branch while
preserving closed variant identity. Ordinary domain tests need not become
pattern extractors. A reusable predicate still needs an account of aliasing and
mutation: a check on one read may not establish a fact about a later read.
A user-authored assertion of a predicate's meaning needs verification or an
explicit trust boundary.

Type annotations and assertions are removed by the compiler; an assertion does
not add runtime validation or an exception when it is wrong.
[Primary reference: everyday types](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html).

The accepted Nomi boundary remains explicit structural Value to typed decode
result to owned value. Foreign annotations may inform tooling but cannot replace
checks on actual received data. Preserve a bad field's path, expected type, and
original value, and accumulate independent decoding errors where specified.

## Type-Level Computation And Tooling

Mapped types transform properties of other types. `satisfies`, introduced in
TypeScript 4.9, checks compatibility while retaining useful information about
the expression's inferred type.
[Primary references: mapped types](https://www.typescriptlang.org/docs/handbook/2/mapped-types.html),
[4.9 release notes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html).

**Nomi inference:** distinguish a type projection, generated implementation, and
runtime schema. A projected record type does not by itself generate a correct
codec. Compare declared field metadata and inspectable derivation against a
general type-level programming facility. Include inference readability, solver
budgets, diagnostics, and separate-compilation contracts. A user should be able
to discover a public function's actual accepted input without evaluating an
unbounded type computation mentally.

A compatibility check that retains local precision is useful, but inferred
local detail must not become an accidental evolving public ABI. Public
contracts need deliberate export and compatibility rules.

## Read-Only Views And Runtime Sharing

A `readonly` property restricts writes through that view during checking. It
neither changes runtime behavior nor necessarily makes nested values immutable;
another alias can still expose changes.
[Primary reference: object types](https://www.typescriptlang.org/docs/handbook/2/objects.html).

**Nomi inference:** binding immutability, read-only access, deep owned-data
immutability, and unique ownership require distinct laws. Avoid using one word
or qualifier to imply all of them. Conversion of a foreign mutable object into
owned data must specify copying, alias isolation, or the remaining shared handle.
These distinctions become critical when values cross tasks or caches.

## Integration Choices And Costs

| Pressure | Candidates | Cost or conflict |
| --- | --- | --- |
| Ecosystem interoperability | Structural foreign values plus explicit decoders | Adapter work versus unchecked trust |
| Lightweight composition | Nominal products; scoped structural products | Identity/invariants versus friction |
| Rich editor inference | Local refinement with deliberate exports | Helpful precision versus unstable public contracts |
| Reusable schemas | Field metadata/derivation; type-level programs | Bounded inspection versus expressive abstraction |
| Safe sharing | Immutable owned values; explicit mutable handles | Copying versus observable aliases |

## Prepared Discriminators

1. Decode a string where an integer is required, an extra property, and an unknown
   variant tag. Require stable paths and no partially published owned value.
2. Adapt two packages' identically shaped nominal identifiers. Compare boilerplate
   and ensure accidental substitution remains detectable.
3. Validate a foreign object, mutate it through a second alias, then read the
   owned candidate. Require isolation or an explicitly shared contract.
4. Declare a derived codec/type projection and compare its actual behavior with
   malformed runtime input. Type compatibility must not count as decoding.
5. Change a local inferred detail while keeping an exported signature fixed.
   Distinguish internal refinement from a breaking package change.
6. Feed a deeply nested type computation into an editor. Measure bounded
   diagnostics and explain the exported type without compiler-internal jargon.

Continue through [types/data](../features/types_data.md), [decoding](../features/decoding.md),
[modules/tooling](../features/modules_tooling.md), [metaprogramming](../features/metaprogramming.md),
and the [maintainer synthesis guide](../synthesis_guide.md).
