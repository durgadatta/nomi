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

## Control Effects And Continuation Ownership

> Research continuation 2026-10-10: questions 4/5/7; a discovery comparison,
> not a selected replacement for Nomi's direct calls or failure channels.

Effect declarations about world access and mechanisms for transferring control
are different axes. OCaml 5.3 handlers can capture and resume a continuation.
Their one-shot discipline checks repeated resumption dynamically, but does not
check that an abandoned continuation is eventually continued/discontinued;
resources can remain retained by suspended computation.
[Primary reference: effect handlers](https://ocaml.org/manual/5.3/effects.html).

Compare a direct callback/Result API, an explicit state-machine or Stream value,
and a one-shot handler challenger for an operation that requests an observation
and continues with the answer. The handler can move scheduling behind an ordinary
looking call; the explicit state machine exposes the suspended state. Each needs
an account of who owns pending computation, which failure ends it, and how authority
and resource regions travel through it. Multiple resumption is a separate,
more demanding challenger, especially when external effects or resources cannot
be duplicated.

**Prepared resource schedule:** enter a scope, request an observation, suspend,
then (a) resume once, (b) attempt resumption twice, (c) abandon the request, or
(d) cancel while release fails. Specify events and causes before implementing
any candidate. At-most-once use alone cannot establish eventual cleanup. A pure
request declaration cannot grant the responding handler world authority.

Keep direct-call expected failure as Result in the accepted target. A handler
research model must name any proposed channel/control conflict explicitly, retain
source-linked suspended state for inspection, and demonstrate a benefit in a
whole program. Remove it if it only hides equivalent ordinary calls or prevents
local reasoning about task/resource ownership. No handler, continuation runtime,
or scheduler was implemented or executed here. The
[maintainer guide](../synthesis_guide.md) keeps this lead with existing owners.
