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
