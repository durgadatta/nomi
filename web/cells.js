// Nomi Web Playground — cell creation, editors, reindex, deletion

function markerMatch(line) { return line.match(/^\s*#\s*%%\s*(.*)$/); }

function splitCode(code) {
  const lines = code.split(/\r\n|\r|\n/);
  const markers = [];
  lines.forEach((line, i) => { const m = markerMatch(line); if (m) markers.push({ line: i+1, title: m[1].trim() }); });
  if (markers.length === 0) return [code.trim() || "# empty cell"];
  return markers.map((mk, i) => {
    const start = mk.line + 1;
    const end = (markers[i+1] ? markers[i+1].line - 1 : lines.length);
    return lines.slice(start - 1, end).join("\n").trim() || "# empty cell";
  });
}

function loadCode(code) {
  disposeAllCells();
  // Restore notebook toolbar
  byId("run-all-btn").onclick = runAllCells;
  byId("run-all-btn").textContent = "Run All";
  const addBtn = byId("add-cell-btn");
  if (addBtn) addBtn.style.display = "";
  byId("nb-scroll").classList.remove("plain-mode");
  byId("nb-cells").classList.remove("plain-mode");

  const chunks = splitCode(code);
  chunks.forEach(c => createCell(c));
  _executionCounter = 0;
  const single = chunks.length === 1;
  byId("nb-scroll").classList.toggle("single-cell", single);
  byId("nb-cells").classList.toggle("single-cell", single);
  layoutAllEditorsSoon();
  updateFooter();
}

function loadPlain(code) {
  disposeAllCells();
  // Plain-mode toolbar: Run instead of Run All, no +Cell
  byId("run-all-btn").onclick = runPlainCode;
  byId("run-all-btn").textContent = "Run";
  const addBtn = byId("add-cell-btn");
  if (addBtn) addBtn.style.display = "none";
  byId("nb-scroll").classList.remove("single-cell");
  byId("nb-scroll").classList.add("plain-mode");
  byId("nb-cells").classList.add("plain-mode");

  createPlainCell(code);
  _executionCounter = 0;
  layoutAllEditorsSoon();
  updateFooter();
}

function addCell(initialCode) {
  if (!_notebookMode) return;
  createCell(initialCode || "");
  byId("nb-scroll").classList.remove("single-cell");
  byId("nb-cells").classList.remove("single-cell");
  layoutAllEditorsSoon();
  scrollToBottom();
}

function createPlainCell(code) {
  const cells = byId("nb-cells");
  const outer = document.createElement("div");
  outer.className = "nb-cell plain";
  outer.dataset.index = "0";
  outer.innerHTML = `
    <div class="nb-cell-editor" data-idx="0"></div>
    <div class="nb-cell-output" data-idx="0">
      <div class="out-label">Out:</div>
      <pre></pre>
    </div>`;
  cells.appendChild(outer);
  createEditor(0, code, true);
  updateFooter();
  setActiveCell(0);
  layoutAllEditorsSoon();
}

function createCell(code) {
  const cells = byId("nb-cells");
  const idx = _cellEditors.length;
  const outer = document.createElement("div");
  outer.className = "nb-cell";
  outer.dataset.index = idx;
  outer.dataset.execCount = "";
  outer.innerHTML = `
    <div class="nb-cell-header">
      <span class="nb-cell-index">In[ ]:</span>
      <button class="nb-cell-run" data-idx="${idx}" title="Run (Ctrl+Enter)">&#9654; Run</button>
      <span class="nb-cell-spacer"></span>
      <span class="nb-cell-time"></span>
      <button class="nb-cell-delete" data-idx="${idx}" title="Delete">&times;</button>
    </div>
    <div class="nb-cell-editor" data-idx="${idx}"></div>
    <div class="nb-cell-output" data-idx="${idx}">
      <div class="out-label">Out[<span class="out-num">?</span>]:</div>
      <pre></pre>
    </div>`;
  cells.appendChild(outer);

  outer.addEventListener("click", () => setActiveCell(idx));

  outer.querySelector(".nb-cell-run").addEventListener("click", (e) => {
    e.stopPropagation();
    runCell(idx, false);
  });

  outer.querySelector(".nb-cell-delete").addEventListener("click", (e) => {
    e.stopPropagation();
    deleteCell(idx);
  });

  createEditor(idx, code);
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
    wordWrap: "on",
    scrollbar: { vertical: "auto", horizontal: "auto" },
    padding: { top: 8, bottom: 8 },
  });

  // Trigger initial layout so onDidContentSizeChange can measure
  // the container post-creation.
  editor.layout();

  // Set initial height for notebook cells so they start expanded —
  // onDidContentSizeChange may not fire synchronously for initial content.
  const nbCls = byId("nb-cells").classList;
  if (!nbCls.contains("single-cell") && !nbCls.contains("plain-mode")) {
    const lineCount = (code.match(/\n/g) || []).length + 1;
    const scrollH = byId("nb-scroll").clientHeight || window.innerHeight;
    const maxH = Math.max(200, scrollH * 0.5);
    const estH = Math.min(maxH, Math.max(60, lineCount * 22 + 16));
    el.style.height = estH + "px";
    editor.layout();
  }

  editor.onDidContentSizeChange((e) => {
    // In single-cell / plain mode the grid controls height;
    // setting it explicitly would overflow the grid track.
    const cls = byId("nb-cells").classList;
    const gridMode = cls.contains("single-cell") || cls.contains("plain-mode");
    if (!gridMode) {
      // Notebook cells grow to content, but cap at ~50% of the
      // scroll area so large cells scroll internally.
      const scrollH = byId("nb-scroll").clientHeight || window.innerHeight;
      const maxH = Math.max(200, scrollH * 0.5);
      const h = Math.min(maxH, Math.max(60, e.contentHeight));
      el.style.height = h + "px";
    }
    layoutEditor(idx);
  });

  editor.onDidFocusEditorText(() => setActiveCell(idx));

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
      run: () => runCell(idx, false),
    });
    editor.addAction({
      id: `run-cell-advance-${idx}`,
      label: "Run Cell and Advance",
      keybindings: [monaco.KeyMod.Shift | monaco.KeyCode.Enter],
      run: () => runCell(idx, true),
    });
  }

  _cellEditors[idx] = editor;
  // Focus the new editor so the user can start typing immediately.
  // (setActiveCell may have run before the deferred editor was ready.)
  editor.focus();
  layoutEditorSoon(idx);
}

function disposeAllCells() {
  _cellEditors.forEach(e => e && e.dispose());
  _cellEditors = [];
  byId("nb-cells").innerHTML = "";
}

function deleteCell(idx) {
  if (_cellEditors.length <= 1) return;
  const editors = _cellEditors[idx];
  if (editors) editors.dispose();
  _cellEditors.splice(idx, 1);
  const el = document.querySelector(`.nb-cell[data-index="${idx}"]`);
  if (el) el.remove();
  reindexCells();
  const single = _cellEditors.length === 1;
  byId("nb-scroll").classList.toggle("single-cell", single);
  byId("nb-cells").classList.toggle("single-cell", single);
  layoutAllEditorsSoon();
  updateFooter();
}

function reindexCells() {
  document.querySelectorAll(".nb-cell").forEach((el, i) => {
    el.dataset.index = i;
    const count = el.dataset.execCount || "";
    el.querySelector(".nb-cell-index").textContent = count ? `In[${count}]:` : "In[ ]:";
    el.querySelector(".nb-cell-run").dataset.idx = i;
    el.querySelector(".nb-cell-delete").dataset.idx = i;
    el.querySelector(".nb-cell-editor").dataset.idx = i;
    el.querySelector(".nb-cell-output").dataset.idx = i;
  });
}

function setActiveCell(idx) {
  _activeCellIndex = idx;
  document.querySelectorAll(".nb-cell").forEach(el => el.classList.remove("active"));
  const el = document.querySelector(`.nb-cell[data-index="${idx}"]`);
  if (el) {
    el.classList.add("active");
    const editor = _cellEditors[idx];
    if (editor) editor.focus();
  }
}

function updateFooter() {
  const n = _cellEditors.length;
  byId("cell-detail").textContent = `${n} cell${n!==1?"s":""}`;
}

function scrollToBottom() {
  const s = byId("nb-scroll");
  s.scrollTop = s.scrollHeight;
}

function isFixedPaneLayout() {
  const cls = byId("nb-cells").classList;
  return cls.contains("single-cell") || cls.contains("plain-mode");
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
