# Nomi Language Synthesis

> Status: active whole-language design synthesis; open contracts are not accepted.

Packet: `docs/research/features/README.md`,
`docs/design/targets/overall.nomi`,
`docs/review/2026-09-29-language-synthesis.md`.

## Read The Language

Start with [the overall import program](targets/overall.nomi), then the
[category suite](targets/README.md). Read the [44 language reviews](../research/languages/README.md)
for critical evidence and the [13 feature comparisons](../research/features/README.md)
for mechanisms along one dimension. The scope is selected, not exhaustive.
The reviews distinguish observed behavior from design judgment; no usability
study or comparative benchmark was conducted.

This synthesis connects those views. Accepted source and behavior still belong
to [syntax](syntax.md), [semantics](semantics.md), [industrial contracts](industrial.md),
and [the decision ledger](decisions.md). Proposed library signatures in target
comments are hypotheses, not exports. The current playground runs a different,
supported prototype surface. Do not advertise these fixtures as executable.

## One Coherent Model

Nomi should borrow semantic mechanisms, not accumulate familiar spellings.

| User act | Evidence synthesis | Nomi shape | Cost paid |
| --- | --- | --- | --- |
| Name | Python's immediacy plus lexical/immutable reasoning | Inferred immutable binding; `var`/`set` for change | Breaks Python assignment habits. |
| Transform | First-class functions without multiple call/control rules | `func`, explicit expression lambda, ordinary calls | More helpers and explicit partial application. |
| Model | ML-style alternatives plus nominal package identity | Immutable product/closed variant `data` | Adapters and breaking variant evolution. |
| Choose | Exhaustive structural choice without hidden extractors | Bool `if`, bounded transactional `match` | Explicit classifiers and host adapters. |
| Repeat | Familiar verbs with domain-specific execution laws | Eager List; explicit Stream/TablePlan/Array APIs | Multiple typed domain contracts, not one magical pipeline. |
| Fail | Typed expected outcomes distinct from absence and bugs | Option, Result, `?`, separate panic/cancellation | Explicit context mapping and outcome composition. |
| Touch the world | Resource and task ownership plus host boundaries | Lexical cleanup, `uses`, grants, cold tasks/groups | Signatures and lifecycle policies require care. |
| Understand | Live inspection, source provenance, package contracts | Shared diagnostic/artifact model, examples/checks | Tooling must be designed with semantics, not appended later. |

These choices largely reaffirm the accepted target. This pass does **not** add
keywords, extractors, implicit conversions, generic declaration syntax, macro
quotation, or a second query language. A beautiful short example is not enough
to admit any of them.

## Where The Previous Program Broke Down

The [legacy target](target.nomi) exposed useful ambitions but hid interactions:

1. CSV rows were decoded into Int and Instant fields without an explicit text
   conversion policy. Strict decoding cannot imply those conversions.
2. Mapping a per-row decoder and collecting Results did not specify preservation
   of original row paths or accumulation behavior.
3. "Rejected" counted age-ineligible valid rows, while malformed data aborted
   the workflow. That is misleading report terminology.
4. Normalization entered constrained constructors without a stated preservation
   argument. A transforming boundary needs validation if predicates can change.
5. TaskGroup had a running limit but no named abnormal-failure policy, queued
   memory bound, or public composed-outcome contract.
6. Config acquisition, retry, and generated codec APIs were underspecified;
   Clock and other inferred effects could disappear from an attractive signature.
7. Constructor values and callback generics/effects were assumed by examples
   before their declaration and dispatch rules were settled.

The revised fixture uses a maximum-128-row JSON batch, validates it as one
owned wrapper before network access, preserves nested decoder paths, and counts
`skipped_ineligible` separately. Trim normalization preserves its stated
nonempty constraints. Explicit lambdas avoid constructor-value assumptions.
Task start is in a loop rather than an apparently pure effectful map callback.
The response identity is checked. No report is written after an ordinary input
or enrichment error. The input bound limits handles in this example; it is not
a substitute for a future streaming/backpressure contract.

The program still relies on **proposed** codecs, task handles, HTTP/file APIs,
and publication guarantees. It deliberately leaves task panic/cancellation
outside ImportError and marks the missing envelope. This is honest pressure on
the design, not a claim the program is already well typed end to end.

## Interactions To Resolve First

| Gate | Competing Nomi-compatible choices | Evidence required |
| --- | --- | --- |
| Cleanup outcome | Domain-visible release Result versus distinct composed abnormal envelope | Body Err + release Err + cancellation, without losing any cause. |
| Handle escape | Static non-escape/lifetime rule versus runtime closed-handle checks | Return, callback capture, and child-task transfer, with exact diagnostic behavior. |
| Callback effects | Pure-only verbs initially versus explicit effect-polymorphic signatures | map/fold, resource callback, query translation, and effect diagnostics. |
| Task policy | Cancel siblings versus collect all on abnormal failure | Event traces separating returned Err, panic, cancellation, and multiple failures. |
| Bounds | Explicit bounded producer/queue versus whole finite batch | Peak active/queued counts and no children after lexical exit. |
| Numeric defaults | Arbitrary-precision Int versus checked fixed-width default | Native/JS/Wasm vectors, narrowing diagnostics, measured representation costs. |
| Boundary evolution | Strict closed schema versus explicit version/rest policy | Typos, unknown tags, rolling deployment, indexed errors, non-projectable constraints. |

Do not answer these with more broad language tours. Use the
[open experiment agenda](../research/open_questions.md). The per-language
exercises are candidate evidence, not 44 independent implementation tasks.

## Action Sequence

Each step owns one reviewable deliverable and a visible user outcome. The
[dated bridge](../review/2026-09-29-language-synthesis.md) records the snapshot
and exact continuation, while this sequence is the live synthesis route.

| Order | Action and ownership | Acceptance | User-facing connection |
| --- | --- | --- | --- |
| 1 | Language design: settle cleanup carrier and handle escape together | Three representative programs, all exit traces, formatter renderings, diagnostic JSON, accepted/rejected escape cases | A failed import explains both body and release causes; no use-after-close surprise. |
| 2 | Language design: specify callback types/effects and minimal generic/protocol surface | Pure/effectful map, conflicting extensions, task handle typing, inspectable resolved calls | Editor hover and playground explain show the actual call/effects. |
| 3 | Runtime design: close cold-task/group policy and bounded queue contract | Deterministic scheduler traces for Err/panic/cancel; active and queued bounds; no lifetime escape | Run/stop is trustworthy and failures are not silently dropped. |
| 4 | Boundary/numeric design: specify codecs and portable scalar vectors | Indexed accumulated decode errors, no coercion, normalization tests, large integers/rounding agree across hosts | Users see accurate values and actionable input paths. |
| 5 | Frontend/tooling: admit the smallest completed category contract | Accepted/rejected source fixtures, typed Surface/Core, source maps, formatter, structured diagnostics | One honest new runnable playground category, not the whole aspirational suite. |
| 6 | CLI/browser owners: promote after cross-backend conformance | Add supported sample to `samples/`, regression coverage, fresh web manifest, browser smoke and CI | GitHub playground sample can actually run and reproduce documented results. |
| 7 | Product/design review: repeat the overall workflow | Locked host profile, bounded inputs, no secret leaks, publication/failure checks | A coherent import/report workflow rather than isolated feature demos. |

Keep the existing registered pattern pass moving in parallel; do not rewrite
its accepted contract from this survey. The playground work is routed through
the [September playground plan](../review/2026-09-29-github-playground-agentic-plan.md)
and the existing runtime checks. No parser/runtime migration is implemented by
this documentation pass.

## Admission And Stop Rules

A target category becomes a supported sample only when it has one meaning
across source, typing, effects, lowering, runtime, diagnostics, and formatter.
Passing doc tests proves links/status/packet consistency, not target parsing or
execution. Keep these sources outside `samples/` until that gate is met.

Library-first is not ambition reduction: tables, arrays, actors, build plans,
and symbolic work remain important. It is a way to discover durable laws before
fixing notation. Admit a scoped surface only if explicit calls genuinely fail
a domain program and the alternative has hygiene, budgets, source maps,
inspection, and a removal path. Stop research when an experiment distinguishes
the candidates, and promote the result into the canonical contract.
