# Using Nomi's Tools

> Status: user instructions for the current browser, CLI, notebook, and editor surfaces.

[User guide](README.md) / Tools and troubleshooting

Choose one environment to begin. The browser is the shortest route to examples;
the CLI is useful for saved files; Jupyter and VS Code are optional local tools.
They share the project direction but do not have identical feature coverage.

## Browser Playground

Use the current local playground for these instructions; the
[online preview](https://durgadatta.github.io/nomi/web/) is an older deployment
without the calculation/report samples or current inspection controls.
From the repository root:

```bash
python3 scripts/launch_web.py --no-wasm
```

Open the printed URL. On a first visit, `calculate.nomi` is selected. Returning
visits restore your selected file and local drafts. **Start here** contains the
calculation and report tasks; **Data and text** contains the two collection
notebooks. **Experiments** labels older prototype tours. Search matches file
names, descriptions, groups, and status. The sidebar's **User guide** link opens
the guide in the repository; a local checkout may be ahead of that published copy.

### Edit and run

Select a sample or use **New scratch** to write your own source. For notebook
documents, `# %%` introduces a cell. `Shift+Enter` runs the current cell; later
cells can use definitions from earlier cells. **Run All** resets the session
and runs from the top. If a later cell says a name is missing, run its defining
cell first or use Run All.

Use **Stop** to interrupt work. It terminates and resets the worker; it is not
a promise that the target language's resource finalizers ran. **Reset runtime
state** clears the session, and **Restart runtime worker** recreates the worker.
These controls affect execution state, not a saved source file.

### Understand results

| View | What it tells you |
| --- | --- |
| Output | Text printed by the program. |
| Bindings | Captured names and values, when this route supplies them. |
| Diagnostics | Problems from parsing, lowering, or execution, with source links when available. |
| Pipeline | Execution path and supplied timing information. |

“Bindings unavailable” differs from a captured empty binding map. Missing
timings are not zero-duration stages. The optional legacy Pyodide route does not
export arbitrary Python bindings; use Output and Diagnostics there.

After you edit source, previous results are marked as belonging to the earlier
source. Rerun before treating them as the result of the edit. The report's JSON
download also rejects stale results.

### Keep source and export a result

**Open local source** loads a UTF-8 file into the editor without running it.
The current limit is 256 KiB. **Download source** saves the current source;
**Copy source** copies it when clipboard access is available. Notebook downloads
preserve their cell markers. These operations are separate from running code.

The browser remembers local drafts when storage is available. **Revert local
changes** restores a sample's original source. Download work you want to keep
before reverting or relying on a draft across browsers/devices.

Report output has a separate path: in Bindings, **Download JSON** beside `wire`
downloads encoded JSON. Download source produces your program; Download JSON
produces its report. The [report walkthrough](getting_started.md#export-the-result)
explains current-revision and failure behavior.

### Run the playground locally

From the repository root, serve the committed parser assets without rebuilding:

```bash
python3 scripts/launch_web.py --no-wasm
```

The launcher reports its URL and opens it when ready. Stop the terminal process
with Ctrl+C when finished. Use `--no-browser` if you want to open the URL yourself.
The default launcher rebuilds WASM and needs the Rust build tools described in
[Developing Nomi](../orientation/development.md#web-playground).

## Command Line

For initial setup, follow [Getting Started](getting_started.md#on-your-computer).
From the repository root, run a saved file:

```bash
nomi samples/calculate.nomi --output program
```

For your own file, replace the sample path with its path. Relative file paths
are resolved from the terminal's current directory. Source files have the
`.nomi` extension; `.nomi.nb` files can be run in their entirety too.

| Option | Use it for |
| --- | --- |
| `--help` | Current command syntax and available options. |
| `--output program` | Program output and failure feedback without the legacy debug display. |
| `--output json` | A structured record separating stdout, diagnostics, and inspected binding strings. |
| `--check` | Experimental source facts without executing the program. |
| `--require known-types` | Requesting supported scalar type evidence with `--check`. |
| `--require pure` | Requesting no known world effects in the supported checker subset. |

Checking and running are distinct commands. A successful check does not run the
file or grant permission to access files, networks, or other host resources.
Without a filename, `nomi` runs a packaged historical demo; use an explicit
filename for the beginner examples. The installed wheel does not include the
checkout's `samples/` directory.

For ordinary runtime failure, `--output program` preserves earlier program
stdout, prints a diagnostic to stderr, and returns a nonzero process exit.
`--output json` keeps the failure record machine-readable. Expected report
validation rejection is different: the current sample returns and prints its
outcome as data, so inspect that outcome rather than relying on the exit code.

The guide does not require choosing a parser or runtime backend. Those are
developer controls; see [Implementation Layers](../orientation/implementation_layers.md).

## Jupyter Notebooks

From the repository root, with the intended virtual environment active:

```bash
python3 tools/jupyter/launch_nomi_notebook.py
```

The launcher installs dependencies and the local kernelspec, checks the kernel,
and opens the first calculation notebook. Choose the **Nomi** kernel if necessary. Definitions
persist across cells, so execution order matters. `%who` lists names, `%reset`
clears state, `%run` runs a file, and `%ast` inspects the prototype's lowered AST.

A failed cell shows an error message; parse errors also identify the source
line and column. Output printed before the failure stays visible. A failure
does not reset the notebook or undo assignments that already ran: repair the
cell and rerun it, or use `%reset` and Run All for a fresh start.

The calculation reuses the same first program as the browser and guide, then
shows a change in a second cell. Save a copy for your own work. The separate
experimental syntax tour includes historical forms. Use the
[language basics](language_basics.md) for the beginner subset and the
[example catalog](examples.md) to interpret the older forms. Browser `.nomi.nb`
source files and Jupyter `.ipynb` documents are different file formats.

The [Jupyter guide](../../tools/jupyter/README.md) covers kernelspec recovery,
the Docker launcher, and host-specific troubleshooting. Docker is an optional
development environment, not a requirement for learning Nomi.

## VS Code

Local extension setup needs VS Code Desktop, Node.js/npm, Python 3.12+ with Nomi's
dependencies, and the `code` CLI (or a compatible configured CLI). Open the
repository folder as a trusted workspace, then run:

```bash
python3 tools/vscode/nomi/scripts/nomi-vscode.py enable-local
```

Use **Nomi: Run File** from the Command Palette to run a saved local file.
Output appears in a task terminal. **Nomi: Run Selection** runs the selected
source separately; it does not reuse a persistent notebook session. Save
cancellation aborts Run File. A task can be stopped with VS Code's task controls.

Highlighting, snippets, symbols, hover notes, and navigation are early prototype
support. Navigation is based on source scanning, not a complete semantic language
server. Setup opens `samples/calculate.nomi` for the beginner task. See
[VS Code setup](../orientation/vscode_extension.md) for detailed settings.

## Troubleshooting

| Symptom | What to check or do |
| --- | --- |
| `nomi` is not found | Activate the environment where you installed it, or use `python3 scripts/cli.py` from the checkout. |
| A file cannot be found | Check the terminal's directory and the supplied path; sample commands assume the repository root. |
| Python cannot import `ast.TypeAlias` | Use Python 3.12+; Python 3.11 cannot run the current interpreter. |
| A dependency such as Lark is missing | Install the package into the interpreter you are using; do not mix system and virtual-environment executables. |
| A parse error appears | Check indentation and the reported construct. Confirm that the syntax belongs to a runnable example, not a target-only design. |
| A name is missing in a notebook | Run its defining cell first or restart with Run All. |
| A calculation has an operand error | Check whether a number was replaced with text; use an explicit conversion only when that is intended. |
| A map key or list index fails | Inspect the supplied data and bounds; missing entries do not silently become absent values. |
| Large integers fail in the browser | Check the documented safe-integer range; Python and browser capacities differ. |
| Report validation reports several paths | Repair all listed fields before expecting a report; validation happens before eligibility filtering. |
| Download JSON is unavailable or stale | Use the default browser route, encode successfully, and rerun after editing source. |
| The browser remains at startup or reports asset loading failure | Retry/restart and inspect the visible error. CDN assets require network access; serving the checkout locally does not make those dependencies offline. |
| The online sample list has no calculation/report or inspection tabs | It is the older published preview. Serve the current checkout locally; deployment parity is awaiting the next fixing pass. |
| VS Code cannot run a file | Open a trusted workspace folder, save the file, and verify its configured Python executable has Nomi dependencies. |
| A Jupyter notebook opens but does not execute | Choose the Nomi kernel and run the kernel check in the [Jupyter troubleshooting guide](../../tools/jupyter/README.md#troubleshooting). |

### Report a reproducible problem

Include the smallest source that shows the issue, the expected and actual output,
the execution path (CLI, default browser, legacy browser, Jupyter, or VS Code),
and the relevant version/error text. For browser behavior, mention whether it
occurs in a scratch document or a sample and whether Run All reproduces it.
Remove credentials and private input before sharing a reproduction.

`nomi --version` reports the installed package version and preview status.
For a checkout, also include `git rev-parse --short HEAD`: local changes can
differ even when the package version is the same. `nomi --help` links this guide
and shows the command for the first calculation task.

Use [Playground problem](../../.github/ISSUE_TEMPLATE/playground.yml) for browser
issues, or [CLI, tools, installation, or documentation problem](../../.github/ISSUE_TEMPLATE/problem.yml)
for the other surfaces above. Support and release expectations remain described in
[Current Support And Growth](status.md#distribution-status).
