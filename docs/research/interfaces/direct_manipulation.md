# Direct Manipulation: Make The Change Explicit

> Status: historical evidence and Nomi projection hypotheses.

## Evidence And Pressure

Sketchpad is a primary example of graphical construction with reusable picture
structure and interactive input. Its thesis supplies historical evidence, not
proof that diagrams outperform text for all programming.
[Primary thesis](https://www.cl.cam.ac.uk/techreports/UCAM-CL-TR-574.html).

A spatial representation can let a person act on the object of interest instead
of first encoding its coordinates. The corresponding risks are accidental
changes, invisible snapping/constraints, ambiguous units, and a gesture that
cannot be reviewed or reproduced. CAD, sliders, and drag/drop are neighboring
design probes, not additional systems benchmarked here.

## Nomi Normal Form And Placement

Dragging an invoice quantity control should propose the same decoded command
as entering a value in text. A candidate change includes the domain target,
base revision, requested value, validation, and a source/value preview. Commit
once after validation; reject stale or invalid changes atomically.

A geometry library may own points, transforms, units, and constraints. A view
may choose scale and layout; it cannot secretly decide whether a drag changes
an input, a formula, or a constraint. An inverse edit may have several valid
source realizations. Ask the user to choose rather than guessing.

**Adapt:** preview and proximity of action/result. **Defer:** bidirectional
editing outside a tightly supported subset. **Reject:** storing pixel coordinates
as semantic entity identity or executing effects on every pointer movement.

## Discriminating Experiment

Compare numeric text input, slider, and a bounded drag for the same model.
Test keyboard-only operation, cancellation midway, constraint failure, stale
revision, undo, and exporting source after editing. Require identical final
values and diagnostics, with view layout stored separately. If source edits
cannot preserve comments and bindings reliably, keep the view read-only.
