// Nomi Web Playground — worker runtime (three backends: wasm-js, js-core-runtime, python-ast)

const PYODIDE_BASE = "https://cdn.jsdelivr.net/pyodide/v0.27.2/full/";

let pyodide = null;
let runNomi = null;
let resetSession = null;
let coreJsonForNomi = null;
let wasmReady = false;

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

async function initWasm() {
  postLog("Loading WASM parser...");
  importScripts("./pkg/nomi_parser_worker.js");
  const response = await fetch("./pkg/nomi_parser_worker_bg.wasm");
  const bytes = await response.arrayBuffer();
  wasm_bindgen.initSync({ module: bytes });
  wasmReady = true;
  postLog("WASM parser ready");
}

async function ensurePyodide() {
  if (pyodide) return;

  postLog("Loading Pyodide (lazy)...");
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

async function initRuntime() {
  importScripts("./core_runtime.js");
  importScripts("./lower_to_core_ir.js");
  await initWasm();
}

function runWithWasmJs(code) {
  const parseStart = performance.now();
  let json;
  try {
    json = wasm_bindgen.parse_nomi(code);
  } catch (e) {
    return { fallback: true, reason: "parse error: " + e.message };
  }
  const rustAst = JSON.parse(json);
  const parseMs = performance.now() - parseStart;

  const lowerStart = performance.now();
  const coreIr = self.NomiCoreLowerer.lowerRustAstToCoreIr(rustAst);
  const lowerMs = performance.now() - lowerStart;

  if (coreIr.diagnosticCount > 0) {
    return { fallback: true, reason: `${coreIr.diagnosticCount} diagnostics`, diagnosticCount: coreIr.diagnosticCount };
  }

  const evalStart = performance.now();
  let result;
  try {
    result = self.NomiCoreRuntime.evaluateCorePayload(coreIr, { displayLastExpr: true });
  } catch (e) {
    return { fallback: true, reason: "eval error: " + e.message };
  }
  const evalMs = performance.now() - evalStart;

  return {
    output: result.stdout || "",
    session: null,
    backend: "wasm-js",
    timing: {
      parse_ms: parseMs,
      lower_ms: lowerMs,
      eval_ms: evalMs,
      total_ms: parseMs + lowerMs + evalMs,
      cache_hit: false,
    },
    bindings: result.bindings || {},
  };
}

async function runWithJsCoreRuntime(code) {
  await ensurePyodide();
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

    if (type === "run") {
      const code = message.data.code || "";
      const backend = message.data.backend || "wasm-js";

      if (backend === "wasm-js") {
        const result = runWithWasmJs(code);
        if (!result.fallback) {
          postMessage({ id, type: "result", result });
          return;
        }
        postLog("Falling back to Pyodide: " + result.reason);
        await ensurePyodide();
        const pyResult = await runNomi(code);
        postMessage({ id, type: "result", result: convertPyValue(pyResult) });
        return;
      }

      if (backend === "js-core-runtime") {
        const result = await runWithJsCoreRuntime(code);
        postMessage({ id, type: "result", result: convertPyValue(result) });
        return;
      }

      // python-ast backend
      await ensurePyodide();
      const result = await runNomi(code);
      postMessage({ id, type: "result", result: convertPyValue(result) });
      return;
    }

    if (type === "reset") {
      await ensurePyodide();
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
