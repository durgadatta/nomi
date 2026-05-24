# Docs Eagle Eye Review

> Status: active distilled review.
>
> Scope: documentation-only. This file preserves the current bridge gaps from
> the purged archive scan and points each gap toward the active document that
> should absorb it.

## Purpose

The full docs tree has already been scanned for coherence, duplication, and
missing bridges. The archived scan is useful source material, but active docs
need a smaller review surface that stays aligned with the current language
spine.

Use this file to answer:

```text
Which gaps block future spec quality?
Where should the next consolidation edit land?
What should not become another parallel spec?
```

For the promotion workflow from research to spec, see
[Spec Readiness Map](spec_readiness_map.md).

For the deliberately hostile version of this review, see
[Adversarial Design Critique](adversarial_design_critique.md). The eagle-eye
review names bridge gaps; the adversarial critique names how the language could
fail even if the bridge gaps are addressed.

## What Is Strong

| Strength | Why it matters | Active home |
| --- | --- | --- |
| Normal forms are stable. | Binding, function, pattern, flow, block, absence/result, data boundary, and explanation can organize nearly all feature pressure. | `language_foundation.md`, `language_spec.md`, `convenience/review_and_roadmap.md` |
| Research is broad enough. | The corpus covers major language families and cross-cutting dimensions; new work should usually consolidate, not re-survey. | `research/language_family_coverage_map.md`, `research/cross_language_synthesis_master.md` |
| Target examples exist. | Fixtures and the tour keep design pressure grounded in ordinary programs rather than local syntax taste. | `target_program_fixtures.md`, `target_language_tour.md` |
| Implementation runway is visible. | Feature manifests, syntax inspection, spans, and runtime facade work have explicit plans. | `flexible_syntax_substrate_plan.md`, `syntax_substrate_todo_audit.md`, `architecture_refactoring_plan.md` |

## Spec-Blocking Gaps

| Gap | Why it blocks spec quality | Best active home |
| --- | --- | --- |
| Current capability matrix | Readers need to know what is implemented, partial, target-only, and rejected. | `spec_readiness_map.md`, then a focused matrix if needed. |
| Decision ledger | Accepted and rejected choices are repeated across docs and can be reopened by accident. | `spec_readiness_map.md`, `language_direction_and_gap_map.md`. |
| Decode boundary spec | External values are central to everyday usefulness, but provenance/defaults/redaction policy is not yet one feature packet. | future `docs/features/data_decode_boundary_feature.md`. |
| Failure taxonomy | `none`, `Result`, exceptions, pattern non-match, and constraint failure need one teaching model. | `absence_and_result.md`, then a focused failure feature if needed. |
| Explanation event model | Binding, match, decode, pipeline, block, examples, and traces should not invent separate diagnostic formats. | `meta_testing.md`, future explanation/trace feature spec. |
| Standard prelude | The spec names ordinary tasks but does not yet define the boring first library surface. | `language_spec.md` appendix or future prelude plan. |
| First-hour path | Nomi needs a tiny learnable path before advanced features dominate the docs. | `README.md`, future first-hour note, target fixtures. |
| State and capability | Files, network, time, subprocesses, mutation, and authority need practical rules before advanced effects appear. | future state/capability note; block feature docs. |
| Syntax/special-form quality gates | Syntax can look coherent locally while still failing UX, status, formatter, explanation, or keyword-budget checks. | `../convenience/syntax_special_forms_quality_review.md`. |
| Implementation evolvability gate | A feature can be attractive and still harden private parser, lowering, runtime, backend, or frontend seams too early. | `implementation_evolvability_gap_review.md`. |

## Consolidation Moves

Use these moves before adding new top-level docs:

| If you find... | Do this |
| --- | --- |
| A stable research decision | Promote the decision into `language_spec.md`, a feature doc, or a convenience doc; leave the research as citation. |
| A broad planning note | Fold actionable items into `implementation_todos.md`, `forward_implementation_plan.md`, or this review. |
| A target-only syntax example | Put it in `target_program_fixtures.md` or `target_language_tour.md`, not runnable samples. |
| Two docs with similar candidate tables | Keep one table authoritative and link to it. |
| A historical source note | Add a status block pointing to the active home. |
| A feature without diagnostics | Keep it design-needed even if the syntax is attractive. |

## Ingested Archive Material

The old `docs/archive/` folder has been purged. Its durable material now lives
in active docs:

| Former source | Material retained | Active replacement |
| --- | --- | --- |
| first-principles model | cognitive-act map and ladder pressure | `spec_readiness_map.md`, `language_foundation.md`. |
| hierarchy plan | layer gates, first implementation spine, research guardrails | `implementation_todos.md`, `forward_implementation_plan.md`, `spec_readiness_map.md`. |
| coherence model | one-story invariants, visible boundaries, rejection tests | `language_foundation.md`, `language_direction_and_gap_map.md`, this file. |
| eagle-eye review | construction/elimination, boundary model, explanation contract | `spec_readiness_map.md`, this file. |
| yield-to-block note | one block-call family, Python-generator caveats | `../features/block_calls_feature.md`. |

Do not recreate the archive. Put future discarded work in `docs/drafts/` only
when it is genuinely temporary, and promote durable decisions into active docs.

## Rejection Tests

Reject or redesign a feature when:

- it exists mainly because another language has it;
- it creates a second story for binding, blocks, patterns, effects, symbolic
  code, or diagnostics;
- it requires global magic to be useful;
- it cannot produce a meaningful explanation when it fails;
- it makes common code read like expert-only notation;
- it cannot be scoped, desugared, or inspected;
- it competes with an existing Nomi spelling for the same operation.

## Required Feature-Spec Shape

Every active feature spec should be able to become a spec section later. Use
the packet in [Spec Readiness Map](spec_readiness_map.md#feature-packet):

```text
Everyday pressure
User syntax
Normal form
Semantic reduction
Diagnostics
Interactions
Rejected alternatives
Implementation slice
Current status
```

If a feature doc cannot fill those sections, it should remain a design note
until the missing rule is known.

## Next Exact Pass

The next highest-leverage docs pass should do this:

1. Add or update a capability matrix that reads across parser, lowering,
   runtime, tests, samples, docs, web, and notebook exposure.
2. Use `syntax_special_forms_quality_review.md` before promoting any new
   syntax; it is now the audit surface for UX, keyword budget, diagnostics, and
   status honesty.
3. Start `data_decode_boundary_feature.md` using the feature packet, because
   decode combines binding, data, diagnostics, security, and everyday adoption.
4. Extract a compact failure taxonomy from `absence_and_result.md`,
   `error_handling.md`, pattern docs, and constraint docs.
5. Add a shared explanation-event vocabulary before implementing more
   feature-specific diagnostics.
6. Use `implementation_evolvability_gap_review.md` before broad implementation
   work; it is the implementation counterpart to the syntax/special-form gate.
7. Keep `language_spec.md` concrete, but mark target-only sections clearly
   until the capability matrix says otherwise.

## Avoid

- Creating another broad language vision document.
- Copying source-language catalogues into `language_spec.md`.
- Treating `docs/research/`, `docs/drafts/`, or purged archive material as
  active specifications.
- Promoting syntax whose diagnostic story is still private or vague.
- Updating samples with target-only code before tests and snapshots prove it.
