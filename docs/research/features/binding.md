# Bindings And State

> Status: comparative evidence; accepted Nomi surface, unresolved interactions.

User pressure: distinguish a new fact from an update during a quick scan.

| Evidence | Mechanism | Nomi consequence |
| --- | --- | --- |
| [Python](../languages/python.md) | Lightweight named local code | Keep short local bindings, deliberately break assignment parity. |
| [Scheme](../languages/scheme.md) | Lexical environments and initializer visibility | Specify shadowing and capture, not merely spelling. |
| [Clojure](../languages/clojure.md) | Immutable values plus explicit coordinated state | Separate ordinary local mutation from shared-state libraries. |
| [Go](../languages/go.md) | Scope influences deferred lifetime | Keep update and release scopes independently readable. |

Accepted target:

```nomi
base = 10
var total: Int = base
set total = total + 2
```

The explicit long form is already the core form; no augmented assignment or
implicit mutable alias is needed. Immutable binding does not automatically
settle deep immutability of host values. Constraints require tentative binding,
validation, and commit: a failed update must not leave invalid observable state.
The canonical semantics already specify immutable value captures and mutable
cell captures. Safe cross-task sharing of those cells still needs its own rule.

**Experiment:** three programs: counter, constrained inventory update, and
closure shared with two tasks. For a rejected update require the old state and
declaration/use-site diagnostic ranges. Compare runtime capture semantics and
static rejection for unsafe sharing. Remove any convenience that obscures which
name changes; do not add a new binding keyword to solve a library problem.

**User-facing gate:** a playground sample must display the same values and
constraint diagnostic on CLI/browser, with a formatter that preserves update
visibility. [Target](../../design/targets/binding.nomi).
