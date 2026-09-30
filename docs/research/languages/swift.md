# Swift

> Status: comparative evidence; Nomi judgments are hypotheses.

## Observe

Swift distinguishes asynchronous work from parallel child work and provides
structured task groups. Its concurrency model makes task lifetime a deliberate
part of program structure.
[Primary reference: concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html).

## Judge And Pay

**Adopt** lexical ownership of child tasks. **Adapt** starting and awaiting to
Nomi's cold-task contract. **Reject** inferring a complete policy from the word
TaskGroup: scheduling limits, observation order, child failure, cancellation,
and release failure are separate choices.

Structured lifetime adds ceremony to a one-off background operation and does
not guarantee bounded queue memory. Nomi's simple examples currently schedule
finite lists; that is not evidence of production backpressure. Copying an
attractive task-group spelling without defining these facts would weaken local
reasoning precisely where failure becomes concurrent.

## Test

Use [concurrency](../../design/targets/concurrency.nomi) with right-child panic
while the left child waits, then parent cancellation during join. Record which
child is cancelled, joined, and reported. Repeat with an ordinary child Err;
it must remain returned data unless an explicit policy says otherwise.
See [concurrency](../features/concurrency.md).
