# Getting Started With Nomi

> Status: user guide for runnable prototype examples.

[User guide](README.md) / Getting started

Start by running a calculation, then change it and repair an error. Next,
try a report that validates JSON before producing a result. These examples
work in the current prototype; future language features are described separately
in the [target design](../design/README.md).

## Choose Where To Run

The [public playground](https://durgadatta.github.io/nomi/web/) needs no checkout.
For local execution and sample commands, download the repository. Download a ZIP
from [the repository's Code menu](https://github.com/durgadatta/nomi) and extract
it, or clone it with Git:

```bash
git clone https://github.com/durgadatta/nomi.git
cd nomi
```

The repository root contains `pyproject.toml`, `samples/`, and `scripts/`.
Run the commands below there. The setup examples use a macOS/Linux shell;
operating-system support has not yet been declared as a distribution matrix.

### In your browser

Open the [playground](https://durgadatta.github.io/nomi/web/) and choose
`calculate.nomi`. For local development, run the same playground from a checkout:

```bash
python3 scripts/launch_web.py --no-wasm
```

Open the printed URL and choose `calculate.nomi` from the sample list. Run it
and inspect Output. The default
browser route also offers Bindings, Diagnostics, and Pipeline views for inspecting
values, problems, and execution details.

For notebook examples, `Shift+Enter` runs the current cell; `Run All` resets
the session and runs cells from the top. The optional legacy Pyodide route has
different inspection support, including no Bindings download control.

The published and local playgrounds use the same committed examples and assets.
CDN editor/runtime assets need network access even when serving locally.

### On your computer

Open a terminal in a checkout of the repository. Use Python 3.12 or newer and
create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
nomi samples/calculate.nomi --output program
```

To run from the checkout without installing the package:

```bash
python3 scripts/cli.py samples/calculate.nomi --output program
```

`--output program` shows the program's output. Without it, the CLI uses its
legacy debug display. `--output json` provides a machine-readable result with
diagnostics and inspected binding strings separate from program stdout.

The current guides describe this source installation path rather than
installation of a public registry release. An installed wheel does not include
the checkout's sample directory; keep the checkout or save an example as your
own `.nomi` file.

## Calculate And Change A Value

The [calculation sample](../../samples/calculate.nomi) is an invoice in cents:

```nomi
func subtotal(price, quantity):
    return price * quantity

price = 1200
quantity = 3
delivery = 250
total = subtotal(price, quantity) + delivery
print(total)
```

`func` defines a function. Its indented body multiplies the two inputs and
returns their product. The lines below name the values used in the calculation;
`subtotal(price, quantity)` calls the function, and `print(total)` shows the result.

The output is `3850`: three items at 1,200 cents plus 250 cents delivery.
Change `quantity = 3` to `quantity = 4`, save if using a local file, and run
again. The output becomes `5050`.

Now change the quantity to `"three"`. The invoice cannot finish with that text
quantity, so execution reports an operand error. Restore a number and
rerun. This example demonstrates runtime feedback; it does not depend on adding
type annotations first.

## Validate A JSON Report

Choose [report.nomi](../../samples/report.nomi) in the playground, or run:

```bash
nomi samples/report.nomi --output program
```

The sample reads JSON text stored in the source, validates every customer,
selects eligible customers, removes surrounding spaces from names and IDs,
and encodes a report as JSON. The default minimum age is 18.

Its two customers are Ada, aged 20, and Bo, aged 12. The result has:

| Report field | Value | Meaning |
| --- | --- | --- |
| `received` | `2` | Two customers were supplied. |
| `eligible` | `1` | One meets the minimum age. |
| `skipped_ineligible` | `1` | One valid customer is below the minimum age. |
| `customers` | Ada's normalized record | The eligible customer's name is `Ada` and ID value is `c-1`. |

### Repair invalid input

Near the bottom of the source, find the `text` value containing the customer JSON.
Change Ada's `"name":" Ada "` to `"name":""` and `"age":20` to `"age":-1`.
Run again. The report rejects the input and identifies both original field paths:

```text
$.customers[0].name
$.customers[0].age
```

The sample prints this validation outcome in Output, including its `path_text`
fields. It is an expected input rejection, so the program itself completes
normally; a successful CLI process exit does not mean the data was valid.

Restore a nonblank name and a nonnegative age, then rerun. All customers are
validated before filtering, so invalid data cannot disappear merely because
that customer would be excluded from the report.

### Export the result

In the default playground, open Bindings and choose **Download JSON** beside
`wire`. This downloads the encoded report as `wire.json`. If you edit the source,
rerun it before exporting: the playground blocks downloads of stale results.
Encoding or download-initiation failure leaves the successful report available
for inspection. The browser confirms download initiation, not a durable save
to your filesystem.

This report uses two built-in schemas and has a maximum batch size of 128.
Input and options are currently edited inside source. General user-defined typed
decoders, separate input controls, and checked module reuse are still future work;
see the [report delivery gates](../orientation/project_roadmap.md#report-and-target-delivery-gates).

The failure record also tells you whether its field-error list is complete.
It retains at most 64 field errors; an observed additional error marks the list
incomplete. Capacity or work-budget refusal can stop validation and return a
different failure record. These refusals do not produce a successful report.
For larger inputs, inspect the outcome rather than assuming the visible errors
are the only problems. Exact provisional limits and measurements are in the
[runtime boundary contract](../orientation/artifacts_and_usage.md#bounded-prototype-library-and-numeric-contracts).

## Check A Program Without Running It

The experimental source checker can inspect a small calculation independently
of executing it. Use the [checking example](../../scripts/check_invoice.nomi):

```bash
python3 scripts/cli.py scripts/check_invoice.nomi --output program
python3 scripts/cli.py scripts/check_invoice.nomi --check --require known-types
python3 scripts/cli.py scripts/check_invoice.nomi --check --require pure --output json
```

The first command runs the program and prints `3850`. The second checks its
scalar types. The third requests purity and reports that `print` uses
`ConsoleWrite`: output touches the outside world. Remove the output statement
in a copy of the file to try checking a pure calculation.

A type-only check can still list the console effect while ending with
`known-types: satisfied`. The selected requirements decide what blocks that
check; seeing an effect does not by itself mean the type requirement failed.

Use `--check` without `--require` to preview facts and unresolved obligations.
You can repeat `--require` to combine restrictions; it requires `--check`.

The checker supports a limited set of scalar expressions, simple bindings,
and direct functions with known scalar arguments. Unsupported constructs stay
unresolved. It does not infer general public interfaces or execute imports,
and success does not prove termination or the absence of every runtime failure.
Checking also grants no permission to run external operations. The detailed
[analysis boundary](../orientation/implementation_layers.md#experimental-source-analysis)
explains its scope.

## Current Limits

Nomi is experimental, and execution paths support different subsets. In
particular:

- The browser rejects integers outside `-9007199254740991` to `9007199254740991`
  instead of silently rounding them. Python supports wider integers; the report
  boundary permits up to 4,300 decimal digits or a lower configured host limit.
- Browser text indexing counts Unicode code points, not visible grapheme
  clusters. Text normalization is not implicit.
- Drafts use browser-local storage. Download source you want to keep;
  drafts are not a backup. Source export and report JSON export are separate actions.
- Stopping browser execution resets its worker. Target resource-cleanup and
  structured-task guarantees are still design and implementation work.
- Examples under `samples/` are runnable prototype fixtures. Programs under
  `docs/design/` describe the intended language and may not run today.

## Continue Exploring

Continue with [Language Basics](language_basics.md) for names, functions,
choices, loops, maps, and collection operations, then use the
[Example Catalog](examples.md) to choose a complete program.

Try [the data pipeline](../../samples/data_pipeline.nomi) for ordered `fold`
and seeded `scan`, or [the text notebook](../../samples/text_pipeline.nomi.nb)
for delimited-text exploration. These are prototype library examples; the text
notebook is not a strict CSV decoder.

For notebook setup, read the [Jupyter guide](../../tools/jupyter/README.md).
For local editor support, read [VS Code setup](../orientation/vscode_extension.md).
For the language's direction, start with the
[growth path](../../README.md#how-nomi-will-grow) and then the
[target design](../design/README.md). The [documentation index](../README.md)
routes to the full design, research, and implementation references.

For help with files, notebook state, tool setup, or an error, use
[Tools And Troubleshooting](tools.md). [Current Support And Growth](status.md)
explains the guarantees being built and which syntax differs from the target.
