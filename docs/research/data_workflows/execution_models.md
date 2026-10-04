# Execution And Workflow Models

> Status: comparative evidence and candidate architecture; no runtime commitment.

[Dossier](README.md) · [Source](source_forms.md) · [Synthesis](nomi_candidates.md)

The [2026-10-04 dependency/time continuation](dependencies_and_time.md) deepens
graph ownership, partial ordering, bitemporal questions, retained snapshots and
change algebras. [AI/ML](ai_ml.md) separates computation/transformation graphs,
state and checkpoint meanings. The mechanisms below retain their original
survey date; neither continuation makes this a complete framework audit.

## Similar Source, Different Lifetimes

| Object the user constructs | Meaning of a connection | Execution boundary | Identity / invalidation | Not interchangeable with |
| --- | --- | --- | --- | --- |
| Strict list calculation | Output value passed to next ordinary call. | The call evaluates now. | Value / explicit mutation. | Query plan or task graph. |
| Table expression | Relational dependencies under a schema. | Explicit engine operation, subject to preview policy. | Schema, source snapshot, plan and backend semantics. | Arbitrary callback. |
| Fitted model pipeline | Transformer's learned output feeds the estimator. | Separate fit, transform and predict. | Training data/split, parameters, feature schema. | Stateless query. |
| Task graph | Dependency availability enables a task. | Scheduler/runner starts graph nodes. | Graph node, inputs, code, environment. | Semantic asset identity. |
| Asset graph | A persistent data product derives from other products. | Materialization of a partition/version. | Asset key, partition, materialization, provenance. | A worker attempt. |
| Durable workflow | Recorded commands/events advance a long-lived execution. | Replay-aware service execution. | Workflow/run/history and compatible code. | A lexical cold task. |
| Stream computation | Events advance state in windows/epochs. | Subscription/runner with progress rules. | Event time, offsets, watermarks and state version. | Daily batch or a finite DAG. |
| Recursive relation | Derived facts contribute to a fixed point. | Evaluation until a declared closure/progress condition. | Relation version and update law. | Topologically ordered one-shot graph. |

This is an original classification, not a universal taxonomy imposed by the
surveyed projects. Frameworks span rows. Each boundary needs a separate contract.

## Workflow Source Forms And Critiques

| System / primary source | Form humans author | Strength to extract | Risk / Nomi synthesis |
| --- | --- | --- | --- |
| [Airflow DAGs](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html) / [TaskFlow](https://airflow.apache.org/docs/apache-airflow/stable/tutorial/taskflow.html) | `@dag`, `@task`, `a >> b`, decorated calls wiring XCom arguments. | Scheduling, dependency and run/data-interval concepts. | Graph-building calls aren't ordinary result-returning calls; `>>` orders work, doesn't itself carry a table. Keep construction inert and phases visible. |
| [Prefect flows](https://docs.prefect.io/v3/concepts/flows) / [tasks](https://docs.prefect.io/v3/concepts/tasks) | `@flow`, `@task`, direct call, `.submit()`, `.delay()`. | Runtime control flow with explicit task submission routes. | Direct, submitted and background calls differ; cannot promise a complete static graph. Distinguish result, scoped handle, durable request. |
| [Dagster assets](https://docs.dagster.io/guides/build/assets/defining-assets) / [partitions](https://docs.dagster.io/guides/build/partitions-and-backfills/partitioning-assets) | `@asset`, input dependency names, partition definitions. | Data products and partitioned materializations as first-class user concepts. | Asset key alone isn't immutable content/version identity; code version is separate. Keep semantic key versus materialization versus attempt distinct. |
| [Luigi](https://luigi.readthedocs.io/en/stable/tasks.html) | `requires()`, `output()`, `run()`, `complete()`. | Requirements and completion evidence are inspectable methods. | File existence can be weak evidence; dynamic dependency yield restarts `run`. Require idempotency and a stronger completion record when needed. |
| [Kedro](https://docs.kedro.org/en/stable/build/nodes/) | `node(fn, inputs="sales", outputs="totals")`, pipeline/catalog. | Separate pure-ish transformation, named ports and storage adapters. | String port names need schema/refactoring support; catalog is a boundary, not global semantic authority. |
| [R targets](https://books.ropensci.org/targets/walkthrough.html) / [branching](https://books.ropensci.org/targets/dynamic.html) | `list(tar_target(sales, read_sales()), tar_target(total, sum(sales)))`. | Code/data-aware incremental builds and inspectable dynamic branches. | Quoted commands and ambient dependencies complicate evidence; `pattern=map(...)` isn't eager list `map`. |
| [Nextflow process](https://docs.seqera.io/nextflow/process) / [workflow](https://docs.seqera.io/nextflow/workflow) | `process` input/output/script; `workflow` take/main/emit; channels. | Tool staging and dataflow composition across external programs. | Channels, paths and process calls introduce another execution algebra; pairing by identity must not be replaced by arrival order. |
| [Snakemake](https://snakemake.readthedocs.io/en/stable/snakefiles/rules.html) | `rule` input/output/wildcards/shell; request desired output. | Backward derivation from artifacts and concrete tool invocations. | Path templates can become accidental domain identity; shell interpolation has an additional parser and authority boundary. |
| [CWL v1.2](https://www.commonwl.org/v1.2/Workflow.html) | YAML workflow inputs, steps, outputs, scatter and conditions. | Portable explicit workflow/tool descriptions. | Machine interchange verbosity shouldn't dictate hand-written Nomi; runner capability and actual tool behavior remain separate. |
| [WDL](https://openwdl.org/spec) | Typed workflow/task/call, scatter, command and outputs. | Typed orchestration around command-line programs. | Interpolation and executor behavior need edition/profile fences; don't transplant task blocks into general control flow. |
| [dbt ref](https://docs.getdbt.com/reference/dbt-jinja-functions/ref) / [incremental](https://docs.getdbt.com/docs/build/incremental-models) | SQL plus Jinja `{{ ref("sales") }}` and materialization config. | Dependency-linked relational models and inspectable compiled SQL. | Template control flow can hide dependencies; incremental cutoffs can miss late corrections. Preserve source and expanded plan. |
| [GNU Make](https://www.gnu.org/software/make/manual/html_node/How-Make-Works.html) | `target: prerequisites` and recipe. | Small dependency-driven update interface. | Timestamp freshness isn't universal content freshness; task/environment effects need more evidence than recipe text. |
| [Temporal](https://docs.temporal.io/workflow-execution) | SDK workflow definitions executed against event history. | Long-lived execution and replay as explicit machinery. | Replay constraints differ from ordinary async; external side effects cannot be made exactly-once by syntax. |
| [Apache Beam](https://beam.apache.org/documentation/programming-guide/) | PCollection/PTransform, windows, triggers, runner. | Event-time/window/progress model across runners. | Late events, pane emission and stateful work aren't a finite list pipeline; report correction policy explicitly. |

An Airflow decorated task call wires a graph proxy; a Prefect task called
directly executes and returns a result, while submission returns a future.
Both look like Python functions. This is decisive evidence **against** assigning
workflow construction semantics to every Nomi function-call chain.
[Airflow TaskFlow](https://airflow.apache.org/docs/apache-airflow/stable/tutorial/taskflow.html),
[Prefect tasks](https://docs.prefect.io/v3/concepts/tasks).

### A Complete Small Shape: Same Call, Different Phase

Original illustrative modules, not executed framework fixtures:

```python
# Airflow 3.x: calls inside build_report describe dependencies.
from airflow.sdk import dag, task

@dag(schedule=None)
def build_report():
    @task
    def load():
        return [2, 3]

    @task
    def total(values):
        return sum(values)

    total(load())

report_dag = build_report()
```

```python
# Prefect v3: direct task calls execute during the flow run.
from prefect import flow, task

@task
def load():
    return [2, 3]

@task
def total(values):
    return sum(values)

@flow
def run_report():
    return total(load())
```

The Nomi challenger is not a third decorator spell: an inert `WorkflowSpec`
constructed from declared input/output ports versus a normal function that runs
now. Require `build`, `inspect` and `run` to remain distinguishable in inspection.
Graph construction may use pure ordinary helper functions; execution authority
must not become available merely because a helper constructs a description.

### Artifacts Versus Values

```snakemake
# Assumes a separately supplied sales-total command; not an installed fixture.
rule total:
    input: "sales.csv"
    output: "totals.csv"
    shell: "sales-total {input:q} > {output:q}"
```

This shape gives the runner artifact dependencies and a host-shell recipe.
It does not make CSV schema, table key policy or the command's external effects
visible. Kedro's named ports put dataset identity at a different layer; CWL/WDL
make tool inputs/outputs explicit in a description language. Nomi should compare
those layers, not promote shell strings to the meaning of a typed transformation.
Sources: [Snakemake rules](https://snakemake.readthedocs.io/en/stable/snakefiles/rules.html),
[Kedro nodes](https://docs.kedro.org/en/stable/build/nodes/),
[CWL workflows](https://www.commonwl.org/v1.2/Workflow.html),
[WDL specification](https://openwdl.org/spec).

## A Layered Design, With Replaceable Engines

Candidate separation for Nomi, not a new mandatory Core IR:

```text
human forms: source, named steps, table / graph / tensor / evidence views
  -> domain contracts: schemas, keys, units, partitions, learned state
  -> typed descriptions: expressions, ports, dependencies, operation intent
  -> validation: binding, shape, null/key laws, effects, runtime grants
  -> planning: optimizations, physical operations, source mapping
  -> execution adapters: Python / Rust / WASM / SQL / scheduler / external tool
  -> evidence: outputs, errors, provenance, observations, attempt history
```

Each layer can reject a description without running it. Inspection is not
authorization. An adapter can optimize a lower layer without making the first
user-facing layers unreadable. A plan should not capture a live resource or
secret simply because it is easier to serialize a closure than name an input.

| Owner | Required contract | Example rejection |
| --- | --- | --- |
| Domain decoder | Valid entities, key policy, accumulated path errors. | `payments[3].order_id: duplicate key A`. |
| Expression model | Bound schema names, operator types and shape. | Column `amount` belongs to schema revision 4, not revision 5. |
| Logical planner | Declared null/order/arithmetic laws, lawful rewrites. | Reassociation changes checked-overflow behavior. |
| Capability boundary | Static requirements and fresh runtime authorization. | Network grant absent at publish, regardless of cached plan. |
| Runner | Start/cancel/retry/cleanup policy, limits and task outcomes. | Cancel during cleanup cannot erase the primary failure. |
| Artifact store | Integrity, snapshot identity and publication visibility. | Successful upload isn't proof of completed publication record. |
| Observation view | Revision/run/epoch identity and stale-state rendering. | Last run's graph result must not attach to edited source. |

These ownership claims must become independent contracts before code is wired.
They are not solved by choosing an existing workflow framework.

## Identity Is The Hard Part Of Incrementality

Candidate computation key:

```text
operation version + normalized parameters + input snapshot identities
+ relevant environment/backend semantics + explicit randomness policy
```

This is not a complete recipe for reproducibility: unrecorded remote state,
wall-clock reads, nondeterminism, secrets and floating-point behavior may matter.
Content hashing protects against some stale inputs; it doesn't grant authority
or make a remote effect repeatable. Keep domain ID, plan ID, artifact ID,
partition ID, attempt ID and observation epoch separate in the UI.

For invoice publication, define a domain operation key, record pending intent,
send using an external service's idempotency mechanism where available, and
reconcile acknowledgment/history. A crash between send and record requires an
explicit uncertain state. Without support at the external boundary, no retry
combinator can honestly promise exactly-once delivery. This is a Nomi candidate
protocol, not a reported guarantee of Airflow, Temporal or Prefect.

## Research That Challenges The DAG Default

| Primary work | Mechanism supported by the evidence | Design pressure for Nomi |
| --- | --- | --- |
| [Build Systems A La Carte](https://www.microsoft.com/en-us/research/publication/build-systems-la-carte/) | Build systems can be analyzed compositionally rather than as one monolithic tool choice. | Separate dependency scheduling from freshness/rebuild policy; test each law. |
| [Differential Dataflow, 2013](https://www.microsoft.com/en-us/research/wp-content/uploads/2013/01/differentialdataflow.pdf) | Incremental computation across nested iterations using structured changes. | Cycles and update propagation need more than a one-shot DAG. |
| [Naiad, 2013](https://www.microsoft.com/en-us/research/wp-content/uploads/2013/11/naiad_sosp2013.pdf) | Cyclic dataflow with logical timestamps and coordinated progress. | Time/progress are semantic state, not just scheduler diagnostics. |
| [DBSP, 2022 preprint](https://arxiv.org/abs/2203.16684) | An algebraic route to incremental view maintenance. | Define change algebra and equivalence before implementing reactive tables. |

This pass uses primary abstracts/selected mechanisms, not a replication of
performance claims or complete proof review. Research consequence: keep the
description format extensible enough for declared feedback/fixed points, but do
not make all user computations cyclic or incremental by default.

## Failure And Security Counterexamples

1. A cached computation containing yesterday's permission result must not
   bypass today's revoked grant.
2. A task that returns `Err` successfully is not a crashed worker; application
   retry must opt into retrying that error category.
3. A partially emitted stream isn't equivalent to a failed all-or-nothing batch.
4. An existing output file may be malformed, stale or from another environment.
5. A fitted preprocessing stage may be valid but trained on the wrong split.
6. A durable execution may replay but have incompatible new workflow code.
7. A graph inspector may render secret metadata even though no node executes.
8. A corrected source event may require retraction, not another additive total.

Each counterexample belongs in the research experiments before a playground
demo promises a universal pipeline, cache, or replay model.
