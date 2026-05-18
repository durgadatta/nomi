# Implementation Codebase Audit

> Status: active implementation critique.
>
> Scope: codebase scan and improvement map. This document links concrete code
> seams to central TODO IDs. It does not specify language behavior; feature
> behavior belongs in `language_spec.md` and focused feature docs.

## Purpose

The design docs now point toward one operational language spec. The
implementation still carries several bootstrap-era choices that are useful but
will fight the target language if they harden:

```text
Lark tree -> direct Python AST -> Python-compatible interpreter
```

That path is good for early execution. It is weak for source-spanned
diagnostics, data boundaries, normal-form explanation, target-only feature
profiles, and feature-owned tests.

This audit records the main implementation improvement areas found in the
May 2026 scan and points each one to an existing or new central TODO.

## High-Priority Findings

| Area | Finding | Risk | Central TODO |
| --- | --- | --- | --- |
| Parser cache and profiles | Parser and raw-tree caches are keyed by extra layers and code hash, not full source identity, feature profile, or versioned grammar state. | Future feature profiles, docs-only parsing, and target-tour inspection can reuse stale or wrong parse artifacts. | `NOMI-SUBSTRATE-029` |
| Surface AST coverage | `BlockCall` has a surface node, but `data`, match expressions, pipeline, and binding targets still lower directly to Python AST. | Normal-form inspection and diagnostics will be inconsistent by feature. | `NOMI-SUBSTRATE-005`, `NOMI-SUBSTRATE-030`, `NOMI-SUBSTRATE-031` |
| Binding and constraints | Runtime constraints are centered on `AnnAssign` name targets; parameters, data fields, patterns, imports, and block params do not share one `BindingTarget`. | The one-binding story can diverge silently at each name-introduction site. | `NOMI-SUBSTRATE-011` |
| Data declarations | `data` currently generates `ClassDef` plus `TypeError` field checks, without owned data surface nodes, decode/provenance, redaction, or `BindingError` integration. | Target `data`/decode semantics cannot be explained or diagnosed through the current path. | `NOMI-SUBSTRATE-030` |
| Match expressions | Match expressions lower through IIFE wrappers with Python `return` semantics. | `return`, source spans, pattern failure, guard failure, and constraint failure can be hard to explain. | `NOMI-SUBSTRATE-031` |
| Runtime result contract | `ExecutionResult` exists, but stdout/stderr, diagnostics, semantic events, stage artifacts, and detailed timings are not wired. | Frontends cannot converge on one explanation/output contract. | `NOMI-ARCH-004`, `NOMI-ARCH-009`, `NOMI-ARCH-013` |
| Interpreter dispatch | `eval_*` method-name dispatch is simple, but feature ownership, node kinds, resumable policy, and trace hooks are not metadata. | Explanation, reduced-interpreter contracts, and feature manifests cannot align with runtime behavior. | `NOMI-SUBSTRATE-024` |
| Resumable control | Generator/block execution has paused-frame TODOs and mixed resumable/non-resumable paths. | Block policies, retries, transactions, cleanup, and future concurrency can inherit unclear control semantics. | `NOMI-ARCH-014` |
| Web/notebook exposure | Runtime facade exists, but feature profiles and inspection are not yet a shared frontend contract. | Target-language labs and current samples may drift apart. | `NOMI-ARCH-003`, `NOMI-SUBSTRATE-027` |
| Tests and capability matrix | Tests are strong by interpreter mode, but feature status is not declared in one machine-readable matrix. | Implemented, partial, target-only, and rejected syntax remain scattered across docs and tests. | `NOMI-SUBSTRATE-021`, `NOMI-SUBSTRATE-026` |
| Postlexer disambiguation | LALR speed depends on token rewrites for contextual syntax. | New expressive syntax can turn the postlexer into an undocumented grammar and perf hotspot. | `NOMI-SUBSTRATE-032` |
| Desugar pass profiles | Default Nomi mode chooses passes by class-name allowlist. | Feature inclusion can drift as names change or profiles multiply. | `NOMI-SUBSTRATE-033` |
| Runtime cache identity | `RuntimeSession` caches lowered ASTs by source text only. | Feature profiles, span modes, grammar versions, or filename changes can reuse unsafe artifacts. | `NOMI-ARCH-015` |
| Call-frame ownership | Function calls shallow-copy environments. | Future constraints, capabilities, and block policies need explicit ownership and faster frame setup. | `NOMI-ARCH-016` |
| Performance budgets | Manual performance notes are strong but not automated. | Flexibility work can quietly erase LALR/session-cache gains. | `NOMI-ARCH-017` |

## Inline TODO Anchors Added

| ID | File | Why this location matters |
| --- | --- | --- |
| `NOMI-SUBSTRATE-011` | `prototype/interpreter/nomi/binding.py` | Current constraint engine assumes annotated assignment names and should become a shared binding target model. |
| `NOMI-SUBSTRATE-029` | `prototype/parser/nomi/usage.py` | Parser/raw-tree cache keys must grow feature profile and source identity before target parsing modes. |
| `NOMI-SUBSTRATE-030` | `prototype/parser/nomi/lowering/data_decl.py` | `data` lowering needs an owned surface node and shared binding/diagnostic/decode semantics. |
| `NOMI-SUBSTRATE-031` | `prototype/parser/nomi/lowering/match_expr.py` | Match-expression IIFE lowering needs a surface/core representation for diagnostics and control clarity. |
| `NOMI-ARCH-013` | `prototype/runtime/api.py` | Public execution should collect diagnostics/events as first-class result fields. |
| `NOMI-ARCH-014` | `prototype/interpreter/python/generator_state.py` | Resumable control needs an explicit frame/policy model before richer block policies. |
| `NOMI-SUBSTRATE-032` | `prototype/parser/nomi/postlexer.py` | Postlexer rewrites need fixture snapshots, feature ownership, and performance budget coverage. |
| `NOMI-SUBSTRATE-033` | `prototype/parser/nomi/desugar/pipeline.py` | Default/reduced/lab pass selection should be feature manifest metadata. |
| `NOMI-ARCH-015` | `prototype/runtime/session.py` | Runtime AST cache keys need mode/profile/source/span/grammar identity. |
| `NOMI-ARCH-016` | `prototype/interpreter/python/function.py`, `prototype/interpreter/python/env.py` | Call-frame/environment ownership needs to be explicit before more semantic state is added. |
| `NOMI-ARCH-017` | `docs/orientation/performance_notes.md` | Performance budgets should protect parse/lower/desugar/eval/session paths. |

## Subsystem Notes

### Parser And Grammar

The grammar assembly is already better than the original hardcoded path:
`BUILTIN_FEATURES` contributes layers and transforms. The next weakness is
selection. Current code can accept `extra_layers`, but it does not model
profiles such as `default`, `lab`, `target-tour`, or `docs-only`.

Next move: add a feature-set parser API that resolves manifests, profile name,
grammar version, and source identity into parser/cache keys.

### Surface And Core Representation

The existence of `SurfaceNode` and `BlockCall` proves the path, but most
interesting features still jump directly to Python AST. That keeps execution
simple but makes explanation hard.

Next move: migrate `DataDecl`, `MatchExpr`, `PipeExpr`, and `BindingTarget` to
surface nodes before implementing more target syntax.

### Binding And Data

The runtime constraint engine is useful and tested, but it is not yet the
one-binding substrate promised by the design. Data fields currently generate
class constructors and field checks directly; they do not cross a decode
boundary or emit structured binding diagnostics.

Next move: implement `BindingTarget` for annotated assignment first, then
reuse it for parameters and data fields.

### Runtime API And Frontends

`prototype/runtime/api.py` and `RuntimeSession` are good facade starts.
However, the facade does not yet own stdout/stderr capture, diagnostics,
semantic events, stage artifacts, or frontend-equivalent behavior.

Next move: extend `ExecutionResult` with passive `diagnostics`, `events`,
`stdout`, and `stderr` fields while keeping existing callers compatible.

### Tests

Interpreter-mode parametrization is strong. Feature-profile parametrization is
not present yet. Target-only docs make this more urgent, because future tests
need to say whether a feature parses, lowers, runs, explains, appears in web,
or belongs only to target fixtures.

Next move: create a passive machine-readable capability matrix, then generate
docs tables from it later if useful.

## Suggested Phase Order

1. Add the capability/spec matrix as passive data.
2. Extend parser/cache APIs to accept feature profiles without changing the
   default language.
3. Add passive diagnostic/event fields to `ExecutionResult`.
4. Move `DataDecl`, `MatchExpr`, and `BindingTarget` onto the surface-node path.
5. Add feature-owned test templates and parse/lowering snapshots.
6. Start implementing data-boundary and failure-taxonomy feature packets.
