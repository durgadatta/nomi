const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const vscode = require("vscode");

const processSuite = vscode.workspace.workspaceFolders?.length ? suite : suite.skip;

processSuite("Nomi process tasks (opened workspace required)", function () {
  this.timeout(30000);
  const cli = path.resolve(__dirname, "../../../../../../scripts/cli.py");
  let directory;
  let document;
  let previous;

  setup(async function () {
    assert.equal(vscode.workspace.isTrusted, true, "execution smoke needs a trusted test host");
    directory = fs.mkdtempSync(path.join(os.tmpdir(), "nomi task spaces "));
    const file = path.join(directory, "example 'quoted'.nomi");
    fs.writeFileSync(file, "print(2 + 3)\n");
    document = await vscode.workspace.openTextDocument(vscode.Uri.file(file));
    await vscode.window.showTextDocument(document);
    const config = vscode.workspace.getConfiguration("nomi", document.uri);
    const settings = {
      runner: "source", sourceCliPath: cli,
      pythonExecutable: process.env.NOMI_TEST_PYTHON || "python3"
    };
    previous = {};
    for (const [key, value] of Object.entries(settings)) {
      previous[key] = config.inspect(key)?.globalValue;
      await config.update(key, value, vscode.ConfigurationTarget.Global);
    }
  });

  teardown(async function () {
    const config = vscode.workspace.getConfiguration("nomi", document.uri);
    for (const [key, value] of Object.entries(previous || {})) {
      await config.update(key, value, vscode.ConfigurationTarget.Global);
    }
    fs.rmSync(directory, { recursive: true, force: true });
  });

  async function completedRun(command) {
    let subscription;
    let timer;
    const ended = new Promise((resolve, reject) => {
      timer = setTimeout(() => reject(new Error("Nomi process task did not complete")), 20000);
      subscription = vscode.tasks.onDidEndTaskProcess(event => {
        if (event.execution.task.source === "Nomi") resolve(event);
      });
    });
    try {
      await vscode.commands.executeCommand(command);
      const event = await ended;
      assert.equal(event.exitCode, 0, "source CLI must succeed in the real process task");
      assert.ok(event.execution.task.execution instanceof vscode.ProcessExecution);
      return event.execution.task.execution;
    } finally {
      clearTimeout(timer);
      subscription.dispose();
    }
  }

  test("runs a file with spaces and quotes through the source CLI", async function () {
    const execution = await completedRun("nomi.runFile");
    assert.deepEqual(execution.args, [cli, document.uri.fsPath]);
    assert.equal(execution.options.cwd, directory);
  });

  test("runs selection in the source directory and cleans its temporary file", async function () {
    const editor = vscode.window.activeTextEditor;
    editor.selection = new vscode.Selection(0, 0, 1, 0);
    const execution = await completedRun("nomi.runSelection");
    assert.equal(execution.options.cwd, directory);
    const selection = execution.args.at(-1);
    assert.notEqual(selection, document.uri.fsPath);
    const deadline = Date.now() + 5000;
    while (fs.existsSync(selection) && Date.now() < deadline) {
      await new Promise(resolve => setTimeout(resolve, 25));
    }
    assert.equal(fs.existsSync(path.dirname(selection)), false);
  });
});
