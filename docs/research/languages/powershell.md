# PowerShell

> Status: comparative evidence; Nomi judgments are hypotheses.

## Observe

PowerShell pipes objects rather than only text. Pipeline binding and array
enumeration can differ from passing an entire array as an ordinary argument.
[Primary reference: about pipelines](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_pipelines).

## Judge And Pay

**Adopt** structured objects at automation boundaries. **Adapt** workflows to
explicit List, Stream, or process types. **Reject** automatic enumeration as a
side effect of the Nomi pipeline operator. The exact same function call should
mean the same thing whether written directly or through `|>`.

PowerShell's command-oriented interface serves interactive administration well.
Nomi's ordinary calls may be less convenient for ad hoc commands, and typed
nominal adapters may impede inspecting unfamiliar host objects. A structural
`Value` inspection surface is therefore important before ownership conversion;
it must not become implicit unchecked `Any` inside application code.

## Test

Pipe a List of three records into a function that expects one List. Assert one
call, not three. Then explicitly create a Stream and inspect pull order and
early termination. Compare error paths for host objects with missing fields.
See [collections](../features/collections.md), [decoding](../features/decoding.md),
and [the collection fixture](../../design/targets/collections.nomi).
