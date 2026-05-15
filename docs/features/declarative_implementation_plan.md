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

### A1: Feature-driven lowering mixin composition ✅

~~**Current:** `prototype/parser/nomi/functions.py` manually imports 13 lowering
mixins and lists them in the `FunctionsMixin` class definition.~~

**Done:** `FunctionsMixin` is built dynamically via `get_lowering_mixins()`
which reads dotted-string references from `BUILTIN_FEATURES`. Adding a
lowering mixin means adding one feature entry + the module — no editing
`functions.py`.

### A2: Feature-driven grammar layer assembly ✅

~~**Current:** `_LAYER_ORDER` in `assemble.py` is a hardcoded list.~~

**Done:** `assemble_grammar()` calls `get_extra_grammar_layers()` to append
feature-declared layers after the base layers. Layer transforms are also
derived from features via `get_layer_transforms()`. Adding a grammar layer
means declaring `grammar_layers` on the feature — no editing `assemble.py`.

### A3: Phase metadata for desugar passes (partial)

~~**Current:** Desugar passes run in declaration order. Dependencies between
passes are implicit comments. No validation that ordering is correct.~~

**Done:** `Phase` enum (syntax → semantic → cleanup), `depends_on` tuple,
and `removed_node_types` fields exist on `BaseDesugarer`. Pipeline validates
dependencies at import time. 10 of 11 passes declare their phase.
`WhereClause` declares `depends_on=(PiecewiseFunction,)`.

**Remaining:** `Precedence` needs a phase declaration. Most passes that
could declare `depends_on` still leave it empty (dependencies are enforced
by ordering in `BUILTIN_FEATURES`). `removed_node_types` is declared on
~half the passes; the rest could declare it for completeness.

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
