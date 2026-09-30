# SQL

> Status: comparative evidence; scope is PostgreSQL table expressions.

## Observe

PostgreSQL table expressions compose sources, joins, filters, grouping, and
related clauses into a relational result. This is a domain model, not simply
iteration over a List of records.
[Primary reference: table expressions](https://www.postgresql.org/docs/current/queries-table-expressions.html).

## Judge And Pay

**Adopt** explicit relational plans and schema-aware operators. **Defer** SQL
surface syntax to a scoped tool, starting with ordinary typed plan calls.
**Reject** translating arbitrary Nomi callbacks to database expressions without
a declared subset and an inspectable plan.

Nomi's call form may make joins and aggregates less readable than SQL. It must
also name nullability, duplicate rows, ordering guarantees, and parameterization
rather than smuggling list assumptions into tables. A common verb vocabulary
does not imply one execution model or one set of laws.

## Test

Compare a left join with missing matches, duplicate keys, and an aggregate over
an empty group. Require a plan artifact, parameterized input, explicit nullable
output, and deliberate ordering. Measure readability before proposing query
grammar. See [collections](../features/collections.md),
[metaprogramming](../features/metaprogramming.md), and
[collections.nomi](../../design/targets/collections.nomi).
