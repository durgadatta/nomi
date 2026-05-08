# Design Review

> Status: active design workspace.

This directory is the active working surface for Nomi language design. It is
not limited to what the prototype already implements. The prototype is a seed
and a laboratory; the design target is a fully operational general-purpose
language optimized for human thought, explanation, and compositional power.

Broad exploratory material has been moved to `../design_review_archive/` so the
active directory can carry one coherent direction instead of nine overlapping
proposals.

## Current Focus

The active design focus is:

> Nomi as a cognition-first general-purpose language: Python-readable at the
> surface, but informed by Haskell, Mathematica, Kotlin, Ruby, Scheme, APL,
> ALGOL, and related traditions.

The first detailed feature spec is constrained binding, because it is a strong
semantic spine for assignment, parameters, patterns, blocks, external data, and
diagnostics. It is not the limit of the language.

The most important design constraint is coherence: Nomi should learn from many
languages without collecting their syntax. Every borrowed idea must be
translated into Nomi's own binding, block, pattern, expression-flow, symbolic,
effect, and diagnostic model.

## Design Spine

Nomi should keep Python's local readability while giving the best cognitive
ideas from other language families a smaller, more uniform semantic account.
The design is allowed to be ambitious when the resulting code becomes easier to
think with.

The current core concepts are:

```text
value
binding
constraint
function
call
block
yield
pattern
shape
data
collection
table
quote
rewrite
effect
world
capability
example
trace
diagnostic
```

The admission rule for new syntax is:

> Add syntax only when it reduces to a small semantic primitive and makes a
> common or cognitively important programming pattern clearer at the call site.

Current implementation effort should follow the design, not shrink the design
to what is easiest to implement this month.

## Active Documents

- [Cognitive Language Vision](cognitive_language_vision.md): the forward-looking
  language thesis, source-language synthesis, cognitive principles, and target
  feature families.
- [Language Coherence Model](language_coherence_model.md): the design constraint
  that prevents Nomi from becoming a syntax collage.
- [Binding Constraints Feature](binding_constraints_feature.md): syntax,
  semantics, desugaring, examples, diagnostics, and edge cases for constrained
  binding as one detailed feature pillar.
- [Implementation Todos](implementation_todos.md): staged tasks for both the
  broad language program and the constrained-binding pillar.

## Archived Source Notes

The previous design-review files were valuable, but they overlapped heavily:
several restated the same small-core philosophy, syntax catalog, cross-language
synthesis, and radical feature staging. They are preserved under
`../design_review_archive/` as source material, not active specification.

Use the archive to recover design context. Use this directory to decide what to
build next.
