// Nomi Web Playground — sample data, manifest loading, sidebar

const DEMOS = {
  demo: {
    title: "demo.nomi", desc: "Guided tour from samples/demo.nomi.",
    source: "samples/demo.nomi",
    code: `add(a, b) = a + b
print("add(3, 4) = " + str(add(3, 4)))`
  },
  "notebook-intro": {
    title: "notebook_intro.nomi.nb", desc: "Notebook cells example.",
    source: "samples/notebook_intro.nomi.nb",
    code: `# %% Define a reusable function
func normalize_name(name):
    return name.strip().title()

print(normalize_name(" ada lovelace "))

# %% Bind data that later cells can reuse
names = [" ada ", "grace", " alan turing "]
clean_names = []

for name in names:
    clean_names.append(normalize_name(name))

print(clean_names)`
  },
  terse: {
    title: "demo_terse.nomi", desc: "Browser-safe quick tour: functions, flow, records, match, and output.",
    source: "samples/demo_terse.nomi",
    code: `priority(ticket) = ticket["impact"] * ticket["urgency"]
is_hot = priority(_) >= 80
label(score) when score >= 90 = "critical"
label(score) when score >= 70 = "watch"
label(_) = "steady"

tickets = [{"service": "checkout", "impact": 10, "urgency": 9}, {"service": "search", "impact": 6, "urgency": 8}, {"service": "billing", "impact": 8, "urgency": 10}]
scores = list(map(priority, tickets))
hot = list(filter(is_hot, tickets))
winner = hot[0]
winner_score = priority(winner)
action = match label(winner_score): case "critical" => "page now"; case "watch" => "assign owner"; case _ => "monitor"
range_total = 1..5 |> list |> sum

print("Nomi triage")
print("scores = " + str(scores))
print("hot tickets = " + str(len(hot)))
print(winner["service"] + " -> " + str(winner_score) + " / " + action)
print("range total = " + str(range_total))`
  },
  collections: {
    title: "collections.nomi", desc: "Collection examples from samples/collections.nomi.",
    source: "samples/collections.nomi",
    code: `inclusive = list(1..5)
print("1..5 = " + str(inclusive))`
  },
  block: {
    title: "blocks.nomi", desc: "Yield-to-block control with a running total.",
    code: `func each(items):
    for item in items:
        yield item

total = 0
each([1, -2, 3, 8]) -> item:
    if item > 0:
        total += item

print(f"total = {total}")`
  },
  constraint: {
    title: "constraints.nomi", desc: "Binding constraints and a match statement.",
    code: `is_positive = (x) => x > 0
score: int, is_positive = 72

match score:
    case 100:
        label = "perfect"
    case _:
        label = "regular"

print(f"score={score}, grade={label}")`
  },
  comprehensive: {
    title: "comprehensive.nomi", desc: "Full coverage suite: functions, lambdas, patterns, control flow, data, blocks, and edge cases.",
    source: "samples/comprehensive.nomi",
    code: `# Functions, lambdas, patterns, data, blocks, edge cases
add(a, b) = a + b
double = x => x * 2

func each(sequence):
    for item in sequence:
        yield item

collected = []
each([1, 2, 3]) -> n:
    collected = collected + [n * 2]

print(collected)`
  }
};

const SAMPLE_DESCRIPTIONS = {
  "samples/demo.nomi": "Guided tour from samples/demo.nomi.",
  "samples/demo_terse.nomi": "Browser-safe quick tour: functions, flow, records, match, and output.",
  "samples/collections.nomi": "Collection examples from samples/collections.nomi.",
  "samples/notebook_intro.nomi.nb": "Notebook cells example."
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
    if (!resp.ok) return;
    const manifest = await resp.json();
    for (const path of (manifest.samples || [])) {
      const key = path === "samples/demo.nomi" ? "demo" : path === "samples/demo_terse.nomi" ? "terse" : sampleKey(path);
      const sampleUrl = new URL(`../${path}`, location.href);
      const r = await fetch(sampleUrl);
      if (!r.ok) { console.warn("[web] Failed to fetch sample", path, r.status); continue; }
      const code = await r.text();
      const existing = DEMOS[key] || {};
      DEMOS[key] = { ...existing, title: path.split("/").pop(), desc: SAMPLE_DESCRIPTIONS[path] || `Sample from ${path}.`, source: path, code };
    }
  } catch (e) { console.warn("[web] Could not load samples from manifest", e); }
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
    persistWorkbenchState();
  } else {
    _draftSaveTimer = setTimeout(persistWorkbenchState, 250);
  }
}

window.newScratch = function() {
  saveCurrentDraft(true);
  const scratchDocs = _workbenchState.scratchDocs || {};
  let number = Object.keys(scratchDocs).length + 1;
  let key = `scratch-${number}`;
  while (DEMOS[key]) {
    number++;
    key = `scratch-${number}`;
  }
  const title = `scratch-${number}.nomi`;
  _workbenchState.scratchDocs = { ...scratchDocs, [key]: { title } };
  _workbenchState.drafts[key] = "";
  DEMOS[key] = { title, desc: "Local browser draft.", code: "", local: true };
  buildFileList();
  persistWorkbenchState();
  loadFile(key);
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
  if (!DEMOS[name]) return;
  if (!options || !options.skipSave) saveCurrentDraft(true);
  _currentSample = name;
  const demo = DEMOS[name];
  byId("current-file").textContent = demo.title;
  const code = documentCode(name);

  const nb = demo.title.endsWith(".nomi.nb") || isNotebookSource(code);
  _notebookMode = nb;
  _documentLoading = true;
  if (nb) {
    loadCode(code);
  } else {
    loadPlain(code);
  }
  _documentLoading = false;
  _workbenchState.active = name;
  persistWorkbenchState();
  updateDocumentState();
  updateSampleSelection();
  if (matchMedia("(max-width: 980px)").matches) toggleSidebar(false);
};
