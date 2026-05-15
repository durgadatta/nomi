# Declarative Implementation Plan

> Status: active. Phase A implementation in progress; B and C are deferred design.
>
> Goal: make the implementation increasingly data-driven so adding syntax
> requires touching fewer files and the Python substrate can eventually be
> replaced by a Nomi-native backend.

## Motivation

The current implementation already has good declarative foundations:
- `SyntaxFeature` registry (single source of truth for features)
- `ModeSpec` registry (interpreter modes as data)
- Auto-derived desugar pipeline and reduced-interpreter stubs

But several extension points still require manual edits across multiple files.
Every manual edit is a place where the next change breaks something.

## Phase A: Complete the Feature-Driven Extension Path

Make the extension path fully declarative so adding a new feature touches only
**one file** (features.py) plus the implementation module. No editing assembly,
lowering composition, or pipeline files.

### A1: Feature-driven lowering mixin composition

**Current:** `prototype/parser/nomi/functions.py` manually imports 13 lowering
mixins and lists them in the `FunctionsMixin` class definition.

**Target:** `FunctionsMixin` is built dynamically from the feature registry.
Each lowering feature declares its mixin as a dotted string; the composition
is auto-derived.

```
Before: FunctionsMixin = class(ImplicitMulMixin, TypeAliasMixin, ...13 total)
After:  FunctionsMixin = build_lowering_mixin()  # derived from BUILTIN_FEATURES
```

### A2: Feature-driven grammar layer assembly

**Current:** `_LAYER_ORDER` in `assemble.py` is a hardcoded list. The
`grammar_layers` field on `SyntaxFeature` exists but is never used.

**Target:** `assemble_grammar()` appends feature-declared layers after the
base layers. No editing `assemble.py` to add a new grammar domain.

### A3: Phase metadata for desugar passes

**Current:** Desugar passes run in declaration order. Dependencies between
passes are implicit comments. No validation that ordering is correct.

**Target:** Each pass declares its phase (`syntax`, `semantic`, `cleanup`) and
optional `depends_on`. The pipeline validates that phases group correctly and
dependencies are satisfied. A pass running in the wrong phase is a loud error,
not a silent bug.

## Phase B: Operation Registry for the Interpreter

**Deferred.** Will be designed and implemented after Phase A settles.

**Goal:** Replace convention-based `eval_*` dispatch with explicit operation
registration. Each operation declares: owning feature, accepted AST node types,
resumability policy, diagnostic category, and trace hooks.

This is a metadata layer on top of existing methods — not a rewrite of the
eval logic. Benefits:
- Auto-generated trace/diagnostic hooks
- Feature gating at runtime (disable a feature → its operations become no-ops
  with clear diagnostics)
- Self-documenting interpreter surface

## Phase C: Semantic IR

**Deferred.** Depends on language design settling further and Phase B being
stable.

**Goal:** A small set of IR nodes (Binding, Call, Match, Block, Flow,
DataConstruct, etc.) between surface AST and interpreter. The interpreter
walks IR instead of Python AST directly.

Benefits:
- Python-independent: the interpreter doesn't know about `ast.Call` vs
  `ast.FunctionDef` — it knows about `ir.Call`, `ir.Function`, etc.
- Cleaner diagnostics: errors speak in IR concepts, not Python AST terms
- Smoother backend migration: a new backend (native code, WASM, etc.) only
  needs to consume the IR, not reimplement Python AST semantics

## Success Criteria

After Phase A:
- Adding a new syntax feature requires: 1 entry in `BUILTIN_FEATURES` + the
  implementation module (lowering, desugar, or both). No editing assembly,
  pipeline, or composition files.
- Phased desugar passes self-validate: a pass in the wrong phase or missing a
  dependency fails fast with a clear error.
