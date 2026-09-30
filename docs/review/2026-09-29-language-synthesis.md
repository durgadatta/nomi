# Language Research And Target Review

> Status: dated evidence and continuation snapshot; not a second live backlog.

Keep this file as evidence, not as a second backlog. Live priorities belong in
[the synthesis](../design/synthesis.md), [open questions](../research/open_questions.md),
and `config/design_passes.json`.

Packet: `docs/research/features/README.md`, `docs/design/synthesis.md`,
`docs/design/targets/overall.nomi`.

## Scope And Outcome

The user requested critical reviews by language, comparisons by feature,
category target files, one overall program, and one synthesis. This pass adds
44 bounded language reviews, 13 feature comparisons, 13 category sources and
an overall source, with navigation and authority made explicit. The pre-existing
uncommitted category drafts were preserved and corrected, not discarded.

Read the [language index](../research/languages/README.md),
[feature index](../research/features/README.md), and
[target index](../design/targets/README.md). Primary documentation supports
mechanism claims; Nomi recommendations remain design judgment. No foreign
program suite, user study, performance benchmark, or target type checker was
run. The comparison set is deliberately scoped, not a universal language survey.

The earlier playground implementation was committed as `e3b88d2`. This language
documentation work is a separate uncommitted change; runtime, parser, runnable
samples, and GitHub deployment are not modified by this pass.

## Findings

The accepted core is coherent in isolation, but the legacy overall program
overclaimed several library interactions: CSV conversions, indexed error
collection, normalization validity, callback typing, group policy, and cleanup
outcomes. Reusing an established language's spelling does not import its
contract. The revised program avoids unsupported coercion, uses a bounded JSON
batch, separates ineligibility from invalid input, and makes task policy and
codec assumptions visible. Legacy source is retained with a superseded header.

The highest-risk unresolved design pair is deterministic cleanup plus handle
escape. The next pair is callbacks/generics plus effects. Cold tasks require
observable start/stop and distinct ordinary versus abnormal outcomes; a running
limit is not a queue-memory bound. Portable numerics and strict boundary paths
are necessary for truthful browser results. These findings are promoted to
the decision ledger as **open gates**, not accepted new features.

## Validation Scope

Use the registered documentation checks and packet validator for this pass.
They establish lifecycle status, navigation, registration, and local consistency.
They do not prove target programs parse, typecheck, or execute. The target-only
sources remain outside `samples/`; no web manifest regeneration is required.
Validation on 2026-09-29: all 10 docs-lifecycle/design-pass tests passed using
the local Python 3.14 environment; both registered packets passed validation;
agent doctor passed; a local scan of 102 Markdown/Nomi files found no broken
relative file links, and new suite/research files had no trailing whitespace.
`git diff --check` passed. The ignored local RAG index was rebuilt with the new
documents. These results are documentation checks, not language conformance.

## Pass Retrospective

### Evidence That Changed The Design

The combined program exposed misleading count semantics and an unstated CSV
conversion contract. Language evidence also separated declaration from authority,
GC from release, pipeline spelling from execution, and task return values from
task failure. Those distinctions changed the active fixture and experiment order,
not the accepted core vocabulary.

### Workflow Friction

The earlier session left category drafts with links to unwritten indexes and
synthesis, so a resumed agent could mistake intention for completion. Several
official sites expose sparse or inaccessible extracted pages; cited scope was
narrowed to retrievable primary documentation, with historical/version limits
stated. Breadth cannot substitute for conformance or user evidence.

### Durable Improvement

The registered `language-coherence` packet now gives subsequent agents one
research/design/target/bridge route. Two indexes satisfy the requested research
dimensions without multiplying authorities. Each page names an observable
experiment and each target labels proposed APIs. The complete docs inventory
and existing design-pass checks guard the routing, while canonical decisions
keep unresolved assumptions open.

### Next Pass

Run `python3 -m tools.design_passes show language-coherence`, then read the
resource comparison and canonical resource semantics. Write three programs
(simple reader, staged acquisition, cancellation plus failed release), compare
two outcome carriers and two escape policies, and produce ordered event traces
and diagnostic JSON. Only after that decision should a frontend/runtime slice
and supported playground sample be proposed. Keep the pattern pass's existing
authority and avoid expanding this survey absent a concrete failed program.
