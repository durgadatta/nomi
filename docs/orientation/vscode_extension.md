# VS Code Extension

> Status: current tooling orientation for the local VS Code extension.
>
> Role: setup, capability map, and roadmap for `tools/vscode/nomi`.

Nomi has an early VS Code extension.

For user setup and everyday run commands, start with
[Using Nomi's Tools](../guide/tools.md#vs-code). This page owns the detailed
extension configuration and developer workflow.

Its source lives under:

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
- `enable-local`: build/install the `.vsix`, then open `samples/calculate.nomi` to activate it.
- `dev`: open the extension folder in VS Code for `F5` debugging.
- `status`: show environment and artifact status.
- `clean`: remove generated artifacts.
- `publish-check`: show Marketplace readiness checklist.
- `publish`: run tests, package, and publish with `vsce`.

## VS Code Tasks

Open the repository root in VS Code and run `Tasks: Run Task`. The root
`.vscode/tasks.json` exposes namespaced extension tasks such as
`Nomi Extension: Test`, `Nomi Extension: Package`, and
`Nomi Extension: Enable Local Package`.

The same task menu connects editor work to the GitHub playground:

| Task | Purpose |
| --- | --- |
| `Nomi Web: Check Runtime` | Run the same manifest, WASM, runtime, and agent checks as CI. |
| `Nomi Web: Browser Smoke` | Open Chromium and verify a real sample, pipeline details, and scratch output. |
| `Nomi Web: Launch Playground` | Check runtime freshness, then open a local server using committed artifacts. Stop the task with Ctrl+C. |
| `Nomi Agent: Doctor` | Check agent instructions, hooks, skills, and local RAG freshness. |

Install `.[dev]` and Node.js for the runtime checks. Browser smoke also needs
`.[web-test]` and `python3 -m playwright install chromium`; see the
[playground setup](../../README.md#web-playground). Tasks run `python3` from the
workspace root, so its environment must contain these dependencies.

Copilot repository instructions live in `.github/copilot-instructions.md`;
path-specific instructions in `.github/instructions/` route playground and
extension work to the canonical `AGENTS.md` and `.agents/skills/` guidance.

The extension folder also has its own `tools/vscode/nomi/.vscode/tasks.json` for
the narrower workflow where only `tools/vscode/nomi` is opened as the VS Code
workspace.

## Enable Locally Without Publishing

Run:

```bash
python3 tools/vscode/nomi/scripts/nomi-vscode.py enable-local
```

This:

1. Installs dependencies if needed.
2. Builds `nomi-vscode-<version>.vsix`.
3. Installs it into VS Code with `code --install-extension ... --force`.
4. Opens `samples/calculate.nomi` to activate the extension.

Use `install-local` instead if you want to install the package without opening a file.

Prerequisites:

- VS Code Desktop
- Python 3
- Node.js/npm
- a VS Code-compatible CLI, usually `code`

To use a different compatible CLI command, set `NOMI_VSCODE_CLI` before running
the wrapper.

## Development Host

Run:

```bash
python3 tools/vscode/nomi/scripts/nomi-vscode.py dev
```

Then press `F5` in VS Code. In the Extension Development Host:

1. Open the Nomi repository folder.
2. Open `samples/calculate.nomi`.
3. Confirm highlighting, snippets, Outline, hover, and go to definition.
4. Run `Nomi: Run File`.
5. Select a few lines and run `Nomi: Run Selection`.

The extension runner defaults to `auto`: inside this repository it uses `python3 scripts/cli.py`; outside the source repository it falls back to an installed `nomi` command.

Execution uses a VS Code **process task**, with separate executable and argv
values, rather than sending shell text. Output appears in the task terminal;
VS Code's task controls can stop it. `nomi.executable` and
`nomi.pythonExecutable` accept a single executable name or path, not a command
with flags. Source execution requires Python 3.12+ and the prototype's
dependencies in that interpreter.

Running code requires workspace trust and at least one opened workspace folder.
VS Code rejects first process tasks with a non-home cwd in an empty window;
the extension reports this requirement before launching. `Run File` requires a saved local file
and aborts when saving a dirty document fails or is cancelled. `Run Selection`
uses resource-scoped settings and the original document's workspace, even in
multi-root workspaces; for files outside workspace roots its cwd is the document directory.
Each selection gets a unique temporary directory, removed when its task ends
or launch fails. A crashed/reloaded extension host may leave temporary files;
selection execution is not a sandbox or a persistent notebook session.

`src/runner.js` owns plain-data runner resolution; `src/run_commands.js` owns
editor/task lifecycle; `src/extension.js` owns activation and navigation.
Language navigation remains regex-based and supports the prototype, not all
target-only language forms. Browser-only/virtual workspaces are not supported.

## Tests

Run:

```bash
python3 tools/vscode/nomi/scripts/nomi-vscode.py test
```

The wrapper first runs `npm run test:unit` for runner/lifecycle checks, then
the official VS Code extension test CLI, backed by `@vscode/test-electron`.
Host tests cover activation, document symbols, same-document go to definition,
and file/selection process execution through the source CLI. Set
`NOMI_TEST_PYTHON` to the Python executable containing Nomi's dependencies for
the process checks, and launch the host with an opened workspace. Unit tests
use a VS Code substitute; neither local suite proves every operating system.
The currently tracked launcher also has a macOS executable-name issue; see the separate
[test review](../review/2026-09-30-test-issues.md) for deferred coverage work.

The argument-based task API and trust gate follow the official
[VS Code API](https://code.visualstudio.com/api/references/vscode-api) and
[Workspace Trust guide](https://code.visualstudio.com/api/extension-guides/workspace-trust).

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

- Replace regex definition scanning with parser-backed symbol extraction from `prototype/grammar/layers/`.
- Add diagnostics by running the parser on document changes.
- Add formatting once the syntax stabilizes.
- Split richer behavior into a Language Server Protocol process.
- Add Marketplace icon/changelog/license polish.
