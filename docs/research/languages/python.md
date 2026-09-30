# Python

> Status: comparative evidence; Nomi judgments are hypotheses.

## Observe

Python makes suites visually explicit with indentation and gives resource
protocols a dedicated `with` statement. Its pattern matching belongs to a
larger compound-statement model rather than replacing all control flow.
[Primary reference: compound statements](https://docs.python.org/3/reference/compound_stmts.html).

## Judge And Pay

**Adopt** the readable suite and short first program. **Adapt** context-managed
resources into Nomi's exactly-once lifetime contract. **Reject** compatibility
as the target's ceiling: Nomi's public types, Bool conditions, immutable default
bindings, and distinct Option/Result channels deliberately demand more explicit
intent. This costs the ability to paste arbitrary Python into Nomi and raises
the effort of exploratory code that changes value shape frequently.

Python familiarity does not establish that `var` and `set` are learnable or
that constraints pay for themselves. Those are Nomi hypotheses. Likewise,
Python's resource protocol is useful evidence, not proof that Nomi's cleanup
failure envelope is settled.

## Test

Use [binding](../../design/targets/binding.nomi) and
[resources](../../design/targets/resources.nomi). Give a newcomer a counter and
a file read that returns early. Ask them to identify every update and every
close without running it. Record mistakes and compare an explicit long form;
reconsider the surface if Nomi adds tokens without improving the answers.
See [bindings](../features/binding.md) and [resources](../features/resources.md).
