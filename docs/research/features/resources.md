# Resource Lifetime

> Status: comparative evidence; lexical release accepted, escape/envelope open.

User pressure: close a resource on every exit without losing the original cause.

| Evidence | Mechanism | Nomi consequence |
| --- | --- | --- |
| [Python](../languages/python.md) | Explicit resource protocol | Dedicated exactly-once scope. |
| [C++](../languages/cpp.md) | RAII | Release lifetime is separate from GC memory reclamation. |
| [Go](../languages/go.md) | Function-scoped defer | Nomi deliberately chooses lexical scope. |
| [Zig](../languages/zig.md) | Error-only cleanup | Rollback is a distinct use case, not admitted syntax yet. |

Conceptual long form: acquire; run body; record its outcome; release exactly
once; compose outcomes without discarding causes. This is a semantic expansion,
not a Nomi `try` form. The accepted surface is:

```nomi
resource = files.open_reader(path)?
with resource as reader:
    return reader.read_all()
```

The fixture assumes infallible release for this narrow reader. General release
may fail or suspend and requires a composed outcome contract. `defer` is
unconditional, LIFO, and lexical; registration/capture timing must be specified.

Two unresolved choices are static non-escape enforcement versus runtime
closed-handle checks, and domain-visible cleanup Results versus a distinct
abnormal envelope. Exactly-once release alone prevents neither alias escape
nor loss of a cleanup error. GC does not choose between these options.

**Experiment:** three programs: early read return, staged acquisition rollback,
and async cancellation while release fails. Also return/capture/send the handle
outside scope. Produce event traces, composed causes, diagnostic locations, and
an explicit rule for each escape. Reject designs that allow double close or
silent use-after-close.

**User-facing gate:** explain output must show enter/body/exit and all causes;
playground promotion waits on the narrow supported contract.
[Target](../../design/targets/resources.nomi).

Continuation: [focused experiment](../resource_lifetime.md),
[completion proposal](../../design/resource_lifetime.md), and
[three pressure programs](../../design/resource_lifetime_target.nomi). The
symbolic comparison is executed; typed protocol and actual async gates remain.

## Foreign Callbacks And Re-Entry

> Research extension checked 2026-10-04. Callback/ABI contracts below are
> hypotheses under the resource and function packets, not supported FFI APIs.

### Existing Coverage And New Pressure

The [completion proposal](../../design/resource_lifetime.md) already requires
whole-completion non-escape, revocation, cause retention and joining outstanding
operations. The [industrial FFI target](../../design/industrial.md#foreign-interfaces)
names ownership, allocation, thread affinity, blocking, effects and panic.
The [interface edge atlas](../interfaces/edge_cases.md#8-state-protocols-and-legal-actions)
distinguishes synchronous event reentrancy from queued delivery. These are
existing obligations, not missing resource concepts.

The additional research pressure is a **bidirectional control crossing**:
Nomi calls a foreign function, that function calls a Nomi closure while the
original operation is unfinished, and the closure can retain or use the
original operation's state. A callback can also arrive on a foreign-created
thread, remain in flight during deregistration, or arrive after a host claims
registration ended. A raw callback pointer does not communicate any of those
lifetime or authority facts.

This is a named subexperiment under open questions 3/4/5/7/15 and the existing
`resource-lifetime`/`function-contracts` packets. It does not admit general
continuations, callback syntax, detached tasks, or host exception semantics.

### Checked Primary Evidence

The rolling [Rustonomicon FFI chapter](https://doc.rust-lang.org/nomicon/ffi.html),
especially its callback and unwinding sections, was checked on 2026-10-04.
It distinguishes callbacks on the triggering thread from callbacks on
foreign-created threads, requires synchronization and preventing later calls
after a callback target is destroyed, and describes ABI-specific unwind
behavior. Rust panic and foreign exceptions do not have interchangeable
behavior at an ABI that disallows unwinding. These are Rust/C boundary facts,
not Nomi rules or evidence that a Nomi registration wrapper is safe.

The [memory-visibility continuation](concurrency.md#memory-visibility-and-publication)
owns publication across tasks/threads. The source evidence above does not
select a Nomi scheduler, prove closure/region checking, or certify a foreign
library's deregistration promise. Pin the particular library, ABI, target,
build configuration and callback protocol before an adapter experiment.

### A Sharp Counterexample

Original event metalanguage, not executable Nomi:

```text
outer Nomi operation holds a lock and a scoped resource
-> calls a foreign operation that synchronously invokes its callback
-> callback tries the same non-reentrant lock or asks to close that resource
-> outer operation cannot finish until callback returns
```

Choosing immediate dispatch can deadlock on the lock, expose a partially
maintained invariant, or attempt release while the foreign operation still uses
the resource. Choosing queued delivery changes when the callback can affect
the outer operation; it is not an invisible equivalent. If the foreign API
needs the callback's immediate return value, a queued observation is not a
substitute for that callback protocol.

A separate late-delivery counterexample: callback A begins and reads its
target; the owner deregisters and frees the target; A resumes. A promise of
"no new callbacks after deregistration" is insufficient if it says nothing
about calls already in flight. The adapter must distinguish admission closed,
in-flight count zero, ordinary lease revoked, and external release completed.

### Competing Contracts

| Candidate | Delivery and retention | Strength | Cost or limit |
| --- | --- | --- | --- |
| Restricted immediate callback | Synchronous, non-retained callback; declared executor, return shape and allowed operations | Supports decision/comparator callbacks needing immediate results | Re-entry, mutable aliases, blocking and panic containment need a precise local contract |
| Owned-event bridge | Foreign callback copies/owns a bounded event and queues it; Nomi processes later under an owner | Avoids entering ordinary Nomi execution on a foreign stack/thread | Cannot satisfy an immediate-response API; queue overflow, copied data, ordering and shutdown policy remain |
| Explicit re-entrant registration | Retained callback has an owned registration, executor/admission policy and drain obligation | Supports richer host/device integrations | Most expensive region, authority, synchronization and invariant proof burden |

These describe different adapter roles, not one universal callback mode switch.
The smallest experiment should retain separate types/protocol owners when the
contracts differ. Foreign calls that cannot state a safe callback/unwind
contract remain outside the checked boundary; marking `UnsafeHost` is not a
proof that a native process will survive a malformed ABI crossing.

For each candidate, compare a non-unwinding adapter that contains Nomi abnormal
completion at the boundary with a specifically supported unwind-capable
adapter/profile. Expected callback Result, Nomi panic, cancellation request,
foreign exception, host abort and adapter containment failure remain distinct.
Do not silently convert a panic into an ordinary domain Err to make a C return
slot convenient. A process-abort path cannot promise cooperative cleanup.

### Edge Matrix

| Case | Fact to preserve | Discriminator |
| --- | --- | --- |
| Callback occurs inside the registering call | Registration may not yet be published to its owner | Initialize target/admission state before foreign code can enter it |
| Callback re-enters an unfinished outer operation | Which invariants and locks are presently exposed | Reject forbidden re-entry or use a documented re-entrant protocol |
| Foreign-created thread invokes callback | Thread/executor, publication and granted authority | Bridge or establish declared thread safety; do not inherit task-local grants ambiently |
| Callback captures a scoped Reader/closure/task | Region travels through registered retention | Registration must end and drain within the resource's admitted lifetime |
| Foreign buffer is valid only during callback | Borrowed bytes versus owned queued event | Copy/retain under an explicit host contract before delayed delivery |
| Deregistration stops future calls but one is active | Admission and quiescence differ | Join the active callback before freeing its target or dependent resource |
| Callback asks to deregister itself | Waiting for its own completion can deadlock | Compare staged close request with a supported non-blocking self-removal protocol |
| Callback fires after completed deregistration | Adapter guarantee has been violated | Retain a safe token/tombstone if supported; never dereference freed memory to discover the violation |
| Target callback panics or foreign code throws | Declared ABI unwind/containment policy | Preserve the abnormal category; unsupported unwinding cannot be normal Result propagation |
| Cancellation arrives while foreign code is active | Request, native interruption and join are separate | Report incomplete work if the foreign operation cannot cooperatively stop |
| Event queue fills or handler fails | Backpressure/drop policy and source of failure | Preserve owned bounded evidence; do not block a foreign callback that must not block |
| Cleanup and callback both fail | Original operation and release causes | Compose without exporting a raw pointer, live handle or retaining closure in diagnostics |

Thread safety, reentrancy, callback retention, cancellation and unwind support
must not be inferred from one another. A thread-safe registration can still
deadlock on self-deregistration; a non-retained synchronous callback can still
re-enter an inconsistent state; a completed foreign call need not end an
independently retained registration.

### Nomi Normal Form And Inspection

Placement: ordinary typed adapters plus resource-owned registration protocols,
function capture/effect/region metadata, and a declared host runtime profile.
No change to `with` or general-profile garbage collection is proposed.

```text
check adapter/ABI/profile and callback contract
-> construct callback target, safe identity and explicit authority context
-> establish admission state before foreign registration can call back
-> register and record the registration owner
-> dispatch only admitted callbacks; retain/copy according to input lifetime
-> track active calls and their owned outcomes
-> close admission and perform the declared foreign deregistration protocol
-> join/drain supported in-flight callbacks before freeing their dependencies
-> revoke ordinary leases and release remaining resources under scope policy
-> publish completion, or explicit incomplete/abnormal evidence
```

The protocol must choose a safe ordering for cancellation, admission closure,
revocation and draining; this outline does not override the resource proposal
or make every host interruptible. Late calls may need a still-live gate whose
lifetime exceeds the target. If the foreign API cannot provide the necessary
ordering, reject the checked adapter rather than invent it from a local counter.

Inspection should show registration and target identities, retention/capture
regions, callback phase, executor, current concrete grants, in-flight state,
and the exact meaning of deregistration completion. Trace payloads contain
owned redacted observations, not native pointers or callbacks retaining live
authority. Diagnostics relate the adapter declaration, callback capture,
resource acquisition and failed close/join obligation.

### Named Subexperiment Under Question 5

**Subexperiment: callback admission and quiescence.** Compare immediate,
owned-event and re-entrant adapters under the existing scope/completion gates.

| Program level | Prepared inputs | Required observations |
| --- | --- | --- |
| Beginner | Synchronous foreign comparator/decision callback with no retained target; one ordinary failure | Call/return nesting, argument ownership and declared result versus abnormal containment |
| Production | Owned watcher registration feeding a bounded queue; normal close; one callback active when close begins | Admission event, publication edge, active-call drain, queue policy and completion only after supported join |
| Failure-heavy | Callback during register, self-close, foreign thread, borrowed buffer reuse, late callback, panic plus release failure | Candidate-specific rejection/containment, no freed-target access, all retained causes, honest incomplete shutdown |

Begin with supplied event histories and callback/ABI contracts, including both
"no new calls" and "no calls remain" deregistration variants. A later removable
host spike needs one pinned test library that deliberately exposes each event
boundary. It must not invoke undefined native behavior just to observe an
error; unsafe scenarios can first be rejected from supplied facts or simulated
with still-live targets. No host/library behavior is inferred from a fake
countermodel's policy.

Falsifiers: queued delivery is offered where immediate results are required;
normal close can race a live target; a callback gains the registering task's
authority implicitly; an abnormal unwind crosses an unsupported ABI; or a
shutdown UI claims completion from admission closure alone. Remove the richer
candidate if its ownership/quiescence assumptions cannot be checked or enforced
by the chosen host. Keep unsupported integration explicit and library-first.

**Unperformed:** no C/JS/Wasm callback adapter, native thread test, actual
deregistration race, ABI unwind probe, lifetime checker, or usability study ran
for this continuation. The resource lab's symbolic traces and hosted context
manager repairs are not foreign callback conformance.
