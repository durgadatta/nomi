# PowerShell

> Status: comparative evidence; Nomi judgments are hypotheses.

## Observe

PowerShell pipes objects rather than only text. Pipeline binding and array
enumeration can differ from passing an entire array as an ordinary argument.
[Primary reference: about pipelines](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_pipelines).

PowerShell cmdlets and functions conventionally use an approved `Verb-Noun`
pair: the general verb identifies the action and the singular noun identifies
the resource. Parameters refine the action. PowerShell's formal naming guidance
does not add adverb and adjective command-name slots; qualifiers normally appear
in the noun, parameters, switches and values. The controlled vocabulary makes
commands discoverable by action while retaining resource-specific names.
[Approved verbs](https://learn.microsoft.com/en-us/powershell/scripting/developer/cmdlet/approved-verbs-for-windows-powershell-commands)
and [naming guidance](https://learn.microsoft.com/en-us/powershell/scripting/developer/cmdlet/strongly-encouraged-development-guidelines).

Several verb distinctions are direct evidence for text APIs:

| Verb family | Documented intent | Boundary exposed |
| --- | --- | --- |
| `Format` | Arrange objects in a form or layout | Human presentation, not serialization |
| `Out` | Send data outside the environment | Destination/effect, not value conversion |
| `ConvertTo` / `ConvertFrom` | Convert toward or from the noun's primary representation | Direction and representation owner |
| `Export` / `Import` | Cross persistent storage or interchange | Persistence/provenance, not display |
| `Read` / `Write` | Acquire from or add information to a source/target | IO remains visible |
| `Get` / `Set` | Retrieve or replace a resource | Resource lifecycle, not text parsing |
| `Test` | Verify a resource or condition | A test result, weaker than diagnostics-rich decode |
| `Select` | Choose/project resources | Selection, not formatting |
| `Join` / `Split` | Combine or separate resources | An explicit boundary rule is still required |

PowerShell also separates object formatting from object flow. This supports a
general design rule: preserve structure through composition and choose a text
representation at the final audience or protocol boundary. Formatting before
`Export-Csv` exports the formatting objects' properties, not the original
records. [Export-Csv warning](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/export-csv).
The deeper
cross-language comparison lives in
[text as a computational interface](../dsls/text_as_interface.md).

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

**Adapt** a small documented glossary for cross-cutting boundary operations,
qualified by modules and explicit result types. **Reject** a language-wide
approved-verb restriction: domain verbs carry useful distinctions, ordinary
methods need not be command names, and spelling alone cannot establish a codec,
effect, loss or authority contract.

The [natural-language continuation](../interfaces/natural_language.md) separates
grammatical class, domain role, resolved binding and display/search label. It
uses this verb/resource vocabulary as one discovery mechanism alongside Swift's
use-site phrasing, not as an English grammar for all Nomi APIs. NL1/NL2 compare
opt-in glossary guidance and named semantic roles before any naming lint;
NL5 keeps localized discovery terms separate from executable command identity.

## Test

Pipe a List of three records into a function that expects one List. Assert one
call, not three. Then explicitly create a Stream and inspect pull order and
early termination. Compare error paths for host objects with missing fields.
Separately classify a small text API under display, inspect, format, encode,
decode, parse, render, import/export and read/write; reject any name whose
signature or documentation contradicts the proposed meaning. This is a lint
experiment, not a compiler naming rule.
See [collections](../features/collections.md), [decoding](../features/decoding.md),
and [the collection fixture](../../design/targets/collections.nomi).
