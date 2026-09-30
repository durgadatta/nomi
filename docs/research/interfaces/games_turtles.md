# Games And Turtles: An Executable Mental Model

> Status: historical Logo evidence and simulation proposals.

## Evidence And Pressure

Brian Harvey's Berkeley Logo manual documents procedures and turtle graphics.
It is a historical implementation reference, not evidence about all Logo
environments or a real-robot control system.
[Author manual](https://people.eecs.berkeley.edu/~bh/usermanual).

A visible agent moving through a grid can externalize sequence, repetition,
orientation, and state. The risk is inferring language semantics from a charming
animation: heading, coordinate origin, update timing, and collision policy
can silently become the real program.

## Nomi Normal Form And Placement

Model a pose and movement command as nominal immutable data. A pure `step`
function returns a new model or an expected invalid-move error. A renderer
observes a trace; animation speed does not change the simulated result. Nested
procedures remain ordinary functions, not an alternate whitespace-call grammar.

This can pressure-test iteration, invariants, and diagnostics without network
or filesystem capabilities. Real robotics would additionally require physical
safety and device contracts and is explicitly outside this experiment.
**Adapt:** inspectable spatial state and beginner-friendly feedback.
**Reject:** hidden global turtle state as a requirement of ordinary Nomi code.

## Discriminating Experiment

Draw a square using explicit movement values, then perturb one turn. Ask users
to explain the final position before playback and identify an invariant.
Compare text plus trace with animation alone. Support keyboard navigation and
a textual pose table. The result could become a runnable teaching sample only
after its library and renderer agree across CLI and browser profiles.
