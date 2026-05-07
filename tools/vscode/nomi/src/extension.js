"use strict";

const fs = require("fs");
const os = require("os");
const path = require("path");
const vscode = require("vscode");

const NOMI_SELECTOR = { language: "nomi" };
const WORD_RE = /[A-Za-z_]\w*/;

let terminal;

function activate(context) {
  context.subscriptions.push(
    vscode.commands.registerCommand("nomi.runFile", runFile),
    vscode.commands.registerCommand("nomi.runSelection", runSelection),
    vscode.commands.registerCommand("nomi.openTerminal", openTerminal),
    vscode.languages.registerDefinitionProvider(NOMI_SELECTOR, new NomiDefinitionProvider()),
    vscode.languages.registerDocumentSymbolProvider(NOMI_SELECTOR, new NomiDocumentSymbolProvider()),
    vscode.languages.registerHoverProvider(NOMI_SELECTOR, new NomiHoverProvider()),
    vscode.languages.registerCompletionItemProvider(NOMI_SELECTOR, new NomiCompletionProvider())
  );
}

function deactivate() {}

async function runFile(resource) {
  const document = await resolveDocument(resource);
  if (!document) {
    vscode.window.showWarningMessage("Open a .nomi file to run it.");
    return;
  }

  if (document.isDirty) {
    await document.save();
  }

  const command = buildRunCommand(document.uri.fsPath);
  if (!command) {
    return;
  }
  sendToNomiTerminal(command);
}

async function runSelection() {
  const editor = vscode.window.activeTextEditor;
  if (!editor || editor.document.languageId !== "nomi") {
    vscode.window.showWarningMessage("Select Nomi code in a .nomi file first.");
    return;
  }

  const selection = editor.selection;
  if (selection.isEmpty) {
    vscode.window.showWarningMessage("Select Nomi code to run.");
    return;
  }

  const code = editor.document.getText(selection);
  const tmpDir = path.join(os.tmpdir(), "nomi-vscode");
  fs.mkdirSync(tmpDir, { recursive: true });
  const tmpFile = path.join(tmpDir, `selection-${Date.now()}.nomi`);
  fs.writeFileSync(tmpFile, code.endsWith("\n") ? code : `${code}\n`, "utf8");

  const command = buildRunCommand(tmpFile);
  if (command) {
    sendToNomiTerminal(command);
  }
}

function openTerminal() {
  getNomiTerminal().show();
}

async function resolveDocument(resource) {
  if (resource && resource.scheme === "file") {
    return vscode.workspace.openTextDocument(resource);
  }

  const editor = vscode.window.activeTextEditor;
  if (editor && editor.document.languageId === "nomi") {
    return editor.document;
  }

  return undefined;
}

function getNomiTerminal() {
  if (!terminal || terminal.exitStatus) {
    terminal = vscode.window.createTerminal("Nomi");
  }
  return terminal;
}

function sendToNomiTerminal(command) {
  const nomiTerminal = getNomiTerminal();
  nomiTerminal.show();
  nomiTerminal.sendText(command);
}

function buildRunCommand(filePath) {
  const config = vscode.workspace.getConfiguration("nomi");
  const runner = config.get("runner", "auto");
  const sourceCli = resolveSourceCliPath(filePath, config);

  if (runner === "source") {
    if (!sourceCli) {
      vscode.window.showErrorMessage("Nomi source runner requested, but scripts/cli.py was not found.");
      return undefined;
    }
    return `${quote(config.get("pythonExecutable", "python3"))} ${quote(sourceCli)} ${quote(filePath)}`;
  }

  if (runner === "auto" && sourceCli) {
    return `${quote(config.get("pythonExecutable", "python3"))} ${quote(sourceCli)} ${quote(filePath)}`;
  }

  return `${quote(config.get("executable", "nomi"))} ${quote(filePath)}`;
}

function resolveSourceCliPath(filePath, config) {
  const configuredPath = config.get("sourceCliPath", "").trim();
  const workspaceFolder = vscode.workspace.getWorkspaceFolder(vscode.Uri.file(filePath)) || vscode.workspace.workspaceFolders?.[0];

  if (configuredPath) {
    const absolutePath = path.isAbsolute(configuredPath)
      ? configuredPath
      : workspaceFolder
        ? path.join(workspaceFolder.uri.fsPath, configuredPath)
        : configuredPath;
    return fs.existsSync(absolutePath) ? absolutePath : undefined;
  }

  if (!workspaceFolder) {
    return undefined;
  }

  const localCli = path.join(workspaceFolder.uri.fsPath, "scripts", "cli.py");
  return fs.existsSync(localCli) ? localCli : undefined;
}

function quote(value) {
  if (/^[A-Za-z0-9_./:=+-]+$/.test(value)) {
    return value;
  }
  return `'${value.replace(/'/g, "'\\''")}'`;
}

class NomiDefinitionProvider {
  async provideDefinition(document, position) {
    const range = document.getWordRangeAtPosition(position, WORD_RE);
    if (!range) {
      return undefined;
    }

    const symbol = document.getText(range);
    const localDefinition = findDefinitionInDocument(document, symbol, position);
    if (localDefinition) {
      return localDefinition;
    }

    const config = vscode.workspace.getConfiguration("nomi");
    const limit = config.get("definitionSearchLimit", 200);
    const files = await vscode.workspace.findFiles("**/*.nomi", "**/{.git,node_modules,dist,out}/**", limit);

    for (const file of files) {
      if (file.toString() === document.uri.toString()) {
        continue;
      }

      const candidate = await vscode.workspace.openTextDocument(file);
      const definition = findDefinitionInDocument(candidate, symbol);
      if (definition) {
        return definition;
      }
    }

    return undefined;
  }
}

class NomiDocumentSymbolProvider {
  provideDocumentSymbols(document) {
    const symbols = [];
    const stack = [];

    for (let line = 0; line < document.lineCount; line += 1) {
      const text = document.lineAt(line).text;
      const item = symbolFromLine(document, line, text);
      if (!item) {
        continue;
      }

      const { indent, symbol } = item;
      while (stack.length && stack[stack.length - 1].indent >= indent) {
        stack.pop();
      }

      if (stack.length) {
        stack[stack.length - 1].symbol.children.push(symbol);
      } else {
        symbols.push(symbol);
      }

      if (symbol.kind === vscode.SymbolKind.Function || symbol.kind === vscode.SymbolKind.Class) {
        stack.push({ indent, symbol });
      }
    }

    return symbols;
  }
}

class NomiHoverProvider {
  provideHover(document, position) {
    const range = document.getWordRangeAtPosition(position, WORD_RE);
    if (!range) {
      return undefined;
    }

    const word = document.getText(range);
    const markdown = hoverMarkdown(word);
    return markdown ? new vscode.Hover(markdown, range) : undefined;
  }
}

class NomiCompletionProvider {
  provideCompletionItems() {
    return [
      keywordCompletion("func", "Define a Nomi function."),
      keywordCompletion("yield", "Yield from a function, including yield-to-block functions."),
      keywordCompletion("match", "Pattern matching statement."),
      keywordCompletion("case", "Pattern matching case."),
      keywordCompletion("async", "Async modifier."),
      keywordCompletion("await", "Await an async expression."),
      snippetCompletion("func", "Function", "func ${1:name}(${2:args}):\n    ${0:pass}"),
      snippetCompletion("arrow", "Arrow function", "(${1:x}) => ${0:x}"),
      snippetCompletion("block", "Yield-to-block call", "${1:callee}(${2:args}):\n    ${0:pass}"),
      snippetCompletion("each", "Block call with parameter", "${1:callee}(${2:items}) -> ${3:item}:\n    ${0:pass}")
    ];
  }
}

function findDefinitionInDocument(document, symbol, currentPosition) {
  const text = document.getText();
  const patterns = [
    { regex: new RegExp(`^([ \\t]*)(?:async\\s+)?func\\s+(${escapeRegExp(symbol)})\\s*\\(`, "gm"), group: 2, kind: "function" },
    { regex: new RegExp(`^([ \\t]*)class\\s+(${escapeRegExp(symbol)})\\b`, "gm"), group: 2, kind: "class" },
    { regex: new RegExp(`^([ \\t]*)(${escapeRegExp(symbol)})\\s*(?::[^=\\n]+)?=`, "gm"), group: 2, kind: "binding" }
  ];

  for (const pattern of patterns) {
    let match;
    while ((match = pattern.regex.exec(text))) {
      const start = match.index + match[0].indexOf(match[pattern.group]);
      const position = document.positionAt(start);
      if (currentPosition && position.line === currentPosition.line) {
        continue;
      }
      return new vscode.Location(document.uri, new vscode.Range(position, position.translate(0, symbol.length)));
    }
  }

  return undefined;
}

function symbolFromLine(document, line, text) {
  const patterns = [
    {
      regex: /^(\s*)(?:async\s+)?func\s+([A-Za-z_]\w*)\s*\(([^)]*)\)\s*(?:->\s*([^:]+))?:/,
      kind: vscode.SymbolKind.Function,
      detail: (match) => `func(${match[3] || ""})${match[4] ? ` -> ${match[4].trim()}` : ""}`
    },
    {
      regex: /^(\s*)class\s+([A-Za-z_]\w*)\b/,
      kind: vscode.SymbolKind.Class,
      detail: () => "class"
    },
    {
      regex: /^(\s*)([A-Za-z_]\w*)\s*(?::[^=\n]+)?=/,
      kind: vscode.SymbolKind.Variable,
      detail: () => "binding"
    }
  ];

  for (const pattern of patterns) {
    const match = pattern.regex.exec(text);
    if (!match) {
      continue;
    }

    const name = match[2];
    const nameStart = text.indexOf(name);
    const range = document.lineAt(line).range;
    const selectionRange = new vscode.Range(line, nameStart, line, nameStart + name.length);
    const symbol = new vscode.DocumentSymbol(name, pattern.detail(match), pattern.kind, range, selectionRange);
    return { indent: match[1].length, symbol };
  }

  return undefined;
}

function hoverMarkdown(word) {
  const notes = {
    func: "Defines a Nomi function. Nomi uses `func` where Python uses `def`.",
    yield: "Yields a value or control point. Nomi also uses this for yield-to-block patterns.",
    "=>": "Creates an expression-level arrow function.",
    match: "Starts a pattern matching statement.",
    case: "Introduces a pattern matching branch.",
    None: "The null-like singleton value inherited from Python semantics.",
    True: "Boolean truth value.",
    False: "Boolean false value."
  };

  return notes[word] ? new vscode.MarkdownString(notes[word]) : undefined;
}

function keywordCompletion(label, documentation) {
  const item = new vscode.CompletionItem(label, vscode.CompletionItemKind.Keyword);
  item.documentation = documentation;
  return item;
}

function snippetCompletion(label, detail, snippet) {
  const item = new vscode.CompletionItem(label, vscode.CompletionItemKind.Snippet);
  item.detail = detail;
  item.insertText = new vscode.SnippetString(snippet);
  return item;
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

module.exports = {
  activate,
  deactivate
};
