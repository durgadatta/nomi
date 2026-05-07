# VS Code Extension

Nomi has an early VS Code extension under:

```text
tools/vscode/nomi
```

The extension intentionally starts lightweight: plain JavaScript activation code, VS Code contribution metadata, TextMate syntax highlighting, and a small test harness. That keeps the first local workflow simple while leaving room to grow into parser-backed diagnostics and an LSP later.

## Current Capabilities

- `.nomi` language registration.
- Syntax highlighting for `func`, arrow functions, validation-style bindings, yield-to-block calls, comments, strings, numbers, and Python-like control flow.
- Language configuration for comments, brackets, indentation, and folding.
- Snippets for common Nomi forms.
- Commands: `Nomi: Run File`, `Nomi: Run Selection`, and `Nomi: Open Terminal`.
- Lightweight editor intelligence: document symbols, hover notes, completions, and first-pass go to definition.

## Friendly Interface

Use the wrapper script instead of calling npm/vsce directly:

```bash
python3 tools/vscode/nomi/scripts/nomi-vscode.py
```

Supported actions:

- `setup`: install npm dependencies.
- `test`: run VS Code extension tests.
- `package`: build a local `.vsix`.
- `install-local`: build and install the `.vsix` into local VS Code.
- `dev`: open the extension folder in VS Code for `F5` debugging.
- `status`: show environment and artifact status.
- `clean`: remove generated artifacts.
- `publish-check`: show Marketplace readiness checklist.
- `publish`: run tests, package, and publish with `vsce`.

On macOS, clickable `.command` wrappers live in:

```text
tools/vscode/nomi/scripts
```

Double-click `install-local.command` for the easiest non-published local install.

## VS Code Tasks

Open `tools/vscode/nomi` in VS Code and run `Tasks: Run Task`.

Tasks are provided for setup, test, package, local install, publish check, and clean.

## Local Install Without Publishing

Run:

```bash
python3 tools/vscode/nomi/scripts/nomi-vscode.py install-local
```

This:

1. Installs dependencies if needed.
2. Builds `nomi-vscode-<version>.vsix`.
3. Installs it into VS Code with `code --install-extension ... --force`.

Prerequisites:

- VS Code Desktop
- Python 3
- Node.js/npm
- VS Code's `code-insiders` or `code` CLI

The wrapper prefers `code-insiders` when it is available, then falls back to
`code`. To install a VS Code CLI, run `Shell Command: Install 'code' command in
PATH` from VS Code or VS Code Insiders.

## Development Host

Run:

```bash
python3 tools/vscode/nomi/scripts/nomi-vscode.py dev
```

Then press `F5` in VS Code. In the Extension Development Host:

1. Open the Nomi repository folder.
2. Open `scripts/demo.nomi`.
3. Confirm highlighting, snippets, Outline, hover, and go to definition.
4. Run `Nomi: Run File`.
5. Select a few lines and run `Nomi: Run Selection`.

The extension runner defaults to `auto`: inside this repository it uses `python3 scripts/cli.py`; outside the source repository it falls back to an installed `nomi` command.

## Tests

Run:

```bash
python3 tools/vscode/nomi/scripts/nomi-vscode.py test
```

The test command uses the official VS Code extension test CLI, backed by `@vscode/test-electron`. Current tests cover activation, document symbols, and same-document go to definition.

## Generated Files

The repo ignores local JavaScript/tooling artifacts:

- `node_modules/`
- `.vscode-test/`
- `*.vsix`
- npm/yarn/pnpm debug logs
- common `dist/` and `out/` build folders

`package-lock.json` is intentionally tracked so dependency resolution is reproducible.

## Packaging

Run:

```bash
python3 tools/vscode/nomi/scripts/nomi-vscode.py package
```

The generated `.vsix` is installable locally and ignored by git.

## Publishing

First inspect readiness:

```bash
python3 tools/vscode/nomi/scripts/nomi-vscode.py publish-check --publisher your-publisher-id
```

Before first public release:

1. Set the real Marketplace publisher id in `package.json`.
2. Confirm repository metadata.
3. Add a license file or decide how the extension inherits repo licensing.
4. Add an icon and changelog.
5. Create a Visual Studio Marketplace publisher.
6. Create an Azure DevOps Personal Access Token.
7. Run `cd tools/vscode/nomi && npx vsce login <publisher-id>`.

Publish:

```bash
python3 tools/vscode/nomi/scripts/nomi-vscode.py publish
```

The same `.vsix` package used for local installation is the artifact `vsce` publishes, so the local activation path and Marketplace path stay close.

Official references:

- VS Code extension quickstart: https://code.visualstudio.com/api/get-started/your-first-extension
- VS Code extension testing: https://code.visualstudio.com/api/working-with-extensions/testing-extension
- VS Code extension publishing: https://code.visualstudio.com/api/working-with-extensions/publishing-extension

## Next Iterations

- Replace regex definition scanning with parser-backed symbol extraction from `prototype/grammar/nomi.lark`.
- Add diagnostics by running the parser on document changes.
- Add formatting once the syntax stabilizes.
- Split richer behavior into a Language Server Protocol process.
- Add Marketplace icon/changelog/license polish.
