# Planning: Ask For A Witness

> Status: primary solver evidence and bounded library proposals.

## Evidence And Pressure

MiniZinc separates modelling from solving in its tutorial. SWI-Prolog's CLP(FD)
documentation distinguishes finite-domain constraints from enumeration through
labelling.
[MiniZinc tutorial](https://docs.minizinc.dev/en/stable/part_2_tutorial.html),
[CLP(FD)](https://www.swi-prolog.org/pldoc/man?section=clpfd).

The cognitive contribution is specifying acceptable relationships before an
algorithm. The costs are ambiguous/multiple answers, search explosion, solver
profiles, and explanations that may be incomplete. SAT and symbolic rewrite
systems are neighboring candidates; their individual engines were not compared
in this pass.

## Nomi Normal Form And Placement

An ordinary library can construct a typed model, supply a solver profile and
budget, then return explicit outcomes: solution/witness, proven infeasibility
within a supported theory, incomplete search, cancellation, or engine failure.
Do not encode timeout as "no solution". Optimization must distinguish a feasible
candidate from a certified optimum and declare the objective/order.

The base evaluator stays eager. A relation value is reified data, not a magical
function that can always run backwards. Hygiene, variable identity, units,
determinism, and explanation are prerequisites for scoped notation. Core
`where` remains checking, not searching.

## Discriminating Experiment

Schedule three tasks under capacity and deadline constraints. Compare explicit
model-builder calls with hand-written search and, only later, scoped notation.
Include two solutions, inconsistent constraints, timeout before a solution, and
timeout after a feasible candidate. Show a bounded witness in the playground;
never imply the general-purpose compiler proves arbitrary programs correct.
