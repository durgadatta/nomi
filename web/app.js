// Nomi Web Playground — global state, utilities, init orchestration

let _runtimeWorker = null;
let _runtimeRequestId = 0;
let _runtimePending = new Map();
let _runtimeGeneration = 0;
let _runFn = null;
let _resetFn = null;
let _ready = false;
let _currentSample = "demo";
let _cellEditors = [];
let _executionCounter = 0;
let _activeCellIndex = 0;
let _notebookMode = false;
let _bootStart = performance.now();
let _evalBackend = "wasm-js";
const RUNTIME_INIT_TIMEOUT_MS = 5000;
const RUNTIME_RUN_TIMEOUT_MS = 10000;

function byId(id) { return document.getElementById(id); }
function log(msg) { console.log("[web]", msg); byId("loading-msg").textContent = msg; }
function esc(s) { return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }

function setStatus(text, mode) {
  byId("status").textContent = text;
  const pill = byId("status-pill");
  pill.classList.remove("ready","running","error");
  if (mode) pill.classList.add(mode);
}

function lineCount(text) { return text ? text.split(/\r\n|\r|\n/).length : 0; }

function setControlsDisabled(disabled) {
  ["reset-btn","restart-btn","run-all-btn"].forEach(id => byId(id).disabled = disabled || !_ready);
  byId("cancel-btn").disabled = !disabled || !_ready;
  document.querySelectorAll(".nb-cell-run").forEach(btn => { btn.disabled = disabled || !_ready; });
}

function rejectRuntimePending(error) {
  _runtimePending.forEach((pending) => {
    if (pending.timer) clearTimeout(pending.timer);
    pending.reject(error);
  });
  _runtimePending.clear();
}

function callRuntime(type, payload, options) {
  if (!_runtimeWorker) return Promise.reject(new Error("Runtime worker is not available"));
  const id = ++_runtimeRequestId;
  const generation = _runtimeGeneration;
  const timeoutMs = options && options.timeoutMs ? options.timeoutMs : 0;
  return new Promise((resolve, reject) => {
    const timer = timeoutMs > 0
      ? setTimeout(() => {
          cancelRuntime(`Runtime request ${id} timed out after ${timeoutMs} ms`);
        }, timeoutMs)
      : null;
    _runtimePending.set(id, { resolve, reject, timer, generation });
    _runtimeWorker.postMessage({ id, type, ...(payload || {}) });
  });
}

function handleRuntimeMessage(event) {
  const msg = event.data || {};
  if (msg.type === "log") {
    log(msg.message);
    return;
  }

  const pending = _runtimePending.get(msg.id);
  if (!pending) return;
  if (pending.generation !== _runtimeGeneration) {
    _runtimePending.delete(msg.id);
    if (pending.timer) clearTimeout(pending.timer);
    pending.reject(new Error(`Stale runtime reply for request ${msg.id}`));
    return;
  }
  _runtimePending.delete(msg.id);
  if (pending.timer) clearTimeout(pending.timer);

  if (msg.type === "error") {
    pending.reject(new Error(msg.error || "Runtime worker error"));
    return;
  }

  pending.resolve(msg.result || msg);
}

async function startRuntimeWorker(options) {
  if (_runtimeWorker) _runtimeWorker.terminate();
  if (!options || options.rejectPending !== false) {
    rejectRuntimePending(new Error("Runtime worker restarted"));
  }
  _runtimeGeneration++;

  _runtimeWorker = new Worker("../prototype/runtime/js/worker.js?v=4");
  _runtimeWorker.onmessage = handleRuntimeMessage;
  _runtimeWorker.onerror = (event) => {
    const error = new Error(event.message || "Runtime worker failed");
    rejectRuntimePending(error);
    setStatus("error", "error");
    byId("runtime-detail").textContent = error.message;
  };

  await callRuntime("init", {}, { timeoutMs: RUNTIME_INIT_TIMEOUT_MS });
  _runFn = (code) => callRuntime("run", { code, backend: _evalBackend }, { timeoutMs: RUNTIME_RUN_TIMEOUT_MS });
  _resetFn = () => callRuntime("reset", {}, { timeoutMs: RUNTIME_INIT_TIMEOUT_MS });
}

async function cancelRuntime(reason) {
  const error = new Error(reason || "Runtime request cancelled");
  if (_runtimeWorker) {
    _runtimeWorker.terminate();
    _runtimeWorker = null;
  }
  rejectRuntimePending(error);
  _runtimeGeneration++;
  _ready = false;
  try {
    await startRuntimeWorker({ rejectPending: false });
    _ready = true;
    setStatus("ready", "ready");
    byId("runtime-detail").textContent = "Runtime cancelled and restarted";
  } catch (restartError) {
    _ready = false;
    setStatus("error", "error");
    byId("runtime-detail").textContent = String(restartError);
  } finally {
    setControlsDisabled(false);
  }
}

function setupResize(handle, left) {
  let dragging = false;
  handle.addEventListener("mousedown", () => {
    dragging = true; handle.classList.add("dragging");
    document.body.style.cursor = "col-resize"; document.body.style.userSelect = "none";
  });
  addEventListener("mousemove", (e) => {
    if (!dragging) return;
    document.documentElement.style.setProperty("--sidebar-width", `${Math.max(180, Math.min(420, e.clientX - left.getBoundingClientRect().left))}px`);
    layoutAllEditorsSoon();
  });
  addEventListener("mouseup", () => {
    dragging = false; handle.classList.remove("dragging");
    document.body.style.cursor = ""; document.body.style.userSelect = "";
  });
}

async function init() {
  await loadSampleSources();
  buildFileList();

  log("Starting runtime worker...");
  const runtimeReady = startRuntimeWorker();
  log("Loading editor...");
  const editorReady = initMonaco();
  await Promise.all([runtimeReady, editorReady]);

  _ready = true;
  byId("loading").style.display = "none";
  setStatus("ready", "ready");
  byId("runtime-detail").textContent = `WASM + JS Runtime ready · ${Math.round(performance.now() - _bootStart)} ms startup`;
  setControlsDisabled(false);

  // Defer by two frames so the browser lays out editor containers
  // before Monaco measures them — avoids 0-height editors on first load.
  requestAnimationFrame(() => {
    requestAnimationFrame(() => loadFile("demo"));
  });
  console.log("[web] Ready");
}
