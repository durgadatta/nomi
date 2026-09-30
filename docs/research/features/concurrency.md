# Concurrency

> Status: comparative evidence; lifetime accepted, policy/API contracts proposed.

User pressure: run independent work together without leaking children or losing
failures when the parent exits.

| Evidence | Mechanism | Nomi judgment |
| --- | --- | --- |
| [JavaScript](../languages/javascript.md) | Promise chains and detached work | Cold work needs an explicit starting owner. |
| [Swift](../languages/swift.md) | Structured task groups | Lexical child lifetime, explicit join/cancel. |
| [Elixir](../languages/elixir.md) | Linked/supervised task processes | Returned Err and task failure are separate layers. |
| [Erlang](../languages/erlang.md) | Restarting supervisors | Service recovery is not a finite task-group policy. |

```nomi
async with TaskGroup(limit=2, failure=TaskFailurePolicy.CancelSiblings) as tasks:
    pending = tasks.start(fetch_text(url))
    outcome = await pending
    return outcome
```

The TaskGroup constructor and policy name are proposed library APIs. Accepted
semantics require cold async calls, visible suspension, and children that cannot
silently outlive their owner. This snippet does not settle an ErrorGroup type.

Important independent choices: running limit versus queued-memory bound;
input-order observation versus completion-order observation; ordinary child
Err versus abnormal child failure; sibling cancellation versus continued work;
parent cancellation during cleanup; multiple-cause ordering. A limit on active
tasks is not backpressure when a million task handles are eagerly allocated.

**Experiment:** pair fetch, finite batch enrichment, and failure-heavy bounded
producer. Use an event-controlled scheduler, not timing sleeps. Assert host
start counts before await, peak active/queued counts, exactly-once release, and
no child events after scope completion. Compare sibling-cancel and collect-all
policies with ordinary Err, panic, and parent cancellation.

**User-facing gate:** playground stop must reach the supported runtime and
explain what cannot be cancelled. Task traces must show actual ownership.
[Target](../../design/targets/concurrency.nomi).
