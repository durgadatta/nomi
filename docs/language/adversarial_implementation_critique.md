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
3. **Performance wins are not yet protected by budgets.** The performance
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
| Cache identity is under-specified | High | Feature profiles and target parsing can reuse wrong artifacts. | Cache invalidation bugs lead to false performance wins or stale execution. | `NOMI-SUBSTRATE-029`, `NOMI-ARCH-015`: typed parse/runtime cache keys. |
| Desugar subsets are name-filtered | Medium | Default/reduced mode behavior can drift when pass names change. | Extra passes become hidden hot-path work. | `NOMI-SUBSTRATE-033`: feature/pass profiles declare default vs reduced inclusion. |
| Runtime session cache uses source text only | Medium | Filename, profile, mode, grammar version, and span mode are not part of the key. | Good speed path can be unsafe as profiles grow. | `NOMI-ARCH-015`: typed runtime cache key and invalidation policy. |
| Environment copy per call remains broad | Medium | Constraints and future capabilities may be copied without explicit ownership. | Function-heavy programs can pay avoidable dictionary-copy cost. | `NOMI-ARCH-016`: call-frame strategy and binding/capability ownership model. |
| Interpreter dispatch lacks semantic metadata | Medium | Feature ownership and explain hooks stay detached from runtime behavior. | Events may be layered later with extra indirection. | `NOMI-SUBSTRATE-024`: dispatch metadata while preserving fast method lookup. |
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

## Desugar Pipeline Critique

The desugar pipeline is much improved: pass metadata, dependencies, and
invariant checks exist. The weak spot is default Nomi desugar selection:

```python
if pass_cls.__name__ in {...}
```

This is a hidden profile. It should become manifest data.

Required response:

- feature manifests should declare default-mode inclusion, reduced-mode
  inclusion, normal form, and performance expectations;
- pass selection should use feature metadata rather than class-name sets;
- inspection should show which passes ran and why.

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
| `NOMI-SUBSTRATE-033` | `prototype/parser/nomi/desugar/pipeline.py` | Replace class-name filtered default passes with feature/pass profile metadata. |
| `NOMI-ARCH-015` | `prototype/runtime/session.py` | Make runtime AST cache keys safe for mode/profile/source/span/grammar changes. |
| `NOMI-ARCH-016` | `prototype/interpreter/python/function.py`, `prototype/interpreter/python/env.py` | Define call-frame/environment ownership before constraints/capabilities make copies expensive or wrong. |
| `NOMI-ARCH-017` | `docs/orientation/performance_notes.md` | Add automated performance budgets for flexibility work. |

## Required Next Moves

1. Add postlexer fixture snapshots before adding more contextual syntax.
2. Add typed parse/runtime cache keys.
3. Move desugar pass inclusion into feature manifest metadata.
4. Add passive diagnostics/events fields to `ExecutionResult`.
5. Create a minimal performance budget suite around `samples/demo.nomi`,
   `samples/demo_verbose.nomi`, and a synthetic feature-heavy file.
6. Migrate `DataDecl`, `MatchExpr`, and `BindingTarget` to surface nodes before
   expanding target syntax.

## Decision Pressure

Nomi should accept a small amount of architecture ceremony now to keep later
syntax cheap. The goal is not a plugin system or a compiler framework. The goal
is a fast hot path with explicit extension seams:

```text
feature manifest -> grammar/postlexer contract -> surface node -> core normal
form -> backend/runtime -> diagnostics/events -> tests/perf budget
```
