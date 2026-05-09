# Design Review

> Status: active design workspace.

This directory is the active working surface for Nomi language design. The
prototype is a seed and a laboratory; the design target is a usable
general-purpose language for ordinary, medium-level programming that can grow
into deeper sophistication without losing its core.

The current canonical entry point is
[Nomi Language Foundation](language_foundation.md). Start there before reading
or editing the older synthesis documents.

## Current Focus

The active design focus is:

> A friendly everyday language whose sophistication emerges from a small set of
> remembered operations: values, bindings, constraints, functions, calls, data,
> patterns, collections, blocks, examples, traces, and diagnostics.

The next design pass should converge from the foundation document into focused
feature specs and executable syntax examples. Broad vision without operational
syntax is not enough; every accepted idea needs a reduction, diagnostic story,
implementation slice, and tests.

## Design Spine

Nomi should start from first principles: what values are, how names work, how
truth is judged, how transformations compose, how values group, how choices are
made, how repeated transformations stay readable, and how programs explain
themselves. Python, ML/Haskell, Lisp/Scheme, ALGOL, Ruby, Kotlin, Rust, Swift,
R, APL, SQL, Mathematica, Pydantic, JSON Schema, and other efforts are reference
experiments, not syntax inventories.

The current core concepts are:

```text
Source
Value
Binding
Constraint
Function
Call
Data
Pattern
Match
Collection
Block
Example
Trace
Diagnostic
Module
```

The admission rule for new syntax is:

> Add syntax only when it reduces to a small semantic primitive and makes a
> common programming pattern clearer at the call site, with diagnostics and
> tests that prove the intended semantics.

Advanced symbolic rewrite, effects, capabilities, async, concurrency, memory
models, and custom notation remain research topics until the everyday core is
stable.

## Active Documents

- [Nomi Language Foundation](language_foundation.md): canonical foundation for
  the next phase. It consolidates the broad design direction, rethinks
  `shape`/`data`, defines the operational core, and gives a concrete syntax
  runway.
- [Nomi Language Specification](language_spec.md): draft concrete language spec
  for the intended Nomi language: lexical structure, values, bindings,
  constraints, functions, data, patterns, collections, blocks, modules,
  examples, diagnostics, and conformance.
- [Binding Constraints Feature](binding_constraints_feature.md): syntax,
  semantics, desugaring, examples, diagnostics, and edge cases for constrained
  binding. This should be revised against the foundation before implementation
  expansion.
- [Block Calls As Control Values](block_calls_feature.md): focused study of
  caller-side block syntax, `yield`, policy blocks, tradeoffs, and small-core
  reduction. This remains useful, but advanced concurrency implications are not
  first-path work.
- [Implementation Todos](implementation_todos.md): staged backlog. It should be
  updated after focused specs are rewritten from the foundation.

## Supporting Source Notes

These files are useful background, but they are no longer parallel canonical
visions:

- [Cognitive Language Vision](cognitive_language_vision.md)
- [First-Principles Programming Model](first_principles_programming_model.md)
- [Hierarchical Language Research Plan](hierarchical_language_research_plan.md)
- [Research Notes Synthesis](research_notes_synthesis.md)
- [Language Coherence Model](language_coherence_model.md)

Use them to recover rationale. Use `language_foundation.md` to decide what to
build next.

## Archived Source Notes

The previous design-review files were valuable, but they overlapped heavily:
several restated the same small-core philosophy, syntax catalog, cross-language
synthesis, and radical feature staging. They are preserved under
`../design_review_archive/` as source material, not active specification.

Use the archive to recover design context. Use this directory to decide what to
build next.
