// Nomi Web Playground — cell execution, run all, restart

function formatTiming(timing, elapsed) {
  if (!timing) return `last run ${elapsed} ms`;
  const total = Math.max(1, Math.round(timing.total_ms || elapsed));
  if (timing.cache_hit) {
    const cache = Math.max(1, Math.round(timing.cache_ms || 0));
    const evalMs = Math.max(1, Math.round(timing.eval_ms || 0));
    return `last run ${total} ms · cached ${cache} · eval ${evalMs}`;
  }
  const parse = Math.max(1, Math.round(timing.parse_ms || 0));
  const desugar = Math.max(1, Math.round(timing.desugar_ms || 0));
  const evalMs = Math.max(1, Math.round(timing.eval_ms || 0));
  return `last run ${total} ms · parse ${parse} · desugar ${desugar} · eval ${evalMs}`;
}

function runtimeLabel(result) {
  return "WASM + JS Runtime";
}

function formatRuntimeValue(value) {
  if (typeof value === "string") return value;
  if (value === null || value === undefined) return "None";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function outputForResult(result) {
  if (result.error) return result.error;
  if (result.output) return result.output;
  if (result.has_value) return formatRuntimeValue(result.value);
  return "(no output)";
}

async function runCell(idx, advance, options) {
  if (!_ready || !_runFn) return;
  const manageControls = !(options && options.batch);
  const editor = _cellEditors[idx];
  if (!editor) return;
  const code = editor.getValue().trim();
  if (!code) return;

  if (manageControls) {
    setControlsDisabled(true);
    setStatus("running", "running");
  }

  const outer = document.querySelector(`.nb-cell[data-index="${idx}"]`);
  const runBtn = outer.querySelector(".nb-cell-run");
  const timeEl = outer.querySelector(".nb-cell-time");
  const outDiv = outer.querySelector(".nb-cell-output");
  const outNum = outDiv.querySelector(".out-num");
  const outPre = outDiv.querySelector("pre");
  runBtn.classList.add("running");
  runBtn.textContent = "...";

  const start = performance.now();
  try {
    const r = await _runFn(code);
    const elapsed = Math.max(1, Math.round(performance.now() - start));
    const error = r.error || "";
    const output = outputForResult(r);

    _executionCounter++;
    outer.dataset.execCount = _executionCounter;
    outer.querySelector(".nb-cell-index").textContent = `In[${_executionCounter}]:`;
    timeEl.textContent = `${elapsed} ms`;
    outNum.textContent = _executionCounter;
    outPre.textContent = output;
    outDiv.className = error ? "nb-cell-output error show" : "nb-cell-output show";

    if (r.session) {
      byId("runtime-detail").textContent = `${runtimeLabel(r)} · session ${r.session} · ${formatTiming(r.timing, elapsed)}`;
    }
  } catch (e) {
    const elapsed = Math.max(1, Math.round(performance.now() - start));
    _executionCounter++;
    outer.dataset.execCount = _executionCounter;
    outer.querySelector(".nb-cell-index").textContent = `In[${_executionCounter}]:`;
    timeEl.textContent = `${elapsed} ms`;
    outNum.textContent = _executionCounter;
    outPre.textContent = String(e);
    outDiv.className = "nb-cell-output error show";
  }

  runBtn.classList.remove("running");
  runBtn.innerHTML = "&#9654; Run";
  if (manageControls) {
    setControlsDisabled(false);
    setStatus("ready", "ready");
  }

  if (advance) {
    const nextIdx = idx + 1;
    if (nextIdx < _cellEditors.length) {
      setActiveCell(nextIdx);
      document.querySelector(`.nb-cell[data-index="${nextIdx}"]`).scrollIntoView({ behavior: "smooth", block: "center" });
    } else {
      addCell("");
      setActiveCell(_cellEditors.length - 1);
      scrollToBottom();
    }
  }
}

async function runAllCells() {
  if (!_ready || !_runFn || !_resetFn) return;
  setControlsDisabled(true);
  setStatus("running", "running");
  _executionCounter = 0;
  document.querySelectorAll(".nb-cell").forEach(el => {
    el.dataset.execCount = "";
    el.querySelector(".nb-cell-index").textContent = "In[ ]:";
  });
  await _resetFn();

  for (let i = 0; i < _cellEditors.length; i++) {
    await runCell(i, false, { batch: true });
    const outDiv = document.querySelector(`.nb-cell-output[data-idx="${i}"]`);
    if (outDiv && outDiv.classList.contains("error")) {
      setStatus("error", "error");
      setControlsDisabled(false);
      gotoCell(i);
      return;
    }
  }
  setStatus("ready", "ready");
  setControlsDisabled(false);
}

async function runPlainCode() {
  if (!_ready || !_runFn) return;
  const editor = _cellEditors[0];
  if (!editor) return;
  const code = editor.getValue().trim();
  if (!code) return;

  setControlsDisabled(true);
  setStatus("running", "running");

  const outDiv = document.querySelector(".nb-cell-output[data-idx='0']");
  const outPre = outDiv.querySelector("pre");

  const start = performance.now();
  try {
    const r = await _runFn(code);
    const elapsed = Math.max(1, Math.round(performance.now() - start));
    const error = r.error || "";
    const output = outputForResult(r);

    outPre.textContent = output;
    outDiv.className = error ? "nb-cell-output error show" : "nb-cell-output show";

    if (r.session) {
      byId("runtime-detail").textContent = `${runtimeLabel(r)} · session ${r.session} · ${formatTiming(r.timing, elapsed)}`;
    }
  } catch (e) {
    outPre.textContent = String(e);
    outDiv.className = "nb-cell-output error show";
  }

  setControlsDisabled(false);
  setStatus("ready", "ready");
}

function gotoCell(idx) {
  const el = document.querySelector(`.nb-cell[data-index="${idx}"]`);
  if (el) el.scrollIntoView({ behavior: "smooth", block: "center" });
}

function clearNotebookOutputs() {
  _executionCounter = 0;
  document.querySelectorAll(".nb-cell").forEach(el => {
    el.dataset.execCount = "";
    el.querySelector(".nb-cell-index").textContent = "In[ ]:";
  });
  document.querySelectorAll(".nb-cell-output").forEach(d => d.className = "nb-cell-output");
  document.querySelectorAll(".nb-cell-time").forEach(d => d.textContent = "");
}

window.resetRuntime = async function() {
  if (!_ready || !_resetFn) return;
  setControlsDisabled(true);
  setStatus("running", "running");
  try {
    const result = await _resetFn();
    clearNotebookOutputs();
    byId("runtime-detail").textContent = "Runtime reset";
    setStatus("ready", "ready");
  } catch (error) {
    byId("runtime-detail").textContent = String(error);
    setStatus("error", "error");
  } finally {
    setControlsDisabled(false);
  }
};

window.restartWorker = async function() {
  if (!_ready) return;
  setControlsDisabled(true);
  setStatus("running", "running");
  byId("runtime-detail").textContent = "Restarting runtime...";
  try {
    _ready = false;
    await startRuntimeWorker();
    _ready = true;
    clearNotebookOutputs();
    byId("runtime-detail").textContent = "Runtime restarted";
    setStatus("ready", "ready");
  } catch (error) {
    _ready = false;
    byId("runtime-detail").textContent = String(error);
    setStatus("error", "error");
  } finally {
    setControlsDisabled(false);
  }
};
