# Data And Workflow Languages

> Status: cross-cutting research evidence, original survey checked 2026-09-30;
> selected data/time, AI/ML and messaging extension checked 2026-10-04;
> not syntax admission.

This dossier extends the [syntax atlas](../syntax_matrix.md) and the registered
[cognitive-interface packet](../interfaces/README.md). It compares the notation
people manipulate **and the execution model that makes that notation honest**.
The companion [notation atlas](../notation_atlas.md) goes beyond software into
mathematics, biology, chemistry, linguistics, music, and argumentation.

## Reading Route

1. [Source Forms](source_forms.md): literal spellings, names, masks, axes,
   formulas, mutability, and critiques of individual systems.
2. [Execution Models](execution_models.md): query versus model versus task,
   orchestration alternatives, incremental research, and ownership boundaries.
3. [Nomi Synthesis And Experiments](nomi_candidates.md): candidate APIs,
   syntax costs, bounded comparisons, diagnostics, and promotion gates.
4. [Research Targets](../../design/targets/research/README.md): independent
   category programs and a combined reconciliation fixture.
5. [Dependencies, Change And Time](dependencies_and_time.md): graph owners,
   ordering, incremental laws, snapshots, bitemporal history and DT1-DT5.
6. [AI And ML](ai_ml.md): numeric transformations, learned/training state,
   data splits, randomness, interchange, agents and ML1-ML6.
7. [Coherent Domain Layers](../domain_composition.md): shared foundations,
   selected domain families, package obligations and DC1-DC6.
8. [Local Composition Experiments](composition_experiments.md): captured
   original counterexamples and named graphlib/SQLite host observations.
9. [Messaging And Event-Driven Architectures](messaging_and_events.md): queues,
   pub/sub, logs, actors, outbox/inbox, projections, sagas and durable workflows;
   MSG1-MSG6, 24 adversarial cases and ten captured finite countermodels.

The live experiment order belongs to the synthesis, not to a second dated
backlog. Canonical [syntax](../../design/syntax.md),
[semantics](../../design/semantics.md), and
[function contracts](../../design/function_contracts.md) remain authoritative.

## Four Pressures, Not A Feature Shopping List

| Program | Human question | Adversarial input | Required observation |
| --- | --- | --- | --- |
| Sales reconciliation | Which eligible orders lack payments, and what is the unpaid amount per customer? | Duplicate payment keys; absent amount; reversed row order; late correction. | Key/cardinality policy, missing-value policy, stable report ordering, trace from result to input. |
| Scientific pipeline | Does the estimator generalize without learning from held-out data? | Temporal split, unseen category, missing measurement, stale fitted scaler. | Split identity, fit-only-on-training evidence, transform versus fit, axes/units, seed and environment. |
| Daily publication | Can yesterday be recomputed safely without sending invoices twice? | Worker crash after send but before acknowledgment; changed input; denied network capability. | Partition versus attempt identity, idempotency/reconciliation, authority checks, publication history. |
| Notation model | What can an overlap, contraction, or reaction drawing actually establish? | Unknown universe; swapped axes; unbalanced reaction; unversioned biological reference. | Explicit binding/context, valid model versus invalid model, explanation without execution. |

Illustrative arithmetic oracle: orders `(A, north, 2, 400)`,
`(B, south, 1, 700)`, `(C, north, 3, 200)` total 2100 minor units;
payment for A leaves unpaid north=600 and south=700. Payment duplicates must
not silently multiply A. This is a designed oracle, not an executed benchmark.

## Scope And Evidence

Coverage is mechanism-led. A framework can supply several mechanisms, and two
frameworks can use identical call syntax for different mechanisms. This dossier
does not add one new language-review file per library or replace the existing
45-language/13-feature matrices.

Official documentation, standards, and primary papers support foreign-system
claims next to each comparison. Original snippets demonstrate source shape;
they have **not** been executed against installed foreign systems. Nomi snippets
are aspirational: proposed `lab.*` APIs do not exist. Documentation checks do not
typecheck those snippets or establish usability.

Version fences matter: pandas indexing/CoW evidence is the 3.0 documentation;
Airflow examples use the 3.x `airflow.sdk` route; Prefect is v3; CWL evidence is
v1.2; WDL source forms are described without mixing editions into a claimed
portable implementation. Polars, Dask, Ibis, JAX, and other rolling documentation
was consulted on the date above, not treated as a pinned conformance suite.

## Extraction Template

For every attractive form record:

```text
relationship made visible
-> binding and identity
-> evaluation and authority boundary
-> laws and counterexample
-> explicit Nomi long form
-> library / scoped tool / core fork
-> diagnostic, projection, and falsifying experiment
```

Count more than tokens: names the reader must resolve, independent namespaces,
implicit axes, hidden state, phase changes, exceptional paths, and context
needed to interpret a line. A shorter expression can be a worse interface.

## Deliberate Non-Claims

- A DAG is not a complete model of streams, recursion, human approval, or
  durable replay.
- A pure callback is not automatically a translatable query expression.
- Arrow buffers are not the definition of a Nomi table.
- Caching is not reproducibility; successful retries are not exactly-once
  external side effects.
- A cell, port, file path, asset key, and domain entity are different identities.
- A graph projection is not permission to run the graph.
- No proposed query, tensor, workflow, or diagram syntax is accepted by this pass.

The synthesis must narrow these claims before an implementation is admitted.

## October Continuation

The requested broader pass starts with data and AI/ML, then tests extension to
web, CLI, visual tools, support, DevOps/cloud, design, databases, research,
mathematics, legal documents, scientific naming, cataloging and communication.
The domain map distinguishes selected reviewed mechanisms from discovery and
existing evidence; it does not claim comprehensive product or knowledge coverage.
The [canonical synthesis proposal](../../design/synthesis.md#domain-layer-proposal)
and [composition target](../../design/targets/research/domain_layers.nomi) stay
within the registered language-coherence packet. Existing D1-D3 contracts are
prerequisites; no domain keywords or universal evaluator are admitted.

The [messaging continuation](messaging_and_events.md) adds architectural
composition without turning transports into core keywords. Delivery ownership,
settlement, position, local atomicity, replay and current authority remain
separate. Its target-only programs and finite probes do not execute a broker or
durable workflow engine; one pinned adapter is a later independent admission gate.

The research-only gap continuation sharpens existing experiments:
[DT4 predicate consistency](dependencies_and_time.md#predicate-consistency-beyond-snapshots-and-row-guards),
[ML1 adaptive holdout feedback](ai_ml.md#adaptive-evaluation-feedback-is-also-a-dependency),
[ML4 learned influence removal](ai_ml.md#data-erasure-and-learned-influence-are-different-operations),
and [DW4 correlated uncertainty](../notation_atlas.md#correlated-uncertainty-shared-origin-is-part-of-the-model).
Snapshots and row guards do not by themselves protect a cross-row predicate;
train-only fitting does not erase evaluation feedback; deleting source data does
not erase a trained descendant; equal uncertainty summaries do not identify
independent measurements. Detailed candidate comparisons and representative
programs are unperformed. Earlier finite captures retain their original claims;
no database isolation guarantee, evaluation budget, removal algorithm or
uncertainty engine is selected.
