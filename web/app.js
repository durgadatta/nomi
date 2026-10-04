// Nomi Web Playground - shared state, worker lifecycle, and workbench controls

let _runtimeWorker = null;
let _runtimeRequestId = 0;
let _runtimePending = new Map();
let _runtimeGeneration = 0;
let _runFn = null;
let _resetFn = null;
let _ready = false;
let _currentSample = "terse";
let _cellEditors = [];
let _cellResults = [];
let _executionCounter = 0;
let _activeCellIndex = 0;
let _notebookMode = false;
let _documentLoading = false;
let _documentGeneration = 0;
let _documentRevision = 0;
let _runEpoch = 0;
let _executionBusy = false;
let _runtimeDocument = null;
let _notebookPreamble = "";
let _cellPrefixes = [];
let _storageFailed = false;
let _bootStart = performance.now();
let _toastTimer = null;
let _workbenchState = { active: "terse", drafts: {}, sidebarWidth: 272, resultPane: 43 };
let _evalBackend = new URLSearchParams(location.search).get("backend") || "wasm-js";

const WORKBENCH_STORAGE_KEY = "nomi.playground.workbench.v2";
const RUNTIME_INIT_TIMEOUT_MS = _evalBackend === "pyodide" ? 60000 : 5000;
const RUNTIME_RUN_TIMEOUT_MS = 10000;

function byId(id) { return document.getElementById(id); }
function log(msg) { console.log("[web]", msg); byId("loading-msg").textContent = msg; }
function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
function lineCount(text) { return text ? text.split(/\r\n|\r|\n/).length : 0; }

function refreshIcons(root) {
  if (typeof lucide === "undefined") return;
  lucide.createIcons({
    attrs: { "aria-hidden": "true" },
    nameAttr: "data-lucide",
    root: root || document,
  });
}

function readWorkbenchState() {
  try {
    const stored = JSON.parse(localStorage.getItem(WORKBENCH_STORAGE_KEY) || "null");
    _workbenchState = normalizeWorkbenchState(stored);
  } catch (error) {
    console.warn("[web] Could not restore workbench state", error);
  }

  const sidebarWidth = Math.max(210, Math.min(420, Number(_workbenchState.sidebarWidth) || 272));
  const resultPane = Math.max(28, Math.min(68, Number(_workbenchState.resultPane) || 43));
  document.documentElement.style.setProperty("--sidebar-width", `${sidebarWidth}px`);
  document.documentElement.style.setProperty("--result-pane", `${resultPane}%`);
}

function persistWorkbenchState() {
  _workbenchState.active = _currentSample;
  try {
    localStorage.setItem(WORKBENCH_STORAGE_KEY, JSON.stringify(_workbenchState));
    _storageFailed = false;
    return true;
  } catch (error) {
    console.warn("[web] Could not persist workbench state", error);
    if (!_storageFailed) showToast("Local storage unavailable. Download source to keep it.");
    _storageFailed = true;
    return false;
  }
}

function showToast(message) {
  const toast = byId("toast");
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add("show");
  if (_toastTimer) clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => toast.classList.remove("show"), 1800);
}

async function copyText(text, confirmation) {
  let copied = false;
  try {
    await navigator.clipboard.writeText(text);
    copied = true;
  } catch (error) {
    const previousFocus = document.activeElement;
    const area = document.createElement("textarea");
    area.value = text;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.opacity = "0";
    document.body.appendChild(area);
    area.select();
    try { copied = document.execCommand("copy"); }
    catch (fallbackError) { console.warn("[web] Clipboard unavailable", fallbackError); }
    finally {
      area.remove();
      if (previousFocus && previousFocus.isConnected) previousFocus.focus();
    }
  }
  showToast(copied ? confirmation || "Copied" : "Clipboard unavailable. Download source to keep it.");
  return copied;
}

function setStatus(text, mode) {
  byId("status").textContent = text;
  const pill = byId("status-pill");
  pill.classList.remove("ready", "running", "error");
  if (mode) pill.classList.add(mode);
  document.body.classList.toggle("is-running", mode === "running");
}

function setControlsDisabled(disabled) {
  _executionBusy = disabled;
  ["reset-btn", "restart-btn", "run-all-btn"].forEach((id) => {
    const control = byId(id);
    if (control) control.disabled = disabled || !_ready;
  });
  byId("cancel-btn").disabled = !disabled || !_ready;
  document.querySelectorAll(".nb-cell-run").forEach((button) => {
    button.disabled = disabled || !_ready;
  });
  document.querySelectorAll(".nb-cell-delete, #add-cell-btn").forEach((button) => { button.disabled = disabled; });
}

function beginExecution() {
  if (!_ready || _executionBusy) return null;
  const epoch = ++_runEpoch;
  setControlsDisabled(true);
  setStatus("running", "running");
  return epoch;
}

function finishExecution(epoch, ok) {
  if (epoch !== _runEpoch) return;
  setControlsDisabled(false);
  setStatus(ok ? "ready" : "error", ok ? "ready" : "error");
}

function currentExecution(context) {
  return context.epoch === _runEpoch && context.document === _documentGeneration
    && _cellEditors[context.index] === context.editor;
}

function rejectRuntimePending(error) {
  _runtimePending.forEach((pending) => {
    if (pending.timer) clearTimeout(pending.timer);
    pending.reject(error);
  });
  _runtimePending.clear();
}

function failRuntime(error) {
  _runEpoch++;
  _runtimeGeneration++;
  if (_runtimeWorker) _runtimeWorker.terminate();
  _runtimeWorker = null;
  _ready = false;
  rejectRuntimePending(error);
  setControlsDisabled(false);
  byId("restart-btn").disabled = false;
  setStatus("error", "error");
  byId("runtime-detail").textContent = error.message;
}

function callRuntime(type, payload, options) {
  if (!_runtimeWorker) return Promise.reject(new Error("Runtime worker is not available"));
  const id = ++_runtimeRequestId;
  const generation = _runtimeGeneration;
  const timeoutMs = options && options.timeoutMs ? options.timeoutMs : 0;
  return new Promise((resolve, reject) => {
    const timer = timeoutMs > 0
      ? setTimeout(() => {
        if (!_runtimePending.has(id) || generation !== _runtimeGeneration) return;
        const message = `Runtime request ${id} timed out after ${timeoutMs} ms`;
        if (type === "run") cancelRuntime(message);
        else failRuntime(new Error(message));
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
  _runtimeDocument = null;

  const workerPath = _evalBackend === "pyodide"
    ? "./worker_pyodide.js?v=5"
    : "../prototype/runtime/js/worker.js?v=5";

  _runtimeWorker = new Worker(workerPath);
  const worker = _runtimeWorker;
  _runtimeWorker.onmessage = handleRuntimeMessage;
  _runtimeWorker.onerror = (event) => {
    if (worker !== _runtimeWorker) return;
    const error = new Error(event.message || "Runtime worker failed");
    failRuntime(error);
  };

  await callRuntime("init", {}, { timeoutMs: RUNTIME_INIT_TIMEOUT_MS });
  _runFn = (code) => callRuntime("run", { code, backend: _evalBackend }, { timeoutMs: RUNTIME_RUN_TIMEOUT_MS });
  _resetFn = () => callRuntime("reset", {}, { timeoutMs: RUNTIME_INIT_TIMEOUT_MS });
}

async function cancelRuntime(reason) {
  const epoch = ++_runEpoch;
  setControlsDisabled(true);
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
    if (epoch === _runEpoch) setControlsDisabled(false);
  }
}

function setupResize(handle, sidebar) {
  let dragging = false;
  function setWidth(width) {
    const value = Math.max(210, Math.min(420, width));
    document.documentElement.style.setProperty("--sidebar-width", `${value}px`);
    _workbenchState.sidebarWidth = Math.round(value);
    handle.setAttribute("aria-valuenow", String(Math.round(value)));
    layoutAllEditorsSoon();
  }
  handle.addEventListener("keydown", (event) => {
    const steps = { ArrowLeft: -20, ArrowRight: 20 };
    if (!(event.key in steps) && !["Home", "End"].includes(event.key)) return;
    event.preventDefault();
    setWidth(event.key === "Home" ? 210 : event.key === "End" ? 420 : _workbenchState.sidebarWidth + steps[event.key]);
    persistWorkbenchState();
  });
  handle.setAttribute("aria-valuenow", String(_workbenchState.sidebarWidth));

  handle.addEventListener("pointerdown", (event) => {
    dragging = true;
    handle.setPointerCapture(event.pointerId);
    handle.classList.add("dragging");
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
  });

  handle.addEventListener("pointermove", (event) => {
    if (!dragging) return;
    setWidth(event.clientX - sidebar.getBoundingClientRect().left);
  });

  function stopDragging(event) {
    if (!dragging) return;
    dragging = false;
    if (handle.hasPointerCapture(event.pointerId)) handle.releasePointerCapture(event.pointerId);
    handle.classList.remove("dragging");
    document.body.style.cursor = "";
    document.body.style.userSelect = "";
    persistWorkbenchState();
  }

  handle.addEventListener("pointerup", stopDragging);
  handle.addEventListener("pointercancel", stopDragging);
}

window.toggleSidebar = function(forceOpen) {
  const currentlyHidden = document.body.classList.contains("sidebar-hidden");
  const shouldHide = typeof forceOpen === "boolean" ? !forceOpen : !currentlyHidden;
  document.body.classList.toggle("sidebar-hidden", shouldHide);
  byId("sidebar-toggle").setAttribute("aria-expanded", String(!shouldHide));
  requestAnimationFrame(layoutAllEditorsSoon);
};

function handleViewportChange() {
  layoutAllEditorsSoon();
}

window.copyCurrentCode = function() {
  copyText(currentDocumentCode(), "Source copied");
};

document.addEventListener("keydown", (event) => {
  const command = event.metaKey || event.ctrlKey;
  if (command && event.key.toLowerCase() === "s") {
    event.preventDefault();
    if (saveCurrentDraft(true)) showToast("Draft saved locally");
  }
  if (command && event.key.toLowerCase() === "p") {
    event.preventDefault();
    toggleSidebar(true);
    byId("sample-search").focus();
  }
  if (event.key === "Escape" && matchMedia("(max-width: 980px)").matches) {
    toggleSidebar(false);
  }
});

addEventListener("pagehide", () => saveCurrentDraft(true));

async function init() {
  if (!["wasm-js", "pyodide"].includes(_evalBackend)) throw new Error(`Unsupported playground backend: ${_evalBackend}`);
  readWorkbenchState();
  byId("runtime-profile").innerHTML = `<i data-lucide="cpu" aria-hidden="true"></i>Prototype · ${_evalBackend === "pyodide" ? "Pyodide + Python" : "WASM + JS"}`;
  refreshIcons();
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
  byId("runtime-detail").textContent = `Ready in ${Math.round(performance.now() - _bootStart)} ms`;
  setControlsDisabled(false);

  if (matchMedia("(max-width: 980px)").matches) toggleSidebar(false);
  const initialSample = Object.prototype.hasOwnProperty.call(DEMOS, _workbenchState.active) ? _workbenchState.active : "terse";
  requestAnimationFrame(() => requestAnimationFrame(() => loadFile(initialSample)));
  console.log("[web] Ready");
}
