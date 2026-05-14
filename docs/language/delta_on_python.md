# Delta On Python

> Status: source rationale note; concrete syntax belongs in
> `language_spec.md`, focused feature docs, and convenience syntax docs.
>
> Consolidation note: this file records why Nomi departs from Python. Fold
> stable decisions into the relevant syntax-facing doc rather than expanding
> this note.

## Purpose

This note keeps the Python-difference rationale in one small place. It should
not restate the full syntax or implementation plan for each feature.

Use it to answer:

```text
What Python pressure caused Nomi to choose a different spelling or model?
```

For the actual Nomi syntax, read the canonical homes below.

## Canonical Homes

| Area | Python pressure | Nomi direction | Canonical doc |
| --- | --- | --- | --- |
| Function definitions | `def` is familiar but generic; `lambda` has historical grammar restrictions. | Use `func` for named behavior and `=>` or holes for concise function values. | [Function Convenience](../convenience/functions.md), [Language Spec](language_spec.md) |
| Binding constraints | Python annotations are mostly advisory at runtime. | Treat assignment, parameters, captures, fields, and decoder slots as checked bindings. | [Binding Constraints Feature](../features/binding_constraints_feature.md) |
| Argument mapping | Python's positional, keyword, default, vararg, and keyword-only rules are useful but subtle. | Preserve Python-compatible argument mapping where possible; apply constraints after mapping. | [Language Spec](language_spec.md), [Binding Constraints Feature](../features/binding_constraints_feature.md) |
| Blocks and control policies | Python context managers and decorators solve narrow cases but cannot naturally express retry, transaction, tracing, fixtures, and caller-side block parameters as one model. | Use block calls: an ordinary call with attached caller-side code invoked by `yield`. | [Block Calls As Control Values](../features/block_calls_feature.md), [Yield To Block](../features/yield_to_block.md) |
| External data | Python dictionaries, dataclasses, Pydantic models, CLI args, env vars, and JSON often use separate validation stories. | Use explicit `Data.decode(...)`, field bindings, constraints, provenance, and explanation. | [Language Foundation](language_foundation.md), [Binding Constraints Feature](../features/binding_constraints_feature.md) |
| Failure | Python commonly mixes `None`, exceptions, sentinel values, and library-specific result objects. | Keep absence, expected failure, exceptions, pattern non-match, and constraint failure distinct. | [Convenience Review And Roadmap](../convenience/review_and_roadmap.md), future failure taxonomy spec |

## Preserved Python Shape

Nomi should keep Python's strengths when they support local readability:

- indentation-based blocks;
- familiar calls and argument mapping;
- ordinary expression syntax where parity is intentional;
- readable names over dense glyphs;
- approachable first programs;
- interop with the Python ecosystem during the prototype phase.

## Deliberate Departures

Nomi departs from Python when the extra precision is worth teaching:

- `func` names function declarations directly.
- Arrow functions and holes replace Python's restricted `lambda`.
- Binding annotations are runtime checks in the Nomi model, not just hints.
- `data` and `decode` make external boundaries explicit.
- `?.` and `??` are absence-only.
- `Result` and `match` carry expected failure rather than overloading absence
  or exceptions.
- Block calls provide a common shape for resource, retry, transaction, trace,
  fixture, and future structured-concurrency policies.

## Non-Goals

Do not use this file as a second language spec. If a Python delta needs syntax,
diagnostics, reduction, tests, or implementation notes, move it to the relevant
syntax-facing doc.
