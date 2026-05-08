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

> Nomi as a first-principles, cognition-first general-purpose language that
> builds upward from the primitive acts of programming, then uses other
> languages as references rather than foundations.

The first detailed feature spec is constrained binding, because it is a strong
semantic spine for assignment, parameters, patterns, blocks, external data, and
diagnostics. It is not the limit of the language.

The most important design constraint is coherence: Nomi should learn from many
languages without collecting their syntax. Every borrowed idea must be
translated into Nomi's own binding, block, pattern, expression-flow, symbolic,
effect, and diagnostic model.

## Design Spine

Nomi should start from first principles: what values are, how names work, how
truth is judged, how transformations compose, how time and effects enter, and
how programs explain themselves. Python, Haskell, Mathematica, Kotlin, Ruby,
Scheme, APL, ALGOL, and other languages are reference experiments that help
answer those questions.

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
- [First-Principles Programming Model](first_principles_programming_model.md):
  the main spine that builds the language upward from primitive cognitive acts
  before consulting other languages.
- [Language Coherence Model](language_coherence_model.md): the design constraint
  that prevents Nomi from becoming a syntax collage.
- [Binding Constraints Feature](binding_constraints_feature.md): syntax,
  semantics, desugaring, examples, diagnostics, and edge cases for constrained
  binding as one detailed feature pillar.
- [Block Calls As Control Values](block_calls_feature.md): focused study of
  caller-side block syntax, `yield`, policy blocks, tradeoffs, and small-core
  reduction.
- [Implementation Todos](implementation_todos.md): staged tasks for both the
  broad language program and the constrained-binding pillar.

## Archived Source Notes

The previous design-review files were valuable, but they overlapped heavily:
several restated the same small-core philosophy, syntax catalog, cross-language
synthesis, and radical feature staging. They are preserved under
`../design_review_archive/` as source material, not active specification.

Use the archive to recover design context. Use this directory to decide what to
build next.
