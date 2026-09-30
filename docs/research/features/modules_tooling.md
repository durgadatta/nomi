# Modules And Tooling

> Status: comparative evidence; package principles accepted, implementation open.

User pressure: grow a script into a shared package while retaining readable
interfaces and useful explanations on every frontend.

| Evidence | Mechanism | Nomi consequence |
| --- | --- | --- |
| [OCaml](../languages/ocaml.md) | Module abstraction | Public signatures must support separate reasoning. |
| [Kotlin](../languages/kotlin.md) | Closed alternatives across boundaries | Variant evolution belongs in API compatibility checks. |
| [Roc](../languages/roc.md) | Host architecture | Explicit capability profiles across deployments. |
| [Dhall](../languages/dhall.md), [Nix](../languages/nix.md) | Integrity and dependency/evaluation boundaries | Pin identity separately from execution grants. |
| [Pkl](../languages/pkl.md) | Contextual errors | Preserve declaration and input locations. |
| [Uiua](../languages/uiua.md), [Racket](../languages/racket.md) | Live inspection and expansion tools | Explanations are product surfaces, not optional reports. |

```nomi
pub func register(raw: Value) -> Result[User, DecodeErrors]:
    return User.decode(raw)
```

A file is a module, declarations are private by default, and public functions
publish types/effects. Discovery must not execute module bodies. Manifests and
exact lockfiles define dependency identity. None of these principles imply a
finished package resolver or a settled generic/interface syntax today.

Tools should share versioned structured diagnostics, typed Surface/Core
artifacts, source maps, and capability metadata. A helpful browser experience
cannot rely on different semantics from the CLI. The current GitHub playground
is a migration surface, not evidence that target syntax is implemented.

**Experiment:** split the overall fixture into three modules; produce a proposed
public API diff, locked dependency graph, typed artifacts, and diagnostic JSON.
Change a variant, remove a grant, and make a lock hash stale. Require distinct
source-stable errors without discovery-time execution.

**User-facing gate:** only after conformance, add the smallest supported sample
to `samples/`, regenerate the manifest, and extend browser smoke coverage.
[Module target](../../design/targets/modules.nomi);
[tooling target](../../design/targets/tooling.nomi).
