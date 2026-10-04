# Collections And Plans

> Status: comparative evidence; pipeline accepted, domain APIs proposed.

User pressure: read data flow while knowing when work runs and how much it holds.

The [data/workflow dossier](../data_workflows/README.md) deepens the table,
masking, formula, fit/transform, dependency and durable-execution comparisons.
Its [DW experiments](../data_workflows/nomi_candidates.md) reuse open questions
8/9/17 rather than treating every framework as another language feature.

| Evidence | Mechanism | Nomi consequence |
| --- | --- | --- |
| [Bash](../languages/bash.md) | Process pipes | Separate bytes/processes from value insertion. |
| [PowerShell](../languages/powershell.md) | Object pipeline enumeration | No implicit per-element expansion from `|>`. |
| [Haskell](../languages/haskell.md) | Non-strict sequences | Nomi List remains eager; Stream is explicit. |
| [C#](../languages/csharp.md), [SQL](../languages/sql.md) | Enumeration versus provider/relational plans | TablePlan has its own inspection and execution contract. |
| [BQN](../languages/bqn.md), [Julia](../languages/julia.md) | Array agreement and broadcast | Do not equate List map with array shape laws. |

```nomi
selected = filter(items, (item) => item.age >= 13)
names = map(selected, (item) => item.name)
```

Accepted convenience:

```nomi
names = items
    |> filter((item) => item.age >= 13)
    |> map((item) => item.name)
```

Both mean the same ordinary eager List calls here. No automatic error
propagation, parallelism, laziness, query translation, or generated parameters.
Shared verb names can help users, but result laws must be specified per domain.
Callback effects and generic dispatch remain admission gates.

The [generic-operation hierarchy](../generic_operations.md) adds seed/history,
state-versus-output, carrier shape, merge laws and demand-aware observation.
A plain sequential fold requires no associative merge law; neither pure map nor
pipeline spelling licenses callback fusion or implicit parallel reduction.

**Experiment:** compare List, explicit Stream, and TablePlan over the same input.
Record call order, partial-consumer behavior, memory bound, result order, and
error paths. Require unsupported query callbacks to fail at construction, not
silently fall back to local execution. Compare joins/windows with ordinary
plan calls before admitting query syntax.

**User-facing gate:** inspect output must label eager values versus deferred
plans; a playground run cannot imply that constructing a plan executes it.
[Target](../../design/targets/collections.nomi).
