# Dependencies, Change And Time

> Status: comparative research and candidate library contracts, not accepted
> syntax, a scheduler implementation or foreign-system conformance.
>
> Selected primary documentation checked 2026-10-04. Older evidence remains
> dated in [execution models](execution_models.md); this is not a refresh of
> every system in that dossier.

[Dossier](README.md) · [Existing candidates](nomi_candidates.md) ·
[AI/ML continuation](ai_ml.md) · [Cross-domain composition](../domain_composition.md)

## Start With A Program, Not A Universal DAG

Extend the daily-publication program: ingest orders and payments, produce a
reconciled daily report, train an estimator on historical features, and publish
an approved report. A late correction must support both questions:

1. What did we report using the information available then?
2. What would the report be for that same business date using corrected data?

Neither question should resend an invoice, retrain a model, reread a remote
source, or reuse an old permission merely because a graph is displayed.

A directed acyclic graph is an important **checked specialization**, not the
meaning of every computation. Ordinary Nomi calls still evaluate eagerly.
Dependencies are explicit values when a program wants planning, scheduling,
invalidation or explanation. A typed description can be fundamental to the
language ecosystem without every binding becoming a lazy/reactive graph node.

## Landscape: Which Mechanism Is Being Borrowed?

The following survey extends, rather than repeats, the fourteen orchestration
comparisons in [execution models](execution_models.md). Rows state a mechanism,
not a product endorsement, adoption ranking, or complete feature inventory.

| System / primary evidence | Mechanism to extract | What must remain separate |
| --- | --- | --- |
| [Airflow Dag](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html) | Task dependencies, runs and data intervals | Logical interval, actual run time and task result; ordering is not a table transformation |
| [Dagster dependencies](https://docs.dagster.io/dagster-basics-tutorial/dependencies) and [partitions](https://docs.dagster.io/examples/full-pipelines/etl-pipeline/partition-asset) | Named data assets and partitioned materializations | Asset identity, partition, content version and execution attempt |
| [Prefect v3 tasks](https://docs.prefect.io/v3/concepts/tasks) | Direct calls, explicit submission, retries and task state | Ordinary result, future and durable request; static graph versus runtime discovery |
| [Dask task graphs](https://docs.dask.org/en/stable/graphs.html) | Dependency descriptions consumed by schedulers | Graph optimization, execution policy, data identity and arbitrary Python effects |
| [Ray tasks](https://docs.ray.io/en/latest/ray-core/tasks.html) | Remote invocation and object-reference dependencies | Remote object handle versus portable snapshot; actor state versus pure task |
| [dbt `ref`](https://docs.getdbt.com/reference/dbt-jinja-functions/ref) | Resolve model references and record model dependencies | Compiled SQL, logical lineage, materialization strategy and late-data correction |
| [Temporal definition](https://docs.temporal.io/workflow-definition) | Compatible command replay against execution history | Workflow code, nondeterministic activity results and external side-effect outcome |
| [Flink event time](https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/time/) | Event-time processing and watermark progress | Event time, processing time, late-event policy and business validity |
| [Flink fault tolerance](https://nightlies.apache.org/flink/flink-docs-stable/docs/learn-flink/fault_tolerance/) | Coordinated state checkpoints plus replay | Managed state consistency versus delivery to a sink with its own protocol |
| [Iceberg branching/tagging](https://iceberg.apache.org/docs/latest/branching/) | Named snapshot references and retention policies | Branch/tag name, snapshot ID and availability; not generic row-level merge |
| [Delta historical reads](https://docs.delta.io/delta-batch/) | Table version/timestamp selection with log and data-file retention | Version identity, wall-clock lookup and physical retention |
| [Datomic filters](https://docs.datomic.com/reference/filters.html) | Immutable database values; `as-of`, `since` and history views | Transaction basis versus domain valid time; a history view is not a current entity view |
| [XTDB temporal queries](https://docs.xtdb.com/reference/main/sql/queries) | Independent valid-time and system-time query filters | When a fact applies versus when the system knew it |
| [Dolt merges](https://www.dolthub.com/docs/sql-reference/version-control/merges/) | Database branching and schema/data merge | Merge resolution versus rechecking uniqueness and foreign-key constraints |
| [Materialize optimization](https://materialize.com/docs/transform-data/optimization/) | Incrementally maintained query results/indexes | Incremental query state versus workflow retry or archived source history |
| [OpenLineage object model](https://openlineage.io/docs/spec/object-model/) | Dataset/job/run entities and extensible facets | Reported lineage versus verified completeness, authorization or reproducibility |

Airflow's current documentation explicitly describes its Dag as more than the
mathematical data structure. Delta requires both the log and backing files for
an older version; its timestamp lookup can change when a table directory is
copied even when version lookup survives. These are reasons to expose precise
domain contracts instead of promise a generic `time_travel(timestamp)`.
[Airflow](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html),
[Delta versions and retention](https://docs.delta.io/delta-batch/#query-an-older-snapshot-of-a-table-time-travel).

Flink's documented exactly-once state guarantee is not a claim that an event is
processed only once. End-to-end guarantees additionally require replayable
sources and transactional or idempotent sinks. The retained distinction is
managed-state recovery versus the actual external protocol, not a rejection of
useful exactly-once guarantees under stated conditions.
[Flink scope](https://nightlies.apache.org/flink/flink-docs-stable/docs/learn-flink/fault_tolerance/#exactly-once-end-to-end).

## Seven Graphs Can Share A Drawing Without Sharing Laws

| Graph | Node | Edge | Law / diagnostic |
| --- | --- | --- | --- |
| Task dependency | Work description | Completion enables readiness under a declared outcome policy | A cycle blocks a one-shot schedule; readiness does not grant permission |
| Asset lineage | Data product or materialization | Derivation from another product/version | A dependency must identify the relevant partition/version, not just its label |
| Relational plan | Typed operator | Data dependence under schema/cardinality/null rules | Rewrites must preserve the engine's declared bag/order/error semantics |
| Provenance | Entity/activity/agent evidence | Used, generated or attributed relationship | Observed lineage can be partial; it need not contain every dependency |
| Stream/dataflow | Operator state | Events and progress | Feedback needs time/progress/state laws; no ordinary topological order suffices |
| Recursive relation | Facts/rules | Derivation, including recursion | A declared bounded positive fragment can reach a fixed point; arbitrary recursion need not terminate |
| ML computation | Numeric operation/state | Value/cotangent dependence | Reverse accumulation follows derivative rules, not generic workflow completion |

The first six rows are a Nomi classification drawn from the sources above and
the primary [incremental-computation comparisons](execution_models.md#research-that-challenges-the-dag-default).
The ML row is developed in [AI/ML](ai_ml.md). A graph viewer can reuse selection,
layout and source navigation; an executor cannot erase these edge distinctions.

Candidate long form, with fictional library APIs:

```nomi
spec = dependencies.describe(nodes=steps, edges=prerequisites)?
dag = dependencies.require_acyclic(spec)?
preview = workflows.explain(dag, inputs=snapshots, policy=policy)?
# No run, file read, network request or capability grant above.
```

`require_acyclic` owns a cycle diagnostic with node/edge identities and related
source spans. Do not use acyclicity of a lineage projection to certify a task
schedule, or reject every recursive relation because its drawing contains a
cycle. Descriptions with feedback must enter a different checked owner.

## Ordering Is A Partial Order, Not A Secret Serial Program

For a diamond `source -> {left, right} -> join`, both sibling orders are valid.
If the siblings write the same resource, the DAG alone does not make either
interleaving safe. A graph checker needs separate resource/effect conflicts,
declared serialization, or a domain transaction protocol.

Candidate scheduler facts:

- `get_ready` means dependencies satisfied under a policy, not started or done.
- Outcome policy states whether success, any terminal outcome, or selected
  alternatives enable a downstream node. Failure and skipped/blocked differ.
- Capacity, fairness, priority, deadlines and backpressure are independent of
  dependency validity; an acyclic graph can still starve or exhaust memory.
- A deterministic tie-break aids repeatability but must not become an
  undocumented dependency or guarantee identical floating-point reductions.
- Dynamic discovery produces a versioned expansion with limits and provenance;
  an earlier preview must label what it did not yet know.
- A returned domain `Err` differs from a worker crash. Retrying it is an
  explicit policy, not the definition of task completion.

Python's `graphlib.TopologicalSorter` exposes readiness and `done`, and detects
cycles. It supplies the algorithm in the local probe; the probe does not build
a competing scheduler or claim distributed execution.
[Primary API](https://docs.python.org/3/library/graphlib.html).

## Time Travel Has Several Independent Meanings

| Operation | Question answered | Required context | It does not do |
| --- | --- | --- | --- |
| Snapshot read | What value belonged to version V? | Store/incarnation, version, schema/codec and retained content | Undo effects or reconstruct deleted files |
| System-time query | What had the system recorded by time S? | Transaction basis and history | Establish when a fact was true in the world |
| Valid-time query | What applies to business time T? | Domain interval/clock and correction rules | Establish what the system knew then |
| Bitemporal query | What applied at T, as known at S? | Both bases and explicit interval boundaries | Eliminate uncertain/incorrect source facts |
| Replay | How does compatible code reconstruct recorded progress? | History, code compatibility and replay-safe operations | Reinvoke every external action safely |
| Backfill/recompute | What would new execution produce for old partitions? | Input versions, code/profile and fresh authority | Preserve the original report by default |
| Restore/branch | What new history begins from old state? | New branch/revision identity and revalidated constraints | Make stale commands or approvals current again |
| Compensation | What new action mitigates a prior external action? | Domain protocol, current state and authority | Turn a sent message into an unsent message |
| Debugging history | What recorded state explains a run? | Observation coverage, redaction and truncation | Prove unobserved state or roll back the world |

These are proposed Nomi operation boundaries, not shared APIs exported by all
surveyed frameworks. Datomic's time filters concern transaction history; XTDB
expressly separates valid and system time; Temporal replay requires compatible
deterministic command behavior. A library can compose these facts without one
global time coordinate or automatic versioning of every value.
[Datomic](https://docs.datomic.com/reference/filters.html),
[XTDB](https://docs.xtdb.com/reference/main/sql/queries),
[Temporal](https://docs.temporal.io/workflow-definition).

### A Concrete Correction Oracle

Original fixture, integer times in two deliberately separate domains:

```text
amount=100 valid=[10,20), known=[1,3)
amount=120 valid=[10,20), known=[3, infinity)
```

At business time 15, the answer as known at system time 2 is 100; as known at
time 4 it is 120. At business time 20 neither record applies. Half-open bounds
avoid double-counting at adjacency. Unknown, absent, redacted and expired
history remain distinct possible results; these two rows are not a general
bitemporal database design.

A snapshot manifest for several sources also needs an explicit consistency
claim: individually pinned orders V7 and payments V9 need not belong to one
atomic database cut. Record a shared transaction basis when available, or name
independent snapshots and the reconciliation assumption. Timestamp equality
alone does not establish causal or transactional consistency.

### Predicate Consistency: Beyond Snapshots And Row Guards

> Research-depth extension checked 2026-10-04; named subexperiment
> **DT4 / predicate-commit**, also refining DT2/DT3 and question 8. Not a new
> transaction API, isolation default or implemented concurrency guarantee.

The preceding consistency claim concerns **what was read**. The stale-edit and
merged-constraint cases below concern **what may be published**. The
[interaction proposal](../../design/interaction_model.md#context-and-evidence-pressure)
already requires an owner-enforced base and names read-set completeness. The
missing discriminator is the scope of that base: validating a row revision is
not necessarily validating a predicate over a collection, including absent rows.
A whole-model revision guard can be sufficient under its single-owner contract;
we must not silently weaken it into unrelated row guards at a database adapter.

Selected primary evidence: PostgreSQL **18** distinguishes stable Repeatable
Read snapshots from Serializable execution. Its documented Repeatable Read
prevents phantom reads yet still permits serialization anomalies; therefore
"no phantoms observed" is not the same property as serializability. Serializable
transactions can abort and require a whole-transaction retry. This is one
engine's edition-specific contract, not a portable meaning inferred from an
isolation-level name. [Isolation semantics](https://www.postgresql.org/docs/18/transaction-iso.html).
Its ordinary `CHECK` constraints do not support general checks against other
table rows. A Nomi value constraint must not be advertised as a database-wide
invariant merely because it lowers to a check-looking expression.
[Constraint boundary](https://www.postgresql.org/docs/18/ddl-constraints.html#DDL-CONSTRAINTS-CHECK-CONSTRAINTS).

Original schedule, not an executed PostgreSQL fixture: a roster has two
responders, A and B, both available; the invariant is at least one available.

```text
T1 reads A=true@1, B=true@1; proposes A=false, guarded only by A@1
T2 reads A=true@1, B=true@1; proposes B=false, guarded only by B@1
T1 commits A=false@2; T2 commits B=false@2
both own-row guards passed; the committed roster violates the invariant
```

Each candidate passes a check against its original snapshot. The combination
does not. Rechecking that same captured snapshot immediately before commit
does not repair the missing atomic boundary. A second discriminator starts
with no overlapping reservation: two transactions find the range empty and
insert different reservation IDs for overlapping times. The read dependency
includes the **absence of matching rows**, not just IDs returned by the query.
This is a predicate/insert countermodel, not a claim that every snapshot engine
allows a repeated query to see new rows.

**Candidate Nomi contracts**, library/protocol first; none is selected:

| Candidate | Meaning and benefit | Cost / falsifier |
| --- | --- | --- |
| Serialized aggregate owner or complete aggregate revision guard | Check and publish one invariant-bearing model under one owner/base | Too coarse for unrelated writes; fails if a bypass writer or external participant escapes that owner |
| Explicit read/predicate dependency validation | Commit validates declared rows, ranges, absence and semantic context in the same protected boundary | An incomplete read set, changed query meaning or check-then-write gap makes the guarantee false |
| Engine-owned transaction profile | Adapter requires a verified isolation/invariant contract and returns conflict/abort distinctly | A profile name alone is insufficient; distributed/external effects are not included unless the participants cooperate |

These alternatives need not force every operation into the strongest profile.
A read-only historical report may want a stable snapshot, while reserving shared
capacity needs a different contract. Locking, database constraints and optimistic
validation can be implementations of an obligation, not interchangeable words
for it. Serial order of database transactions also does not guarantee real-time
ordering across services, authorization freshness, fairness or external delivery.

Candidate normal form, **protocol metalanguage rather than accepted syntax**:

```text
declare invariant and atomic participants
-> acquire/read under named consistency profile and current authority
-> derive candidate plus its complete relevant read/predicate basis
-> validate and publish inside the owner's protected commit boundary
-> observe committed / conflict-or-abort / uncertain outcome
-> expose receipt or reconcile; retry only the permitted replay-safe work
```

Keep a speculative report or notification out of committed output until its
transaction outcome is known. A retry must not replay a send performed before
an abort. Current authority, unknown commit outcome and application `Err` remain
different facts; [messaging commit/settlement](messaging_and_events.md#normal-forms-and-architecture-composition)
owns the cooperating external protocol.

| Program / protocol | Required observations | Adversarial edge |
| --- | --- | --- |
| Beginner: change one immutable roster through one owner | Show base, invariant, proposed roster and committed revision | Two proposals share a base; at most one stale-base publication succeeds |
| Production: reserve a capacity/time range through a profiled store | Identify predicate/range, atomic participants, commit point and conflict outcome | Disjoint written IDs still overlap; an empty query result is a read dependency |
| Failure-heavy: reserve, then notify through recorded intent | Separate transaction abort, successful commit and lost response; show permissible reconciliation | A retry sends twice, publishes aborted evidence or uses an old authorization decision |

Inspection should show the guarded object and **property guaranteed**, not only
"transactional". A redacted predicate description may be necessary; inspection
does not execute the query or disclose protected matches. Candidate diagnostics
include `row revisions match, but predicate basis is not protected` and
`commit outcome unknown; reconcile operation K before selecting a new ID`.
Do not infer predicate completeness from declared purity or an acyclic graph.

**Falsifiers and stop/removal criteria:** enumerate the two schedules above,
same-row conflict, phantom insertion, irrelevant concurrent write, changed
predicate edition, bypass writer, aborted read-only result and uncertain commit.
Reject a generic wrapper if its protection cannot include the invariant's actual
scope; keep carrier-specific contracts instead. Reject retry convenience that
conceals side-effect multiplicity. Stop before API admission when the engine
profile, conflict taxonomy or protected participants are unspecified.

**Unperformed:** no concurrent engine test, model checker, predicate/read-set
inference, crash injection, typed contract, adapter or reader study has been run
for this subexperiment. The schedules are designed reasoning oracles, not new
captured results or closure of DT2-DT4.

## Incrementality Needs An Algebra And A Read Set

[Build Systems A La Carte](https://www.microsoft.com/en-us/research/publication/build-systems-la-carte/)
separates build-system concerns compositionally. The existing dossier's
[Differential Dataflow/Naiad/DBSP evidence](execution_models.md#research-that-challenges-the-dag-default)
adds changes, feedback and progress. This is selected mechanism evidence, not
a proof audit or replicated performance comparison.

Nomi candidates must separate:

1. **Scheduling:** when a dependent computation is eligible.
2. **Freshness:** whether the recorded result is usable for these inputs/code.
3. **Change propagation:** how an update becomes a new result.
4. **Commit/publication:** when a candidate becomes visible and durable.
5. **Authorization:** whether the current operation may read/write now.

For additive aggregates, signed changes can maintain a sum. For `min`, deleting
the current minimum requires retained alternatives or recomputation; subtracting
the deleted value is meaningless. Joins require multiplicity/null/key laws.
Non-monotone negation needs completion/coordination assumptions. An update law
is a domain contract, not a universal `Delta[T]` implementation inferred from
the existence of `+` and `-`.

Cache-key candidates include resolved operation/version, parameters, all input
snapshots, schema/policies and relevant backend/environment/numeric semantics.
Declared purity does not establish that a read set is complete. Clocks, remote
state, secrets, nondeterminism and undeclared files invalidate naive reuse.
Keep authentication tokens out of keys/logs; do not retain authorization in a
cached result. Reusing secret-bearing content must obey current read policy.

## Proposed Data Primitives And Layers

The four layers are the existing [Nomi admission layers](../../design/README.md#surface-layers),
not a new stack of global syntax modes.

| Candidate | Existing core foundation | Initial owner | Promotion evidence needed |
| --- | --- | --- | --- |
| Nominal entity/version/partition references | Immutable `data`, equality, explicit decode | Ordinary library; no single universal ID | Rename/reset/branch/collision fixtures and scoped identity contract |
| Typed ports and dependency relations | Calls, typed values, Result | Library description/checker | Schema/edge-role/cycle diagnostics; no invocation during construction |
| Snapshot manifest and temporal basis | Owned values and explicit IO effects | Storage/history library | Missing retention, independent sources, schema evolution and fresh read grants |
| Plan/check/run boundary | Values, functions, effects, resources and tasks | Library/protocol; scoped plan tool if earned | No implicit callback quotation or live-handle serialization |
| Changes and commit receipts | Immutable candidates and explicit failure | Domain-specific update protocols | Update laws, atomic publication, conflict and uncertain completion |
| Provenance/evidence reference | Data plus diagnostic/inspection contracts | Shared envelope with domain-owned payload | Incomplete/redacted trace, authenticity and source-context distinctions |
| Feedback/progress | Explicit state and concurrency | Specialized dataflow/relational owner | Termination/progress/frontier/late-data laws; not ordinary DAG execution |

The possible core gap is **compositional contracts** for generics, callback
effects, retained regions and typed descriptions, already owned by D1-D3.
Adding `dag`, `asset`, `snapshot` or `as_of` keywords does not close that gap.
An integrated standard domain layer can be first-class in docs, tooling and
conformance while remaining an ordinary module with replaceable engines.

## Failure Cases That Must Shape The Design

| Case | Required distinction / response |
| --- | --- |
| Same asset label, different tenant/store/incarnation | Reject wrong owner; labels are not globally unique IDs |
| Recomputed partition, old approved payload | New result invalidates exact-payload approval; a broad policy grant is separate |
| Cache hit after privilege revocation | Fresh permission at use; do not reveal stored data or replay a grant |
| Historical schema differs from current decoder | Select source schema and explicit migration; retain migration provenance |
| History metadata survives but a backing file is gone | Typed unavailable/expired result; never silently read latest |
| Old state restored with repeated revision counter | New history context; stale edits stay stale |
| One task failed, sibling still emitting | Structured cancellation/join and partial-output policy; graph color is insufficient |
| Send completed but acknowledgement lost | Uncertain, reconcile through external protocol; no blind exactly-once claim |
| Late correction after a window was emitted | Explicit replacement/retraction/new pane policy, not silent append |
| Concurrent merge preserves rows but breaks a constraint | Recheck the merged candidate before publication |
| Empty graph or disconnected component | Validity, chosen outputs and execution scope are separate |
| Dynamic dependency reveals a cycle or unauthorized source | Validate expansion before newly enabled work; retain partial discovery evidence |
| Historic read violates present privacy policy | Retention is not permission; deletion/revocation can defeat reproducibility |
| Inspection could query a live catalog | Read captured facts or expose an explicit refresh effect; opening a view stays inert |

## Bounded Continuation

These IDs extend DW1-DW8 without changing their status. Original local models
are recorded separately in [composition probes](composition_experiments.md).

| ID | Comparison / oracle | Stop or promotion gate |
| --- | --- | --- |
| DT1 | Checked DAG wrapper versus unrestricted typed dependency relation; diamond, cycle and incompatible edge roles | Keep owners separate if lawful composition cannot be stated; no graph keyword |
| DT2 | Snapshot-only versus explicit bitemporal basis; correction oracle above, expired backing content and independent sources | Do not unify time types when questions differ; no implicit latest fallback |
| DT3 | Recompute versus domain-specific incremental update; sum insertion/deletion and deleted minimum | Admit only proven update laws under named fragment/retained-state assumptions |
| DT4 | Cache reuse and backfill with fake capability/publication records; changed inputs, revoked read/write and lost acknowledgement | Never conflate result availability, current authority, review and effect completion |
| DT5 | Calls versus one scoped workflow surface; beginner report, partitioned production report and failure-heavy publication | Close D1/D2 type/effect/lifetime contracts before engine or notation admission |

Next useful slice: type an inert two-input report description and its snapshot
manifest, then execute it through one fenced adapter with independent value,
error, source-map and authority fixtures. No new runnable sample until CLI and
browser capability profiles honestly execute or reject the same contract.
