"""Editor startup must terminate visibly without mutating state after failure."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")
pytestmark = [
    pytest.mark.contract,
    pytest.mark.frontend,
    pytest.mark.skipif(NODE is None, reason="node is not installed"),
]


def editor_startup(scenario):
    script = r"""
const fs = require('fs'), vm = require('vm');
const scenario = process.argv[1], events = [], timers = new Map();
let onLoad, onError, timerId = 0, deadline;
const context = {
  setTimeout(callback, delay) { deadline = delay; timers.set(++timerId, callback); return timerId; },
  clearTimeout(id) { timers.delete(id); },
  monaco: {
    languages: {
      register() { events.push('register'); if (scenario === 'setup_error') throw new Error('registration failed'); },
      setMonarchTokensProvider() { events.push('tokens'); },
      setLanguageConfiguration() { events.push('configuration'); },
    },
    editor: { defineTheme() { events.push('theme'); } },
  },
};
if (scenario !== 'missing_loader') {
  context.require = (deps, loaded, failed) => {
    if (scenario === 'request_error') throw new Error('loader invocation failed');
    onLoad = loaded; onError = failed;
  };
  context.require.config = () => {
    if (scenario === 'config_error') throw new Error('loader configuration failed');
  };
}
vm.createContext(context);
vm.runInContext(fs.readFileSync('./web/editor.js', 'utf8'), context);
(async () => {
  const result = context.initMonaco().then(
    () => ({ status: 'ready' }),
    error => ({ status: 'failed', message: error.message }),
  );
  if (scenario === 'load_error') {
    if (typeof onError === 'function') onError(new Error('editor HTTP 404'));
  } else if (scenario === 'event_error') {
    if (typeof onError === 'function') onError({ type: 'error' });
  } else if (scenario === 'timeout') {
    if (timers.size) [...timers.values()][0]();
  } else if (onLoad) {
    onLoad();
  }
  const outcome = await Promise.race([
    result,
    new Promise(resolve => setTimeout(() => resolve({ status: 'pending' }), 20)),
  ]);
  const beforeLate = events.slice();
  if (scenario === 'timeout' && onLoad) onLoad();
  if (scenario === 'success' && typeof onError === 'function') onError(new Error('late error'));
  process.stdout.write(JSON.stringify({ outcome, deadline, timerCount: timers.size, events, beforeLate }));
})();
"""
    result = subprocess.run(
        [NODE, "-e", script, scenario],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    return json.loads(result.stdout)


@pytest.mark.parametrize(
    ("scenario", "message"),
    [
        ("load_error", "editor HTTP 404"),
        ("event_error", "Editor asset could not be loaded"),
        ("timeout", "timed out"),
        ("missing_loader", "Editor loader unavailable"),
        ("config_error", "loader configuration failed"),
        ("request_error", "loader invocation failed"),
        ("setup_error", "registration failed"),
    ],
)
def test_editor_failure_rejects_and_clears_its_deadline(scenario, message):
    result = editor_startup(scenario)
    assert result["outcome"]["status"] == "failed"
    assert message in result["outcome"]["message"]
    assert result["timerCount"] == 0


def test_stalled_editor_has_a_bounded_deadline_and_ignores_late_success():
    result = editor_startup("timeout")
    assert 0 < result["deadline"] <= 30_000
    assert result["events"] == result["beforeLate"] == []


def test_successful_editor_setup_clears_deadline_and_ignores_late_error():
    result = editor_startup("success")
    assert result["outcome"] == {"status": "ready"}
    assert result["timerCount"] == 0
    assert result["events"] == ["register", "tokens", "configuration", "theme"]


def startup_failure_state(scenario):
    script = r"""
const fs = require('fs'), vm = require('vm'), nodes = new Map();
let workerStops = 0, pendingRejected = 0;
const classes = { add() {}, remove() {}, toggle() {} };
function node(id) {
  if (!nodes.has(id)) nodes.set(id, { textContent: '', hidden: false, disabled: false, classList: classes, style: {} });
  return nodes.get(id);
}
const context = {
  URLSearchParams, location: { search: '' }, performance: { now: () => 0 },
  document: {
    getElementById: node, querySelector: node, querySelectorAll: () => [], addEventListener() {},
    body: { classList: classes },
  },
  window: {}, addEventListener() {}, console: { log() {}, error() {} },
  setTimeout, clearTimeout,
  worker: { terminate() { workerStops++; } },
  rejectPending() { pendingRejected++; },
};
vm.createContext(context);
vm.runInContext(fs.readFileSync('./web/app.js', 'utf8'), context);
vm.runInContext(fs.readFileSync('./web/runtime.js', 'utf8'), context);
vm.runInContext('_runtimeWorker = worker; _runtimePending.set(1, { reject: rejectPending });', context);
let restartIgnored;
if (process.argv[1] === 'startup') {
  context.failStartup(new Error('editor HTTP 404'));
  context.handleRuntimeMessage({ data: { type: 'log', message: 'WASM parser ready' } });
  context.log('late direct progress');
  const epoch = vm.runInContext('_runEpoch', context);
  context.window.restartWorker();
  restartIgnored = vm.runInContext('_runEpoch', context) === epoch;
} else {
  context.failRuntime(new Error('ordinary worker failure'));
  context.log('worker restart progress');
}
process.stdout.write(JSON.stringify({
  workerStops, pendingRejected, restartIgnored,
  message: node('loading-msg').textContent,
  title: node('loading-title').textContent,
  retryHidden: node('loading-retry-btn').hidden,
  spinnerHidden: node('.spinner').hidden,
  restartDisabled: node('restart-btn').disabled,
  runDisabled: node('run-all-btn').disabled,
  pendingCount: vm.runInContext('_runtimePending.size', context),
  workerCleared: vm.runInContext('_runtimeWorker === null', context),
}));
"""
    result = subprocess.run(
        [NODE, "-e", script, scenario],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    return json.loads(result.stdout)


def test_terminal_startup_failure_keeps_its_error_and_clears_boot_worker():
    result = startup_failure_state("startup")
    assert result["message"] == "editor HTTP 404"
    assert result["title"] == "Nomi unavailable"
    assert result["retryHidden"] is False
    assert result["spinnerHidden"] is True
    assert result["runDisabled"] is True
    assert result["restartDisabled"] is True
    assert result["restartIgnored"] is True
    assert result["workerStops"] == result["pendingRejected"] == 1
    assert result["pendingCount"] == 0
    assert result["workerCleared"] is True


def test_ordinary_runtime_failure_remains_restartable_without_terminal_boot_state():
    result = startup_failure_state("runtime")
    assert result["message"] == "worker restart progress"
    assert result["restartDisabled"] is False
    assert result["runDisabled"] is True
