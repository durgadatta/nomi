# Adversarial Implementation Critique

> Status: active implementation critique.
>
> Scope: current parser, lowering, desugar, runtime, caching, and performance
> architecture. This document is intentionally skeptical. It does not change
> behavior; it identifies where the implementation can become brittle or slow
> as Nomi adds more expressive language features.

## Purpose

Nomi's current prototype has made real progress: LALR parsing, feature
manifests, selected default desugar passes, source-span opt-in, a runtime
facade, sessions, and AST caching. The implementation is now fast enough for
current demos.

Refresh note, 2026-05-19: this document was updated after a second codebase
scan. The earlier "class-name filtered desugar profile" critique is no longer
accurate; desugar pass selection now comes from feature metadata. The remaining
adversarial point is harsher: the registry can describe layers and profiles
better than the rest of the system can enforce, inspect, or expose them.

The adversarial question is different:

```text
Will this architecture stay flexible and fast after more syntax, data
boundaries, block policies, explain traces, feature profiles, and target-only
parse modes are added?
```

Answer: not without a few structural guardrails.

## Executive Critique

The current implementation has three major pressure points:

1. **Parser flexibility is concentrated in the postlexer.** This was the right
   move for LALR speed, but every new context-sensitive convenience can add
   another token-rewrite rule unless the postlexer gains a declared contract
   and regression snapshots.
2. **Lowering still jumps too quickly to Python AST.** Direct Python AST is
   fast and executable, but it hides Nomi's normal forms and source spans,
   making future diagnostics and explain views harder.
3. **Public surfaces do not yet share one result contract.** CLI, web, and
   notebook execution still package output, timings, and errors differently,
   which will make diagnostics/events drift unless `ExecutionResult` becomes
   the shared adapter boundary.
4. **Performance wins are not yet protected by budgets.** The performance
   notes show excellent manual profiling, but there is no automated gate that
   catches parser construction, postlexer, desugar, session-cache, or runtime
   regressions.

The implementation should not optimize prematurely, but it should make fast
paths explicit now, before expressive syntax multiplies.

## Risk Register

| Risk | Severity | Flexibility impact | Speed impact | Required response |
| --- | --- | --- | --- | --- |
| Postlexer becomes a hidden grammar | High | New syntax depends on token-rewrite heuristics that are hard to reason about locally. | Full token buffering and repeated scans can grow with every disambiguation. | `NOMI-SUBSTRATE-032`: declared postlexer contract + fixtures + perf notes. |
| Direct Python AST lowering hides Nomi nodes | High | New features cannot be inspected as Nomi normal forms. | Later diagnostics require expensive reverse mapping. | Continue `DataDecl`, `MatchExpr`, `BindingTarget`, `PipeExpr` surface-node migration. |
| Core IR becomes decorative | High | The project can point at Core IR while real semantics still flow through Python AST. | Future backends and diagnostics inherit a misleading artifact boundary. | `NOMI-ARCH-019`: make Surface -> Core lowering authoritative for a tiny subset. |
| Capability status lies by omission | High | Derived capability axes exist, but some rows still infer support from status/docs/tests rather than feature-owned proof. | Tooling and docs can overstate maturity. | `NOMI-SUBSTRATE-035`: make incomplete axes explicit per feature. |
| Cache identity is under-specified | High | Parser caches can still reuse wrong artifacts once feature profiles and target parsing arrive. | Cache invalidation bugs lead to false performance wins or stale execution. | `NOMI-SUBSTRATE-029`: typed parser cache keys. |
| Profile plumbing stops halfway | Medium | Desugar metadata exists, but parser/runtime inspection still cannot fully select or prove named profiles. | Extra passes or missing passes become hidden hot-path work. | `NOMI-SUBSTRATE-033`, `NOMI-ARCH-002`: end-to-end profile selection and inspection. |
| Runtime session cache key can go stale | Medium | `RuntimeCacheKey` exists, but grammar/profile version fields are placeholders until profiles become real. | Good speed path can become unsafe if future profile work bypasses the key. | `NOMI-ARCH-015`: update typed key inputs as profile/version APIs land. |
| Environment copy per call remains broad | Medium | Constraints and future capabilities may be copied without explicit ownership. | Function-heavy programs can pay avoidable dictionary-copy cost. | `NOMI-ARCH-016`: call-frame strategy and binding/capability ownership model. |
| Interpreter dispatch lacks semantic metadata | Medium | Feature ownership and explain hooks stay detached from runtime behavior. | Events may be layered later with extra indirection. | `NOMI-SUBSTRATE-024`: dispatch metadata while preserving fast method lookup. |
| Frontend result contracts fork | Medium | CLI, web, and notebook display different error/output/timing shapes. | Future diagnostics require adapter-specific code. | `NOMI-ARCH-023`, `NOMI-ARCH-024`: one `ExecutionResult` contract. |
| Performance remains manually checked | Medium | Contributors cannot know which changes are safe. | Regressions arrive silently. | `NOMI-ARCH-017`: performance budget suite for parse/lower/desugar/session/eval. |

## Parser And Grammar Critique

### What Is Strong

- LALR migration removed the old Earley bottleneck.
- Persistent Lark analysis cache addresses short-lived CLI startup.
- Source spans are opt-in on the fast path.
- Grammar layers and parse-tree transforms are registry-derived.

### What Is Fragile

`NomiPostLexer` currently buffers the full indented token stream and performs
several context scans to emit virtual tokens. That is acceptable for current
files. It becomes risky when new features add:

- more contextual operators;
- syntax islands;
- query/table row shorthand;
- target-only profile tokens;
- Unicode/source-text diagnostics;
- soft-keyword expansion.

The danger is not only runtime cost. The danger is semantic opacity: the
postlexer becomes a second grammar hidden in Python code.

Required response:

- add fixtures for postlexer token rewrites;
- document every virtual token as part of a postlexer contract;
- keep O(n) scans visible and measured;
- refuse syntax that needs a maze of token rewrites when a surface node or
  clearer grammar rule would do.

## Lowering And Surface AST Critique

Surface nodes are the escape route from Python AST gravity. Right now only
`BlockCall` fully proves that path. Data declarations, match expressions,
pipelines, binding targets, and future syntax islands still need it.

Direct Python AST lowering is tempting because it runs immediately. But the
cost shows up later:

- source spans are lost or need side tables;
- normal-form expansion is hard to show;
- diagnostics speak Python internals;
- target-only parse modes cannot inspect partial syntax;
- reduced-interpreter invariants track Python AST shapes instead of Nomi core
  shapes.

Required response:

- migrate awkward features to surface nodes before adding more syntax;
- keep Python AST as a backend, not the semantic substrate;
- expose surface/core/backend stages through inspection tools;
- avoid generated Python AST tricks for any feature whose diagnostic story
  matters.

## Desugar Pipeline And Profile Critique

The desugar pipeline is much improved: pass metadata, dependencies, and
invariant checks exist. Feature metadata now declares default and reduced
desugar inclusion. The weak spot has moved up a layer: runtime and inspection
profiles are still too shallow.

The hostile reading: Nomi now has a feature manifest that looks like a source
of truth, but the parser, runtime facade, inspection API, docs matrix, web, and
notebook do not yet prove the same feature set end to end.

Required response:

- keep pass selection manifest-derived;
- route runtime profiles through parser, lowering, desugar, inspection, and
  session caches;
- inspection should show which passes ran and why for the selected mode/profile;
- tests should fail when docs claim a feature is runnable but the profile
  cannot actually parse/lower/run it.

## Runtime And Interpreter Critique

The interpreter is serviceable and easy to read. It is also Python-AST-shaped
in ways that will strain Nomi-specific semantics.

Current risks:

- every call copies an environment;
- constraints live on environment dictionaries rather than binding targets;
- resumable control relies on paused-frame dictionaries and list order;
- exceptions are pass-through or wrapped, not structured diagnostics;
- dispatch is fast but semantically anonymous;
- block policy behavior is piggybacked on generator creation.

Required response:

- add semantic metadata to dispatch without slowing the fast path;
- define call-frame and constraint ownership before data/decode/capability work;
- model resumable frames explicitly before retry/transaction/concurrency;
- move diagnostics/events into `ExecutionResult` and runtime sessions.

## Frontend And Tooling Critique

The current frontends are useful, but adversarially they are three forks of the
same truth:

- `scripts/cli.py` still calls compatibility runners directly;
- `web/nomi_web.py` captures stdout and returns a private dictionary shape;
- `tools/jupyter/nomi_kernel.py` maps exceptions to Jupyter traceback payloads
  without a shared diagnostic/event source.

This is acceptable while output is mostly text. It will become expensive once
binding errors, decode diagnostics, traces, examples, and redaction policies
matter.

Required response:

- make `ExecutionResult` carry passive stdout/stderr, diagnostics, events, and
  structured errors;
- make CLI/web/notebook adapters display that shared result instead of
  inventing local payloads;
- add contract tests that prove the same source produces equivalent structured
  failure information across surfaces.

## Performance Critique

The current performance notes are unusually good for a prototype. The missing
piece is an automated guardrail.

Performance should be tracked at these layers:

```text
grammar assembly
parser construction/load
raw parse
postlexer token rewrite
tree transform
surface lowering
desugar passes
runtime eval
session cache hit
web/notebook bridge
```

Required response:

- add a small benchmark suite with budgets, not just manual profiler output;
- keep budgets loose enough for CI but sharp enough to catch 2x regressions;
- include default mode, reduced mode, span-enabled mode, and session-cache mode;
- record performance-sensitive design decisions in feature manifests.

## Inline TODO Anchors Added

| ID | File | Why it matters |
| --- | --- | --- |
| `NOMI-SUBSTRATE-032` | `prototype/parser/nomi/postlexer.py` | Prevent token rewrites from becoming an undocumented grammar and performance sink. |
| `NOMI-SUBSTRATE-033` | `prototype/parser/nomi/desugar/pipeline.py`, `prototype/runtime/api.py` | Keep manifest-backed pass selection and make inspection honor concrete runtime profiles. |
| `NOMI-SUBSTRATE-035` | `prototype/syntax/features.py` | Derived capability axes exist; prevent inferred axes from becoming fake proof. |
| `NOMI-ARCH-019` | `prototype/syntax/core.py` | Prevent passive Core IR from becoming decorative while Python AST remains authoritative. |
| `NOMI-ARCH-015` | `prototype/runtime/session.py` | Runtime cache key is typed; keep profile/grammar/span fields honest as those APIs grow. |
| `NOMI-ARCH-016` | `prototype/interpreter/python/function.py`, `prototype/interpreter/python/env.py` | Define call-frame/environment ownership before constraints/capabilities make copies expensive or wrong. |
| `NOMI-ARCH-017` | `docs/orientation/performance_notes.md` | Add automated performance budgets for flexibility work. |
| `NOMI-ARCH-023` | `scripts/cli.py` | CLI now uses the public runtime facade; structured diagnostic display remains future work. |
| `NOMI-ARCH-024` | `web/nomi_web.py`, `tools/jupyter/nomi_kernel.py` | Web consumes captured runtime results; notebook still needs result-contract migration. |

## Required Next Moves

1. Add postlexer fixture snapshots before adding more contextual syntax.
2. Split feature status into capability axes.
3. Make tiny Surface -> Core lowering authoritative before expanding Core IR.
4. Add typed parser cache keys and keep runtime cache version fields current.
5. Make runtime/profile inspection show concrete selected passes.
6. Migrate notebook onto the shared result contract.
7. Route real parser/lowering/runtime events through `RuntimeEventCollector`
   without letting features invent private diagnostic shapes.
8. Create a minimal performance budget suite around `samples/demo.nomi`,
   `samples/demo_verbose.nomi`, and a synthetic feature-heavy file.
9. Migrate `DataDecl`, `MatchExpr`, and `BindingTarget` to surface nodes before
   expanding target syntax.

## Extreme Failure Scenario

The worst plausible outcome is not that Nomi lacks features. It is that Nomi
gets enough attractive syntax to demo well while the implementation cannot say
what the syntax means except by showing generated Python AST. In that world:

- the feature manifest becomes decorative metadata;
- Core IR is an inspection toy;
- diagnostics reverse-engineer meaning after the fact;
- web and notebook behavior diverge;
- target examples make the language look further along than it is;
- performance fixes become folklore rather than tests;
- future contributors add conveniences by finding the nearest lowering hack.

The antidote is deliberately small and concrete: one capability matrix, one
shared result contract, one real Surface -> Core path for a tiny subset, and
no new high-level syntax without inspection, diagnostics, tests, and status.

## Decision Pressure

Nomi should accept a small amount of architecture ceremony now to keep later
syntax cheap. The goal is not a plugin system or a compiler framework. The goal
is a fast hot path with explicit extension seams:

```text
feature manifest -> grammar/postlexer contract -> surface node -> core normal
form -> backend/runtime -> diagnostics/events -> tests/perf budget
```
