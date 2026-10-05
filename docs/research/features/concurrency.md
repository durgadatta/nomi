# Concurrency

> Status: comparative evidence; lifetime accepted, policy/API contracts proposed.

User pressure: run independent work together without leaking children or losing
failures when the parent exits.

Compare [workflow execution models](../data_workflows/execution_models.md)
before borrowing orchestration APIs: a lexical task group, durable replay,
asset materialization and an event-time stream have different lifetime laws.

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

## Memory Visibility And Publication

> Research extension checked 2026-10-04. Shared-memory contracts below are
> alternatives, not accepted atomics syntax or a new Nomi memory-model guarantee.

### Lifetime Is Not Visibility

The existing task-group comparison owns child lifetime, failure policy,
backpressure, cancellation and cleanup. [Binding research](binding.md) already
leaves safe cross-task sharing of captured cells open. The additional pressure
is what a reader may observe **between tasks that legally share state**, and
which operations establish that observation boundary.

Joining a child, publishing an immutable result, transferring a message,
receiving a cancellation request and releasing a lock are different acts. A
structured lifetime prevents escaped children but does not, by itself, define
read/write visibility, atomicity, or the publication of an initialized value.
A host's GIL, event-loop turn, current CPU, or convenient test scheduler cannot
quietly supply the portable answer. This deepens open questions 3/4/7/15 and
the existing language-coherence D1-D3 gates; no concurrency packet or global
experiment series is added.

### Checked Primary Evidence

Sources checked 2026-10-04:

- [Go memory model, version June 6, 2022](https://go.dev/ref/mem) specifies
  synchronization and data-race-free sequential consistency. It distinguishes
  goroutine exit from synchronization and states specific channel/lock edges.
  Its treatment of racy programs is not a proposed Nomi failure policy.
- [Java SE 25 JLS chapter 17](https://docs.oracle.com/javase/specs/jls/se25/html/jls-17.html)
  separates program order, synchronization, happens-before, data races and
  causality; correctly synchronized programs have sequentially consistent
  behavior. A consistent sequence of individually safe accesses still need
  not make a multi-step business operation atomic.
- [Rust atomic Ordering documentation](https://doc.rust-lang.org/std/sync/atomic/enum.Ordering.html)
  is a rolling API reference. It distinguishes relaxed atomic accesses from
  acquire/release and sequential consistency. These are low-level ordering
  choices, not evidence that ordinary Nomi users need ordering annotations.

These sources establish real distinctions in their specified models. They do
not prove a Nomi compiler, channel, task join, host adapter, or scheduler correct.

### A Sharp Counterexample

Original event metalanguage; not executable Nomi:

```text
Initially: payload = absent; ready = false
Producer: construct payload; store shared payload; mark ready
Consumer: observe ready; read payload
```

Without a stated publication edge, source order in the producer and seeing a
flag do not establish the intended initialized-payload guarantee. A model in
which `ready` is an atomic flag with only relaxed ordering still needs a rule
for the payload and its lifetime; flag atomicity alone is insufficient. If
ordinary shared mutable captures are statically rejected, this program should
be rejected rather than granted accidental host visibility.

The second counterexample is independent: two tasks each read an available
capacity of one, each decide to reserve, then each perform a separately safe
write. Visibility and absence of torn reads do not make the read/check/write
sequence one reservation. A transaction, lock-owned update, or versioned
compare-and-commit owner is required under the proposed domain contract.

### Competing Contracts

| Candidate | Ordinary task sharing | Synchronization burden | Cost or limit |
| --- | --- | --- | --- |
| Message/owned-value boundary first | Immutable owned values may transfer; unsynchronized mutable cell captures across tasks are rejected | Channel/task-result protocols define publication and ownership | More copying or explicit shared-state handles; clarify deep immutability and transferred host buffers |
| Guarded shared-state protocols | Shared mutation only through declared concurrency-safe handles | Locks/transactions/channels/joins publish documented ordering and atomic-operation boundaries | Protocol metadata and capture checking; a safe handle still cannot make arbitrary multi-call sequences atomic |
| Specialized low-level profile | Explicit atomics/foreign shared buffers under a named profile | Ordering and lifetime are part of a typed adapter/library contract | Greater optimization freedom and greater proof burden; not a silent relaxation of the portable core |

The first two can compose: the question is which sharing is admitted initially
and what each abstraction promises. A specialized profile must keep unsupported
operations explicit rather than reinterpret ordinary bindings. Sequential
consistency of an atomic API is another candidate restriction, not a proof of
domain serializability, fairness, bounded waiting, or cancellation completion.

### Edge Matrix

| Case | Fact to preserve | Discriminator |
| --- | --- | --- |
| Parent constructs immutable input before child start | Initialization versus child observation | State the start/publication edge and any copying/ownership requirement |
| Parent awaits a completed child result | Joined lifetime versus visibility of declared outputs | Identify the synchronization edge; do not infer remote durability |
| Child mutates an outer captured cell | Shared storage and allowed access | Reject unsafe capture or require a concurrency-safe owner |
| Producer signals readiness for a payload | Flag ordering versus payload initialization | A flag read cannot substitute for a declared publication guarantee |
| Buffered versus unbuffered channel | Matching communication, capacity and protocol ownership | Do not copy one carrier's ordering rules into another without evidence |
| Queue publishes a borrowed buffer then producer reuses it | Transfer/reference lifetime after enqueue | Copy, transfer, or retain a declared lease; publication alone does not stop mutation |
| Two safe reads/writes maintain capacity | Multi-step invariant | Require one owned atomic transition, not merely atomic scalar operations |
| Cancellation flag is observed | Request visibility versus completed cleanup | Do not claim the task or resource has stopped from the flag alone |
| Foreign callback writes shared state | Foreign thread/executor and adapter boundary | Join or bridge through a documented publication mechanism |
| Optimizer moves a read across a call | Call's possible synchronization and failure | Preserve declared observation edges and ordinary evaluation semantics |
| Trace timestamps look ordered | Display order versus semantic dependency | Report known synchronization/causal edges separately from wall-clock sorting |
| Safe code reaches an unsupported host sharing mode | Portable capability and data-race policy | Fail honestly at the adapter/profile boundary, not by inheriting undefined host behavior |

### Nomi Normal Form And Inspection

Placement: core rules for admissible sharing and cross-profile observations;
ordinary synchronization libraries for operations; specialized adapters for
foreign/device memory. No new keyword or universal atomic wrapper is proposed.

```text
identify shared value/cell/handle and its owner
-> check transfer, capture and mutation eligibility
-> select the synchronization protocol/profile
-> record publication and matching observation edges
-> check each operation and compound transition boundary
-> preserve edges in lowering/optimization
-> expose outcome and bounded causal evidence
```

The inspector should show which data are owned copies, shared immutable values,
or mutable protocol handles; relate a rejected cell capture to both tasks; and
name the primitive that publishes an observation. A type/effect view must not
equate `uses` permission with synchronization. A race-free claim must identify
its admitted storage and interfaces, while an atomic-update claim names the
operation protected. Host thread IDs can be useful observations but must not
become the language-level task identity.

### Named Subexperiment Under Question 15

**Subexperiment: publication versus lexical join.** Compare owned-message and
guarded-sharing candidates using the existing task/callback/resource contracts.

| Program level | Prepared inputs | Required observations |
| --- | --- | --- |
| Beginner | Parent initializes a value; child returns a result; parent joins; contrast an illegal outer-cell update | Permitted capture, publication edge, returned value and a local rejected-sharing diagnostic |
| Production | Bounded producer/consumer queue with owned messages versus borrowed/reused buffers; concurrent capacity reservation | Ownership transfer, matching send/receive evidence, one transition boundary, queue and resource limits |
| Failure-heavy | Readiness flag without publication; cancellation during handoff; deregistering foreign producer; abandoned child/cleanup | Explicit rejection or admitted outcomes, no false completed Stop, no reuse of a live borrowed buffer |

First write finite litmus outcomes and the edges required by each candidate.
An event scheduler enumerating sequential interleavings is not a weak-memory
oracle; a later memory-model spike must state which compiler/hardware
reorderings it includes. Compare a single-threaded executor with a parallel
profile against the same declared portable contract, not against identical
timing. Reader tasks ask which value may be observed and which operation owns
an invariant, not whether a diagram has an attractive arrow.

Falsifiers: a supposedly safe program reads incompletely published owned data;
join is advertised as a synchronization edge but lowered without it; borrowed
messages permit concurrent reuse; or a safe abstraction's separate operations
are presented as an atomic compound transaction. Remove a relaxed candidate
if its proof obligations cannot be kept local or its unsupported modes leak
into ordinary code. A failure can justify a smaller allowed-sharing boundary,
not an ambient unchecked escape.

**Unperformed:** no Nomi memory model is accepted here; no hardware litmus test,
memory-model checker, native/Wasm differential run, race detector, compiler
proof, or reader study executed this experiment. Existing task lifetime and
messaging probes do not establish memory visibility.
