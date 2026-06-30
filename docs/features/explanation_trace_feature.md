# Explanation And Trace Feature

> Status: active feature packet; Runtime Event Schema V1 implemented, feature
> producers still partial.
>
> Normal form: explanation.
>
> Canonical homes: this file owns semantic event vocabulary and explainable
> traces; feature-specific docs own the event producers.

## Everyday Pressure

Nomi's promise depends on users seeing what happened. Good syntax is not enough
if failed constraints, decode errors, block retries, query plans, and examples
each invent their own output format.

The core rule:

```text
semantic event -> trace record -> diagnostic, example, test, or explain view
```

## Event Shape

Every semantic event should be representable as data:

| Field | Meaning |
| --- | --- |
| `kind` | binding, decode, match, call, block, pipeline, query, example, capability, rewrite |
| `action` | checked, failed, entered, yielded, resumed, matched, skipped, emitted |
| `span` | source span when available |
| `subject` | name, field path, call target, block policy, query stage |
| `value` | involved value, redacted when needed |
| `rule` | constraint, pattern, decoder, policy, capability, example expectation |
| `result` | success, non-match, expected failure, exception, cancellation |
| `next` | repair hint or next inspectable artifact |
| `redactions` | fields or paths hidden by policy |

## User Syntax

```nomi
explain(Config.decode(raw))

trace "import people":
    people =
        read_csv(path)
        |> select(Person.decode)
        |> collect_results

func normalize_email(email:str) -> str:
    examples:
        " A@B.COM " => "a@b.com"
    return email.strip().lower()
```

## Required Producers

| Producer | Event pressure |
| --- | --- |
| Binding constraints | what value violated which rule at which binding site |
| Decode | source path, field path, raw value, expected rule |
| Match | subject, tried cases, pattern non-match, guard/constraint failure |
| Pipeline | stage name, input/output summary, failure propagation |
| Block policy | enter, yield, resume, retry, cancel, cleanup |
| Query plan | logical plan, materialization, backend capability |
| Examples/checks | input, expected output, actual output, diff |
| Capability/world | authority requested, granted, denied, touched |
| Rewrite/symbolic | quoted form, rule, expansion, provenance |

## Source Evidence

Unison abilities, Effekt handlers, and Roc platforms all show that world
contact and control effects are easier to reason about when the surrounding
context is explicit. Nomi should expose this at the product layer through
events and explanation before it exposes advanced effect typing.

Rust, Elm, Racket, TypeScript, Gleam, and Swift diagnostics show that helpful
errors need source spans, expected/actual values, and repair guidance.
Interactive systems such as notebooks and Darklang show that explanation also
has to cover successful execution, not only errors.

## Integration Comments

- `explain` is a view over trace records, not a separate evaluator.
- Trace records are useful even when no user asks for `explain`: tests,
  playgrounds, notebooks, agent tools, and docs can consume the same data.
- Redaction is part of the event contract, not a logging afterthought.
- Feature implementations should add producers one at a time. Binding
  constraints are the first real producer; decode and block policies are next.

## Rejected Alternatives

| Alternative | Why not first |
| --- | --- |
| Plain strings as diagnostics | Cannot power UI, tests, agents, or redaction. |
| One event shape per feature | Makes cross-feature traces incoherent. |
| Always-on verbose traces | Too noisy for ordinary programs. |
| Unsafe explain by default | Leaks secrets and PII. |

## Implementation Slice

1. [x] Extend runtime diagnostics with the event fields above.
   (`RuntimeEvent.to_record()` now exposes V1 fields and
   `RuntimeEventCollector` assigns stable event IDs.)
2. [x] Add shared helper functions for planned producer families.
   (`record_decode_event`, `record_match_event`, `record_pipeline_event`,
   `record_block_policy_event`, and `record_capability_event` now wrap the
   shared semantic event shape; concrete feature producers remain pending.)
3. Add source-span propagation for more surface nodes.
4. Produce decode events from `Data.decode`.
5. Produce match and pipeline events after their normal forms stabilize.
6. Add `explain` rendering for terminal, notebook, and web playground.
