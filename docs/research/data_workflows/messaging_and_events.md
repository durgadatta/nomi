# Messaging And Event-Driven Architectures

> Status: selected primary-source research and Nomi composition hypotheses,
> checked 2026-10-04; no broker integration, accepted API or new syntax.

[Domain composition](../domain_composition.md), [Dependencies/time](dependencies_and_time.md),
[Generic operations](../generic_operations.md), [Canonical synthesis](../../design/synthesis.md#domain-layer-proposal)

## Start With A Program, Not A Broker

An order is accepted, inventory is reserved, a projection is updated, and a
notification is requested. A process crashes after reserving inventory but
before acknowledging its delivery. Another worker receives the event. Can a
reader tell what may repeat, which state is durable, who owns the next action,
and whether a timeout means nothing happened?

This challenges existing D1-D3 contracts: callback effects, task/resource
completion, wire values, identity and evidence. It does not demonstrate a need
for `publish`, `subscribe`, `actor`, `topic` or `workflow` keywords. The
[target challenger](../../design/targets/research/messaging.nomi) uses ordinary
calls; [finite probes](probe_messaging.py) separate several tempting conflations.

The ecosystem can accommodate architecture knowledge as domain packages with
explicit laws and adapters. Not every application should become event-sourced,
and not every relation should become a queue or DAG. The extraction below is a
selected mechanism map, not exhaustive IT knowledge or a popularity ranking.

## Distinctions Before Abstractions

| Concept | Question answered | Not implied |
| --- | --- | --- |
| Command | What action is being requested, under whose authority? | The action happened or will be accepted |
| Event | What occurrence does this producer assert? | Independent truth, current authorization or complete history |
| Message | What envelope/payload crosses this boundary? | Event semantics; commands and replies can also be messages |
| Delivery | Which attempt, owner and settlement context is this? | Unique event, completed handler or exclusive external effect |
| Queue | Which work is available to competing recipients? | Broadcast, retained history or permanent single ownership |
| Pub/sub | Which subscriptions receive matching publications? | Persistence, replay, ordering or business success |
| Log | Which records/positions remain readable? | A work queue, global order or a complete event-sourcing record |
| Stream | Which temporal sequence/progress contract is exposed? | Durability, pull-only behavior or a list with async spelling |
| Actor | Who serializes access to this state/protocol? | Durable mailbox, exactly-once effects or transparent distribution |
| Workflow | Which durable state/timer/action transitions constitute progress? | A task DAG or an ordinary stack that survives a crash |

Topology, persistence, routing, execution and failure policy are independent
axes. Pub/sub can fan out to durable queues; competing workers can share one
subscription; logs can support both projections and work distribution. A graph
view must label publication, subscription, dependency and compensation edges.

## Selected Primary Mechanisms

Version fences: Kafka **4.1** is a deliberately pinned mechanism reference,
not the latest release; RabbitMQ rolling docs currently label **4.3**; Akka is
**2.9.0**; MQTT **5.0**, CloudEvents **1.0.2**, AsyncAPI **3.0.0** and Reactive
Streams **1.0.4** are explicit editions. Redis, NATS, Beam, Temporal, Debezium,
AWS and Azure references are rolling documentation checked above. No cited
product was installed or executed. NATS references use its official source
repository because older documentation URLs redirected to unrelated index pages.

| Family / evidence | Mechanism extracted | Boundary Nomi must preserve |
| --- | --- | --- |
| [Kafka design](https://kafka.apache.org/41/design/design/) and [consumer config](https://kafka.apache.org/41/configuration/consumer-configs/) | Partition-local logs, classic consumer groups, committed positions, producer idempotence/transactions and read isolation | Name the consumer/profile; position and transaction scope are not arbitrary external business completion |
| [RabbitMQ acknowledgments](https://www.rabbitmq.com/docs/confirms) and [reliability](https://www.rabbitmq.com/docs/reliability) | Publisher confirms, consumer settlement, channel-local delivery tags and outstanding-delivery credit | Confirming publication and acknowledging consumption are independent; connection loss can produce redelivery |
| [NATS consumers](https://github.com/nats-io/nats.docs/blob/master/nats-concepts/jetstream/consumers.md) and [JetStream model](https://github.com/nats-io/nats.docs/blob/master/using-nats/jetstream/model_deep_dive.md) | Core delivery versus durable consumers; publish deduplication windows and acknowledged acknowledgment | Broker dedup/settlement assurances do not transact an unrelated payment or database write |
| [Redis Pub/Sub](https://redis.io/docs/latest/develop/pubsub/) and [Streams](https://redis.io/docs/latest/develop/data-types/streams/) | Ephemeral subscriptions versus retained entries, consumer groups and pending/claimed work | An offline subscriber can miss Pub/Sub; overlapping subscriptions can yield two application callbacks for one publication |
| [SQS FIFO dedup](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/FIFO-queues-exactly-once-processing.html) and [visibility](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html) | Bounded send deduplication and temporary invisibility of received work | Five-minute send dedup is not an unlimited business ledger; undeleted work can become visible again |
| [MQTT 5.0](https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html) | QoS delivery handshakes, session/message expiry and retained publications | A per-protocol QoS guarantee is not an end-to-end application transaction; retained publication is not full history |
| [EventBridge target retries](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-rule-retry-policy.html) | Routed targets, finite retry policy and optional dead-letter destination | Exhausted delivery can be dropped without a DLQ; fanout does not atomically complete all targets |
| [Akka reliable delivery](https://doc.akka.io/libraries/akka-core/2.9.0/typed/reliable-delivery.html) | Ordinary actor delivery versus explicit producer/consumer controllers | Serial state access and delivery reliability require separate contracts |
| [Reactive Streams](https://www.reactive-streams.org/) | Asynchronous demand and nonblocking backpressure | Element credit alone is not a byte, worker or durable backlog bound |
| [Beam guide](https://beam.apache.org/documentation/programming-guide/) | Event time, processing time, watermarks, windows and triggers | Estimated progress and allowed lateness need an explicit correction/discard policy |
| [CloudEvents](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md) and [AsyncAPI](https://www.asyncapi.com/docs/reference/specification/v3.0.0) | Event envelope identity; channel/message/operation descriptions and protocol bindings | Envelope/schema description does not implement delivery or authorize execution |
| [AWS outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html) and [Debezium router](https://debezium.io/documentation/reference/stable/transformations/outbox-event-router.html) | Store business state and outbound intent together, then relay/route | Local atomicity removes a dual-write gap, not duplicate relay or downstream effect races |
| [Event sourcing](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing), [CQRS](https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs), [sagas](https://learn.microsoft.com/en-us/azure/architecture/patterns/saga) | Authoritative history, separate read/write models and coordinated local transactions/compensation | CQRS need not imply event sourcing; a projection can lag; compensation is a new business action, not rollback |
| [Temporal tasks](https://docs.temporal.io/tasks) | History-driven workflow reconstruction versus activity execution/retry | Durable workflow replay and repeated external activity effects are distinct |

These are selected reviewed mechanisms, not interchangeable implementations.
AMQP 0-9-1 evidence is not a full AMQP 1.0 analysis. Broker defaults, adapters,
schema registries, federation and failover protocols require separately pinned
conformance before use. A documentation claim is not a Nomi guarantee.

## A Small Foundation And A Composition Hierarchy

Reuse the core: immutable nominal values and variants, functions/structural
choice, explicit Result/Option, checked boundaries, effects/capabilities,
resource scope, structured tasks and modules. Candidate shared domain pieces:

| Small contract | Minimum owned fact | Where it belongs initially |
| --- | --- | --- |
| Envelope/identity | Payload schema, producer-scoped event ID, domain key and provenance where needed | Values/codecs library; CloudEvents adapter optional |
| Endpoint/reference | Resource incarnation, address and declared protocol/profile | Domain reference value; acquiring a live handle requires authority |
| Delivery/ownership | Receipt or position, attempt, lease/generation and permitted settlement | Scoped runtime adapter; not copyable execution permission |
| Progress/position | Owner-defined sequence/checkpoint/frontier and retained coverage | Queue/log/stream-specific protocol, not one global integer |
| Transition/completion | Which local facts commit together, what is known and what needs reconciliation | Pure transition descriptions plus explicit effectful owner |
| Policy/budget | Delivery/order/retry/overflow/retention/latency and resource limits | Typed validated configuration/profile; no guarantees inferred from names |

These are related contracts, not six mandatory fields on every value. A local
UI notification need not carry durable offsets; a log checkpoint must. Broker
capabilities and feature tables should be declarative and inspectable, but a
table cannot prove an engine honors its declarations.

```text
values + functions + effects + scoped tasks/resources
  -> typed local channels, credit, pure state transitions
  -> envelopes, endpoints, delivery settlement, positions
  -> competing queues / subscriptions / partitioned logs / actor protocols
  -> inbox/outbox, projections, checkpoints, replay and reconciliation
  -> CQRS, event-sourced aggregates, sagas, durable workflows, stream processing
  -> operations: deployment, tracing, repair, migration, retention and review
```

This is a learning/composition hierarchy, not an inheritance chain or claim
that distributed guarantees can be derived from local channels alone. Durable
storage, arbitration, clock/failure assumptions and participating transaction
owners add new contracts. Cyclic event feedback needs progress and overload
analysis, unlike an acyclic task-dependency specialization.

### Architectural Compositions

The following are Nomi package design hypotheses drawn from those mechanisms,
not accepted APIs or assertions that the listed systems share an implementation:

| Composition | Explicit pieces | Law or cost added at this level |
| --- | --- | --- |
| Work distribution | Queue + competing recipients + transition + settlement | A retryable attempt is not permanent exclusive ownership |
| Event bus | Routing + independent subscriptions + delivery policies | Per-subscriber progress; no atomic fanout success |
| Request/reply | Operation identity + reply correlation + deadline + observation | Late/duplicate replies and uncertain timeout remain meaningful |
| Event-sourced aggregate | Append + expected version + retained history + pure transition | Conflict arbitration and compatible reconstruction basis |
| CQRS projection | Write owner + event/change feed + read model + checkpoint | Read coverage/lag and a separately specified consistency expectation |
| CDC/outbox relay | Local transaction + recorded intent + extraction + publication | Storage/change-feed guarantees and duplicate relay recovery |
| Actor protocol | Mailbox + serialized local state + typed messages | Supervision, persistence and remote effects are separate choices |
| Reactive processing | Demand + buffer + transformations + terminal observation | Count/byte bounds and cancellation, not necessarily durable progress |
| Saga | Local commits + coordinator/choreography + compensation intents | Partial completion, competing decisions and non-invertible compensation |
| Durable workflow | Recorded decisions + timers + activity intents + replay | Deterministic history interpretation and retry-safe external participants |

For ordinary in-process transformation, prefer an ordinary function or bounded
channel. For reconstructable state, demand retained history and an edition-bound
reducer. For effects across owners, demand explicit reconciliation/compensation;
do not add event sourcing merely to make a small CRUD application look uniform.
An adapter profile must reject unsupported operations rather than silently
downgrade durability, ordering or settlement to a lowest common denominator.

## Guarantees Are Scoped Vectors

Replace one `reliable=true` flag with declared facts:

```text
delivery domain and attempts
ordering key/partition and consumption versus completion order
durability acknowledgment point and failure assumptions
settlement/checkpoint owner and atomic participants
deduplication identity, payload policy, retention and retry horizon
resource bounds, overflow, cancellation and recovery evidence
```

Kafka's transactions can coordinate records and consumer positions inside
their declared Kafka scope; an external sink needs a cooperating commit
protocol. Classic partition/group behavior is not a universal work-distribution
API: 4.1 also describes share groups. Compaction preserves selected keyed
state rather than every intermediate event; replay requires an explicit retained
basis. A committed position alone does not establish an external effect.
[Kafka design](https://kafka.apache.org/41/design/design/).

RabbitMQ confirms concern publisher/broker communication; consumer acks concern
broker/consumer communication. Prefetch limits outstanding delivery count, not
every application's queues and payload bytes. [Acknowledgment contract](https://www.rabbitmq.com/docs/confirms).

For Nomi, `ExactlyOnce` without participants, identity scope, retention and
failure assumptions should be an incomplete contract, not a convenient default.
This is our design inference from the sources, not a denial of their scoped
guarantees. At-least-once also needs stated availability/retention assumptions;
it cannot promise infinite progress through permanent outage or deletion.

## Normal Forms And Architecture Composition

**Consumption long form:** receive a delivery; strictly decode; select a
transition; enforce current ownership; atomically commit the declared local
state/inbox/outbox facts; only then settle delivery. On uncertain commit or
settlement, reconcile the same operation rather than invent a fresh ID.

**Publication long form:** prepare a schema-bound immutable envelope; acquire
the permitted producer; send; observe broker acceptance, explicit rejection or
unknown outcome. A timeout is not proof of rejection. Business completion needs
a separately correlated result with its own authenticity and timing policy.

**Projection long form:** read retained history under a pinned decoder/reducer
edition; fold pure transitions; checkpoint state together with its consumed
basis; expose coverage and lag. A replay-only rebuild must not send notifications.
Changed reducer/schema editions invalidate an incompatible snapshot basis.

**Outbox/inbox:** local business state + outbound intent can share a database
transaction; relay may publish again after lost confirmation. An inbox marker
and local effect must commit together for local deduplication. Checking a marker,
doing a remote effect and then recording the marker still has a crash window.
The external participant needs its own idempotency/reconciliation contract.
[Outbox evidence](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html).

**Saga/durable workflow:** compose local decisions, intents, timeouts, receipts
and compensations; keep unknown effects unresolved until observed/reconciled.
History reconstruction, retrying a task, redriving a message and compensating an
action are separate operations. Do not replay captured credentials or old grants.
[Saga mechanism](https://learn.microsoft.com/en-us/azure/architecture/patterns/saga),
[workflow tasks](https://docs.temporal.io/tasks).

The target fixture contains a beginner pure event fold, a production one-delivery
inbox/outbox path, and failure-heavy publication/reconciliation. All `lab.*`
signatures are proposals. A consumer scope releases a handle; `with` never
silently calls a handler repeatedly. A long-running loop uses ordinary explicit
iteration/suspension and a scoped task owner once D1/D2 are closed.

## Function Names And Cognitive Boundaries

| Verb | Visible contract | Avoid conflating with |
| --- | --- | --- |
| `publish` / `send` / `append` | Route a publication / address a recipient / extend a log | One undifferentiated write guarantee |
| `subscribe` / `receive` | Establish interest/consumer state / obtain an attempt | Execute a callback or complete work |
| `acknowledge` / `commit_position` / `checkpoint` | Settle a receipt / advance progress / persist state with basis | Domain effect or a global offset |
| `project` / `replay` / `redrive` | Derive a view / reconstruct under a history basis / resubmit work | Permission to resend all side effects |
| `retry` / `reconcile` / `compensate` | Try again under policy / resolve uncertainty / request a counter-action | Universal undo |
| `drain` / `close` / `cancel` | Finish admitted work / release a resource / request task cessation | Empty backlog, remote rejection or durable completion |

This extends [text API naming](../dsls/text_as_interface.md) and
[PowerShell](../languages/powershell.md) with architecture-specific nouns and
effects. Equal verb names need not hide unequal completion contracts. Correlation
IDs, entity IDs, event IDs, receipt handles, attempts and offsets remain distinct.
CloudEvents scopes event uniqueness by source and ID; that pair is not an
authenticated business-operation key. [Envelope specification](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md).

## Edge Cases And Falsifiers

| Case | Trigger / distinction | Failure that rejects a candidate |
| --- | --- | --- |
| ME01 | Effect commits, ack is lost | Retrying creates a second business effect |
| ME02 | Ack/offset precedes durable effect | Crash silently loses work |
| ME03 | Dedup check and effect are separate | Crash or two workers pass the check and both act |
| ME04 | Lease expires/rebalance assigns a new owner | Old owner commits without owner-enforced fencing |
| ME05 | Later offset completes before an earlier one | Max-completed commit skips an unresolved delivered record |
| ME06 | Different partitions contain noncommuting transitions | Implementation invents a global order |
| ME07 | An event arrives after the reported watermark | An estimate is rendered as proof no correction can occur |
| ME08 | Envelope validates but payload version changes | Schema parse is treated as domain decode or semantic compatibility |
| ME09 | Retention/compaction removes required records | Rebuild silently substitutes latest or claims full historical coverage |
| ME10 | Retry outlives dedup retention | A short dedup window is advertised as lifetime idempotence |
| ME11 | Same source/ID carries a different payload | Suppression hides a conflict or mutation |
| ME12 | Two sources reuse the same local ID | Global ID-only dedup drops an unrelated occurrence |
| ME13 | DLQ captures credentials/personal payload; later redrive | Debug inspection leaks data or old authority is replayed |
| ME14 | Local cancellation follows remote acceptance | Stop is reported as no-action and a new operation is sent |
| ME15 | Worker limit is finite but prefetch/fanout/bytes are not | Memory still grows without bound |
| ME16 | Two bounded feedback channels both block on send | Boundedness is mistaken for deadlock freedom/fairness |
| ME17 | Poison event blocks strict order; DLQ skips it | Claimed ordered state progresses across an unexplained hole |
| ME18 | One fanout target succeeds, another fails | One success bit says all business consumers completed |
| ME19 | Outbox relay crashes after acceptance before marking sent | Atomic local intent is mistaken for single publication |
| ME20 | A previously allowed command is replayed after revocation | Event history recreates an execution grant |
| ME21 | Untrusted correlation/trace metadata selects tenant/entity | Observation metadata becomes authorization or business identity |
| ME22 | A retry storm moves load across topics/services | Per-handler retry bounds hide unbounded global amplification |
| ME23 | Snapshot uses another reducer edition/epoch | Position equality is mistaken for compatible reconstructed state |
| ME24 | Append-only history conflicts with erasure/expiry policy | Retention hides payload copies, snapshots or downstream projections |

For ME05, a frontier is over the adapter's *delivered obligations*, not every
integer in a physical log. Compaction, isolation and control records can create
numeric gaps. Never repair max-offset commits by assuming all integer offsets
must exist. For ME04, a number copied into a message is not fencing: the store
must reject old ownership at commit, and every protected participant must honor it.

## Diagnostics, Views And Philosophy

Candidate diagnostics identify operation, endpoint/profile, ownership epoch,
position units, known commit facts and next permissible repair. Examples:
`Position p0:12 cannot commit: delivered p0:11 is unresolved`;
`Old owner epoch 7 cannot commit under epoch 8`;
`History before this checkpoint is unavailable`;
`Publication may have succeeded; reconcile operation K before retry`.
These are proposed human/machine records, not new runtime codes. Keep source
spans only when known; redact payloads and credentials in diagnostics/DLQ views.

A topology diagram, schema document and lag dashboard are derived views, not
execution authority. Show separate received/processed/settled frontiers, units,
retained basis and observation time. A diagram edge cannot promise fairness,
delivery, atomically shared state or an authorized repair.

[Leibniz, Boole and Dijkstra](../cognition.md) motivate practical obligations:
name distinct concepts rather than compress them into one word; separate a
predicate over known facts from unknown observations; state invariants before
every commit/ack and distinguish safety from eventual progress. A verified
local transition does not prove a distributed system meets its failure model.
This is a design translation, not historical endorsement or a universal logic
for all institutions and machines.

## Bounded Experiments And Admission

| Experiment | Credible fork | Discriminator / owner |
| --- | --- | --- |
| MSG1 | Shared delivery interface versus carrier-specific adapters | Queue receipt, log position and ephemeral callback; reject unsupported settlement/order promises; DC1/DC6 |
| MSG2 | Per-record settlement versus partition frontier | Out-of-order completion, numeric holes, rebalance and strict-order poison events; D2 |
| MSG3 | Local inbox/outbox versus external transactional/idempotent participant | Every crash cut, conflicting key/payload, dedup expiry and lost responses; D2/DC5 |
| MSG4 | Handler callback versus explicit receive/transition/commit loop | Effects, retained handles, cancellation, count/byte/queued budgets and deadlock trace; D1/D2 |
| MSG5 | Replayable pure projection versus effectful durable workflow | Reducer/schema edition, retained history, late correction and no unintended external effects; D3/DT/DC1 |
| MSG6 | Declarative portable profile versus broker-specific verified feature set | Pinned broker/adapter negative vectors, explain without run, current grants and repair projections; D4/D7/DC6 |

[The local capture](messaging_probe_results.json) executes only original finite
subcases, not MSG1-MSG6 in full. It has no network, broker, Nomi checker, real
leases, durable transaction, authenticated grant or asynchronous scheduler.
Reproduce the ten captured finite countermodels:

```bash
python3 docs/research/data_workflows/probe_messaging.py --check docs/research/data_workflows/messaging_probe_results.json
```

Next: close D1-D3, type the three target programs, then choose **one** real
adapter profile and test crash/recovery/settlement with independent fixtures.
No universal broker API or new syntax is accepted. Admission must name identity,
ordering, completion, budgets, codecs, current authority, diagnostics, inspection,
removal criteria and unsupported features. Delete a wrapper that only renames
Kafka/RabbitMQ operations while concealing these facts. Broader architecture
families enter through this same contract discipline, not core-feature accumulation.
