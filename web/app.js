// Nomi Web Playground — global state, utilities, init orchestration

let _pyodide = null;
let _runFn = null;
let _resetFn = null;
let _ready = false;
let _currentSample = "demo";
let _cellEditors = [];
let _executionCounter = 0;
let _activeCellIndex = 0;
let _notebookMode = false;

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

  log("Loading Pyodide...");
  _pyodide = await loadPyodide();
  log("Installing lark...");
  await _pyodide.loadPackage("micropip");
  const mp = _pyodide.pyimport("micropip");
  await mp.install("lark");

  log("Initializing Nomi...");
  const nomiPy = await fetch("./nomi_web.py").then(r => r.text());
  await _pyodide.runPythonAsync(nomiPy);
  await _pyodide.globals.get("init_nomi")();
  _runFn = _pyodide.globals.get("run_nomi");
  _resetFn = _pyodide.globals.get("reset_session");

  log("Loading editor...");
  await initMonaco();

  _ready = true;
  byId("loading").style.display = "none";
  setStatus("ready", "ready");
  byId("runtime-detail").textContent = "Pyodide runtime ready";
  setControlsDisabled(false);

  // Defer by two frames so the browser lays out editor containers
  // before Monaco measures them — avoids 0-height editors on first load.
  requestAnimationFrame(() => {
    requestAnimationFrame(() => loadFile("demo"));
  });
  console.log("[web] Ready");
}
