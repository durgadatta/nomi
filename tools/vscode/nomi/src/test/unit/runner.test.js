"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const test = require("node:test");
const { resolveRunPlan } = require("../../runner");
const { registerRunCommands } = require("../../run_commands");

test("source runner preserves executable and file names as literal argv", () => {
  const workspacePath = path.resolve("project with spaces");
  const filePath = path.join(workspacePath, "a';&$().nomi");
  assert.deepEqual(resolveRunPlan({ workspacePath, filePath, pythonExecutable: "python with spaces" }, () => true), {
    executable: "python with spaces", args: [path.join(workspacePath, "scripts", "cli.py"), filePath], cwd: workspacePath
  });
});

test("installed runner stays selected even if the source CLI exists", () => {
  const plan = resolveRunPlan({ filePath: path.resolve("x.nomi"), runner: "installed", executable: "custom nomi" }, () => true);
  assert.equal(plan.executable, "custom nomi");
  assert.equal(plan.args.length, 1);
});

test("auto falls back, explicit source fails, unknown modes fail", () => {
  const options = { filePath: path.resolve("x.nomi"), workspacePath: path.resolve("project") };
  assert.equal(resolveRunPlan(options, () => false).executable, "nomi");
  assert.throws(() => resolveRunPlan({ ...options, runner: "source" }, () => false), /not found/);
  assert.throws(() => resolveRunPlan({ ...options, runner: "shell" }), /Unknown/);
});

test("configured relative CLI resolves against the original workspace, not selection temp", () => {
  const workspacePath = path.resolve("second workspace");
  const plan = resolveRunPlan({ filePath: path.join(os.tmpdir(), "selection.nomi"), workspacePath, sourceCliPath: "local/cli.py" }, () => true);
  assert.equal(plan.args[0], path.join(workspacePath, "local", "cli.py"));
  assert.equal(plan.cwd, workspacePath);
});

function fixture(t, options = {}) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "nomi-runner-test-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const commands = new Map();
  const tasks = [];
  const warnings = [];
  const errors = [];
  let onEnd;
  const document = {
    languageId: "nomi", uri: { scheme: "file", fsPath: path.join(root, "main.nomi") },
    isDirty: options.dirty || false, save: async () => options.save !== false,
    getText: () => "print(5)"
  };
  const vscode = {
    workspace: {
      isTrusted: options.trusted !== false,
      workspaceFolders: options.emptyWorkspace ? [] : [{ uri: { fsPath: root } }],
      getWorkspaceFolder: () => options.noWorkspace ? undefined : { uri: { fsPath: root } },
      getConfiguration: (_name, uri) => {
        assert.equal(uri, document.uri);
        return { get: (key, fallback) => options.config?.[key] ?? fallback };
      },
      openTextDocument: async () => document
    },
    window: {
      activeTextEditor: { document, selection: { isEmpty: options.empty || false } },
      showWarningMessage: message => warnings.push(message),
      showErrorMessage: message => errors.push(message)
    },
    commands: { registerCommand: (name, fn) => { commands.set(name, fn); return { dispose() {} }; } },
    tasks: {
      onDidEndTask: fn => { onEnd = fn; return { dispose() {} }; },
      executeTask: async task => { tasks.push(task); if (options.failLaunch) throw new Error("launch failed"); }
    },
    ProcessExecution: class { constructor(executable, args, opts) { Object.assign(this, { executable, args, ...opts }); } },
    Task: class { constructor(definition, scope, name, source, execution) { Object.assign(this, { definition, scope, name, source, execution }); } },
    TaskScope: { Global: 1 }, TaskRevealKind: { Always: 1 }, TaskPanelKind: { Shared: 1 }
  };
  registerRunCommands(vscode, { subscriptions: [] });
  return { root, document, commands, tasks, warnings, errors, end: task => onEnd({ execution: { task } }) };
}

test("cancelled save aborts without creating a process task", async t => {
  const f = fixture(t, { dirty: true, save: false });
  await f.commands.get("nomi.runFile")();
  assert.equal(f.tasks.length, 0);
});

test("untrusted workspace blocks both execution commands", async t => {
  const f = fixture(t, { trusted: false });
  await f.commands.get("nomi.runFile")();
  await f.commands.get("nomi.runSelection")();
  assert.equal(f.tasks.length, 0);
  assert.equal(f.warnings.length, 2);
});

test("file command creates a process task, not a shell string", async t => {
  const f = fixture(t);
  await f.commands.get("nomi.runFile")();
  assert.deepEqual(f.tasks[0].execution.args, [f.document.uri.fsPath]);
  assert.equal(f.tasks[0].execution.cwd, f.root);
});

test("selections outside workspace roots use source cwd and clean unique files", async t => {
  const f = fixture(t, { noWorkspace: true });
  await f.commands.get("nomi.runSelection")();
  await f.commands.get("nomi.runSelection")();
  const files = f.tasks.map(task => task.execution.args.at(-1));
  t.after(() => files.forEach(file => fs.rmSync(path.dirname(file), { recursive: true, force: true })));
  assert.notEqual(files[0], files[1]);
  for (const task of f.tasks) {
    const file = task.execution.args.at(-1);
    assert.equal(fs.readFileSync(file, "utf8"), "print(5)\n");
    assert.equal(task.execution.cwd, f.root);
    f.end(task);
    assert.equal(fs.existsSync(path.dirname(file)), false);
  }
});

test("empty workspace aborts before preparing tasks or selection files", async t => {
  const f = fixture(t, { emptyWorkspace: true });
  await f.commands.get("nomi.runFile")();
  await f.commands.get("nomi.runSelection")();
  assert.equal(f.tasks.length, 0);
  assert.equal(f.warnings.length, 2);
});

test("failed task launch cleans the prepared selection", async t => {
  const f = fixture(t, { failLaunch: true });
  await f.commands.get("nomi.runSelection")();
  assert.equal(fs.existsSync(path.dirname(f.tasks[0].execution.args.at(-1))), false);
  assert.match(f.errors[0], /launch failed/);
});

test("untitled and empty selections do not launch", async t => {
  const f = fixture(t, { empty: true });
  await f.commands.get("nomi.runSelection")();
  f.document.uri.scheme = "untitled";
  await f.commands.get("nomi.runFile")();
  assert.equal(f.tasks.length, 0);
  assert.equal(f.warnings.length, 2);
});
