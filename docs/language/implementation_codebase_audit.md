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

## Latest Refresh: 2026-05-19

This pass checked the current code against the earlier audit. Several earlier
findings have improved: desugar pass selection is now derived from feature
metadata, pass phases are executable, reduced-mode checks are linked to pass
metadata, and the passive Core IR skeleton plus inspection stages exist.

The hard critique now shifts from "add the first seams" to "make the seams
truthful enough to steer work." The current risks are:

- feature `status` is still one coarse label rather than a capability matrix;
- Core IR inspection is currently a backward projection from Python AST, not
  the authoritative Surface -> Core path;
- CLI, web, and notebook still shape output/errors differently;
- parser cache keys remain too small for feature profiles and
  docs-only/target-tour parsing; runtime session cache keys are now typed;
- postlexer rules are fast and practical but still need token-rewrite fixtures;
- generated Python AST is still doing too much semantic work for data, match,
  and binding.

The adversarial version of this refresh is tracked in
[`adversarial_implementation_critique.md`](adversarial_implementation_critique.md).

## High-Priority Findings

| Area | Finding | Risk | Central TODO |
| --- | --- | --- | --- |
| Parser cache and profiles | Parser and raw-tree caches are keyed by extra layers and code hash, not full source identity, feature profile, or versioned grammar state. | Future feature profiles, docs-only parsing, and target-tour inspection can reuse stale or wrong parse artifacts. | `NOMI-SUBSTRATE-029` |
| Surface AST coverage | `BlockCall` has a surface node, but `data`, match expressions, pipeline, and binding targets still lower directly to Python AST. | Normal-form inspection and diagnostics will be inconsistent by feature. | `NOMI-SUBSTRATE-005`, `NOMI-SUBSTRATE-030`, `NOMI-SUBSTRATE-031` |
| Core IR authority | `prototype.syntax.core` exists, but current lowering is Python AST -> Core for inspection only. | Core IR can look like a plan while Python AST remains the real language definition. | `NOMI-ARCH-019` |
| Capability status | `SyntaxFeature.status` is a single lifecycle label. | A feature can look implemented while parse, runtime, reduced, docs, samples, web, notebook, and explain coverage differ. | `NOMI-SUBSTRATE-035` |
| Binding and constraints | Runtime constraints are centered on `AnnAssign` name targets; parameters, data fields, patterns, imports, and block params do not share one `BindingTarget`. | The one-binding story can diverge silently at each name-introduction site. | `NOMI-SUBSTRATE-011` |
| Data declarations | `data` currently generates `ClassDef` plus `TypeError` field checks, without owned data surface nodes, decode/provenance, redaction, or `BindingError` integration. | Target `data`/decode semantics cannot be explained or diagnosed through the current path. | `NOMI-SUBSTRATE-030` |
| Match expressions | Match expressions lower through IIFE wrappers with Python `return` semantics. | `return`, source spans, pattern failure, guard failure, and constraint failure can be hard to explain. | `NOMI-SUBSTRATE-031` |
| Runtime result contract | `ExecutionResult` exists, but stdout/stderr, diagnostics, semantic events, stage artifacts, and detailed timings are not wired. | Frontends cannot converge on one explanation/output contract. | `NOMI-ARCH-004`, `NOMI-ARCH-009`, `NOMI-ARCH-013` |
| Frontend adapters | CLI, web, and notebook use or adapt different runtime/result paths. | Error display, stdout capture, timing, session state, and future diagnostics will drift across user surfaces. | `NOMI-ARCH-023`, `NOMI-ARCH-024` |
| Interpreter dispatch | `eval_*` method-name dispatch is simple, but feature ownership, node kinds, resumable policy, and trace hooks are not metadata. | Explanation, reduced-interpreter contracts, and feature manifests cannot align with runtime behavior. | `NOMI-SUBSTRATE-024` |
| Resumable control | Generator/block execution has paused-frame TODOs and mixed resumable/non-resumable paths. | Block policies, retries, transactions, cleanup, and future concurrency can inherit unclear control semantics. | `NOMI-ARCH-014` |
| Web/notebook exposure | Runtime facade exists, but feature profiles and inspection are not yet a shared frontend contract. | Target-language labs and current samples may drift apart. | `NOMI-ARCH-003`, `NOMI-SUBSTRATE-027` |
| Tests and capability matrix | Tests are strong by interpreter mode, but feature status is not declared in one machine-readable matrix. | Implemented, partial, target-only, and rejected syntax remain scattered across docs and tests. | `NOMI-SUBSTRATE-021`, `NOMI-SUBSTRATE-026` |
| Postlexer disambiguation | LALR speed depends on token rewrites for contextual syntax. | New expressive syntax can turn the postlexer into an undocumented grammar and perf hotspot. | `NOMI-SUBSTRATE-032` |
| Desugar and feature profiles | Desugar profiles are manifest-driven now, but runtime/parser profiles are still basically `default`. | The feature manifest can say more than the parser/runtime API can actually select or prove. | `NOMI-SUBSTRATE-033`, `NOMI-ARCH-002` |
| Runtime cache identity | `RuntimeSession` now uses `RuntimeCacheKey`, but parser/profile versioning is still mostly placeholder data. | Future feature profiles must update the key rather than bypassing it. | `NOMI-ARCH-015` |
| Call-frame ownership | Function calls shallow-copy environments. | Future constraints, capabilities, and block policies need explicit ownership and faster frame setup. | `NOMI-ARCH-016` |
| Performance budgets | Manual performance notes are strong but not automated. | Flexibility work can quietly erase LALR/session-cache gains. | `NOMI-ARCH-017` |
| Agent artifact hygiene | `.codex/hooks/**` is intentionally unignored, which can re-include generated Python caches unless explicitly blocked. | AI-tooling artifacts can leak into review noise or commits. | `NOMI-AGENT-001` |

## Inline TODO Anchors Added

| ID | File | Why this location matters |
| --- | --- | --- |
| `NOMI-SUBSTRATE-011` | `prototype/interpreter/nomi/binding.py` | Current constraint engine assumes annotated assignment names and should become a shared binding target model. |
| `NOMI-SUBSTRATE-029` | `prototype/parser/nomi/usage.py` | Parser/raw-tree cache keys must grow feature profile and source identity before target parsing modes. |
| `NOMI-SUBSTRATE-030` | `prototype/parser/nomi/lowering/data_decl.py` | `data` lowering needs an owned surface node and shared binding/diagnostic/decode semantics. |
| `NOMI-SUBSTRATE-031` | `prototype/parser/nomi/lowering/match_expr.py` | Match-expression IIFE lowering needs a surface/core representation for diagnostics and control clarity. |
| `NOMI-ARCH-013` | `prototype/runtime/api.py` | Public execution should collect diagnostics/events as first-class result fields. |
| `NOMI-ARCH-019` | `prototype/syntax/core.py` | Core IR must become a real Surface -> Core lowering target, not only Python AST back-projection. |
| `NOMI-ARCH-014` | `prototype/interpreter/python/generator_state.py` | Resumable control needs an explicit frame/policy model before richer block policies. |
| `NOMI-SUBSTRATE-032` | `prototype/parser/nomi/postlexer.py` | Postlexer rewrites need fixture snapshots, feature ownership, and performance budget coverage. |
| `NOMI-SUBSTRATE-033` | `prototype/parser/nomi/desugar/pipeline.py`, `prototype/runtime/api.py` | Desugar pass selection is manifest-backed; runtime inspection still needs to show the concrete mode/profile pass set. |
| `NOMI-SUBSTRATE-035` | `prototype/syntax/features.py` | Feature status must split into capability axes instead of one optimistic lifecycle label. |
| `NOMI-ARCH-015` | `prototype/runtime/session.py` | Runtime AST cache keys now carry mode/profile/source/span/grammar identity; update them as profiles become real. |
| `NOMI-ARCH-016` | `prototype/interpreter/python/function.py`, `prototype/interpreter/python/env.py` | Call-frame/environment ownership needs to be explicit before more semantic state is added. |
| `NOMI-ARCH-017` | `docs/orientation/performance_notes.md` | Performance budgets should protect parse/lower/desugar/eval/session paths. |
| `NOMI-ARCH-023` | `scripts/cli.py` | CLI should use the public runtime facade and structured result contract. |
| `NOMI-ARCH-024` | `web/nomi_web.py`, `tools/jupyter/nomi_kernel.py` | Frontends should adapt one `ExecutionResult` diagnostics/events/output shape. |
| `NOMI-AGENT-001` | `.gitignore` | Re-ignore generated hook caches after the tracked `.codex/hooks/**` allowlist. |

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
`ExecutionResult` now carries stdout/stderr plus passive diagnostics/events,
`execute()` captures stdout/stderr, `RuntimeSession.run()` can opt into output
capture, `RuntimeEventCollector` provides a no-op sink, and the CLI plus web
bridge consume the shared runtime facade. Notebook execution still streams
through kernel redirects, and real diagnostic/event producers are not wired
yet.

Next move: migrate notebook output display once the result contract can
preserve Jupyter streaming expectations, then route parser/lowering/runtime
events through the collector one feature at a time.

### Tests

Interpreter-mode parametrization is strong. Feature-profile parametrization is
not present yet. Target-only docs make this more urgent, because future tests
need to say whether a feature parses, lowers, runs, explains, appears in web,
or belongs only to target fixtures.

Next move: create a passive machine-readable capability matrix, then generate
docs tables from it later if useful.

## Suggested Phase Order

1. Add the capability/spec matrix as passive data.
2. Make Core IR lowering flow from Surface -> Core for the tiny supported
   subset, keeping Python AST as a backend view.
3. Extend parser/cache APIs to accept feature profiles without changing the
   default language.
4. Move notebook onto the shared runtime result shape.
5. Route parser/lowering/runtime events through `RuntimeEventCollector` one
   feature at a time.
6. Move `DataDecl`, `MatchExpr`, and `BindingTarget` onto the surface-node path.
7. Add feature-owned test templates and parse/lowering snapshots.
8. Start implementing data-boundary and failure-taxonomy feature packets.
