// Nomi Web Playground — Pyodide worker runtime

const PYODIDE_BASE = "https://cdn.jsdelivr.net/pyodide/v0.27.2/full/";

let pyodide = null;
let runNomi = null;
let resetSession = null;
let coreJsonForNomi = null;

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

async function initRuntime() {
  postLog("Loading Pyodide...");
  importScripts("./core_runtime.js");
  importScripts(PYODIDE_BASE + "pyodide.js");
  pyodide = await loadPyodide({ indexURL: PYODIDE_BASE });

  postLog("Installing lark...");
  await pyodide.loadPackage("micropip");
  const micropip = pyodide.pyimport("micropip");
  await micropip.install("lark");

  postLog("Initializing Nomi...");
  const nomiPy = await fetch("./nomi_web.py").then((response) => response.text());
  await pyodide.runPythonAsync(nomiPy);
  await pyodide.globals.get("init_nomi")();
  runNomi = pyodide.globals.get("run_nomi");
  resetSession = pyodide.globals.get("reset_session");
  coreJsonForNomi = pyodide.globals.get("core_json_for_nomi");
}

async function runWithJsCoreRuntime(code) {
  const lowerStart = performance.now();
  const lowered = convertPyValue(await coreJsonForNomi(code || ""));
  const lowerMs = performance.now() - lowerStart;
  const evalStart = performance.now();
  const result = self.NomiCoreRuntime.evaluateCorePayload(
    JSON.parse(lowered.core_json),
  );
  const evalMs = performance.now() - evalStart;
  return {
    output: result.stdout || "",
    session: lowered.session,
    backend: result.backend,
    timing: {
      ...(lowered.timing || {}),
      parse_ms: lowerMs,
      eval_ms: evalMs,
      total_ms: lowerMs + evalMs,
      cache_hit: false,
    },
    bindings: result.bindings,
  };
}

async function handleMessage(message) {
  const { id, type } = message.data;
  try {
    if (type === "init") {
      await initRuntime();
      postMessage({ id, type: "ready" });
      return;
    }

    if (!runNomi || !resetSession || !coreJsonForNomi) {
      throw new Error("Nomi runtime is not ready");
    }

    if (type === "run") {
      const result = message.data.backend === "js-core-runtime"
        ? await runWithJsCoreRuntime(message.data.code || "")
        : await runNomi(message.data.code || "");
      postMessage({ id, type: "result", result: convertPyValue(result) });
      return;
    }

    if (type === "reset") {
      const result = resetSession();
      postMessage({ id, type: "reset-done", result: convertPyValue(result) });
      return;
    }

    throw new Error(`Unknown worker message type: ${type}`);
  } catch (error) {
    postMessage({
      id,
      type: "error",
      error: error && error.stack ? error.stack : String(error),
    });
  }
}

self.onmessage = (message) => {
  handleMessage(message);
};
