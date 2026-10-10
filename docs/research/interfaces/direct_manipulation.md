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

### A Shared Edit Interface Is A Candidate

Ziegler, Cao, Lubin and Chasins's August 2026 primary preprint connects direct
manipulation and natural-language editing through structured edits in a cartokit
variant. In its 18-participant within-subjects study, participants used natural
language for 6.14% of edits when both modalities were available. This is evidence
from a particular system and task setting; it does not settle Nomi's primary
representation or a general preference across users and domains.
[Primary preprint](https://arxiv.org/abs/2608.26359v1).

**Nomi inference:** compare modalities that produce explicit domain changes,
including a proposal that needs clarification. Measure what a person understood
and corrected, alongside which modality they chose. Reuse HX3/HX8 with equal
facts and failure tasks; compare domain-specific edit families with a shared
command envelope. A common edit representation may improve inspectability while
also limiting expressive freedom. No edit API or natural-language evaluator is
accepted by this evidence.

### Proposed Invoice Command

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
