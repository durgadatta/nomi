# JavaScript

> Status: comparative evidence; Nomi judgments are hypotheses.

## Observe

Promises compose asynchronous completion through chaining; forgetting to
return a promise can detach work from the intended chain. Promise construction
and later observation are distinct operations.
[Primary reference: using promises](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Using_promises).

## Judge And Pay

**Adopt** convenient asynchronous composition, but **adapt** it to cold tasks
with an explicit starting owner. **Reject** an API where dropping an observation
silently leaves unowned work running. Nomi's `await` must mark suspension, while
a task group marks lifetime; these are different facts.

Cold tasks add a learning cost for browser developers accustomed to APIs that
start requests immediately. A Nomi browser adapter cannot simply rename every
Promise to Task: it must document when host work begins, how cancellation
reaches the host, and whether the host operation is actually cancellable.
Otherwise the attractive source contract is false at the boundary.

## Test

In [concurrency](../../design/targets/concurrency.nomi), construct two tasks
without starting them and assert zero host requests. Start them in a group,
cancel the parent, and record both completion and host cancellation events.
An uncancellable adapter must expose that limitation, not claim structured
cleanup it cannot supply. See [concurrency](../features/concurrency.md).
