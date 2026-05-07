# Nomi for VS Code

Early VS Code support for the Nomi language.

## Features

- Registers `.nomi` files as the Nomi language.
- Adds syntax highlighting for current Nomi constructs such as `func`, arrow functions, validation-style bindings, and yield-to-block calls.
- Adds snippets for common Nomi forms.
- Adds `Nomi: Run File`, `Nomi: Run Selection`, and `Nomi: Open Terminal`.
- Adds lightweight document symbols, hover text, completions, and go to definition.

## One-Click Workflow

On macOS, the easiest path is to open `tools/vscode/nomi/scripts` in Finder and double-click:

- `setup.command`: installs extension dependencies.
- `dev.command`: opens the extension project in VS Code; press `F5` there.
- `test.command`: runs extension tests.
- `package.command`: builds a local `.vsix`.
- `install-local.command`: builds and installs the local `.vsix` into VS Code.
- `clean.command`: removes generated local artifacts.

The same interface is available from a terminal:

```bash
python3 tools/vscode/nomi/scripts/nomi-vscode.py setup
python3 tools/vscode/nomi/scripts/nomi-vscode.py install-local
```

Run this to see every action:

```bash
python3 tools/vscode/nomi/scripts/nomi-vscode.py
```

## VS Code Task Workflow

Open `tools/vscode/nomi` in VS Code and run `Tasks: Run Task`.

Available tasks:

- `Nomi Extension: Setup`
- `Nomi Extension: Test`
- `Nomi Extension: Package`
- `Nomi Extension: Install Local Package`
- `Nomi Extension: Publish Check`
- `Nomi Extension: Clean`

## Prerequisites

- VS Code Desktop
- Python 3
- Node.js and npm
- VS Code's `code-insiders` or `code` CLI for `install-local` and `dev`

On macOS with Homebrew:

```bash
brew install node
```

The wrapper prefers `code-insiders` when it is available, then falls back to `code`.
To install a VS Code CLI, open VS Code or VS Code Insiders and run `Shell Command:
Install 'code' command in PATH` from the Command Palette.

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

## Local Install

To install the extension locally without publishing:

```bash
python3 tools/vscode/nomi/scripts/nomi-vscode.py install-local
```

This installs dependencies if needed, builds the `.vsix`, and runs
`code-insiders --install-extension ... --force` when Insiders is available.

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
