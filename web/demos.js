// Samples are loaded from the generated manifest; source has one owner.
const DEMOS = {};

const SAMPLE_DESCRIPTIONS = {
  "samples/demo.nomi": "Guided tour from samples/demo.nomi.",
  "samples/demo_terse.nomi": "Browser-safe quick tour: functions, flow, records, match, and output.",
  "samples/collections.nomi": "Collection examples from samples/collections.nomi.",
  "samples/notebook_intro.nomi.nb": "Notebook cells example.",
  "samples/data_pipeline.nomi": "Paid orders, integer cents, ordered fold and seeded scan.",
  "samples/text_pipeline.nomi.nb": "Normalize delimited text, convert fields, accumulate counts."
};

let _draftSaveTimer = null;

function sampleKey(path) {
  return path.replace(/^samples\//,"").replace(/\.nomi(\.nb)?$/,"").replace(/_/g,"-");
}

function isNotebookSource(code) {
  return /^\s*#\s*%%/m.test(code);
}

async function loadSampleSources() {
  restoreScratchDocuments();
  try {
    const resp = await fetch("./manifest.json");
    if (!resp.ok) throw new Error(`Sample manifest returned HTTP ${resp.status}`);
    const manifest = await resp.json();
    for (const path of (manifest.samples || [])) {
      const key = path === "samples/demo.nomi" ? "demo" : path === "samples/demo_terse.nomi" ? "terse" : sampleKey(path);
      const sampleUrl = new URL(`../${path}`, location.href);
      const r = await fetch(sampleUrl);
      if (!r.ok) throw new Error(`Sample ${path} returned HTTP ${r.status}`);
      const code = await r.text();
      const existing = DEMOS[key] || {};
      DEMOS[key] = { ...existing, title: path.split("/").pop(), desc: SAMPLE_DESCRIPTIONS[path] || `Sample from ${path}.`, source: path, code };
    }
  } catch (e) { console.warn("[web] Could not load samples from manifest", e); throw e; }
}

function restoreScratchDocuments() {
  const scratchDocs = _workbenchState.scratchDocs || {};
  for (const [key, item] of Object.entries(scratchDocs)) {
    DEMOS[key] = {
      title: item.title || `${key}.nomi`,
      desc: "Local browser draft.",
      code: "",
      local: true,
    };
  }
}

function documentCode(name) {
  if (Object.prototype.hasOwnProperty.call(_workbenchState.drafts, name)) {
    return _workbenchState.drafts[name];
  }
  return DEMOS[name] ? DEMOS[name].code : "";
}

function hasDocumentDraft(name) {
  const demo = DEMOS[name];
  if (!demo) return false;
  if (!Object.prototype.hasOwnProperty.call(_workbenchState.drafts, name)) return false;
  return demo.local || _workbenchState.drafts[name] !== demo.code;
}

function buildFileList() {
  const list = byId("file-list");
  list.innerHTML = "";
  const entries = Object.entries(DEMOS);
  byId("sample-count").textContent = `${entries.length} files`;
  const groups = [
    ["Local", entries.filter(([, demo]) => demo.local)],
    ["Examples", entries.filter(([, demo]) => !demo.local)],
  ];

  for (const [label, groupEntries] of groups) {
    if (!groupEntries.length) continue;
    const heading = document.createElement("span");
    heading.className = "sample-group-label";
    heading.dataset.sampleGroup = label.toLowerCase();
    heading.textContent = label;
    list.appendChild(heading);

    for (const [name, demo] of groupEntries) {
    const el = document.createElement("button");
    el.type = "button";
    el.className = "sample";
    el.dataset.sample = name;
    el.dataset.search = `${demo.title} ${demo.desc}`.toLowerCase();
    el.onclick = () => loadFile(name);
    el.classList.toggle("has-draft", hasDocumentDraft(name));
    el.innerHTML = `<span class="sample-icon"><i data-lucide="${demo.local ? "file-pen-line" : "file-code-2"}"></i></span><span class="sample-name">${esc(demo.title)}</span><span class="sample-meta">${lineCount(documentCode(name))} lines</span><span class="sample-desc">${esc(demo.desc)}</span>`;
    list.appendChild(el);
    }
  }

  const empty = document.createElement("div");
  empty.className = "sample-empty";
  empty.id = "sample-empty";
  empty.hidden = true;
  empty.textContent = "No matching samples";
  list.appendChild(empty);
  refreshIcons(list);
  updateSampleSelection();
}

function updateSampleSelection() {
  document.querySelectorAll(".sample").forEach((el) => {
    el.classList.toggle("active", el.dataset.sample === _currentSample);
    el.setAttribute("aria-current", el.dataset.sample === _currentSample ? "page" : "false");
    el.classList.toggle("has-draft", hasDocumentDraft(el.dataset.sample));
    const meta = el.querySelector(".sample-meta");
    if (meta) meta.textContent = `${lineCount(documentCode(el.dataset.sample))} lines`;
  });
}

window.filterSamples = function(value) {
  const query = String(value || "").trim().toLowerCase();
  let visible = 0;
  document.querySelectorAll(".sample").forEach((el) => {
    const matches = !query || el.dataset.search.includes(query);
    el.classList.toggle("hidden", !matches);
    if (matches) visible++;
  });
  document.querySelectorAll(".sample-group-label").forEach((heading) => {
    let sibling = heading.nextElementSibling;
    let groupVisible = false;
    while (sibling && !sibling.classList.contains("sample-group-label")) {
      if (sibling.classList.contains("sample") && !sibling.classList.contains("hidden")) groupVisible = true;
      sibling = sibling.nextElementSibling;
    }
    heading.hidden = !groupVisible;
  });
  byId("sample-empty").hidden = visible !== 0;
  byId("sample-count").textContent = query ? `${visible} found` : `${Object.keys(DEMOS).length} files`;
};

function updateDocumentState() {
  const demo = DEMOS[_currentSample];
  if (!demo) return;
  const dirty = hasDocumentDraft(_currentSample);
  const state = byId("document-state");
  state.textContent = demo.local ? "Local" : dirty ? "Draft" : "Sample";
  state.classList.toggle("dirty", dirty);
  byId("revert-btn").disabled = demo.local ? !currentDocumentCode().trim() : !dirty;
  byId("document-kind").textContent = _notebookMode ? "Notebook" : "Program";
  byId("document-lines").textContent = `${lineCount(currentDocumentCode())} lines`;
  updateSampleSelection();
}

function saveCurrentDraft(immediate) {
  if (_documentLoading || !_cellEditors.length || !DEMOS[_currentSample]) return;
  const demo = DEMOS[_currentSample];
  const code = currentDocumentCode();
  if (!demo.local && code === demo.code) {
    delete _workbenchState.drafts[_currentSample];
  } else {
    _workbenchState.drafts[_currentSample] = code;
  }
  updateDocumentState();

  if (_draftSaveTimer) clearTimeout(_draftSaveTimer);
  if (immediate) {
    return persistWorkbenchState();
  } else {
    _draftSaveTimer = setTimeout(persistWorkbenchState, 250);
  }
}

function createLocalDocument(title, code) {
  saveCurrentDraft(true);
  const scratchDocs = _workbenchState.scratchDocs || {};
  let number = Object.keys(scratchDocs).length + 1;
  let key = `scratch-${number}`;
  while (DEMOS[key]) {
    number++;
    key = `scratch-${number}`;
  }
  title = title || `scratch-${number}.nomi`;
  _workbenchState.scratchDocs = { ...scratchDocs, [key]: { title } };
  _workbenchState.drafts[key] = code || "";
  DEMOS[key] = { title, desc: "Local browser draft.", code: "", local: true };
  buildFileList();
  persistWorkbenchState();
  loadFile(key);
  return key;
}

window.newScratch = function() {
  createLocalDocument();
};

window.openLocalSource = async function(input) {
  const file = input.files[0];
  input.value = "";
  if (!file) return;
  if (file.size > 256 * 1024) { showToast("Source exceeds the 256 KiB limit"); return; }
  try {
    const source = new TextDecoder("utf-8", { fatal: true }).decode(await file.arrayBuffer());
    createLocalDocument(file.name, source);
  } catch (error) {
    showToast("Could not open UTF-8 source");
  }
};

window.downloadCurrentSource = function() {
  const demo = DEMOS[_currentSample];
  if (!demo) return;
  const url = URL.createObjectURL(new Blob([currentDocumentCode()], { type: "text/plain;charset=utf-8" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = demo.title;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
};

window.revertCurrentDocument = function() {
  const demo = DEMOS[_currentSample];
  if (!demo || !hasDocumentDraft(_currentSample)) return;
  if (!window.confirm(`Discard local changes to ${demo.title}?`)) return;
  if (demo.local) {
    _workbenchState.drafts[_currentSample] = "";
  } else {
    delete _workbenchState.drafts[_currentSample];
  }
  persistWorkbenchState();
  loadFile(_currentSample, { skipSave: true });
  showToast("Local changes discarded");
};

window.loadFile = function(name, options) {
  if (!Object.prototype.hasOwnProperty.call(DEMOS, name)) return;
  if (!options || !options.skipSave) saveCurrentDraft(true);
  _documentGeneration++;
  _documentRevision = 0;
  _runtimeDocument = null;
  if (_executionBusy) cancelRuntime("Document changed during execution");
  _currentSample = name;
  const demo = DEMOS[name];
  byId("current-file").textContent = demo.title;
  const code = documentCode(name);

  const nb = demo.title.endsWith(".nomi.nb") || isNotebookSource(code);
  _notebookMode = nb;
  _documentLoading = true;
  try {
    if (nb) loadCode(code);
    else loadPlain(code);
  } finally {
    _documentLoading = false;
  }
  _workbenchState.active = name;
  persistWorkbenchState();
  updateDocumentState();
  updateSampleSelection();
  if (matchMedia("(max-width: 980px)").matches) toggleSidebar(false);
};
