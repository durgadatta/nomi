# Failure Taxonomy Feature

> Status: active feature packet; design-settled direction, implementation
> pending.
>
> Normal forms: absence/result, pattern, binding, explanation.
>
> Canonical homes: this file owns the vocabulary of non-success;
> [absence_and_result.md](../convenience/absence_and_result.md) owns
> convenience syntax; [explanation_trace_feature.md](explanation_trace_feature.md)
> owns events and diagnostics.

## Everyday Pressure

Useful programs do not merely succeed or crash. They encounter missing values,
expected failures, invalid input, non-matching cases, cancelled work, denied
capabilities, and unexpected bugs.

Nomi should make these distinct:

| Kind | Meaning | Primary surface |
| --- | --- | --- |
| Absence | no value is present | `none`, `Option`, `?.`, `??` |
| Expected failure | operation failed in a recoverable way | `Result`, `Ok`, `Err`, `match` |
| Unexpected error | bug or host failure not handled here | exception/error value |
| Pattern non-match | shape did not fit | `match`, `if pattern = value` |
| Constraint failure | value fit position but violated rule | binding diagnostic |
| Decode failure | external value could not become owned data | `Err(DecodeErrorList)` |
| Capability denial | code tried to touch unavailable world authority | capability diagnostic |
| Cancellation | time-shaped work was stopped by policy | block policy result/event |

## User Syntax

```nomi
name = user?.profile?.name ?? "anonymous"

match parse_int(raw):
    case Ok(n):
        n
    case Err(error):
        explain(error)

match event:
    case {"type": "click", "target": target}:
        record(target)
    case _:
        none
```

## Semantic Boundaries

Absence is not failure. `??` should not catch `Err`, exceptions, false values,
or pattern non-match.

Expected failure is data. It can be matched, transformed, collected, retried,
or explained.

Unexpected errors are fenced at host/runtime boundaries and surfaced as
structured exceptions or `ErrorValue` only when the caller chooses that
boundary.

Pattern non-match is control. Constraint failure is judgment. A match case may
skip both before body entry, but explanation must preserve which one happened.

Decode failure is expected failure plus provenance. It carries field paths,
source identity, redaction policy, and repair guidance.

## Source Evidence

Roc's current tutorial says recoverable errors should be represented with
normal types and handled without crashing, while `crash` is for unreachable or
infeasible recovery situations. That maps cleanly to Nomi's expected-failure
versus unexpected-error split.

Gleam, Rust, Elm, and Roc all reinforce explicit result values. Kotlin, Swift,
Dart, TypeScript, and C# reinforce visible absence/nullability. Elixir and
Racket reinforce pattern failure as choice rather than error. Pydantic, CUE,
Pkl, serde, and Elm decoders reinforce decode failure as structured evidence,
not a string message.

## Integration Comments

- Teach `match` as the first way to consume `Result`.
- Defer `expr?` until return constraints and error conversion are explicit.
- Let block policies return `Result` for expected policy failure:

  ```nomi
  result = retry(3, on=NetworkError):
      fetch(url)
  ```

- Let collections carry failures without erasing them:

  ```nomi
  rows
  |> select(Person.decode)
  |> collect_results
  ```

- Make `explain` use the same vocabulary everywhere: absence, expected
  failure, constraint failure, decode failure, capability denial, cancellation.

## Rejected Alternatives

| Alternative | Why not first |
| --- | --- |
| One catch-all failure operator | Blurs absence, expected failure, and exceptions. |
| `?? return` | Mixes absence fallback with statement-level exit too early. |
| Exceptions for decode/parse | Makes ordinary boundary failures harder to compose. |
| Silent pattern failure diagnostics | Makes constrained captures impossible to explain. |

## Implementation Slice

1. Define shared status vocabulary in runtime diagnostics.
2. Add `Result`/`Option` conventions to the prelude design.
3. Route decode and binding failures through structured diagnostic records.
4. Add match examples that distinguish pattern non-match from constraint
   failure.
5. Add explain output examples for each failure kind.

