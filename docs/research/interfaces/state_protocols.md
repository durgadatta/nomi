# State And Protocols: Validity Over Time

> Status: state-machine evidence and proposed library experiments.

## Evidence And Pressure

SCXML specifies hierarchical state-machine behavior, including event handling
and transitions. The standard is evidence for one explicit temporal model,
not a proposal to import XML into Nomi.
[Primary specification](https://www.w3.org/TR/scxml/).

Petri nets and BPMN are useful next probes for resource counts and workflow
coordination; their detailed semantics were not validated in this pass. The
shared cognitive question is what actions are legal now, and what changes
their availability. Data validity at one instant does not establish temporal
protocol correctness.

## Nomi Normal Form And Placement

Use variant `data` for state and events, and a pure exhaustive function:
`transition(state, event) -> Result[Transition, ProtocolError]`. The transition
may contain proposed actions; an executor separately supplies capabilities.
State diagrams project this function and must not invent a second dispatcher.
Ordering, reentrancy, duplicate events, and cancellation are explicit policy.

A typed resource-state protocol may eventually prove which operations are
available, but must align with the [resource proposal](../../design/resource_lifetime.md).
It cannot be implied by a drawing or user-defined method name. Model checking
belongs in a bounded tool; arbitrary Nomi programs are not promised decidable.

## Discriminating Experiment

Model playground Run/Stop as Idle, Running, Stopping, and Completed, with run IDs.
Test repeated Stop, a late old-worker completion, and an error during stopping.
Compare an explicit transition table with nested conditionals. Require a trace
and missing-event witness, then map only the settled state contract into the
actual frontend. Success means a user can tell whether their current run really
stopped, not that the language acquired statechart syntax.
