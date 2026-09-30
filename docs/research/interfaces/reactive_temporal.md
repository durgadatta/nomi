# Reactive Interfaces: Recalculation Is Not Repetition

> Status: historical notebook evidence and Nomi temporal hypotheses.

## Evidence And Pressure

Observable's archived notebook-JavaScript documentation describes cell
dependencies and invalidation. This reference is to that dialect, not a claim
that every current Observable product shares its execution model.
[Archived cell contract](https://observablehq.github.io/documentation/cells/observable-javascript).

A cell interface makes experimentation incremental. Its risk is confusing a
dependency graph with a history of external actions. An old result may remain
visible after its inputs changed, or a harmless edit may repeat a costly action.
Nomi's current browser/notebook sessions are persistent prototype surfaces;
they do not establish the target reactive contract.

## Nomi Normal Form And Placement

Ordinary bindings stay eager and immutable. An explicit library/tool graph may
recompute pure nodes for a particular input epoch. Record dependencies, source
revision, host observations, cache status, and resource budgets. Effects require
an explicit execution action; invalidation alone is not authorization to retry.

A completed result belongs to its epoch. Newer editing does not rewrite the
history or allow a late response to commit against changed input. Cycles need
an explicit fixed-point or feedback contract; do not quietly iterate until a
number appears stable.

## Discriminating Experiment

Change an invoice quantity while a delayed import is running. Compare explicit
Run with pure-only automatic recomputation. Verify old results are identifiable,
late completions cannot replace current results, and no network request repeats
on inspection. Include cancellation, cache invalidation, and a cyclic dependency.
The proposed improvement is trustworthy live feedback in the GitHub playground,
not hidden global reactive semantics.
