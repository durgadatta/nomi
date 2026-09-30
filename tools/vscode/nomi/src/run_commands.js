"use strict";

const fs = require("fs");
const os = require("os");
const path = require("path");
const { resolveRunPlan } = require("./runner");

function registerRunCommands(vscode, context) {
  const selections = new Map();
  let nextId = 0;

  function trusted() {
    if (!vscode.workspace.isTrusted) {
      vscode.window.showWarningMessage("Trust this workspace before running Nomi code.");
      return false;
    }
    if (!vscode.workspace.workspaceFolders?.length) {
      vscode.window.showWarningMessage("Open a folder in this workspace before running Nomi code.");
      return false;
    }
    return true;
  }

  function cleanup(id) {
    const directory = selections.get(id);
    if (directory) {
      fs.rmSync(directory, { recursive: true, force: true });
      selections.delete(id);
    }
  }

  async function launch(document, filePath, directory) {
    const id = ++nextId;
    if (directory) selections.set(id, directory);
    try {
      const folder = vscode.workspace.getWorkspaceFolder(document.uri);
      const config = vscode.workspace.getConfiguration("nomi", document.uri);
      const plan = resolveRunPlan({
        filePath,
        workspacePath: folder?.uri.fsPath,
        cwd: path.dirname(document.uri.fsPath),
        runner: config.get("runner", "auto"),
        executable: config.get("executable", "nomi"),
        pythonExecutable: config.get("pythonExecutable", "python3"),
        sourceCliPath: config.get("sourceCliPath", "")
      });
      const execution = new vscode.ProcessExecution(plan.executable, plan.args, { cwd: plan.cwd });
      const task = new vscode.Task(
        { type: "nomi", runId: id }, folder || vscode.TaskScope.Global,
        directory ? "Run Selection" : "Run File", "Nomi", execution, []
      );
      task.presentationOptions = { reveal: vscode.TaskRevealKind.Always, panel: vscode.TaskPanelKind.Shared };
      await vscode.tasks.executeTask(task);
    } catch (error) {
      cleanup(id);
      vscode.window.showErrorMessage(`Could not run Nomi: ${error.message}`);
    }
  }

  async function runFile(resource) {
    if (!trusted()) return;
    const document = resource?.scheme === "file"
      ? await vscode.workspace.openTextDocument(resource)
      : vscode.window.activeTextEditor?.document;
    if (!document || document.languageId !== "nomi" || document.uri.scheme !== "file") {
      vscode.window.showWarningMessage("Open a saved .nomi file to run it.");
      return;
    }
    if (document.isDirty && !(await document.save())) return;
    await launch(document, document.uri.fsPath);
  }

  async function runSelection() {
    if (!trusted()) return;
    const editor = vscode.window.activeTextEditor;
    if (!editor || editor.document.languageId !== "nomi" || editor.document.uri.scheme !== "file") {
      vscode.window.showWarningMessage("Select Nomi code in a saved .nomi file first.");
      return;
    }
    if (editor.selection.isEmpty) {
      vscode.window.showWarningMessage("Select Nomi code to run.");
      return;
    }
    const directory = fs.mkdtempSync(path.join(os.tmpdir(), "nomi-vscode-"));
    try {
      const code = editor.document.getText(editor.selection);
      const filePath = path.join(directory, "selection.nomi");
      fs.writeFileSync(filePath, code.endsWith("\n") ? code : `${code}\n`, "utf8");
      await launch(editor.document, filePath, directory);
    } catch (error) {
      fs.rmSync(directory, { recursive: true, force: true });
      vscode.window.showErrorMessage(`Could not prepare Nomi selection: ${error.message}`);
    }
  }

  context.subscriptions.push(
    vscode.commands.registerCommand("nomi.runFile", runFile),
    vscode.commands.registerCommand("nomi.runSelection", runSelection),
    vscode.tasks.onDidEndTask(event => {
      if (event.execution.task.definition.type === "nomi") cleanup(event.execution.task.definition.runId);
    })
  );
}

module.exports = { registerRunCommands };
