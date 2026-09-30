# Effects And Authority

> Status: comparative evidence; uses/grants accepted, callback model open.

User pressure: know what a function can touch and what the host actually permits.

| Evidence | Mechanism | Nomi consequence |
| --- | --- | --- |
| [Roc](../languages/roc.md) | App/platform boundary | Host capability contracts are first-class. |
| [Dhall](../languages/dhall.md) | Evaluation safety distinct from import policy | Purity is not a time/memory budget or a network grant. |
| [Clojure](../languages/clojure.md) | Retried transactions | Do not hide replayable effects in resource scope. |
| [HCL](../languages/hcl.md), [Nix](../languages/nix.md) | Description versus execution environment | Plan construction must not execute operations. |

```nomi
pub func load(path: Path) -> Result[Text, IoError] uses FileRead:
    return files.read_text(path)
```

`uses FileRead` declares a requirement, not a grant to read every path. Concrete
handles and host policy narrow authority. A pure predicate must not observe
the clock; a secret needs redacted display independent of the surrounding effect
set. Private effect inference must remain inspectable.

Costs: public signatures grow, host adapters need wrappers, and higher-order
APIs need an effect story. Examples using map over a world-touching callback
cannot settle that story by omission. Candidates are initially pure-only verbs
versus an explicit effect-polymorphic callback contract, not implicit authority.

**Experiment:** CLI path grant, browser no-files profile, and service callback
that sends a request. Require denial before unauthorized host access and an
effect diagnostic at the callback argument. Separately budget pure evaluation.
Use the [function contract proposal](../../design/function_contracts.md) for
the pure-only/effect-polymorphic comparison; do not duplicate its type model here.

**User-facing gate:** playground capabilities and diagnostics must reflect the
actual sandbox. A declared Network effect cannot invent browser permissions.
[Target](../../design/targets/effects.nomi).
