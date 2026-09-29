---
applyTo: "tools/vscode/nomi/**,.vscode/tasks.json,docs/orientation/vscode_extension.md"
---

# VS Code Extension Instructions

Use `docs/orientation/vscode_extension.md`,
`tools/vscode/nomi/README.md`, and `.agents/skills/nomi-ai-native/SKILL.md`
before changing the editor workflow.

Use the wrapper script instead of calling npm or vsce directly:

```bash
python3 tools/vscode/nomi/scripts/nomi-vscode.py test
python3 tools/vscode/nomi/scripts/nomi-vscode.py package
python3 tools/vscode/nomi/scripts/nomi-vscode.py enable-local
```

If syntax highlighting changes, keep VS Code TextMate grammar and Monaco
highlighting in sync:

```text
tools/vscode/nomi/syntaxes/nomi.tmLanguage.json
web/editor.js
```

The extension should support the same first-hour story as the GitHub Pages
playground: open a `.nomi` file, recognize the language, run the file or
selection, and keep diagnostics understandable.
