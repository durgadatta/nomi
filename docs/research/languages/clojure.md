# Clojure

> Status: comparative evidence; scope is refs and STM.

## Observe

Clojure refs coordinate changes through transactions over immutable values.
Transactions may retry, so effects inside a transaction require particular
care rather than ordinary exactly-once assumptions.
[Primary reference: refs](https://clojure.org/reference/refs).

## Judge And Pay

**Adopt** separating immutable values from state coordination. **Adapt** shared
state to explicit concurrency-safe libraries. **Reject** overloading Nomi's
resource `with` with a retrying transaction meaning: a read, send, or close
inside it cannot unexpectedly run twice.

Persistent data and STM can simplify concurrent state transitions; excluding
STM from the core does not establish that locks or actors are easier. Nomi
loses a powerful declarative coordination mechanism and needs evidence before
choosing a default shared-state API. GC also does not make mutation safe.

## Test

Use two concurrent transfers and a notification effect. Force a conflict and
count notifications, committed transfers, and retries. Any future transaction
library must prohibit or explicitly stage effects and use a distinct API.
See [bindings](../features/binding.md), [effects](../features/effects.md), and
[concurrency](../features/concurrency.md).
