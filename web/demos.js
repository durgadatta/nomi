// Nomi Web Playground — sample data, manifest loading, sidebar

const DEMOS = {
  demo: {
    title: "demo.nomi", desc: "Guided tour from samples/demo.nomi.",
    source: "samples/demo.nomi",
    code: `func greet(name):
    return f"Hello, {name}!"

result = greet("World")
print(result)`
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
    title: "demo_terse.nomi", desc: "Compact syntax tour from samples/demo_terse.nomi.",
    source: "samples/demo_terse.nomi",
    code: `func greet(name): return "Hello, " + name
print(greet("Nomi"))`
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
  "samples/demo_terse.nomi": "Compact syntax tour from samples/demo_terse.nomi.",
  "samples/collections.nomi": "Collection examples from samples/collections.nomi.",
  "samples/notebook_intro.nomi.nb": "Notebook cells example."
};

function sampleKey(path) {
  return path.replace(/^samples\//,"").replace(/\.nomi(\.nb)?$/,"").replace(/_/g,"-");
}

function isNotebookSource(code) {
  return /^\s*#\s*%%/m.test(code);
}

async function loadSampleSources() {
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

function buildFileList() {
  const list = byId("file-list");
  list.innerHTML = "";
  const entries = Object.entries(DEMOS);
  byId("sample-count").textContent = `${entries.length} files`;
  for (const [name, demo] of entries) {
    const el = document.createElement("button");
    el.type = "button"; el.className = "sample"; el.dataset.sample = name;
    el.onclick = () => loadFile(name);
    el.innerHTML = `<span class="sample-name">${esc(demo.title)}</span><span class="sample-meta">${lineCount(demo.code)} lines</span><span class="sample-desc">${esc(demo.desc)}</span>`;
    list.appendChild(el);
  }
}

window.loadFile = function(name) {
  if (!DEMOS[name]) return;
  _currentSample = name;
  const demo = DEMOS[name];
  byId("current-file").textContent = demo.title;
  document.querySelectorAll(".sample").forEach(el => el.classList.toggle("active", el.dataset.sample === name));

  const nb = demo.title.endsWith(".nomi.nb") || isNotebookSource(demo.code);
  _notebookMode = nb;
  if (nb) {
    loadCode(demo.code);
  } else {
    loadPlain(demo.code);
  }
};
