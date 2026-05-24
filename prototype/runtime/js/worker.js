// Nomi JS runtime worker — WASM parser + JS Core Runtime host (no Python/Pyodide)

let runtime = null;

function postLog(message) {
  postMessage({ type: "log", message });
}

async function initWasm() {
  postLog("Loading WASM parser...");
  importScripts("./pkg/nomi_parser_worker.js?v=2");
  const response = await fetch("./pkg/nomi_parser_worker_bg.wasm");
  const bytes = await response.arrayBuffer();
  wasm_bindgen.initSync({ module: bytes });
  postLog("WASM parser ready");
}

async function initRuntime() {
  importScripts("./core_runtime.js?v=2");
  importScripts("./lower_to_core_ir.js?v=2");
  await initWasm();
  runtime = new NomiCoreRuntime.CoreRuntime();
}

function runWithWasmJs(code) {
  const parseStart = performance.now();
  let json;
  try {
    json = wasm_bindgen.parse_nomi(code);
  } catch (e) {
    return { error: "parse error: " + e.message };
  }
  const rustAst = JSON.parse(json);
  const parseMs = performance.now() - parseStart;

  const lowerStart = performance.now();
  const coreIr = self.NomiCoreLowerer.lowerRustAstToCoreIr(rustAst);
  const lowerMs = performance.now() - lowerStart;

  if (coreIr.diagnosticCount > 0) {
    return { error: `${coreIr.diagnosticCount} lowering diagnostic(s) — some constructs not yet handled by the JS lowerer` };
  }

  const evalStart = performance.now();
  let result;
  try {
    result = runtime.evaluate(coreIr, { displayLastExpr: true });
  } catch (e) {
    return { error: "eval error: " + e.message };
  }
  const evalMs = performance.now() - evalStart;

  return {
    output: result.stdout || "",
    backend: "wasm-js",
    value: result.value,
    has_value: result.has_value === true,
    diagnostics: result.diagnostics || [],
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
      const result = runWithWasmJs(code);
      postMessage({ id, type: "result", result });
      return;
    }

    if (type === "reset") {
      runtime = new NomiCoreRuntime.CoreRuntime();
      postMessage({ id, type: "reset-done", result: { ok: true } });
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
