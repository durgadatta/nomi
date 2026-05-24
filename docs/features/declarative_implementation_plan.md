# Declarative Implementation Plan

> Status: active. Phase A implementation in progress; B and C are deferred design.
>
> Goal: make the implementation increasingly data-driven so adding syntax
> requires touching fewer files and the Python substrate can eventually be
> replaced by a Nomi-native backend.

This plan now sits under the broader
[`Exploratory Implementation Doctrine`](../orientation/exploratory_implementation_doctrine.md):
Nomi is early language-design work, so declarative metadata is not ceremony for
its own sake. It is how the implementation stays reversible while the language
is still being discovered.

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

**Remaining:** Most passes that could declare `depends_on` still leave it
empty (dependencies are enforced by ordering in `BUILTIN_FEATURES`).
`removed_node_types` is declared on ~half the passes; the rest could
declare it for completeness. Dead `precedence.py` (Python-AST-level
duplicate of `parse_tree_precedence.ExpressionLayer`) was removed.

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

## Phase B2: Capability And Host Manifests

**Design next.** The Rust/WASM parser, JavaScript Core Runtime, Python runtime,
Node wrapper, browser worker, and future Wasm/WASI hosts need a shared way to
say what they support.

Goal: define data tables for:

- parser frontend capabilities and payload schema versions;
- eval backend CoreNode coverage and promotion gates;
- host capabilities such as `print`, `range`, `map`, filesystem, clock,
  randomness, network, and package loading;
- result and diagnostic schemas shared by CLI, web, notebook, tests, and AI
  inspection.

Benefits:

- Browser fast paths can be useful without pretending to be full language
  defaults.
- Unsupported features produce structured diagnostics instead of stringly
  fallback errors.
- AI agents can inspect one capability table before changing behavior.

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

After Phase B/B2:
- Runtime behavior and host availability are declared in data before they are
  treated as language behavior.
- Browser, Node, Python, and notebook paths expose compatible result and
  diagnostic shapes.
- Capability claims can be checked by tests rather than maintained only in
  prose.
