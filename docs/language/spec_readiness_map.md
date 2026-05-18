# Spec Readiness Map

> Status: active consolidation map.
>
> Scope: documentation-only. This file does not add language features. It
> explains how Nomi's existing foundation, research, convenience notes, feature
> docs, fixtures, and implementation plans should converge into a future
> language specification.

## Purpose

Nomi already has enough design material to support a real specification. The
main risk is not missing inspiration; it is fragmentation:

```text
foundation idea -> research note -> convenience decision -> feature spec
-> implementation TODO -> language_spec section
```

This map keeps that chain explicit. It answers:

- which documents are active decision surfaces;
- which documents are source evidence;
- what a feature must contain before it can move into the spec;
- where each normal form belongs in `language_spec.md`;
- which bridge docs are still needed before the spec can harden.

Use this file before adding broad synthesis docs. Prefer improving one existing
artifact in the chain above.

## Operational Spec Convergence Loop

The long-term target is one operational language specification, not a permanent
mesh of partially overlapping design notes. Treat each design pass as a loop:

```text
research evidence
-> global/local interaction map
-> focused feature packet
-> target demo or fixture
-> language_spec section
-> implementation slice
-> runnable sample and tests
```

Each artifact has a distinct job:

| Artifact | Job | Promotion rule |
| --- | --- | --- |
| Research deep dive | Preserve source-language evidence and community lessons. | Promote only reduced decisions, not catalogues. |
| [Global Feature Interaction Map](../convenience/interaction_map.md) | Catch cross-feature friction before local syntax hardens. | Use it when a feature touches more than one normal form. |
| Focused feature packet | Specify syntax, reduction, diagnostics, interactions, and status. | Required before normative spec text hardens. |
| [Target Program Fixtures](target_program_fixtures.md) | Keep ordinary tasks short and comparable. | Use for local pressure and open questions. |
| [Target Demo Script](demo_target.nomi) | Show one compact future program across typical cases. | Update when syntax decisions change globally. |
| [Target Language Tour](target_language_tour.md) | Stress-test whole-program coherence at larger scale. | Keep aspirational; do not treat as runnable proof. |
| `language_spec.md` | Define the user-facing contract. | Promote only design-settled or clearly marked forward-looking behavior. |
| `samples/*.nomi` | Demonstrate currently runnable behavior. | Add only after parser, runtime, tests, and snapshots agree. |

This loop is intentionally iterative. A target demo may reveal a conflict that
sends a feature back to the interaction map. An implementation slice may reveal
diagnostic or parser friction that sends wording back to the feature packet.
The goal is convergence, not one perfect pass.

## Document Roles

| Role | Authority | Main files | What belongs there |
| --- | --- | --- | --- |
| Foundation | Highest design authority below the spec. | `language_foundation.md`, `language_degrees_of_freedom.md`, `language_design_dimensions.md` | Normal forms, admission rules, first-language boundaries. |
| Specification | Concrete user-facing contract. | `language_spec.md` | Normative syntax, behavior, diagnostics, conformance. |
| Spec readiness | Promotion and coverage control. | this file, `language_direction_and_gap_map.md`, `docs_eagle_eye_review.md` | Gaps, decision ledger, conversion order, doc hygiene. |
| Feature specs | One semantic pillar at a time. | `docs/features/`, focused `docs/convenience/` docs | User syntax, reductions, diagnostics, rejected alternatives, tests. |
| Research evidence | Rationale and comparisons. | `docs/research/`, `docs/notes/`, `docs/drafts/` | Source-language lessons, historical review, long-horizon ideas. |
| Implementation plans | Work packages and gates. | `implementation_todos.md`, `forward_implementation_plan.md`, substrate plans | Ordered work, test expectations, status tracking. |

Only the foundation, feature specs, and `language_spec.md` should define active
language behavior. Research files may motivate behavior, but they should not be
quoted as a competing spec.

## Documentation Modes

Nomi docs should stop mixing learning, reference, explanation, and planning in
the same page. Use this split:

| Mode | User need | Nomi home | Sharp rule |
| --- | --- | --- | --- |
| Tutorial | Learn the language by doing one small task. | `README.md`, future first-hour note. | No feature catalogue. One path, runnable code, immediate feedback. |
| How-to | Complete a concrete job. | focused task docs and examples. | Give steps and expected output; link out for rationale. |
| Reference/spec | Know exactly what syntax means. | `language_spec.md`, feature specs. | Terse, normative, scan-friendly; examples are complete and relevant. |
| Explanation/rationale | Understand why Nomi chooses a model. | `language_foundation.md`, research, notes. | Explain tradeoffs, but do not define behavior by essay. |
| Planning | Decide implementation order. | `implementation_todos.md`, `forward_implementation_plan.md`. | Must end in files, tests, gates, or explicit deferrals. |

This follows the same practical separation used by mature documentation
systems: Diátaxis separates tutorial, how-to, reference, and explanation; the
Python reference separates terse syntax/core semantics from tutorials and
standard library docs; Rust and Kotlin keep explicit grammar/reference
surfaces; Gleam's tour teaches syntax through small operational reductions.

## External Spec Lessons

The external scan adds a few operational rules for Nomi:

| Source | Useful lesson | Nomi rule |
| --- | --- | --- |
| [Python Language Reference](https://docs.python.org/3/reference/) | A reference should be terse, exact, and focused on syntax plus core semantics, with library behavior elsewhere. | Keep `language_spec.md` normative and move standard-library detail to a prelude plan or appendix. |
| [Rust Reference grammar summary](https://doc.rust-lang.org/reference/grammar.html) | Grammar summaries are useful when they are searchable and tied to precise syntax notation. | Keep a grammar summary, but link each production to the semantic section and normal form. |
| [Kotlin Specification](https://kotlinlang.org/spec/kotlin-spec.html) | Sections can combine syntax, type/semantic restrictions, examples, and expansion rules. | Every surface feature needs restrictions, expansion/reduction, and failure behavior. |
| [Gleam Tour: pipelines](https://tour.gleam.run/functions/pipelines/) and [Result](https://tour.gleam.run/everything/) | Pipelines, results, and callback flattening are teachable when each feature explains what smaller operation it performs. | Teach Nomi features by reduction first, not by source-language ancestry. |
| [Diátaxis](https://diataxis.fr/) | Docs improve when each page has one user context. | Mark pages as tutorial, how-to, reference/spec, explanation, source research, or planning. |

## Status Vocabulary

Use these labels consistently across language, feature, and convenience docs:

| Status | Meaning | Spec treatment |
| --- | --- | --- |
| `implemented` | The prototype supports it with tests or runnable examples. | May be normative if design-settled. |
| `partial` | Some parser/lowering/runtime pieces exist, but behavior is incomplete. | Document as current status, not final contract. |
| `core` | Required for the first complete language. | Belongs in the main spec body. |
| `surface` | Convenience syntax that reduces to core semantics. | Belongs in the spec near its normal form. |
| `prototype-ready` | Syntax, reduction, and tests are clear enough for an implementation slice. | Can be specified with explicit open questions. |
| `design-needed` | The everyday need is real, but semantics or diagnostics are unsettled. | Keep out of normative spec text. |
| `library-first` | Should begin as functions, data values, policies, or plans. | Mention as library direction, not syntax. |
| `future layer` | Compatible with Nomi, but not part of the first language. | Place in out-of-scope or extension sections. |
| `research-only` | Source material without a Nomi normal form. | Keep in research/source notes. |
| `rejected-for-now` | Too costly or incoherent for the first language. | Record in rejection tables to prevent churn. |

Avoid using `planned` alone. It hides whether a feature is design-settled,
prototype-ready, library-first, or merely desired.

## Feature Packet

Before a feature can be promoted into `language_spec.md`, its home doc should
answer this packet in one place:

| Section | Required question |
| --- | --- |
| Everyday pressure | What ordinary programming problem justifies the feature? |
| User syntax | What code does the user write? |
| Normal form | Does it reduce to binding, function, pattern, flow, block, absence/result, data boundary, or explanation? |
| Semantic reduction | What smaller operations explain the feature? |
| Diagnostics | What failure does the user see, with source spans and vocabulary? |
| Interactions | How does it combine with constraints, patterns, blocks, results, imports, and examples? |
| Rejected alternatives | Which attractive spellings or models are refused, and why? |
| Implementation slice | What parser, lowering, runtime, test, docs, and sample work is needed? |
| Current status | Is it implemented, partial, prototype-ready, design-needed, library-first, future, research-only, or rejected? |

If a proposed feature cannot fill this packet, keep it in research or in a
target fixture until the missing piece is known.

## Cognitive Act Map

Each feature should name the primitive cognitive act it improves. This map
absorbs the old first-principles source material into an operational checklist:

| Act | Language role | Spec pressure |
| --- | --- | --- |
| Distinguish | values, literals, identity, variants | Define what values exist before adding clever syntax around them. |
| Name | binding, scope, context | Treat assignment, parameters, imports, captures, and block parameters as one naming operation. |
| Judge | constraints, predicates, examples, diagnostics | Do not split types, validation, contracts, tests, and explanations into unrelated systems. |
| Transform | functions, calls, pipelines, rules | Make pipelines, composition, queries, and rewrite reduce to visible transformation. |
| Choose | conditionals, patterns, guards, result cases | Prefer structural choice over stringly or ad hoc branching. |
| Group | data, collections, modules, tables | Keep owned data, external shape, collections, and table structure related but not confused. |
| Repeat | iteration, collection verbs, folds, rank, streams | Treat loops, pipelines, queries, and array ideas as repeated transformation. |
| Sequence | blocks, yield, retry, transaction, cleanup | Model time-shaped control through block policies instead of one keyword per policy. |
| Touch the world | files, network, time, subprocesses, capabilities | Make external authority visible enough to test, replay, and explain. |
| Explain | examples, traces, diagnostics, counterexamples | Require features to explain success, failure, and boundary crossings. |
| Reflect | quote, rewrite, notation, expansion | Fence code-as-data behind explicit quotation or scoped notation. |

If the act is unclear, the feature is probably still research.

## Construction And Elimination

A spec-ready feature must define both sides of use:

```text
construction: provide enough information to make a value or semantic event
elimination: use that value or event by exposing what it guarantees
```

| Area | Construction | Elimination |
| --- | --- | --- |
| Product data | `User(id, email)` | field access, destructuring |
| Variants/results | `Ok(value)`, `Err(error)` | `match result` |
| Decode | external mapping to owned value | decode diagnostics and field paths |
| Constraints | accepted binding | failed judgement explanation |
| Patterns | structural pattern form | case choice and captures |
| Examples/checks | expected behavior | assertion or counterexample explanation |
| Symbolic syntax | `quote:` syntax value | rewrite or pattern over syntax |

Data, decode, variants, patterns, constraints, and diagnostics should be
designed as one construction/elimination family, not as isolated tracks named
"types", "schemas", "patterns", and "errors".

## Boundary Model

Most hard Nomi design questions are boundary questions:

| Boundary | Question | Examples |
| --- | --- | --- |
| Data boundary | When does external mess become owned meaning? | decode, constraints, config, HTTP, CSV |
| Control boundary | Who owns time-shaped execution? | block calls, retry, transaction, using, tasks |
| Power boundary | When does advanced capability become visible and fenced? | world, quote, rewrite, scoped notation, macros |

Feature specs should name which boundary they cross and what explains that
crossing.

## Explanation Contract

Every major feature spec should answer:

```text
What happened?
Where did it happen?
What value was involved?
What rule was being checked?
What can the user do next?
What is redacted?
```

Diagnostics are the product surface for Nomi's precision. If a feature cannot
answer these questions, keep it design-needed.

## Obsolescence Policy

Nomi should delete or quarantine docs that no longer have a live role. Use
these labels at the top of old files:

| Label | Meaning | Required action |
| --- | --- | --- |
| `active` | Current decision surface. | Keep indexed and maintained. |
| `source` | Useful rationale or research, not authority. | Link to active home; do not add new decisions here. |
| `historical` | Records a path Nomi no longer follows. | Mark why it was superseded and where the durable parts moved. |
| `obsolete` | Misleading or duplicative enough to harm future work. | Remove from reading order; keep only if history is valuable. |
| `scratch` | Temporary draft material. | Do not cite from active docs unless promoted. |

When marking a doc obsolete, say exactly what replaced it. Do not write a vague
"kept for reference" note.

## Spec Conversion Matrix

Use this table when deciding where a durable decision should land.

| Normal form | Primary spec sections | Source docs to mine | Bridge still needed |
| --- | --- | --- | --- |
| Binding | 6. Bindings And Scope; 7. Constraints; 9.2 Parameters | `language_foundation.md`, `binding_constraints_feature.md`, `scope_context.md` | Central `BindingTarget`/diagnostic contract. |
| Function | 8. Expressions; 9. Functions And Calls | `functions.md`, `syntax_synthesis_matrix.md` | Clear status split for holes, sections, equations, and composition. |
| Pattern | 11. Patterns And Match; 10.3 Sum Data | `patterns.md`, `pattern_matching_synthesis.md` | Pattern failure versus constraint failure examples across assignment, match, and guard. |
| Flow | 12. Collections And Repetition; 18. Standard Prelude | `flow_and_collections.md`, `structured_collections_query_language.md`, `table_and_flow_systems_deep_dive.md` | Stable collection/table verb vocabulary and explainable plan model. |
| Block | 13. Blocks And Yield | `block_calls_feature.md`, `absence_and_result.md`, `block_calls_feature.md` design context | One block-policy spec for `using`, `retry`, `transaction`, `trace`, `test`. |
| Absence/result | 8.5 Absence-Aware Expressions; 14. Errors | `absence_and_result.md`, `error_handling.md`, error/resource deep dive | Focused failure taxonomy spanning `none`, `Result`, exceptions, pattern failure, and constraint failure. |
| Data boundary | 10. Data Declarations; 18. Standard Prelude | `data_and_types.md`, `data_boundary_systems_deep_dive.md`, `binding_constraints_feature.md` | Focused decode boundary spec covering provenance, defaults, optional fields, extra fields, redaction. |
| Explanation | 15. Examples; 19. Diagnostics, Trace, And Explain; 23. Conformance | `meta_testing.md`, diagnostics and interactive deep dives | Event model shared by binding, call, match, decode, pipeline, blocks, and examples. |

The `language_spec.md` sections should become more normative only after their
source docs have converged on the same normal form, status, diagnostics, and
rejected alternatives.

## Consolidation Rules

- Promote decisions, not whole research essays.
- Prefer appending a focused "Spec implications" section to an existing doc
  over creating another broad synthesis note.
- Keep examples small unless they test cross-feature composition.
- When two docs repeat the same table, keep the authoritative table in one
  place and link to it.
- When a doc is historical, say so at the top and link to the active home.
- Do not let target-only examples appear as runnable samples until parser,
  lowering, runtime behavior, and tests agree.

## Spec Hardening Order

This is the recommended order for turning current docs into a stronger spec:

1. **Capability matrix**: separate implemented, partial, prototype-ready,
   design-needed, library-first, future, research-only, and rejected features.
2. **Decision ledger**: record accepted, rejected, deferred, and revisit-later
   choices with links to rationale.
3. **Binding and diagnostics**: make `BindingError`, `Constraint`,
   `BindingTarget`, and source spans the first shared semantic substrate.
4. **Data boundary**: specify `Data.decode(...)`, field constraints,
   provenance, defaults, optional fields, extra fields, nested paths, and
   redaction.
5. **Failure taxonomy**: distinguish absence, expected failure, unexpected
   error, pattern non-match, and constraint failure.
6. **Flow vocabulary**: specify collection/table verbs as library-first calls
   and plan values before adding query syntax.
7. **Block policies**: specify `using`, `retry`, `transaction`, `trace`, and
   `test` as one block-call family.
8. **Explanation model**: unify examples, checks, diagnostics, traces, decode
   errors, and query plans as structured semantic events.
9. **Prelude and first hour**: make ordinary tasks teachable before advanced
   layers expand.

This order keeps the spec grounded in the highest-reuse pieces first.

## Current Coverage Snapshot

| Area | Coverage today | Spec-readiness risk |
| --- | --- | --- |
| Core normal forms | Strong and repeated across foundation, spec, and convenience docs. | Mostly terminology consistency. |
| Syntax catalogue | Broad coverage in `language_spec.md` and convenience docs. | Some features are target-only but sound more settled than implementation allows. |
| Research evidence | Strong corpus with synthesis and Adopt/Refuse/Adapt tables. | Stable decisions need continued promotion into active docs. |
| Diagnostics | Strong design pressure. | Needs one event vocabulary before features invent private error shapes. |
| Data decode | Well motivated. | Needs a focused feature spec before spec text hardens. |
| Failure | Well researched. | Split across absence, error, patterns, constraints, and blocks. |
| Standard library | Direction exists. | Needs a concrete first prelude and ordinary-task examples. |
| Teaching | Target examples exist. | First-hour path still missing. |
| Implementation status | Backlog is detailed. | Needs a capability matrix that is easier to scan than TODO prose. |

## Definition Of Spec-Ready

A Nomi feature is spec-ready when a reader can answer:

```text
What code do I write?
What smaller operation explains it?
What happens on success?
What happens on failure?
What does the diagnostic say?
What is intentionally not allowed?
Is it core, surface, library-first, future, or rejected?
Where are the tests or target fixtures?
```

If any answer requires hunting across more than two active docs, consolidate
before implementing.
