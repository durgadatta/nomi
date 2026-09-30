# Bash

> Status: comparative evidence; Nomi judgments are hypotheses.

## Observe

A Bash pipe connects command processes. Pipeline status normally follows the
last command; `pipefail` changes it to a failing command's status. Subshell
execution also affects which updates survive.
[Primary reference: pipelines](https://www.gnu.org/software/bash/manual/html_node/Pipelines).

## Judge And Pay

**Adopt** left-to-right workflow readability. **Reject** importing process
streaming, exit-status aggregation, or subshell mutation into Nomi's `|>`.
That operator only inserts a value into the first argument of an ordinary call.
Process pipelines belong to a library with explicit process authority, byte
streams, statuses, and cancellation.

This means a familiar-looking Nomi pipeline is not a shell pipeline. The cost
is extra API ceremony for automation, where Bash excels. Nomi must make the
common three-command workflow genuinely usable without erasing which process
failed or interpreting user-controlled text as executable source.

## Test

Specify an argv-based process pipeline with a failing producer, successful
consumer, and early-closing consumer. Require individual outcomes and cleanup
traces. Compare with [collections](../../design/targets/collections.nomi), which
must remain pure call insertion. Do not add shell expansion to core syntax.
See [collections](../features/collections.md) and [failure](../features/failure.md).
