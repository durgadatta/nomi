# Resource Completion Proposal

> Status: designing; recommendations below are not yet accepted target extensions.

Packet: `docs/research/resource_lifetime.md`,
`docs/design/resource_lifetime_target.nomi`,
`docs/review/2026-09-29-resource-lifetime.md`.

## Existing Contract Versus Proposal

[Semantics](semantics.md#resources-and-scope) already require exactly-once body
and release, lexical LIFO defer, and retention of body/cleanup causes. They do
not specify a complete typed release carrier or a handle-escape checker.
This proposal fills the **experiment**, not those implementation gaps by fiat.
It introduces no accepted syntax and does not change runnable prototype behavior.

Recommended direction: recoverable release errors use an ordinary Result with
an explicit scope-failure error value; handles are statically non-escaping where
checked and runtime-revocable at unchecked boundaries. The
[research comparison](../research/resource_lifetime.md) explains the alternatives.

## Source And Types

The explicit long form is a proposed library call:

```nomi
pub func read_text(path: Path) -> Result[Text, ScopeFailure[IoError]] uses FileRead:
    return run_scope(files.reader_resource(path), read_body)
```

`reader_resource` constructs a description; enter performs acquisition. The
proposed protocol has separate acquisition, borrowed-use, and release phases.
`run_scope` accepts a body `Reader -> Result[Text, IoError]` and owns composition.
Generic declarations, effect-polymorphic callback types, and region metadata
are deliberately not assigned new syntax here. The full
[target](resource_lifetime_target.nomi) labels every proposed API.

Conceptual completion error metadata retains phase (`enter`, `body`, `cleanup`),
typed E, operation, resource identity, and source span. It does not store a raw
handle or reveal a pending successful return value in default diagnostics.
Nested heterogeneous failures require explicit mapping to a declared E; neither
Any nor a magically coercing universal error union is an acceptable fallback.
The [callback paper audit](function_contracts.md#resource-callback-where-the-derivation-must-stop)
exposes a further typing gate: non-escape covers the entire completion, including
E, nested causes, and exported diagnostic/trace payloads, not only Ok(A).
An error, closure, aggregate or cold task retaining the reader is still an
escape. Copy owned redacted observations and stable resource IDs instead.

## Normal Form

```text
construct resource description once
-> enter once
-> register exit immediately after successful enter
-> bind/check acquired handle
-> run body once if binding succeeded
-> freeze pending transfer/outcome
-> unwind registered actions in reverse registration order
-> revoke ordinary handle access before starting its release
-> attempt every release/defer once, recording each outcome
-> compose completion
-> observe completion only after unwind finishes
```

Enter failure does not register that resource's exit; earlier acquisitions still
unwind. A protocol whose enter partially acquires internally must own rollback
of that partial work and retain its rollback causes. Successful enter followed
by binding failure does register release. The current experiment covers enter
failure, but not the latter binding phase; that is an explicit next fixture.

Revocation prevents *new* ordinary operations while close suspends. Release
itself uses a privileged internal reference. Outstanding operations must be
joined or safely cancelled before revocation/release; a token check alone is
not enough to prove race freedom. This is a runtime/type gate, not model evidence.

## Completion Table

| Pending body | Cleanup | Proposed observation |
| --- | --- | --- |
| Ok/return/break/continue | succeeds | Preserve original value/transfer destination. |
| Err(E) | succeeds | Return typed body failure. |
| normal completion | Err(E) | Return typed scope failure; do not report success. |
| Err(E) | one/many Err(E) | Body primary; cleanup causes in attempted LIFO order. |
| cancellation | Err(E) | Cancellation stays a control signal with cleanup causes. |
| panic | Err(E) | Panic stays a panic with cleanup causes. |
| Err(E) | panic | Panic becomes primary; retain original body error. |
| cancellation | panic | Panic primary, cancellation retained; proposed precedence. |

The experiment chooses panic before cancellation before expected errors and
the earliest cause within one class; secondary causes retain encounter order.
This priority is **a candidate**, not established cross-backend semantics.
Repeated cancellation requests are trace events, not repeated root causes.

For `run_scope`, an ordinary Err returns from the combinator and the caller may
use normal `?`. Break/continue cannot cross a callback's function boundary.
Their fixture rows test unwind ordering only. Any future fallible `with` needs
an explicit enclosing-result/error mapping rule for those transfers; do not
claim the current library long form solves that core integration.

Cleanup cannot redirect return to another function, retry a body, or suppress
an existing failure as Python's exit boolean can. A failed cleanup can prevent
successful completion; the original destination and pending transfer remain
inspectable. Infallible release requires a protocol guarantee, not a comment
pretending a host close cannot fail.

## Cancellation And Limits

Recommended cooperative policy: latch cancellation while registered cleanup
is running, continue cleanup, and join it before publishing the final outcome.
Shielding without joining is insufficient. Release protocols must declare their
bounded/non-blocking behavior or explicit cleanup deadline policy. A timed-out
cleanup must be reported as incomplete, never as successful release.

No source language can guarantee completed cleanup after process termination,
host crash, or a non-cooperative host operation. Exactly once means one attempted
release per successfully entered resource under supported cooperative unwind,
not proof of external durability. The symbolic experiment assumes finite cleanup
and does not demonstrate timeout or real scheduler behavior.

## Escape Rules To Pressure-Test

| Program | Recommended result |
| --- | --- |
| Return owned text/bytes read from a handle | Allowed; owned value independent of the lease. |
| Return the borrowed reader | Reject at return; relate acquisition span. |
| Return Err with a reader, or export a cause/diagnostic retaining it | Reject whole-completion escape; relate payload/capture and acquisition. |
| Return a closure capturing the reader | Reject at capture/escape boundary. |
| Call that closure entirely inside scope | Allow, subject to effects. |
| Child joins in an inner group before scope exit | Allow only with a safe-sharing protocol. |
| Child or outer group can outlive the reader | Reject transfer. |
| Unsafe host stashes an alias | Runtime closed-handle failure after revocation; no new host operation. |

The experiment consumes these lifetime facts; it does not prove them. A future
checker must propagate regions through calls, aggregates, closures, and task
handles. Runtime revocation is a backstop, not a substitute for that analysis.

## Diagnostics And Formatting

Formatter examples use 80-column-oriented multiline parameters; `->` stays on
the closing parameter line. No new token gains a second meaning.

Expected terminal message: `Read failed; closing the reader also failed.`
The editor relates the read, scope, acquisition, and close declaration spans.
Playground explain shows enter/body/revoke/close/observe, with safe cause labels.
The experiment uses existing passive Diagnostic records, `phase=design-experiment`,
and null spans; it never invents parsed source locations.

```json
{
  "code": "NOMI-RESOURCE-OUTCOME-CANDIDATE",
  "phase": "design-experiment",
  "span": null,
  "details": {
    "channel": "result",
    "kind": "err",
    "pending_transfer": "err",
    "primary": {"kind": "err", "cause": "read", "phase": "body"},
    "secondary": [{"kind": "err", "cause": "close", "phase": "cleanup"}]
  }
}
```

## Admission Gate

Before acceptance: resolve generic/error/callback/region contracts, type the
three programs, add binding-failure/timeout/concurrent-use cases, specify defer
argument capture timing, and compare real async traces. Before playground
promotion: lossless Surface/Core scope nodes, typed diagnostics, formatter,
backend agreement, host capability metadata, and supported sample smoke coverage.
Remove the proposal if typed composition becomes less local than the explicit
public envelope alternative. Remove the lab when a versioned conformance runner
owns these fixtures; do not turn this symbolic script into the production runtime.
