// Nomi Web Playground - document cells, Monaco instances, and result panes

function markerMatch(line) { return line.match(/^\s*#\s*%%\s*(.*)$/); }

function splitCode(code) {
  return splitNotebookDocument(code).cells.map((cell) => cell.code);
}

function currentDocumentCode() {
  if (!_cellEditors.length) return "";
  if (!_notebookMode) return _cellEditors[0] ? _cellEditors[0].getValue() : "";
  return joinNotebookDocument(_notebookPreamble, _cellEditors.map((editor, index) => ({
    prefix: _cellPrefixes[index] || "", code: editor.getValue(),
  })));
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
      <div class="result-stale" hidden><i data-lucide="history"></i><span>Previous source</span></div>
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
  outer.querySelector(".result-tabs").addEventListener("keydown", (event) => {
    const tabs = [...outer.querySelectorAll(".result-tab")];
    const current = tabs.indexOf(document.activeElement);
    if (current < 0 || !["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
    event.preventDefault();
    const next = event.key === "Home" ? 0 : event.key === "End" ? tabs.length - 1
      : (current + (event.key === "ArrowRight" ? 1 : -1) + tabs.length) % tabs.length;
    tabs[next].click();
    tabs[next].focus();
  });
  activateResultTab(Number(outer.dataset.index), "output");
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
    button.tabIndex = active ? 0 : -1;
    button.id = `result-tab-${idx}-${button.dataset.resultTab}`;
    button.setAttribute("aria-controls", `result-view-${idx}-${button.dataset.resultTab}`);
  });
  outer.querySelectorAll(".result-view").forEach((view) => {
    view.classList.toggle("active", view.dataset.resultView === tabName);
    view.id = `result-view-${idx}-${view.dataset.resultView}`;
    view.setAttribute("aria-labelledby", `result-tab-${idx}-${view.dataset.resultView}`);
  });
}

function setupPaneResize(outer) {
  const handle = outer.querySelector(".pane-resize-handle");
  if (!handle) return;
  let dragging = false;
  handle.tabIndex = 0;
  handle.setAttribute("aria-valuemin", "28");
  handle.setAttribute("aria-valuemax", "68");
  function setPercent(percent) {
    const value = Math.max(28, Math.min(68, percent));
    document.documentElement.style.setProperty("--result-pane", `${value}%`);
    _workbenchState.resultPane = Math.round(value * 10) / 10;
    handle.setAttribute("aria-valuenow", String(value));
    layoutAllEditorsSoon();
  }
  handle.setAttribute("aria-valuenow", String(_workbenchState.resultPane));
  handle.addEventListener("keydown", (event) => {
    if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
    event.preventDefault();
    setPercent(event.key === "Home" ? 28 : event.key === "End" ? 68 : _workbenchState.resultPane + (event.key === "ArrowLeft" ? 5 : -5));
    persistWorkbenchState();
  });

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
    setPercent(fromRight);
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

  const document = splitNotebookDocument(code);
  _notebookPreamble = document.preamble;
  document.cells.forEach((cell) => createCell(cell.code, cell));
  _executionCounter = 0;
  const single = document.cells.length === 1;
  byId("nb-scroll").classList.toggle("single-cell", single);
  byId("nb-cells").classList.toggle("single-cell", single);
  layoutAllEditorsSoon();
  updateFooter();
}

function loadPlain(code) {
  const existingPlain = byId("nb-cells").classList.contains("plain-mode")
    && _cellEditors.length === 1
    && document.querySelector(".nb-cell.plain");
  if (existingPlain) {
    byId("run-all-btn").onclick = runPlainCode;
    setRunButtonLabel("Run");
    byId("add-cell-btn").style.display = "none";
    _cellEditors[0].setValue(code);
    _executionCounter = 0;
    resetResultPanel(0);
    _cellEditors[0].focus();
    layoutAllEditorsSoon();
    updateFooter();
    return;
  }

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
  if (!_notebookMode || _executionBusy) return;
  createCell(initialCode || "", { prefix: `\n# %% Cell ${_cellEditors.length + 1}\n`, title: `Cell ${_cellEditors.length + 1}` });
  _documentRevision++;
  markResultsStale();
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

function createCell(code, framing) {
  const idx = _cellEditors.length;
  const outer = document.createElement("div");
  outer.className = "nb-cell";
  outer.dataset.index = idx;
  outer.dataset.execCount = "";
  outer.innerHTML = `
    <div class="nb-cell-header">
      <span class="nb-cell-index">In[ ]:</span>
      <span class="nb-cell-title">${esc(framing && framing.title || "")}</span>
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
  _cellPrefixes[idx] = framing ? framing.prefix : `# %% Cell ${idx + 1}\n`;
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
    // Monaco 0.52's WordHighlighter rejects a pending delay on disposal (#4859).
    // Restore automatic occurrences only after its disposal stress gate is clean.
    occurrencesHighlight: "off",
    smoothScrolling: true,
    cursorBlinking: "smooth",
    wordWrap: "on",
    scrollbar: { vertical: "auto", horizontal: "auto", useShadows: false },
    padding: { top: 10, bottom: 10 },
  });

  // Monaco defaults to LF; retain the loaded cell's line-ending convention.
  if (code.includes("\r\n")) editor.getModel().setEOL(monaco.editor.EndOfLineSequence.CRLF);

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
    const currentIndex = _cellEditors.indexOf(editor);
    if (currentIndex >= 0) layoutEditor(currentIndex);
  });

  editor.onDidChangeModelContent(() => {
    if (!_documentLoading) {
      _documentRevision++;
      markResultsStale();
    }
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
  _cellEditors.forEach((editor) => {
    if (!editor) return;
    const model = editor.getModel();
    editor.dispose();
    if (model) model.dispose();
  });
  _cellEditors = [];
  _cellResults = [];
  _cellPrefixes = [];
  _notebookPreamble = "";
  byId("nb-cells").innerHTML = "";
}

function deleteCell(idx) {
  if (_cellEditors.length <= 1 || _executionBusy) return;
  if (_cellEditors[idx]) {
    const model = _cellEditors[idx].getModel();
    _cellEditors[idx].dispose();
    if (model) model.dispose();
  }
  _cellEditors.splice(idx, 1);
  _cellResults.splice(idx, 1);
  _cellPrefixes.splice(idx, 1);
  _documentRevision++;
  const cell = document.querySelector(`.nb-cell[data-index="${idx}"]`);
  if (cell) cell.remove();
  reindexCells();
  markResultsStale();
  const single = _cellEditors.length === 1;
  byId("nb-scroll").classList.toggle("single-cell", single);
  byId("nb-cells").classList.toggle("single-cell", single);
  _activeCellIndex = Math.max(0, Math.min(idx, _cellEditors.length - 1));
  setActiveCell(_activeCellIndex);
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
    const activeTab = cell.querySelector(".result-tab.active");
    activateResultTab(index, activeTab ? activeTab.dataset.resultTab : "output");
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
