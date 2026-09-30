# Failure And Absence

> Status: comparative evidence; channels accepted, composed envelopes open.

User pressure: tell missing data, expected rejection, and broken invariants apart.

| Evidence | Mechanism | Nomi consequence |
| --- | --- | --- |
| [Rust](../languages/rust.md) | Result and explicit propagation | Typed expected failure; locally visible `?`. |
| [Zig](../languages/zig.md) | Error paths and error-only cleanup | Examine exit taxonomy before borrowing convenience. |
| [Bash](../languages/bash.md) | Pipeline status policy | Never infer aggregation from pipeline spelling. |
| [Elixir](../languages/elixir.md) | Returned value versus process failure | Child Err is not automatically a task crash. |

Explicit long form:

```nomi
func parse_count(text: Text) -> Result[Int, ParseError]:
    outcome = Int.parse(text)
    match outcome:
        Ok(value):
            return Ok(value)
        Err(error):
            return Err(error)
```

The accepted convenience is `value = Int.parse(text)?`. Absence uses Option and
`??`/`?.`, never error fallback. Panic and cancellation remain distinct from
returned Result. Explicit error mapping keeps domain context but adds ceremony;
measure it before admitting implicit conversion.

Unclosed interaction: a body returning Err plus a failed release has two
causes. The declared domain error cannot silently absorb arbitrary cleanup,
panic, and cancellation envelopes. Specify that type-level story before
claiming a public function enumerates every exit.

**Experiment:** beginner parse, five-layer import, failure-heavy nested cleanup.
Record returned values and abnormal outcome records separately, preserving all
causes and stable order. Compare explicit mapping with one proposed declared
conversion protocol; reject any option that discards provenance.

**User-facing gate:** terminal, editor, and playground distinguish channels and
retain paths/cause chains rather than display a generic failure string.
[Target](../../design/targets/failure.nomi).
