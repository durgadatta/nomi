# Nomi for VS Code

Early VS Code support for the Nomi language.

New to Nomi? Start with the [user guide](../../../docs/guide/README.md) and
open `samples/calculate.nomi` for the first task. The extension also highlights
older experimental syntax; the [example catalog](../../../docs/guide/examples.md)
explains which samples to learn from and which explore historical forms.

## Features

- Registers `.nomi` files as the Nomi language.
- Adds syntax highlighting for current Nomi constructs such as `func`, arrow functions, validation-style bindings, and yield-to-block calls.
- Adds snippets for common Nomi forms.
- Adds `Nomi: Run File`, `Nomi: Run Selection`, and `Nomi: Open Terminal`.
- Adds lightweight document symbols, hover text, completions, and go to definition.

Run commands create process tasks, not shell command strings. Workspace trust
and an opened workspace folder are required; cancelled saves do not run stale files. Runner settings accept
single executable names or paths (no shell flags). Selections use their source
workspace settings and cwd, and their temporary files are deleted when the
task ends. Source execution needs Python 3.12+ with Nomi's dependencies.

## Local Workflow

Use the project wrapper from a terminal:

```bash
python3 tools/vscode/nomi/scripts/nomi-vscode.py setup
python3 tools/vscode/nomi/scripts/nomi-vscode.py enable-local
```

Run this to see every action:

```bash
python3 tools/vscode/nomi/scripts/nomi-vscode.py
```

## VS Code Task Workflow

If the repository root is open in VS Code, run `Tasks: Run Task` and choose one
of the namespaced `Nomi Extension: ...` tasks from the root `.vscode/tasks.json`.

If only `tools/vscode/nomi` is open as the VS Code workspace, VS Code uses this
folder's `.vscode/tasks.json` instead.

Available tasks:

- `Nomi Extension: Setup`
- `Nomi Extension: Test`
- `Nomi Extension: Package`
- `Nomi Extension: Install Local Package`
- `Nomi Extension: Enable Local Package`
- `Nomi Extension: Publish Check`
- `Nomi Extension: Clean`

## Prerequisites

- VS Code Desktop
- Python 3
- Node.js and npm
- a VS Code-compatible CLI, usually `code`, for `install-local` and `dev`

To use a different compatible CLI command, set `NOMI_VSCODE_CLI` before running
the wrapper.

## Local Development

Run the isolated runner checks with `npm run test:unit` from this folder. The
wrapper's `test` action runs those checks and the VS Code host suite.

For active extension development:

```bash
python3 tools/vscode/nomi/scripts/nomi-vscode.py dev
```

Then press `F5` in VS Code to launch an Extension Development Host.

Manual smoke test:

1. In the Extension Development Host, open the Nomi repository folder.
2. Open `samples/calculate.nomi`.
3. Confirm syntax highlighting appears.
4. Run `Nomi: Run File`.
5. Select a few lines and run `Nomi: Run Selection`.
6. Use Outline, hover, completions, and go to definition on a local function call.

## Enable Locally

To install or update the extension locally without publishing and activate it immediately:

```bash
python3 tools/vscode/nomi/scripts/nomi-vscode.py enable-local
```

This installs dependencies if needed, builds the `.vsix`, and runs
`code --install-extension ... --force`.
It then opens `samples/calculate.nomi`, which activates the extension because `.nomi`
files are registered to the Nomi language.

If you only want to install/update the package without opening a file:

```bash
python3 tools/vscode/nomi/scripts/nomi-vscode.py install-local
```

## Publish Prep

To see the publishing checklist:

```bash
python3 tools/vscode/nomi/scripts/nomi-vscode.py publish-check --publisher your-publisher-id
```

To publish after Marketplace credentials are configured:

```bash
python3 tools/vscode/nomi/scripts/nomi-vscode.py publish
```

Repository metadata matches the project's Git origin. Before the first public
release, confirm the Marketplace publisher and add an icon, changelog, and
owner-approved license file. Local packaging does not publish the extension.

Official references:

- https://code.visualstudio.com/api/get-started/your-first-extension
- https://code.visualstudio.com/api/working-with-extensions/testing-extension
- https://code.visualstudio.com/api/working-with-extensions/publishing-extension
