# Query And Search: Evidence Has A Domain

> Status: Nomi hypotheses grounded in relational evidence already reviewed.

## Evidence And Pressure

The [SQL review](../languages/sql.md) and
[collection comparison](../features/collections.md) own checked relational
mechanisms. Facets, pivot views, and ranked retrieval are additional interface
probes: each helps a person ask a question without spelling an execution loop.
They should not be treated as identical implementations of selection.

## Cognitive Distinctions

An exact query over a closed snapshot can return an empty set. A search system
may instead have incomplete coverage, a threshold, or uncertain ranking. "No
result" is not universally evidence that no matching object exists. Grouping,
ordering, duplicates, absence, and pagination also change what a displayed
table means. Nomi needs types and explanations for these distinctions before
a pleasant query notation can be judged coherent.

## Nomi Normal Form And Placement

Start with ordinary `filter`, `map`, and explicit aggregation on owned data.
A table-plan library may build a typed expression value, explain its schema
and execution strategy, then execute with a supplied capability. A retrieval
library should return coverage/provenance and ranking information appropriate
to its contract. Never make generic `|>` imply remote query execution.

**Adapt:** inspecting schema and intermediate relations, reusable named queries.
**Defer:** SQL-like scoped syntax pending joins, windows, and nullable boundary
cases. **Reject:** hidden network activity when inspecting a plan or treating
ranked model output as checked truth.

## Discriminating Experiment

Compare explicit calls and a plan builder for invoice grouping, missing-price
rows, duplicate IDs, and a remotely paginated dataset. Explain whether the
display is complete and when computation occurs. A playground table view should
display row count and snapshot identity; correctness precedes query brevity.
