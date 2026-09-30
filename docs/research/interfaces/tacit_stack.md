# Stack And Tacit Forms: Where Did The Argument Go?

> Status: Forth evidence and comparison with existing array-language research.

## Evidence And Pressure

The Forth standard documents stack-effect notation and execution/dictionary
concepts. The [APL](../languages/apl.md), [J](../languages/j.md), and
[Uiua](../languages/uiua.md) reviews own their respective mechanisms.
[Forth notation](https://forth-standard.org/standard/notation),
[Forth usage](https://forth-standard.org/standard/usage).

RPN calculators and tacit composition invite an important question: how much
meaning can order and context carry before the reader must simulate an invisible
machine? Argument omission can compress a familiar calculation while making
reordering and error diagnosis harder.

## Nomi Normal Form And Placement

Use explicit parameters, ordinary calls, and named intermediate values as the
baseline. Pipeline call insertion has one documented role. A stack-machine
library or teaching tool can model push/pop operations and show stack effects
without giving ordinary Nomi an implicit operand stack. Array rank/shape
contracts similarly belong in typed library operations before dense notation.

**Adapt:** visible effect summaries and compositional laws for a supported
domain. **Defer:** scoped calculator/array notation with an explicit entry type.
**Reject for core:** point-free aliases, arbitrary operators, and missing
parameters inferred from punctuation. Existing rejected syntax stays rejected
unless a whole program supplies new counterevidence.

## Discriminating Experiment

Calculate an invoice and a shape-changing array transform in explicit-call,
pipeline, and stack/tacit representations. Ask a reader to insert a diagnostic
and handle an empty input. Count reconstruction mistakes and explanation effort,
not just characters. A scoped domain form earns admission only if it improves
the actual reasoning task while exporting an inspectable long form.
