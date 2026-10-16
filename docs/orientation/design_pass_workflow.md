# Design Pass Workflow

> Status: current research-to-design-to-implementation workflow.

A registered packet connects one question to evidence, target meaning, pressure
programs and a current implementation bridge. `config/design_passes.json` routes
work; it does not specify the language. Discovery may begin outside the registry.

## Packet Contract

| Artifact | Location | Responsibility |
| --- | --- | --- |
| Research | `docs/research/` | Primary evidence, alternatives, costs and counterexamples. |
| Design | `docs/design/` | Accepted laws and explicitly unaccepted proposals. |
| Target | `docs/design/` | Coherent positive/rejection examples, kept outside runnable samples. |
| Bridge | `docs/review/<topic>.md` | Current evidence, open gaps, validation and next actions. |

All four artifacts link one another by repository path. Broad syntax, semantics,
decisions and active target programs also receive accepted cross-cutting changes.
Use stable topical filenames; dates belong in evidence metadata when needed.

## Lifecycle

`researching` gathers evidence; `designing` compares credible candidates;
`design-accepted` means target closure; `implementing` aligns execution surfaces;
`validated` means declared conformance; `paused` names a deferral and trigger;
`rejected` retains the reason a candidate failed. Update status, `last_reviewed`,
validation and next actions when their actual facts change.

## Pass Loop

1. Discover the concrete activity and existing owner.
2. Compare primary mechanisms and credible alternatives with an independent oracle.
3. Accept, reject or retain a bounded fork in its canonical owner.
4. Pressure-test source, meaning, diagnostics, formatting, effects and completion.
5. Update the implementation bridge with present evidence and gaps.
6. Run the relevant declared checks; promote samples only after conformance.
7. Refresh current status and the next exact action in place.

## Current Bridge Contract

Every bridge contains these nonempty sections in order:

- `## Current Evidence`: what actually runs or is checked, with scope and owners.
- `## Open Gaps`: missing semantics, implementation or host/human evidence.
- `## Validation`: reproducible commands and what they can establish.
- `## Next Actions`: the smallest dependency-ordered closure steps.

Do not append session retrospectives, conversation summaries, commit trails or
old test totals. Narrative evolution belongs only in [HISTORY.md](../../HISTORY.md),
kept short; Git retains detailed old versions. Raw execution reports and source/
host/version provenance remain with their evidence artifacts. Keep current docs
self-contained enough that a reader does not need the project chronology.

## Validation And Routing

```bash
python3 -m tools.design_passes list
python3 -m tools.design_passes show pattern-matching
python3 -m tools.design_passes check
```

The validator checks metadata, allowed authority paths, cross-links and current
bridge sections. It does not typecheck target programs or run listed commands.
Hooks and MCP expose packet navigation; agents still read the source files.
Use skills for variable reasoning, deterministic checks for invariants and
current docs for maintained state. Promote process changes only when they solve
repeated friction; avoid expanding instructions for one-off events.

## Completion Gate

A packet is validated only when canonical laws/examples agree; independent
parse/Surface/Core/value/error/effect/completion fixtures exist; supported CLI
and browser surfaces agree or refuse honestly; declared relevant checks pass;
and every remaining gap is either closed or a separately bounded continuation.
Publication, human benefit and foreign-host behavior require their own evidence.
