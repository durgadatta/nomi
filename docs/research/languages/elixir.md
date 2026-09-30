# Elixir

> Status: comparative evidence; scope is Task APIs.

## Observe

Elixir Task APIs distinguish linked asynchronous processes and supervised
variants. Starting a task and observing its result are concrete process
operations with failure consequences.
[Primary reference: Task](https://hexdocs.pm/elixir/Task.html).

## Judge And Pay

**Adopt** explicit ownership and the distinction between a returned failure
value and an abnormal process failure. **Adapt** finite workflows to Nomi cold
tasks and lexical groups. **Reject** treating every returned Err as a task
crash or calling process linking a complete cancellation policy.

Nomi loses the direct fit with a mature actor runtime. Its GC and host tasks
will need evidence for cancellation responsiveness and isolation rather than
assuming that message passing solves all shared-state hazards. A task returning
Result has two layers of outcome: task completion and the returned value.

## Test

Run four cases: child Ok, child Err, child panic, and parent cancellation.
Assert distinct traces and policy-dependent sibling behavior. Observe results
in input order and completion order to expose diagnostic-order assumptions.
See [concurrency](../features/concurrency.md) and
[concurrency.nomi](../../design/targets/concurrency.nomi).
