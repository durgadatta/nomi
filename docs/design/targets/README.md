# Target Program Suite

> Status: aspirational design fixtures, not runnable samples or conformance claims.

These programs make the target readable at two scales: one category at a time,
then an integrated import workflow. Read [the synthesis](../synthesis.md) for
the reasoning and [syntax](../syntax.md) and [semantics](../semantics.md) for
authority. The programs are independent modules; repeated small declarations
are intentional so each can be reviewed alone.

| Category | Program | User pressure | Comparison |
| --- | --- | --- | --- |
| Naming and state | [binding.nomi](binding.nomi) | Distinguish a new fact from an update. | [Bindings](../../research/features/binding.md) |
| Functions | [functions.nomi](functions.nomi) | Read a reusable calculation and its call sites. | [Functions](../../research/features/functions.md) |
| Owned data | [data.nomi](data.nomi) | Model valid concepts and closed alternatives. | [Types and data](../../research/features/types_data.md) |
| Structural choice | [patterns.nomi](patterns.nomi) | Handle every state without leaking captures. | [Patterns](../../research/features/patterns.md) |
| Failure | [failure.nomi](failure.nomi) | Separate absence, expected rejection, and bugs. | [Failure](../../research/features/failure.md) |
| Boundaries | [boundaries.nomi](boundaries.nomi) | Reject malformed input with useful paths. | [Decoding](../../research/features/decoding.md) |
| Authority | [effects.nomi](effects.nomi) | Know what a public operation can touch. | [Effects](../../research/features/effects.md) |
| Lifetime | [resources.nomi](resources.nomi) | Clean up on early exit and failure. | [Resources](../../research/features/resources.md) |
| Concurrent work | [concurrency.nomi](concurrency.nomi) | Bound children and observe their outcomes. | [Concurrency](../../research/features/concurrency.md) |
| Collection flow | [collections.nomi](collections.nomi) | Transform data without hiding execution mode. | [Collections](../../research/features/collections.md) |
| Numerical work | [numerics.nomi](numerics.nomi) | Make rounding, overflow, and shape meaningful. | [Numerics](../../research/features/numerics.md) |
| Package boundaries | [modules.nomi](modules.nomi) | Publish a small stable interface. | [Modules and tooling](../../research/features/modules_tooling.md) |
| Explainable behavior | [tooling.nomi](tooling.nomi) | Turn examples and mistakes into shared diagnostics. | [Modules and tooling](../../research/features/modules_tooling.md) |
| Whole program | [overall.nomi](overall.nomi) | Import, validate, enrich, and publish one report. | [Synthesis](../synthesis.md) |

The detailed [pattern fixture](../pattern_matching_target.nomi) still owns the
registered pattern pass. `patterns.nomi` is a short user-story view, not a
second pattern specification. [The legacy target](../target.nomi) is retained
as a superseded predecessor for historical links; this suite owns the active
overall fixture.

## What The Source Does And Does Not Claim

Core syntax follows the accepted target. Standard-library APIs below are
**proposed contracts used to expose design questions**, not existing exports.
Comments mark deliberate rejection cases; those lines are never active code.
No whole-target parser/type checker exists yet. A passing documentation check
only proves navigation and packet consistency.

| Proposed API family | Assumption made by these fixtures | Unclosed gate |
| --- | --- | --- |
| `Int.parse` | Pure `Text -> Result[Int, ParseError]`, no coercion at construction. | Numeric literal/range limits and complete parse diagnostics. |
| `json.parse`, `json.encode` | Parse text to `Value`; explicitly encode supported data. | Generated codec/protocol coherence and round trips. |
| `http.post_text` | Cold task returning `Result[Text, HttpError]`; bearer Secret is not logged. | Request/response limits, deadlines, status handling, secret-safe tracing. |
| `T.decode` | Strict structural validation, accumulated independent errors. | Field decoder customization and explicit `Value` construction. |
| `files.read_text` | All operation and cleanup failures represented by `IoError`. | Body/cleanup cause grouping and resource limits. |
| `files.write_text_atomic` | On reported success publish complete text; no partial destination on ordinary write failure. | Crash durability, filesystem guarantees, temporary-file cleanup; this name is a proposal, not proof of atomicity. |
| `files.open_reader` | Read-only resource; release is infallible in the narrow example. | General fallible and asynchronous release remains open. |
| `TaskGroup`, `TaskFailurePolicy` | Cold tasks, bounded execution, explicit panic policy, ordered observation. `Err` is a normal child return value. | Group failure envelope, cancellation during cleanup, queue-memory bounds. |
| `http.get_text` | Cold network task returning `Result[Text, HttpError]`. | Status policy, response limits, deadlines, and authorization. |
| `Decimal.parse`, `decimal.divide` | Exact parsing and explicit rounding policy. | Decimal context, overflow, division errors, and cross-backend vectors. |
| `.map`, `.map_error`, collection verbs | Ordinary typed calls with no implicit propagation. | Generic/protocol declarations and callback effect polymorphism. |

## Review Gates

For each file ask: what are the input/output types; which expressions can fail;
where does `?` return; what is mutable; what authority is needed; when can it
suspend; and which cleanup still runs? Reject a proposed convenience if these
answers get less local.

Before a category can become a playground sample, it needs accepted/rejected
parse fixtures, typed Surface/Core artifacts, expected values/diagnostics,
formatter output, and matching CLI/browser results. Use the existing browser
smoke mechanism with a new supported sample only after that gate. Never copy
these files into `samples/` just to make the sample list look more complete.
