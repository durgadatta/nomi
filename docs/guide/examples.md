# Choose An Example

> Status: user catalog of current runnable samples and their experimental boundaries.

[User guide](README.md) / Example catalog

Start with the small task you want to understand. You do not need to read the
largest sample or a research dossier first. The [public playground](https://durgadatta.github.io/nomi/web/)
and local checkout load the same committed `samples/` files, including the
recommended calculation, report, data and text examples.

## Recommended Examples

| Example | What to learn | What to change |
| --- | --- | --- |
| [calculate.nomi](../../samples/calculate.nomi) | Define a function, use its result, and print integer cents. | Quantity `3` → `4`; output `3850` → `5050`. Try text, inspect the error, and repair it. |
| [report.nomi](../../samples/report.nomi) | Validate JSON before filtering, normalize fields, inspect counts, and encode JSON. | Make Ada's name blank and age negative; repair both reported fields. |
| [data_pipeline.nomi](../../samples/data_pipeline.nomi) | Select paid orders, transform their amounts, and accumulate total/history. | Change an order's status or quantity and compare the resulting totals. |
| [text_pipeline.nomi.nb](../../samples/text_pipeline.nomi.nb) | Strip text, select rows, convert fields, and inspect bounded windows in cells. | Add a simple `name,count` line; run cells in order. This is not a general CSV parser. |

For these introductory tasks, use the CLI or default browser route. Detailed
walkthroughs are in [Getting Started](getting_started.md), and the operations are
explained in [Language Basics](language_basics.md).

### Read the data pipeline

The sample's paid orders contain 900 and 360 cents, so `total_cents` is `1260`.
`scan` includes the seed, making the history `[0, 900, 1260]`. An empty fold
returns `0`. These outputs help distinguish the total from its intermediate
states. `|>` feeds the amount collection into the fold call in this example;
ordinary calls are sufficient when learning the operation.

### Read the text notebook

After stripping whitespace and removing the comment and empty line, there are
three records. Their counts are `[3, 5, 2]`, the total is `10`, and the history is
`[0, 3, 8, 10]`. The final cell demonstrates indexing and slices. Malformed fields
can fail at conversion; this notebook does not collect structured decode errors
as the report does.

## Experimental Samples

These remain useful implementation experiments, not the recommended route for
learning the future language. A title such as “guided tour” or “comprehensive”
describes prototype coverage and does not make the file the target specification.
Support differs by execution path; start with the hosted CLI when investigating
an experimental form, and use the playground's diagnostics for unsupported operations.

| Sample | What it explores | Reading caution |
| --- | --- | --- |
| [demo.nomi](../../samples/demo.nomi) | Broad tour of implemented prototype syntax. | Includes equation functions, piecewise forms, and other syntax rejected by the target. |
| [demo_terse.nomi](../../samples/demo_terse.nomi) | Compact ticket-triage program. | Concise experimental notation; listed under Experiments in the playground. |
| [demo_verbose.nomi](../../samples/demo_verbose.nomi) | More explicit presentation of a prototype program. | Still a prototype fixture, not a target migration guide. |
| [collections.nomi](../../samples/collections.nomi) | Collection helpers and shorthand. | Some shorthands and callback conventions differ from the target. |
| [constraint.nomi](../../samples/constraint.nomi) | Constraints, data, and patterns. | Old constraint tuples and pattern shortcuts are not the target `where`/`match` contract. |
| [block.nomi](../../samples/block.nomi) | Caller blocks and `yield`. | The target does not use universal block/yield control for resources or concurrency. |
| [others.nomi](../../samples/others.nomi) | Defer, try expressions, shortcuts, and composition. | Contains several deliberately rejected target forms. |
| [comprehensive.nomi](../../samples/comprehensive.nomi) | Large compatibility/edge-case corpus. | An implementation exercise; read a focused example first. |
| [notebook_intro.nomi.nb](../../samples/notebook_intro.nomi.nb) | Cell state, functions, and collection work. | Its final constraint cell uses experimental notation. |

The [decision ledger](../design/decisions.md#syntax-simplification-decisions)
explains the rejected forms. The [support guide](status.md#prototype-and-target-differences)
summarizes the differences without requiring a design review first.

## Run And Keep Your Changes

### Jupyter lessons

Jupyter uses separate `.ipynb` documents. Choose the Nomi kernel and run cells
from top to bottom; save a copy for your work.

| Lesson | Purpose |
| --- | --- |
| [nomi_calculation.ipynb](../../notebooks/nomi_calculation.ipynb) | First calculation, a cross-cell change, and repair instructions; selected by the local notebook launcher. |
| [nomi_minimal.ipynb](../../notebooks/nomi_minimal.ipynb) | Small kernel smoke test with experimental prototype notation. |
| [nomi_syntax_tour.ipynb](../../notebooks/nomi_syntax_tour.ipynb) | Experimental compatibility tour; includes forms outside the target. |

### Source files

From the repository root:

```bash
nomi samples/data_pipeline.nomi --output program
nomi samples/text_pipeline.nomi.nb --output program
```

The CLI runs the whole notebook file in order. The browser can run its cells
separately, which makes execution order matter. Use Run All for a fresh result.
Copy a sample to your own file before experimenting if you want to preserve the
checkout fixture. In the browser, use Download source to keep your changes;
draft storage is a convenience rather than a backup.

Continue with [Using Nomi's Tools](tools.md) for files, cells, and troubleshooting.
