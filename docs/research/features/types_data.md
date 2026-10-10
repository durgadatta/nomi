# Types And Owned Data

> Status: comparative evidence; nominal data accepted, representation gates open.

User pressure: model valid concepts without annotating every temporary value.

| Evidence | Mechanism | Nomi consequence |
| --- | --- | --- |
| [OCaml](../languages/ocaml.md), [Gleam](../languages/gleam.md), [Elm](../languages/elm.md) | Inference and explicit alternatives | Inferred locals, nominal products and closed variants. |
| [TypeScript](../languages/typescript.md) | Structural union narrowing | Convenient outside; explicitly decoded ownership inside. |
| [Java](../languages/java.md) | Data carriers and generated members | Specify deep immutability and every derived projection. |
| [Kotlin](../languages/kotlin.md) | Constrained inheritance and exhaustive handling | Closed variants are not extensible class hierarchies. |

```nomi
data TicketId:
    value: Int where value > 0

data State:
    Queued
    Assigned(owner: Text)
```

Nomi combines explicit public contracts with locally inferred types. A
constructor expresses an internal fact and may signal a contract violation;
external input uses decode and returns expected errors. Nominal identity costs
adapters between similarly shaped types. Closure of variants costs compatibility
when adding a case. Immutable products cost copying or persistent representation
unless an accepted update mechanism preserves semantics.

**Experiment:** model the same ticket workflow as nominal products/variants and
as boundary Value. Add one variant and attempt a nested-collection alias update.
Require explicit ownership conversion, exact affected matches, and a specified
alias result. Export a schema containing a non-projectable predicate and report
the limit honestly.

**User-facing gate:** type hover, exhaustive diagnostics, decoder paths, and API
compatibility reports must tell one story across hosts. No implicit Any may
appear merely to make a sample run. [Target](../../design/targets/data.nomi).

## Identity, Representation, And Read-Only Access

> Research continuation 2026-10-10: questions 2/11/13; representation and
> borrowing alternatives below remain unselected.

The expanded [Scala](../languages/scala.md) opaque-type comparison,
[Haskell](../languages/haskell.md) role discussion,
[TypeScript](../languages/typescript.md) structural/read-only discussion, and
[Mojo](../languages/mojo.md) access conventions sharpen the target's terminology.
Their sourced mechanisms differ; Nomi must choose its own composed laws.

| Fact | Does not by itself establish |
| --- | --- |
| Binding cannot be reassigned | Nested values cannot change through another alias |
| One view forbids writes | The underlying object is deeply immutable |
| Storage representations coincide | Nominal concepts and their constraints are interchangeable |
| A type argument can be safely represented another way | Arbitrary semantic conversion or external validation |
| A reference remains memory-valid | Resource permission, non-escape, or cleanup completion |
| A static assertion refines a tool's view | Received runtime data satisfied an owned-data decoder |

Compare a wrapped owned product, an opaque concept with explicit constructors,
and a shared foreign handle for a validated identifier and a numerical buffer.
State equality/hash behavior, nested alias isolation, variance of public type
parameters, schema projection, and conversion rules. Avoid treating a cheap
representation as evidence for an unchecked semantic cast.

**Prepared alias discriminator:** obtain a foreign record with a nested mutable
list, validate its fields, construct the owned candidate, and mutate the original
list through a second alias. A deeply immutable owned candidate must retain its
value; an explicitly shared candidate must expose that sharing in its contract.
A shallow read-only view cannot satisfy the immutable oracle merely because the
local caller lacks a write operation.

**Prepared nominal discriminator:** independently define two positive-integer
identifier concepts, then cross their package boundary. Representation agreement
must not erase declaration identity. Compare an explicit checked adapter with
an identity-preserving re-export. The existing
[package-instance experiment](modules_tooling.md#nominal-identity-across-package-instances)
owns the detailed identity choices.

These are unexecuted cases. Generalization/variance remains linked to
[function contracts](functions.md#polymorphic-sharing-and-generalization);
foreign ownership and escape remain linked to [resources](resources.md).
The [maintainer guide](../synthesis_guide.md) connects the questions before a
representation optimization or new type notation is accepted.
