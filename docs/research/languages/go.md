# Go

> Status: comparative evidence; Nomi judgments are hypotheses.

## Observe

Go's `defer` schedules a call for function return, with deferred calls executed
in reverse order. Its scope is not an arbitrary lexical block.
[Primary reference: defer statements](https://go.dev/ref/spec#Defer_statements).

## Judge And Pay

**Adopt** visible deferred cleanup and **adapt** its lifetime to Nomi's lexical
scope. **Reject** assuming Go behavior because Nomi reuses the word `defer`.
The distinction matters inside loops: a function-scoped defer can retain many
resources until the outer function exits.

Nomi's lexical rule can shorten lifetimes, but it requires precise registration,
capture, and exit-order semantics. A shorter lifetime is not automatically a
better one if cleanup needs a value that was subsequently updated. Explicit
Result also costs more typing than Go-style pairs in some APIs, while gaining
a named success/failure distinction.

## Test

Acquire and release one resource in each of three loop iterations. Require
open/close interleaving, not three opens followed by three closes. Then mutate
a value referenced by deferred cleanup and settle capture timing explicitly.
See [resources](../features/resources.md) and
[the resource fixture](../../design/targets/resources.nomi).
