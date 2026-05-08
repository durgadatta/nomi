# Nomi for VS Code

Early VS Code support for the Nomi language.

## Features

- Registers `.nomi` files as the Nomi language.
- Adds syntax highlighting for current Nomi constructs such as `func`, arrow functions, validation-style bindings, and yield-to-block calls.
- Adds snippets for common Nomi forms.
- Adds `Nomi: Run File`, `Nomi: Run Selection`, and `Nomi: Open Terminal`.
- Adds lightweight document symbols, hover text, completions, and go to definition.

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

For active extension development:

```bash
python3 tools/vscode/nomi/scripts/nomi-vscode.py dev
```

Then press `F5` in VS Code to launch an Extension Development Host.

Manual smoke test:

1. In the Extension Development Host, open the Nomi repository folder.
2. Open `scripts/demo.nomi`.
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
It then opens `scripts/demo.nomi`, which activates the extension because `.nomi`
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

Before the first public release, update the placeholder publisher/repository metadata and add Marketplace polish such as icon, changelog, and license file.

Official references:

- https://code.visualstudio.com/api/get-started/your-first-extension
- https://code.visualstudio.com/api/working-with-extensions/testing-extension
- https://code.visualstudio.com/api/working-with-extensions/publishing-extension
