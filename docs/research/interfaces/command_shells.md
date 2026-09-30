# Shells: Invocation Is A Boundary

> Status: interface evidence; complements existing Bash and PowerShell reviews.

## Evidence And Pressure

Bash pipelines connect commands through process streams; history expansion can
reuse earlier input. PowerShell pipelines pass objects, while pipeline-chain
operators make a separate success-dependent execution choice.
[Bash pipelines](https://www.gnu.org/software/bash/manual/html_node/Pipelines),
[History](https://www.gnu.org/s/bash/manual/html_node/History-Interaction.html),
[PowerShell pipelines](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_pipelines),
[Chain operators](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_pipeline_chain_operators?view=powershell-7.5).

This interface excels at composing familiar actions incrementally. Its design
pressure is not merely a pipe token: expansion, current directory, process
status, environment, object formatting, and persistent session state can all
affect the action. A prompt is a context-bearing interface, not just a line of
source with a different color.

## Nomi Normal Form And Placement

Keep `values |> map(f)` as eager call insertion. A process proposal instead
constructs a typed invocation value with an explicit argument list, environment,
working directory, input/output limits, and capability requirements, then asks
an executor to run it. Bytes/text and object streams need explicit adapters.
An unsuccessful exit code is an expected typed outcome, not a Bool inferred
from the display or an exception borrowed from the host.

**Adapt:** discoverable commands, structured completion, inspect-before-run
history, concise composition. **Reject:** treating text interpolation as shell
escaping or giving `|>` stream/backpressure semantics. **Library destination:**
process and stream APIs; **tool destination:** invocation preview and history.

## Discriminating Experiment

Compare an explicit process builder with shell text on arguments containing
spaces, leading dashes, wildcard characters, and newlines. Deny Process in the
browser and verify the preview remains inspectable without a spawn. History
replay must display the current context and never restore an old grant. Existing
language pages own shell behavior; this page owns the human invocation workflow.
