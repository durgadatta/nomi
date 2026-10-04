// Nomi Web Playground - execution and structured result rendering

function formatTiming(timing, elapsed) {
  if (!timing || timingEntries({ timing }).some(([, value]) => value === null)) return `${elapsed} ms elapsed`;
  const total = observedDuration(timing.total_ms);
  if (total === null) return `${elapsed} ms elapsed`;
  if (timing.cache_hit) {
    const cache = observedDuration(timing.cache_ms);
    const evalMs = observedDuration(timing.eval_ms);
    if (cache !== null) return `${total} ms total, ${cache} ms cached, ${evalMs} ms eval`;
  }
  const [[, parse], [, lower], [, evalMs]] = timingEntries({ timing });
  return `${total} ms total, ${parse} ms parse, ${lower} ms lower, ${evalMs} ms eval`;
}

function runtimeLabel(result) {
  const backend = (result.pipeline && result.pipeline.eval_backend) || result.backend;
  if (backend === "python-ast") return "Pyodide";
  if (["wasm-js", "js-core-runtime"].includes(backend)) return "WASM + JS";
  return backend || "Unavailable";
}

function formatRuntimeValue(value) {
  if (typeof value === "string") return value;
  if (value === null || value === undefined) return "None";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function formatInspectableValue(value) {
  if (typeof value === "string") return JSON.stringify(value);
  if (value === null || value === undefined) return "None";
  if (typeof value === "object") return JSON.stringify(value, null, 2);
  return String(value);
}

function outputForResult(result) {
  if (result.error) return result.error;
  if (result.output) return result.output;
  if (result.has_value) return formatRuntimeValue(result.value);
  return "(no output)";
}

function bindingEntries(result) {
  return Object.entries(bindingsAvailable(result) ? result.bindings : {})
    .sort(([left], [right]) => left.localeCompare(right));
}

function bindingsAvailable(result) {
  return Boolean(result && result.bindings && typeof result.bindings === "object" && !Array.isArray(result.bindings));
}

function diagnosticsForResult(result) {
  const diagnostics = Array.isArray(result && result.diagnostics) ? result.diagnostics : [];
  if (diagnostics.length) return diagnostics;
  if (result && result.error) {
    return [{ phase: "runtime", severity: "error", message: result.error }];
  }
  return [];
}

function observedDuration(value) {
  return typeof value === "number" && Number.isFinite(value) && value >= 0 ? Math.round(value) : null;
}

function timingEntries(result) {
  const timing = (result && (result.timings || result.timing)) || {};
  return [
    ["Parse", timing.parse_ms],
    ["Lower", timing.lower_ms ?? timing.desugar_ms],
    ["Evaluate", timing.eval_ms],
  ].map(([label, value]) => [label, observedDuration(value)]);
}

function pipelineEntries(result) {
  const pipeline = (result && result.pipeline) || {};
  return [
    ["Frontend", pipeline.parser_frontend],
    ["Lowerer", pipeline.lowerer],
    ["Backend", pipeline.eval_backend],
    ["Host", pipeline.host],
  ].map(([label, value]) => [label, typeof value === "string" && value.trim() ? value : "Unavailable"]);
}

function emptyResultMarkup(icon, label) {
  return `<div class="empty-result"><div class="empty-result-inner"><i data-lucide="${icon}"></i><span>${esc(label)}</span></div></div>`;
}

function renderBindings(view, entries, available) {
  view.innerHTML = "";
  if (!entries.length) {
    view.innerHTML = emptyResultMarkup("braces", available ? "No public bindings" : "Bindings unavailable");
    return;
  }
  const table = document.createElement("div");
  table.className = "binding-table";
  entries.forEach(([name, value]) => {
    const key = document.createElement("div");
    key.className = "binding-name";
    key.textContent = name;
    const rendered = document.createElement("div");
    rendered.className = "binding-value";
    rendered.textContent = formatInspectableValue(value);
    table.append(key, rendered);
  });
  view.appendChild(table);
}

function diagnosticMeta(diagnostic) {
  const parts = [];
  if (diagnostic.phase) parts.push(diagnostic.phase);
  if (diagnostic.span && typeof diagnostic.span === "object") {
    const line = diagnostic.span.line || diagnostic.span.start_line;
    const column = diagnostic.span.column || diagnostic.span.start_column;
    if (line) parts.push(`line ${line}${column ? `:${column}` : ""}`);
  }
  if (diagnostic.capability) parts.push(diagnostic.capability);
  return parts.join(" · ");
}

function renderDiagnostics(view, diagnostics, idx) {
  view.innerHTML = "";
  if (!diagnostics.length) {
    view.innerHTML = emptyResultMarkup("circle-check", "No diagnostics");
    return;
  }
  const list = document.createElement("div");
  list.className = "diagnostic-list";
  diagnostics.forEach((diagnostic) => {
    const severity = diagnostic.severity === "warning" ? "warning" : "error";
    const item = document.createElement("article");
    item.className = `diagnostic ${severity}`;
    const icon = document.createElement("span");
    icon.className = "diagnostic-icon";
    icon.innerHTML = `<i data-lucide="${severity === "warning" ? "triangle-alert" : "circle-x"}"></i>`;
    const content = document.createElement("div");
    const message = document.createElement("div");
    message.className = "diagnostic-message";
    message.textContent = diagnostic.message || "Unknown diagnostic";
    content.appendChild(message);
    const metaText = diagnosticMeta(diagnostic);
    if (metaText) {
      const meta = document.createElement("div");
      meta.className = "diagnostic-meta";
      meta.textContent = metaText;
      content.appendChild(meta);
    }
    const editor = _cellEditors[idx];
    const position = editor && diagnosticPosition(diagnostic, editor.getValue());
    if (position) {
      const link = document.createElement("button");
      link.type = "button";
      link.className = "diagnostic-location";
      link.textContent = `Line ${position.lineNumber}:${position.column}`;
      link.title = "Go to source";
      link.addEventListener("click", () => {
        if (view.closest(".nb-cell-output").classList.contains("stale")) return;
        editor.revealPositionInCenter(position);
        editor.setPosition(position);
        editor.focus();
      });
      content.appendChild(link);
    }
    if (diagnostic.source_excerpt) {
      const excerpt = document.createElement("div");
      excerpt.className = "diagnostic-meta";
      excerpt.textContent = diagnostic.source_excerpt;
      content.appendChild(excerpt);
    }
    item.append(icon, content);
    list.appendChild(item);
  });
  view.appendChild(list);
}

function renderPipeline(view, result, elapsed) {
  view.innerHTML = "";
  const fields = pipelineEntries(result);
  const grid = document.createElement("div");
  grid.className = "pipeline-grid";
  fields.forEach(([name, value]) => {
    const key = document.createElement("div");
    key.className = "pipeline-key";
    key.textContent = name;
    const rendered = document.createElement("div");
    rendered.className = "pipeline-value";
    rendered.textContent = value;
    grid.append(key, rendered);
  });
  view.appendChild(grid);

  const timings = document.createElement("div");
  timings.className = "timing-strip";
  timingEntries(result, elapsed).forEach(([label, value]) => {
    const segment = document.createElement("div");
    segment.className = "timing-segment";
    const name = document.createElement("span");
    name.textContent = label;
    const duration = document.createElement("strong");
    duration.textContent = value === null ? "Unavailable" : `${value} ms`;
    segment.append(name, duration);
    timings.appendChild(segment);
  });
  view.appendChild(timings);
}

function renderResult(idx, result, elapsed, context) {
  const outer = document.querySelector(`.nb-cell[data-index="${idx}"]`);
  if (!outer) return;
  const pane = outer.querySelector(".nb-cell-output");
  const outputView = pane.querySelector('[data-result-view="output"]');
  const outputPre = outputView.querySelector("pre");
  const empty = outputView.querySelector(".empty-result");
  const bindings = bindingEntries(result);
  const diagnostics = diagnosticsForResult(result);

  _cellResults[idx] = result;
  const stale = Boolean(context && context.revision !== _documentRevision);
  pane.classList.toggle("stale", stale);
  pane.querySelector(".result-stale").hidden = !stale;
  outputPre.hidden = false;
  outputPre.textContent = result.error && result.stdout ? result.stdout : outputForResult(result);
  if (empty) empty.hidden = true;
  pane.classList.add("show");
  pane.classList.toggle("error", Boolean(result.error));
  pane.querySelector('[data-result-count="bindings"]').textContent = bindingsAvailable(result) ? String(bindings.length) : "-";
  pane.querySelector('[data-result-count="diagnostics"]').textContent = String(diagnostics.length);
  renderBindings(pane.querySelector('[data-result-view="bindings"]'), bindings, bindingsAvailable(result));
  renderDiagnostics(pane.querySelector('[data-result-view="diagnostics"]'), diagnostics, idx);
  const model = _cellEditors[idx].getModel();
  const markers = stale ? [] : diagnostics.flatMap((diagnostic) => {
    const position = diagnosticPosition(diagnostic, model.getValue());
    if (!position) return [];
    return [{
      startLineNumber: position.lineNumber, endLineNumber: position.lineNumber,
      startColumn: position.column, endColumn: Math.min(model.getLineMaxColumn(position.lineNumber), position.column + 1),
      severity: diagnostic.severity === "warning" ? monaco.MarkerSeverity.Warning : monaco.MarkerSeverity.Error,
      message: diagnostic.message || "Unknown diagnostic", code: diagnostic.code || undefined,
    }];
  });
  monaco.editor.setModelMarkers(model, "nomi", markers);
  renderPipeline(pane.querySelector('[data-result-view="pipeline"]'), result, elapsed);
  activateResultTab(idx, result.error ? "diagnostics" : "output");
  refreshIcons(pane);
  layoutAllEditorsSoon();

  const timing = result.timings || result.timing;
  byId("runtime-detail").textContent = `${runtimeLabel(result)} · ${formatTiming(timing, elapsed)}`;
}

function markResultsStale() {
  _cellEditors.forEach((editor, idx) => {
    if (editor) monaco.editor.setModelMarkers(editor.getModel(), "nomi", []);
    if (!_cellResults[idx]) return;
    const pane = document.querySelector(`.nb-cell[data-index="${idx}"] .nb-cell-output`);
    if (!pane) return;
    pane.classList.add("stale");
    pane.querySelector(".result-stale").hidden = false;
  });
}

function resetResultPanel(idx) {
  const outer = document.querySelector(`.nb-cell[data-index="${idx}"]`);
  if (!outer) return;
  const pane = outer.querySelector(".nb-cell-output");
  pane.classList.remove("show", "error", "stale");
  pane.querySelector(".result-stale").hidden = true;
  const editor = _cellEditors[idx];
  if (editor) monaco.editor.setModelMarkers(editor.getModel(), "nomi", []);
  const output = pane.querySelector('[data-result-view="output"]');
  const pre = output.querySelector("pre");
  const empty = output.querySelector(".empty-result");
  pre.hidden = true;
  pre.textContent = "";
  if (empty) empty.hidden = false;
  pane.querySelector('[data-result-view="bindings"]').innerHTML = emptyResultMarkup("braces", "No binding result");
  pane.querySelector('[data-result-view="diagnostics"]').innerHTML = emptyResultMarkup("circle-check", "No diagnostic result");
  pane.querySelector('[data-result-view="pipeline"]').innerHTML = emptyResultMarkup("waypoints", "No pipeline result");
  pane.querySelector('[data-result-count="bindings"]').textContent = "0";
  pane.querySelector('[data-result-count="diagnostics"]').textContent = "0";
  activateResultTab(idx, "output");
  refreshIcons(pane);
  _cellResults[idx] = null;
}

function setCellRunning(outer, running) {
  const button = outer && outer.querySelector(".nb-cell-run");
  if (!button) return;
  button.classList.toggle("running", running);
  const label = button.querySelector("span");
  if (label) label.textContent = running ? "Running" : "Run";
}

async function runCell(idx, advance, options) {
  if (!_ready || !_runFn) return { ok: false };
  const manageControls = !(options && options.batch);
  const editor = _cellEditors[idx];
  if (!editor) return { ok: false };
  const code = options && options.code !== undefined ? options.code : editor.getValue();
  if (!code.trim()) return { ok: true };

  const epoch = manageControls ? beginExecution() : options.epoch;
  if (epoch === null) return { ok: false };
  const context = { epoch, index: idx, editor, document: _documentGeneration, revision: options && options.revision !== undefined ? options.revision : _documentRevision };

  const outer = document.querySelector(`.nb-cell[data-index="${idx}"]`);
  const time = outer.querySelector(".nb-cell-time");
  setCellRunning(outer, true);
  const start = performance.now();
  let ok = false;

  try {
    if (_runtimeDocument !== _currentSample) {
      await _resetFn();
      if (!currentExecution(context)) return { ok: false };
      _runtimeDocument = _currentSample;
    }
    const result = await _runFn(code);
    if (!currentExecution(context)) return { ok: false };
    const elapsed = Math.max(1, Math.round(performance.now() - start));
    _executionCounter++;
    outer.dataset.execCount = _executionCounter;
    outer.querySelector(".nb-cell-index").textContent = `In[${_executionCounter}]:`;
    time.textContent = `${elapsed} ms`;
    renderResult(idx, result, elapsed, context);
    ok = !result.error;
  } catch (error) {
    if (!currentExecution(context)) return { ok: false };
    const elapsed = Math.max(1, Math.round(performance.now() - start));
    _executionCounter++;
    outer.dataset.execCount = _executionCounter;
    outer.querySelector(".nb-cell-index").textContent = `In[${_executionCounter}]:`;
    time.textContent = `${elapsed} ms`;
    renderResult(idx, { error: String(error), diagnostics: [], backend: _evalBackend }, elapsed, context);
  } finally {
    setCellRunning(outer, false);
    if (manageControls) finishExecution(epoch, ok);
  }

  if (advance && ok && currentExecution(context)) {
    const nextIdx = idx + 1;
    if (nextIdx < _cellEditors.length) {
      setActiveCell(nextIdx);
      _cellEditors[nextIdx].focus();
      document.querySelector(`.nb-cell[data-index="${nextIdx}"]`).scrollIntoView({ behavior: "smooth", block: "center" });
    } else {
      addCell("");
      setActiveCell(_cellEditors.length - 1);
      scrollToBottom();
    }
  }
  return { ok };
}

async function runAllCells() {
  if (!_ready || !_runFn || !_resetFn) return;
  const epoch = beginExecution();
  if (epoch === null) return;
  const revision = _documentRevision;
  const codes = _cellEditors.map((editor) => editor.getValue());
  _executionCounter = 0;
  clearNotebookOutputs();

  try {
    await _resetFn();
    if (epoch !== _runEpoch) return;
    _runtimeDocument = _currentSample;
    for (let idx = 0; idx < codes.length; idx++) {
      const result = await runCell(idx, false, { batch: true, epoch, code: codes[idx], revision });
      if (epoch !== _runEpoch) return;
      if (!result.ok) {
        setStatus("error", "error");
        gotoCell(idx);
        return;
      }
    }
    setStatus("ready", "ready");
  } catch (error) {
    if (epoch !== _runEpoch) return;
    byId("runtime-detail").textContent = String(error);
    setStatus("error", "error");
  } finally {
    if (epoch === _runEpoch) setControlsDisabled(false);
  }
}

async function runPlainCode() {
  if (!_ready || !_runFn || !_resetFn) return;
  const editor = _cellEditors[0];
  if (!editor || !editor.getValue().trim()) return;
  const epoch = beginExecution();
  if (epoch === null) return;
  const code = editor.getValue();
  const context = { epoch, editor, index: 0, document: _documentGeneration, revision: _documentRevision };

  const start = performance.now();
  let ok = false;
  try {
    await _resetFn();
    if (!currentExecution(context)) return;
    _runtimeDocument = _currentSample;
    const result = await _runFn(code);
    if (!currentExecution(context)) return;
    const elapsed = Math.max(1, Math.round(performance.now() - start));
    renderResult(0, result, elapsed, context);
    ok = !result.error;
  } catch (error) {
    if (!currentExecution(context)) return;
    const elapsed = Math.max(1, Math.round(performance.now() - start));
    renderResult(0, { error: String(error), diagnostics: [], backend: _evalBackend }, elapsed, context);
  } finally {
    finishExecution(epoch, ok);
  }
}

function gotoCell(idx) {
  const cell = document.querySelector(`.nb-cell[data-index="${idx}"]`);
  if (cell) cell.scrollIntoView({ behavior: "smooth", block: "center" });
}

function clearNotebookOutputs() {
  _executionCounter = 0;
  document.querySelectorAll(".nb-cell").forEach((cell, idx) => {
    cell.dataset.execCount = "";
    const index = cell.querySelector(".nb-cell-index");
    if (index) index.textContent = "In[ ]:";
    const time = cell.querySelector(".nb-cell-time");
    if (time) time.textContent = "";
    resetResultPanel(idx);
  });
}

window.resetRuntime = async function() {
  if (!_ready || !_resetFn) return;
  const epoch = beginExecution();
  if (epoch === null) return;
  try {
    await _resetFn();
    if (epoch !== _runEpoch) return;
    _runtimeDocument = _currentSample;
    clearNotebookOutputs();
    byId("runtime-detail").textContent = "Runtime state reset";
    setStatus("ready", "ready");
  } catch (error) {
    if (epoch !== _runEpoch) return;
    byId("runtime-detail").textContent = String(error);
    setStatus("error", "error");
  } finally {
    if (epoch === _runEpoch) setControlsDisabled(false);
  }
};

window.cancelRun = async function() {
  if (!_ready) return;
  setStatus("running", "running");
  byId("runtime-detail").textContent = "Cancelling runtime request";
  await cancelRuntime("Runtime request cancelled by user");
};

window.restartWorker = async function() {
  if (_executionBusy) return;
  const epoch = ++_runEpoch;
  setControlsDisabled(true);
  setStatus("running", "running");
  byId("runtime-detail").textContent = "Restarting runtime";
  try {
    _ready = false;
    await startRuntimeWorker();
    if (epoch !== _runEpoch) return;
    _ready = true;
    clearNotebookOutputs();
    byId("runtime-detail").textContent = "Runtime worker restarted";
    setStatus("ready", "ready");
  } catch (error) {
    _ready = false;
    byId("runtime-detail").textContent = String(error);
    setStatus("error", "error");
  } finally {
    if (epoch === _runEpoch) setControlsDisabled(false);
  }
};

if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    bindingEntries,
    bindingsAvailable,
    diagnosticsForResult,
    formatTiming,
    formatRuntimeValue,
    outputForResult,
    pipelineEntries,
    runtimeLabel,
    timingEntries,
  };
}
