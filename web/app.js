// Nomi Web Playground — global state, utilities, init orchestration

let _runtimeWorker = null;
let _runtimeRequestId = 0;
let _runtimePending = new Map();
let _runFn = null;
let _resetFn = null;
let _ready = false;
let _currentSample = "demo";
let _cellEditors = [];
let _executionCounter = 0;
let _activeCellIndex = 0;
let _notebookMode = false;
let _bootStart = performance.now();

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
  ["restart-btn","run-all-btn"].forEach(id => byId(id).disabled = disabled || !_ready);
  document.querySelectorAll(".nb-cell-run").forEach(btn => { btn.disabled = disabled || !_ready; });
}

function callRuntime(type, payload) {
  if (!_runtimeWorker) return Promise.reject(new Error("Runtime worker is not available"));
  const id = ++_runtimeRequestId;
  return new Promise((resolve, reject) => {
    _runtimePending.set(id, { resolve, reject });
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
  _runtimePending.delete(msg.id);

  if (msg.type === "error") {
    pending.reject(new Error(msg.error || "Runtime worker error"));
    return;
  }

  pending.resolve(msg.result || msg);
}

async function startRuntimeWorker() {
  if (_runtimeWorker) _runtimeWorker.terminate();
  _runtimePending.forEach(({ reject }) => reject(new Error("Runtime worker restarted")));
  _runtimePending.clear();

  _runtimeWorker = new Worker("./worker.js");
  _runtimeWorker.onmessage = handleRuntimeMessage;
  _runtimeWorker.onerror = (event) => {
    const error = new Error(event.message || "Runtime worker failed");
    _runtimePending.forEach(({ reject }) => reject(error));
    _runtimePending.clear();
    setStatus("error", "error");
    byId("runtime-detail").textContent = error.message;
  };

  await callRuntime("init");
  _runFn = (code) => callRuntime("run", { code });
  _resetFn = () => callRuntime("reset");
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
    _cellEditors.forEach(ed => ed && ed.layout());
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
  byId("runtime-detail").textContent = `Pyodide ready · ${Math.round(performance.now() - _bootStart)} ms startup`;
  setControlsDisabled(false);

  // Defer by two frames so the browser lays out editor containers
  // before Monaco measures them — avoids 0-height editors on first load.
  requestAnimationFrame(() => {
    requestAnimationFrame(() => loadFile("demo"));
  });
  console.log("[web] Ready");
}
