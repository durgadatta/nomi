# Implementation Evolvability Gap Review

> Status: active implementation review.
>
> Scope: project-wide evolvability. This document is not a language spec and
> not a rewrite plan. It names the implementation contracts that let Nomi keep
> changing quickly without making each new feature harder to unwind.

## Purpose

Nomi is an exploratory language lab. That makes implementation quality less
about freezing the current prototype and more about preserving optionality while
still making real progress. The project should be easy to evolve in three
directions at once:

- language surface experiments: strings, functions, collections, data, patterns,
  resources, blocks, modules, diagnostics, and future focused surfaces;
- semantic consolidation: binding, calls, flow, blocks, data boundaries,
  absence/result, patterns, and explanation as reusable normal forms;
- backend/tool growth: Python AST, Core IR, JS runtime, web, notebook, CLI,
  tests, and future compiler work.

The current codebase already has promising seams: `SyntaxFeature` manifests,
inspection stages, passive surface/core nodes, runtime sessions, structured
results, backend capability tables, and cross-backend fixtures. The remaining
gap is consistency. These seams must become truthful enough that a person or
agent can add a feature by filling a packet, not by discovering private parser,
lowering, runtime, frontend, and test conventions one file at a time.

## Evolvability Thesis

Every feature should become:

```text
feature-owned
  -> capability-honest
  -> layer-classified
  -> inspectably reduced
  -> tested by declared contracts
  -> exposed consistently through frontends
  -> reversible while experimental
```

The most important implementation posture is:

```text
new syntax is cheap only when its ownership, status, reduction, diagnostics,
tests, and frontend exposure are data.
```

If those facts live only in grammar rules, transformer branches, evaluator
methods, snapshots, or prose, the project can still move, but every movement
adds hidden debt.

## Project-Wide Scorecard

| Evolvability axis | Current strength | Main gap | Next pressure |
| --- | --- | --- | --- |
| Feature ownership | `BUILTIN_FEATURES` names syntax features and drives grammar layers, transforms, passes, and capability inspection. | Several axes are derived or defaulted rather than explicit: reduced mode, docs/spec status, samples, web, notebook, diagnostics, and explanation. | Make capability axes explicit per feature before large syntax promotion. |
| Layer separation | L0-L7 vocabulary and feature layer metadata exist. | Python AST still does too much semantic work for several source forms. | Make Surface -> Core authoritative for the tiny stable subset before relying on Core for diagnostics or backend claims. |
| Surface representation | `SurfaceNode`, spans, and `BlockCall` prove the path. | `DataDecl`, `MatchExpr`, `PipeExpr`, and `BindingTarget` still need owned surface nodes. | Add passive nodes first, then migrate lowering one feature at a time. |
| Core IR and backends | Core IR, verifier, Core Runtime, Core JSON, and JS runtime exist with growing parity fixtures. | Some Core lowering still projects backward from Python AST, so the source language is not fully represented before backend lowering. | Promote small Surface -> Core paths and mark unsupported forms honestly. |
| Runtime result contract | `ExecutionResult`, stdout/stderr capture, runtime sessions, and passive diagnostics/events exist. | Real diagnostics, semantic events, and detailed stage artifacts are sparse; notebook still has a separate streaming shape. | Wire no-op-to-real event producers gradually and migrate notebook once streaming semantics are clear. |
| Frontend consistency | CLI and web have moved toward the runtime facade. | Web, notebook, CLI, tests, and future REPL do not yet consume one complete diagnostic/event/output contract. | Treat frontend adapters as contract tests for the runtime API. |
| Feature profiles | Parser/cache keys have typed placeholders for profile, parser, grammar, source identity, and span mode. | Named profiles such as `default`, `lab`, `target-tour`, and `docs-only` are not fully selectable. | Add profile selection without changing default behavior, then use it for target fixtures. |
| Tests | Multi-interpreter regression and backend fixture parity are strong. | Feature-owned test templates are not yet mandatory across parse, lower, runtime, reduced, backend, docs, web, and notebook. | Add a template and require each promoted feature to declare what it covers and what remains target-only. |
| Diagnostics and explanation | The docs have a strong explanation direction and passive event records. | Binding, match, decode, pipeline, block, and backend errors can still invent private failure shapes. | Define one semantic event vocabulary before adding feature-specific explanations. |
| Performance | Manual performance notes and cache work are visible. | Budgets are not automated enough to protect LALR, postlex, session-cache, and Pyodide gains. | Add loose opt-in budget checks before richer parser profiles and frontends increase variance. |

## Leverage Gap Map

| Gap | Why it matters | Evolvable shape | First safe slice |
| --- | --- | --- | --- |
| Feature ownership packet | A feature can parse, lower, run, document, and expose unevenly while still looking "done." | One packet names owner, layer, normal form, status axes, grammar, surface node, Core node, reduction, diagnostics, tests, docs, samples, web, notebook, and backend requirements. | Extend existing feature metadata and render missing axes explicitly as unknown, target-only, partial, or unsupported. |
| Capability truth | Optimistic status labels make target-only syntax look implemented. | Capability axes are explicit facts, not lifecycle adjectives. | Promote reduced-mode, docs/spec, samples, web, notebook, diagnostics, and explanation from defaults to declared feature fields. |
| Surface/Core authority | Diagnostics and backends need Nomi-owned source representation, not Python AST side effects. | Surface nodes preserve source spans; Core IR owns stable normal forms; Python AST is one backend view. | Add passive `DataDecl`, `MatchExpr`, `PipeExpr`, and `BindingTarget` nodes before changing runtime behavior. |
| Binding target model | Assignments, parameters, data fields, block params, imports, and pattern captures are all name-introduction sites. | One `BindingTarget` model handles tentative bind, constraints, destructuring, commit/rollback, and diagnostics. | Start with annotated assignment, then reuse it for parameters and data fields. |
| Data declaration boundary | `data` currently risks becoming Python class sugar instead of a data-boundary story. | Owned data values plus explicit decode, provenance, defaults, redaction, and field constraints. | Move `data` to a surface node and write the decode-boundary feature packet before adding more field syntax. |
| Match expression semantics | IIFE lowering can accidentally define source-level `return` and failure behavior. | One `match` semantic core with expression value contract and clear statement/expression lowering. | Give `MatchExpr` a surface/core representation and align it with expression/statement orientation. |
| Semantic event protocol | Each feature can explain failure differently unless events are shared. | Parser, lowering, runtime, and backend stages emit typed events with source span, rule, value summary, failure kind, and redaction policy. | Keep no-op collector hooks, then add binding and match events first. |
| Runtime/frontend result contract | A feature is not really user-facing until CLI, web, notebook, and tests agree on output and errors. | `ExecutionResult` carries bindings, value, stdout, stderr, diagnostics, events, timings, artifacts, and exception policy. | Add stage artifact fields after frontend adapters settle; migrate notebook carefully. |
| Feature profiles | Target-language exploration needs syntax that can parse for docs without pretending to run. | `default`, `lab`, `target-tour`, and `docs-only` profiles select features, diagnostics strictness, and cache identity. | Thread profile through parser and runtime APIs while keeping `default` unchanged. |
| Test matrix | Snapshots alone cannot say whether syntax is accepted, target-only, rejected, or partially implemented. | Feature tests declare parse snapshots, lowering snapshots, diagnostics, runtime behavior, reduced invariants, backend parity, samples, docs, web, and notebook. | Add a generated or hand-maintained template and fail only on promoted axes at first. |
| Soft keyword and postlexer contract | Contextual syntax is powerful but can turn into invisible grammar policy. | Token rewrites have owner metadata, fixtures, conflict review, and performance notes. | Keep token-stream contract tests near every new soft keyword or virtual token. |
| Host capability boundary | Browser, CLI, notebook, Docker, and future backends should not learn different language meanings. | Host adapters declare filesystem, stdout, timing, package loading, cancellation, secrets, network, and artifact access. | Treat the web manifest as the first runtime artifact bundle contract. |
| Agent workflow contract | AI tools can overfit to stale implementation mechanics unless the workflow says what is prototype residue. | Skills and docs require feature-owned, status-honest, layer-aware, inspectable changes. | Link this review from the language-design skill and TODO index. |

## Feature Packet Gate

Before promoting a major feature from design to implementation, the feature
should answer these questions. It can answer "not yet" honestly, but the answer
should be visible.

| Packet field | Required question |
| --- | --- |
| Everyday pressure | What common programming act does this improve? |
| Primary surface | Is this syntax, function/library convention, block policy, data value, or tooling view? |
| Normal form | Does it reduce to binding, function, pattern, flow, block, absence/result, data boundary, or explanation? |
| Layer | Is it L2 semantic core, L3 canonical surface, L4 sugar, L5 library, L6 scoped extension, or L7 backend? |
| Reduction target | If sugar, what does it expand to before eval? |
| Surface/Core shape | Which Nomi-owned nodes represent it before backend lowering? |
| Capability axes | Does it parse, lower, run, reduce, explain, document, sample, web-expose, notebook-expose, and backend-port? |
| Diagnostics | What failure kind, source span, value summary, and user next step appear? |
| Tests | Which parse, lowering, runtime, reduced, backend, frontend, and docs checks prove the status? |
| Reversibility | What can be changed later without breaking user code, and what would become hard to undo? |

This gate should stay lightweight. It is a guard against accidental permanence,
not a reason to delay useful spikes.

## Implementation Slice Order

The safest next implementation line is mostly passive at first:

1. Add this review to the planning spine so future implementation work sees the
   evolvability bar before it touches grammar or runtime.
2. Make the feature capability matrix more explicit: docs/spec, samples, web,
   notebook, reduced mode, diagnostics, explanation, and backend support should
   be feature facts, not inferred optimism.
3. Add passive Nomi-owned surface nodes for `BindingTarget`, `DataDecl`,
   `MatchExpr`, and `PipeExpr`, preserving existing behavior where possible.
4. Define the semantic event schema as records and no-op collection paths before
   feature-specific diagnostics grow.
5. Promote a tiny authoritative Surface -> Core lowering path for stable forms
   and keep unsupported forms visible as diagnostics or capability gaps.
6. Complete the shared `ExecutionResult` contract with stage artifacts and
   migrate notebook display without losing streaming behavior.
7. Thread named feature profiles through parser/runtime/cache identity while
   leaving the default language unchanged.
8. Add feature-owned test templates, then require them only for features being
   promoted from target/design to prototype-ready.
9. Use capability-aware frontend toggles in web/notebook so users can see what
   is implemented, experimental, target-only, or intentionally unavailable.

## What Not To Do

- Do not do a package-wide move before facades and contract tests prove the
  migration path.
- Do not add permanent evaluator behavior for L4 sugar; reduce it before eval.
- Do not make Python AST or any one backend the language definition.
- Do not promote target-only examples into runnable samples before parser,
  runtime, tests, and snapshots agree.
- Do not add special-case syntax for a narrow domain when a library function,
  data value, block policy, or scoped extension can carry the pressure.
- Do not treat derived capability tables as proof of completeness.
- Do not let web, notebook, CLI, and tests develop private error formats.
- Do not optimize by removing inspection or source provenance; measure first.

## Definition Of Evolvable

A Nomi implementation change is evolvable when:

- it names the feature owner and layer;
- it states whether current behavior is implemented, prototype-ready,
  design-needed, target-only, library-first, research-only, or rejected-for-now;
- it has an inspectable normal form or explicitly explains why it does not yet;
- it keeps source spans and diagnostics available at the earliest practical
  stage;
- it updates capability metadata rather than relying on prose alone;
- it adds focused tests at the lowest useful layer;
- it does not make one frontend or backend the hidden source of truth;
- it preserves a clear path to remove or revise the experiment.

This is the implementation counterpart to
[`syntax_special_forms_quality_review.md`](../convenience/syntax_special_forms_quality_review.md):
syntax quality asks whether a form deserves to exist; evolvability asks whether
the project can keep learning after it exists.

For a grounded survey of modern implementation tools and the concrete artifacts
they teach Nomi to preserve, see
[`modern_language_implementation_artifacts.md`](modern_language_implementation_artifacts.md).
