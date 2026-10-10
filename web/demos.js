// Samples are loaded from the generated manifest; source has one owner.
const DEMOS = Object.create(null);

// Learning metadata only: the manifest and sample files still own source.
const SAMPLE_CATALOG = {
  "samples/calculate.nomi": { group: "Start here", rank: 0, status: "Prototype", description: "Calculate an invoice. Change quantity, inspect a mistake, and repair it." },
  "samples/report.nomi": { group: "Start here", rank: 1, status: "Prototype", description: "Validate JSON, repair two fields, and download a report from Bindings." },
  "samples/data_pipeline.nomi": { group: "Data and text", rank: 0, status: "Prototype", description: "Select paid orders and accumulate a total and history in integer cents." },
  "samples/text_pipeline.nomi.nb": { group: "Data and text", rank: 1, status: "Prototype", description: "Normalize simple delimited text, convert fields, and run cells in order." },
  "samples/demo_terse.nomi": { group: "Experiments", rank: 0, status: "Experiment", description: "Ticket triage with prototype match and range notation." },
  "samples/notebook_intro.nomi.nb": { group: "Experiments", rank: 1, status: "Experiment", description: "Notebook state and an older constraint spelling." },
  "samples/demo.nomi": { group: "Experiments", status: "Experiment", description: "Historical syntax tour; several forms are rejected by the target." },
  "samples/demo_verbose.nomi": { group: "Experiments", status: "Experiment", description: "Compare explicit and experimental prototype forms." },
  "samples/collections.nomi": { group: "Experiments", status: "Experiment", description: "Prototype collection helpers and shorthand." },
  "samples/constraint.nomi": { group: "Experiments", status: "Experiment", description: "Older constraint, data, and pattern experiments." },
  "samples/block.nomi": { group: "Experiments", status: "Experiment", description: "Caller blocks and yield; not the target resource/task model." },
  "samples/others.nomi": { group: "Experiments", status: "Experiment", description: "Historical shortcuts, cleanup, and composition experiments." },
  "samples/comprehensive.nomi": { group: "Experiments", status: "Experiment", description: "Large prototype compatibility corpus; start with a focused task." },
};

function sampleInfo(path) {
  return Object.prototype.hasOwnProperty.call(SAMPLE_CATALOG, path)
    ? SAMPLE_CATALOG[path]
    : { group: "Experiments", status: "Experiment", description: `Prototype sample from ${path}.` };
}

function sampleGroups(entries) {
  const groups = [["Local", entries.filter(([, demo]) => demo.local)]];
  for (const label of ["Start here", "Data and text", "Experiments"]) {
    const members = entries.filter(([, demo]) => !demo.local && sampleInfo(demo.source).group === label);
    members.sort(([a, left], [b, right]) => {
      const rank = (sampleInfo(left.source).rank ?? 100) - (sampleInfo(right.source).rank ?? 100);
      return rank || (left.title || a).localeCompare(right.title || b);
    });
    groups.push([label, members]);
  }
  return groups.filter(([, members]) => members.length);
}

let _draftSaveTimer = null;
const SAMPLE_LOAD_TIMEOUT_MS = 30000;

function sampleKey(path) {
  if (path === "samples/demo.nomi") return "demo";
  if (path === "samples/demo_terse.nomi") return "terse";
  return path.replace(/^samples\//,"").replace(/\.nomi(\.nb)?$/,"").replace(/_/g,"-");
}

function isNotebookSource(code) {
  return /^\s*#\s*%%/m.test(code);
}

async function loadSampleSources() {
  restoreScratchDocuments();
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), SAMPLE_LOAD_TIMEOUT_MS);
  try {
    const resp = await fetch("./manifest.json", { signal: controller.signal });
    if (!resp.ok) throw new Error(`Sample manifest returned HTTP ${resp.status}`);
    const manifest = await resp.json();
    if (!manifest || typeof manifest !== "object" || Array.isArray(manifest)
      || !Array.isArray(manifest.samples) || !manifest.samples.length
      || !manifest.samples.every((path) => typeof path === "string" && path.trim())) {
      throw new Error("Sample manifest needs a nonempty text-path samples list");
    }
    if (!manifest.samples.includes("samples/demo_terse.nomi")) {
      throw new Error("Sample manifest is missing samples/demo_terse.nomi");
    }
    const paths = new Set();
    const keys = new Set();
    for (const path of manifest.samples) {
      const parts = path.split("/");
      if (parts[0] !== "samples" || parts.length < 2
        || parts.some((part) => !part || part === "." || part === "..")
        || /[\u0000-\u001f\u007f\\%?#]/.test(path) || !/\.nomi(?:\.nb)?$/.test(path)) {
        throw new Error(`Invalid sample manifest path: ${path}`);
      }
      if (paths.has(path)) throw new Error(`Duplicate sample manifest path: ${path}`);
      paths.add(path);
      const key = sampleKey(path);
      if (keys.has(key) || (Object.prototype.hasOwnProperty.call(DEMOS, key) && DEMOS[key].local)) {
        throw new Error(`Colliding sample manifest identity: ${key}`);
      }
      keys.add(key);
    }
    for (const path of manifest.samples) {
      const key = sampleKey(path);
      const sampleUrl = new URL(`../${path}`, location.href);
      const r = await fetch(sampleUrl, { signal: controller.signal });
      if (!r.ok) throw new Error(`Sample ${path} returned HTTP ${r.status}`);
      const code = await r.text();
      const existing = DEMOS[key] || {};
      DEMOS[key] = { ...existing, title: path.split("/").pop(), desc: sampleInfo(path).description, source: path, code };
    }
  } catch (e) {
    const error = controller.signal.aborted
      ? new Error(`Sample loading timed out after ${SAMPLE_LOAD_TIMEOUT_MS} ms`) : e;
    console.warn("[web] Could not load samples from manifest", error);
    throw error;
  } finally {
    clearTimeout(timer);
  }
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
  const groups = sampleGroups(entries);

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
      const status = demo.local ? "Local draft" : sampleInfo(demo.source).status;
      el.dataset.search = `${demo.title} ${demo.desc} ${label} ${status}`.toLowerCase();
      el.onclick = () => loadFile(name);
      el.classList.toggle("has-draft", hasDocumentDraft(name));
      el.title = `${status}: ${demo.desc}`;
      el.innerHTML = `<span class="sample-icon"><i data-lucide="${demo.local ? "file-pen-line" : "file-code-2"}"></i></span><span class="sample-name">${esc(demo.title)}</span><span class="sample-meta">${lineCount(documentCode(name))} lines</span><span class="sample-desc">${esc(status)} · ${esc(demo.desc)}</span>`;
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
