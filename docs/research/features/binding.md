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

## Shared Binding Responsibilities

> Discovery lead retained from the earlier consolidated brief, integrated
> 2026-10-16. This compares responsibilities; it does not accept a universal
> binding protocol or additional binding syntax.

The useful question is whether source evaluation, decomposition, tentative
names, constraints and atomic commit can share a description across constructs.
Their surrounding scope, mismatch and completion policies still have owners:

| Context | Common responsibility | Distinction that must survive |
| --- | --- | --- |
| Local declaration and destructuring | Evaluate once, check tentative names, commit atomically | Ordinary destructuring is statically irrefutable; refutable choice uses `match`. |
| Function parameters | Map arguments to bindings and check before entering the body | Labels, defaults, arity and call-time evaluation belong to the call contract. |
| Match captures and `as` | Decompose an already evaluated subject and retain immutable captures | Structural non-match or false guard selects another arm; contract failure is a different outcome. |
| Iteration variables | Bind each supplied element in the loop's scope | Consumption, repetition and cleanup belong to the iterator/loop contract. |
| Acquired resource value | Bind after successful acquisition | Binding failure must still release the acquired resource; `with` never retries its body. |
| Exception payload or coroutine reception | Potentially present a value to a binder | Host compatibility is not target exception-binding or `yield` admission; suspension and abnormal completion need separate contracts. |

**Prepared comparison:** describe a constrained pair both as local decomposition
and as parameter binding; reject the second component and require no committed
names or body events. Contrast this with a refutable match that continues to a
fallback arm. Then place the same failed bind after resource acquisition and
require one release. Finally model a sent coroutine value without changing the
ordinary evaluator. Compare shared declarative binding descriptions with
construct-specific adapters, including source ranges and lexical scope.

These cases have not been executed by this intake. Retain a shared mechanism
only if it preserves those distinct outcomes and simplifies inspection. Do not
turn mutation into fresh binding, guards into constraints, or received external
data into trusted nominal data. [Semantics](../../design/semantics.md#binding),
[resource completion](../../design/resource_lifetime.md), and
[question 7](../open_questions.md#7-generator-and-stream-semantics) own the laws
and remaining gates.
