// Nomi Web Playground - document cells, Monaco instances, and result panes

function markerMatch(line) { return line.match(/^\s*#\s*%%\s*(.*)$/); }

function splitCode(code) {
  const lines = code.split(/\r\n|\r|\n/);
  const markers = [];
  lines.forEach((line, index) => {
    const match = markerMatch(line);
    if (match) markers.push({ line: index + 1, title: match[1].trim() });
  });
  if (markers.length === 0) return [code.trim() || "# empty cell"];
  return markers.map((marker, index) => {
    const start = marker.line + 1;
    const end = markers[index + 1] ? markers[index + 1].line - 1 : lines.length;
    return lines.slice(start - 1, end).join("\n").trim() || "# empty cell";
  });
}

function currentDocumentCode() {
  if (!_cellEditors.length) return "";
  if (!_notebookMode) return _cellEditors[0] ? _cellEditors[0].getValue() : "";
  return _cellEditors
    .filter(Boolean)
    .map((editor, index) => `# %% Cell ${index + 1}\n${editor.getValue()}`)
    .join("\n\n");
}

function setRunButtonLabel(label) {
  const button = byId("run-all-btn");
  const text = button.querySelector("[data-run-label]");
  if (text) text.textContent = label;
  button.setAttribute("aria-label", label === "Run all" ? "Run all cells" : "Run current program");
}

function resultShellMarkup(idx, alwaysShow) {
  return `
    <section class="nb-cell-output${alwaysShow ? " always-show" : ""}" data-idx="${idx}" aria-label="Execution result">
      <div class="result-toolbar">
        <div class="result-tabs" role="tablist" aria-label="Result views">
          <button type="button" class="result-tab active" data-result-tab="output" role="tab" aria-selected="true">Output</button>
          <button type="button" class="result-tab" data-result-tab="bindings" role="tab" aria-selected="false">Bindings <span class="result-count" data-result-count="bindings">0</span></button>
          <button type="button" class="result-tab" data-result-tab="diagnostics" role="tab" aria-selected="false">Diagnostics <span class="result-count" data-result-count="diagnostics">0</span></button>
          <button type="button" class="result-tab" data-result-tab="pipeline" role="tab" aria-selected="false">Pipeline</button>
        </div>
        <div class="result-actions">
          <button type="button" class="icon-button copy-result" title="Copy current result" aria-label="Copy current result">
            <i data-lucide="copy"></i>
          </button>
        </div>
      </div>
      <div class="result-body">
        <div class="result-view active" data-result-view="output" role="tabpanel">
          <div class="empty-result"><div class="empty-result-inner"><i data-lucide="terminal-square"></i><span>No result</span></div></div>
          <pre hidden></pre>
        </div>
        <div class="result-view" data-result-view="bindings" role="tabpanel"></div>
        <div class="result-view" data-result-view="diagnostics" role="tabpanel"></div>
        <div class="result-view" data-result-view="pipeline" role="tabpanel"></div>
      </div>
    </section>`;
}

function wireResultShell(outer) {
  outer.querySelectorAll(".result-tab").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      const idx = Number(outer.dataset.index);
      activateResultTab(idx, button.dataset.resultTab);
    });
  });
  outer.querySelector(".copy-result").addEventListener("click", (event) => {
    event.stopPropagation();
    const view = outer.querySelector(".result-view.active");
    const text = view ? view.innerText.trim() : "";
    copyText(text || "No result", "Result copied");
  });
}

function activateResultTab(idx, tabName) {
  const outer = document.querySelector(`.nb-cell[data-index="${idx}"]`);
  if (!outer) return;
  outer.querySelectorAll(".result-tab").forEach((button) => {
    const active = button.dataset.resultTab === tabName;
    button.classList.toggle("active", active);
    button.setAttribute("aria-selected", String(active));
  });
  outer.querySelectorAll(".result-view").forEach((view) => {
    view.classList.toggle("active", view.dataset.resultView === tabName);
  });
}

function setupPaneResize(outer) {
  const handle = outer.querySelector(".pane-resize-handle");
  if (!handle) return;
  let dragging = false;

  handle.addEventListener("pointerdown", (event) => {
    if (matchMedia("(max-width: 760px)").matches) return;
    dragging = true;
    handle.setPointerCapture(event.pointerId);
    handle.classList.add("dragging");
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
  });

  handle.addEventListener("pointermove", (event) => {
    if (!dragging) return;
    const rect = outer.getBoundingClientRect();
    const fromRight = ((rect.right - event.clientX) / rect.width) * 100;
    const percent = Math.max(28, Math.min(68, fromRight));
    document.documentElement.style.setProperty("--result-pane", `${percent}%`);
    _workbenchState.resultPane = Math.round(percent * 10) / 10;
    layoutAllEditorsSoon();
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

function loadCode(code) {
  disposeAllCells();
  byId("run-all-btn").onclick = runAllCells;
  setRunButtonLabel("Run all");
  byId("add-cell-btn").style.display = "inline-flex";
  byId("nb-scroll").classList.remove("plain-mode");
  byId("nb-cells").classList.remove("plain-mode");

  const chunks = splitCode(code);
  chunks.forEach((chunk) => createCell(chunk));
  _executionCounter = 0;
  const single = chunks.length === 1;
  byId("nb-scroll").classList.toggle("single-cell", single);
  byId("nb-cells").classList.toggle("single-cell", single);
  layoutAllEditorsSoon();
  updateFooter();
}

function loadPlain(code) {
  disposeAllCells();
  byId("run-all-btn").onclick = runPlainCode;
  setRunButtonLabel("Run");
  byId("add-cell-btn").style.display = "none";
  byId("nb-scroll").classList.remove("single-cell");
  byId("nb-scroll").classList.add("plain-mode");
  byId("nb-cells").classList.remove("single-cell");
  byId("nb-cells").classList.add("plain-mode");

  createPlainCell(code);
  _executionCounter = 0;
  layoutAllEditorsSoon();
  updateFooter();
}

window.addCell = function(initialCode) {
  if (!_notebookMode) return;
  createCell(initialCode || "");
  byId("nb-scroll").classList.remove("single-cell");
  byId("nb-cells").classList.remove("single-cell");
  layoutAllEditorsSoon();
  saveCurrentDraft(false);
  scrollToBottom();
};

function createPlainCell(code) {
  const outer = document.createElement("div");
  outer.className = "nb-cell plain";
  outer.dataset.index = "0";
  outer.innerHTML = `
    <div class="nb-cell-editor" data-idx="0"></div>
    <div class="pane-resize-handle" role="separator" aria-orientation="vertical" aria-label="Resize result pane"></div>
    ${resultShellMarkup(0, true)}`;
  byId("nb-cells").appendChild(outer);
  wireResultShell(outer);
  setupPaneResize(outer);
  createEditor(0, code, true);
  refreshIcons(outer);
  updateFooter();
  setActiveCell(0);
  layoutAllEditorsSoon();
}

function createCell(code) {
  const idx = _cellEditors.length;
  const outer = document.createElement("div");
  outer.className = "nb-cell";
  outer.dataset.index = idx;
  outer.dataset.execCount = "";
  outer.innerHTML = `
    <div class="nb-cell-header">
      <span class="nb-cell-index">In[ ]:</span>
      <button type="button" class="nb-cell-run" title="Run cell" aria-label="Run cell">
        <i data-lucide="play"></i><span>Run</span>
      </button>
      <span class="nb-cell-spacer"></span>
      <span class="nb-cell-time"></span>
      <button type="button" class="nb-cell-delete" title="Delete cell" aria-label="Delete cell">
        <i data-lucide="trash-2"></i>
      </button>
    </div>
    <div class="nb-cell-editor" data-idx="${idx}"></div>
    <div class="pane-resize-handle" role="separator" aria-orientation="vertical" aria-label="Resize result pane"></div>
    ${resultShellMarkup(idx, false)}`;
  byId("nb-cells").appendChild(outer);

  outer.querySelector(".nb-cell-run").addEventListener("click", (event) => {
    event.stopPropagation();
    runCell(Number(outer.dataset.index), false);
  });
  outer.querySelector(".nb-cell-delete").addEventListener("click", (event) => {
    event.stopPropagation();
    deleteCell(Number(outer.dataset.index));
  });

  wireResultShell(outer);
  setupPaneResize(outer);
  createEditor(idx, code, false);
  refreshIcons(outer);
  updateFooter();
  if (_cellEditors.length === 1) setActiveCell(0);
  layoutAllEditorsSoon();
  return idx;
}

function createEditor(idx, code, plain) {
  const el = document.querySelector(`.nb-cell-editor[data-idx="${idx}"]`);
  if (!el || typeof monaco === "undefined") return;

  const editor = monaco.editor.create(el, {
    value: code,
    language: "nomi",
    theme: "nomi-dark",
    fontSize: 14,
    fontFamily: "'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace",
    lineHeight: 22,
    lineNumbers: "on",
    glyphMargin: false,
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    folding: true,
    automaticLayout: true,
    overviewRulerBorder: false,
    renderLineHighlight: "line",
    renderWhitespace: "selection",
    smoothScrolling: true,
    cursorBlinking: "smooth",
    wordWrap: "on",
    scrollbar: { vertical: "auto", horizontal: "auto", useShadows: false },
    padding: { top: 10, bottom: 10 },
  });

  editor.layout();
  const notebookList = byId("nb-cells").classList;
  if (!notebookList.contains("single-cell") && !notebookList.contains("plain-mode")) {
    const lines = (code.match(/\n/g) || []).length + 1;
    const scrollHeight = byId("nb-scroll").clientHeight || window.innerHeight;
    const maxHeight = Math.max(200, scrollHeight * 0.5);
    el.style.height = `${Math.min(maxHeight, Math.max(72, lines * 22 + 20))}px`;
    editor.layout();
  }

  editor.onDidContentSizeChange((event) => {
    if (!isFixedPaneLayout()) {
      const scrollHeight = byId("nb-scroll").clientHeight || window.innerHeight;
      const maxHeight = Math.max(200, scrollHeight * 0.5);
      el.style.height = `${Math.min(maxHeight, Math.max(72, event.contentHeight))}px`;
    }
    layoutEditor(idx);
  });

  editor.onDidChangeModelContent(() => {
    saveCurrentDraft(false);
    updateFooter();
  });
  editor.onDidFocusEditorText(() => {
    const currentIndex = _cellEditors.indexOf(editor);
    if (currentIndex >= 0) setActiveCell(currentIndex);
  });
  editor.onDidChangeCursorPosition((event) => {
    const currentIndex = _cellEditors.indexOf(editor);
    if (_activeCellIndex === currentIndex) {
      byId("cursor-detail").textContent = `Ln ${event.position.lineNumber}, Col ${event.position.column}`;
    }
  });

  if (plain) {
    editor.addAction({
      id: "run-plain",
      label: "Run",
      keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter],
      run: () => runPlainCode(),
    });
  } else {
    editor.addAction({
      id: `run-cell-${idx}`,
      label: "Run Cell",
      keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter],
      run: () => runCell(_cellEditors.indexOf(editor), false),
    });
    editor.addAction({
      id: `run-cell-advance-${idx}`,
      label: "Run Cell and Advance",
      keybindings: [monaco.KeyMod.Shift | monaco.KeyCode.Enter],
      run: () => runCell(_cellEditors.indexOf(editor), true),
    });
  }

  _cellEditors[idx] = editor;
  _cellResults[idx] = null;
  editor.focus();
  layoutEditorSoon(idx);
}

function disposeAllCells() {
  _cellEditors.forEach((editor) => editor && editor.dispose());
  _cellEditors = [];
  _cellResults = [];
  byId("nb-cells").innerHTML = "";
}

function deleteCell(idx) {
  if (_cellEditors.length <= 1) return;
  if (_cellEditors[idx]) _cellEditors[idx].dispose();
  _cellEditors.splice(idx, 1);
  _cellResults.splice(idx, 1);
  const cell = document.querySelector(`.nb-cell[data-index="${idx}"]`);
  if (cell) cell.remove();
  reindexCells();
  const single = _cellEditors.length === 1;
  byId("nb-scroll").classList.toggle("single-cell", single);
  byId("nb-cells").classList.toggle("single-cell", single);
  _activeCellIndex = Math.max(0, Math.min(idx, _cellEditors.length - 1));
  layoutAllEditorsSoon();
  saveCurrentDraft(false);
  updateFooter();
}

function reindexCells() {
  document.querySelectorAll(".nb-cell").forEach((cell, index) => {
    cell.dataset.index = index;
    const count = cell.dataset.execCount || "";
    const indexLabel = cell.querySelector(".nb-cell-index");
    if (indexLabel) indexLabel.textContent = count ? `In[${count}]:` : "In[ ]:";
    cell.querySelector(".nb-cell-editor").dataset.idx = index;
    cell.querySelector(".nb-cell-output").dataset.idx = index;
  });
}

function setActiveCell(idx) {
  _activeCellIndex = idx;
  document.querySelectorAll(".nb-cell").forEach((cell) => cell.classList.remove("active"));
  const cell = document.querySelector(`.nb-cell[data-index="${idx}"]`);
  if (cell) cell.classList.add("active");
}

function updateFooter() {
  const count = _cellEditors.length;
  byId("cell-detail").textContent = `${count} cell${count !== 1 ? "s" : ""}`;
  if (byId("document-lines")) byId("document-lines").textContent = `${lineCount(currentDocumentCode())} lines`;
}

function scrollToBottom() {
  const scroll = byId("nb-scroll");
  scroll.scrollTop = scroll.scrollHeight;
}

function isFixedPaneLayout() {
  const classes = byId("nb-cells").classList;
  return classes.contains("single-cell") || classes.contains("plain-mode");
}

function layoutEditor(idx) {
  const editor = _cellEditors[idx];
  const el = document.querySelector(`.nb-cell-editor[data-idx="${idx}"]`);
  if (!editor || !el) return;
  if (!isFixedPaneLayout()) {
    editor.layout();
    return;
  }
  const rect = el.getBoundingClientRect();
  editor.layout({
    width: Math.max(1, Math.floor(rect.width)),
    height: Math.max(1, Math.floor(rect.height)),
  });
}

function layoutEditorSoon(idx) {
  requestAnimationFrame(() => requestAnimationFrame(() => layoutEditor(idx)));
}

function layoutAllEditorsSoon() {
  requestAnimationFrame(() => requestAnimationFrame(() => {
    _cellEditors.forEach((editor, idx) => {
      if (editor) layoutEditor(idx);
    });
  }));
}
