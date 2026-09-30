# Resource Outcome And Escape Experiment

> Status: focused evidence; candidate recommendation, not accepted semantics.

Packet: `docs/design/resource_lifetime.md`,
`docs/design/resource_lifetime_target.nomi`,
`docs/review/2026-09-29-resource-lifetime.md`.

## Pressure And Evidence

The overall import returns typed errors, but closing a resource may fail after
the body has already selected a return. Returning the body Err alone discards
cleanup. Raising a panic for an ordinary close error misclassifies expected IO.
Exactly-once close also says nothing about an alias used after that close.

Primary evidence, checked 2026-09-29:

- Python calls exit after successful enter, including target-binding failure,
  and permits an exit method to suppress a body exception.
  [With specification](https://docs.python.org/3/reference/compound_stmts.html#the-with-statement).
- Java closes initialized resources in reverse order, continues closing after
  failure, and retains additional exceptions as suppressed causes.
  [JLS 21 resource statements](https://docs.oracle.com/javase/specs/jls/se21/html/jls-14.html#jls-14.20.3).
- Python's shielding API distinguishes a protected operation from the cancelled
  caller; using shield alone is not evidence that the caller has joined cleanup.
  [Asyncio shielding](https://docs.python.org/3/library/asyncio-task.html#shielding-from-cancellation).
- Rust's Drop guidance discourages panicking during destruction, especially
  while unwinding another panic. A destruction hook is not a typed completion API.
  [Drop](https://doc.rust-lang.org/std/ops/trait.Drop.html).

These mechanisms suggest tests; they do not decide Nomi's error carrier,
unwind precedence, or lifetime model.

## Two Outcome Candidates

**A: typed completion.** A fallible scope produces an ordinary
`Result[T, ScopeFailure[E]]`, where E is a deliberately mapped domain error
family. Body and cleanup causes are ordered records. Panic/cancellation retain
their separate control channels and can carry cleanup causes. The explicit
long form is a proposed ordinary `run_scope(resource, body_function)` call.

**B: separate cleanup envelope.** The body signature remains `Result[T, E]`,
but failed cleanup exits via an additional scope-failure channel with the body's
outcome attached. This can retain causes without changing every Result signature,
but public effect/outcome metadata must expose that channel. Hiding it would
recreate an exception-like surprise under apparently exhaustive error types.

Both preserve causes; only A exposes expected cleanup recovery in ordinary
Result matching. **Recommend A for recoverable release failures**, initially
through a library combinator. Do not yet desugar `with` into it: function result
checking, nested heterogeneous errors, and break/continue propagation need a
complete type/protocol contract. Infallible-release `with` remains the narrow
accepted fixture. No new core shorthand is admitted.

## Two Escape Candidates

**Static scoped use:** a resource-derived handle cannot outlive its scope;
capture is allowed when the closure's use stays inside, and child transfer is
allowed only when join precedes release and sharing is safe. Runtime revocation
backs up foreign/unchecked boundaries. This needs lifetime/protocol metadata,
not necessarily ownership syntax in ordinary source.

**Dynamic scoped use:** handles can escape; revocation rejects operations after
scope close. This is simpler for interactive adapters but moves a predictable
mistake from authoring to execution and may leave a useless returned value.

**Recommend static non-escape with runtime revocation as a backstop.** This is
not a claim that current inference supports it. Concurrent use, parameter-region
propagation, stored closures, and resource ownership transfer remain admission
gates. Returning copied text is not handle escape.

## Executed Experiment

Run `python3 -m tools.resource_scope_experiment` or add `--json` for traces and
records. The [declarative fixtures](../design/fixtures/resource_scope_cases.json)
contain 16 scope scenarios and seven supplied lifetime facts. The tool compares
32 candidate traces and 14 escape-policy predictions. Tests also cover all 28
body/cleanup outcome pairs.

Covered: early return, failed first/second enter, rollback failure, body plus
close failure, multiple closes, deferred failure, panic, cancellation before or
during release, repeated cancellation, break, and continue. All successfully
entered resources get one close attempt and a revoked lease; an unentered
resource is never closed; one cleanup failure does not skip later actions.

This is a **symbolic state machine**, not foreign-language execution, actual
async scheduling, a Nomi parser, or lifetime inference. Lifetime facts are input,
not discovered from source. Finite injected cleanup completes by assumption;
unresponsive cleanup and host termination are not simulated. It detects missing
causes and order regressions, not real scheduler correctness or learnability.

## What Could Change The Recommendation

Reject A if realistic nested scopes force recursive error wrapping or opaque
implicit conversions that are harder to review than B's explicit public outcome
metadata. Reject static non-escape if it needs pervasive ownership annotations
for ordinary scripts; compare a deliberately capability-scoped dynamic profile
instead of weakening every host silently. Neither candidate may permit silent
use-after-close, skipped cleanup, or lost causes.

Next evidence: type three examples without implicit Any, specify Resource and
callback protocols, model binding failure after successful enter, and produce
real asynchronous cancellation/join traces before marking the packet accepted.
