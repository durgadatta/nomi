// Nomi web playground — opt-in Pyodide backend worker.
// Only loaded when ?backend=pyodide is set explicitly.
// Default flow uses prototype/runtime/js/worker.js (WASM + JS, no Pyodide).

const PYODIDE_BASE = "https://cdn.jsdelivr.net/pyodide/v0.27.2/full/";

let pyodide = null;
let runNomi = null;
let resetSession = null;

function postLog(message) {
  postMessage({ type: "log", message });
}

function convertPyValue(value) {
  if (value && typeof value.toJs === "function") {
    const converted = value.toJs();
    if (value.destroy) value.destroy();
    return convertPyValue(converted);
  }
  if (value instanceof Map) {
    const obj = {};
    for (const [key, item] of value.entries()) {
      obj[key] = convertPyValue(item);
    }
    return obj;
  }
  if (Array.isArray(value)) {
    return value.map(convertPyValue);
  }
  return value;
}

async function initPyodide() {
  if (pyodide) return;

  postLog("Loading Pyodide...");
  importScripts(PYODIDE_BASE + "pyodide.js");
  pyodide = await loadPyodide({ indexURL: PYODIDE_BASE });

  postLog("Installing lark...");
  await pyodide.loadPackage("micropip");
  const micropip = pyodide.pyimport("micropip");
  await micropip.install("lark");

  postLog("Initializing Nomi...");
  const nomiPy = await fetch("./nomi_web.py").then(function (response) { return response.text(); });
  await pyodide.runPythonAsync(nomiPy);
  await pyodide.globals.get("init_nomi")();
  runNomi = pyodide.globals.get("run_nomi");
  resetSession = pyodide.globals.get("reset_session");
}

async function handleMessage(message) {
  const { id, type } = message.data;
  try {
    if (type === "init") {
      await initPyodide();
      postMessage({ id, type: "ready" });
      return;
    }

    if (type === "run") {
      const code = message.data.code || "";
      const result = await runNomi(code);
      postMessage({ id, type: "result", result: convertPyValue(result) });
      return;
    }

    if (type === "reset") {
      const result = resetSession();
      postMessage({ id, type: "reset-done", result: convertPyValue(result) });
      return;
    }

    throw new Error("Unknown worker message type: " + type);
  } catch (error) {
    postMessage({
      id,
      type: "error",
      error: error && error.stack ? error.stack : String(error),
    });
  }
}

self.onmessage = function (message) {
  handleMessage(message);
};
