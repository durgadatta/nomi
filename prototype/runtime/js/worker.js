// Nomi JS runtime worker — WASM parser + JS Core Runtime host.
let runtime = null;

function postLog(message) {
  postMessage({ type: "log", message });
}

async function initWasm() {
  postLog("Loading WASM parser...");
  importScripts("./pkg/nomi_parser_worker.js?v=2");
  const response = await fetch("./pkg/nomi_parser_worker_bg.wasm");
  if (!response.ok) throw new Error(`WASM parser returned HTTP ${response.status}`);
  const bytes = await response.arrayBuffer();
  wasm_bindgen.initSync({ module: bytes });
  postLog("WASM parser ready");
}

async function initRuntime() {
  importScripts("./core_runtime.js?v=4");
  importScripts("./lower_to_core_ir.js?v=4");
  await initWasm();
  runtime = new NomiCoreRuntime.CoreRuntime();
}

function diagnosticRecord({ phase, message, severity, capability, frontend, backend, code, span, sourceExcerpt }) {
  return {
    phase,
    severity: severity || "error",
    message,
    span: span || null,
    source_excerpt: sourceExcerpt || null,
    node_type: null,
    capability: capability || null,
    frontend: frontend || "rust-fast-ast-wasm",
    backend: backend || "js-core-runtime",
    code: code || null,
  };
}

function parseErrorLocation(message, source) {
  const match = String(message).match(/ at byte (\d+)$/);
  if (!match) return {};
  const offset = Number(match[1]);
  const bytes = new TextEncoder().encode(source);
  if (offset > bytes.length) return {};
  let prefix;
  try { prefix = new TextDecoder("utf-8", { fatal: true }).decode(bytes.slice(0, offset)); }
  catch (_) { return {}; }
  const line = prefix.split("\n").length;
  const column = prefix.length - prefix.lastIndexOf("\n");
  return {
    span: { line, column, byte_offset: offset, coordinate_unit: "utf16-code-unit" },
    sourceExcerpt: source.split(/\r?\n/)[line - 1] || "",
  };
}

function resultEnvelope({
  ok,
  bindings,
  value,
  hasValue,
  stdout,
  stderr,
  diagnostics,
  timings,
  error,
}) {
  const output = stdout || "";
  return {
    ok,
    error: error || "",
    output,
    stdout: output,
    stderr: stderr || "",
    backend: "wasm-js",
    value: value === undefined ? null : value,
    has_value: hasValue === true,
    bindings: bindings === undefined ? null : bindings,
    diagnostics: diagnostics || [],
    timings: timings || {},
    timing: timings || {},
    pipeline: {
      parser_frontend: "rust-fast-ast-wasm",
      lowerer: "js-core-lowerer",
      eval_backend: "js-core-runtime",
      host: "browser-worker",
    },
  };
}

function runWithWasmJs(code) {
  const parseStart = performance.now();
  let json;
  try {
    json = wasm_bindgen.parse_nomi(code);
  } catch (e) {
    const totalMs = performance.now() - parseStart;
    const message = "parse error: " + (e && e.message ? e.message : String(e));
    return resultEnvelope({
      ok: false,
      error: message,
      diagnostics: [
        diagnosticRecord({
          phase: "parse",
          message,
          capability: "rust-fast-ast-wasm.parse",
          backend: null,
          code: "NOMI-PARSE",
          ...parseErrorLocation(message, code),
        }),
      ],
      timings: {
        parse_ms: totalMs,
        total_ms: totalMs,
        cache_hit: false,
      },
    });
  }
  const rustAst = JSON.parse(json);
  const parseMs = performance.now() - parseStart;

  const lowerStart = performance.now();
  const coreIr = self.NomiCoreLowerer.lowerRustAstToCoreIr(rustAst);
  const lowerMs = performance.now() - lowerStart;

  if (coreIr.diagnosticCount > 0) {
    const diagnostics = coreIr.diagnostics || [];
    const first = diagnostics[0] || diagnosticRecord({
      phase: "lower",
      message: `${coreIr.diagnosticCount} lowering diagnostic(s)`,
      capability: "js-lowerer.unsupported",
    });
    return resultEnvelope({
      ok: false,
      error: first.message,
      diagnostics,
      timings: {
        parse_ms: parseMs,
        lower_ms: lowerMs,
        total_ms: parseMs + lowerMs,
        cache_hit: false,
      },
    });
  }

  const evalStart = performance.now();
  let result;
  try {
    result = runtime.evaluate(coreIr, { displayLastExpr: true });
  } catch (e) {
    const evalMs = performance.now() - evalStart;
    const message = "eval error: " + e.message;
    return resultEnvelope({
      ok: false,
      error: message,
      stdout: runtime.stdout.join(""),
      diagnostics: [
        diagnosticRecord({
          phase: "eval",
          message,
          capability: "js-core-runtime.eval",
          code: e.code || "NOMI-RUNTIME",
        }),
      ],
      timings: {
        parse_ms: parseMs,
        lower_ms: lowerMs,
        eval_ms: evalMs,
        total_ms: parseMs + lowerMs + evalMs,
        cache_hit: false,
      },
    });
  }
  const evalMs = performance.now() - evalStart;

  return resultEnvelope({
    ok: true,
    value: result.value,
    hasValue: result.has_value === true,
    stdout: result.stdout || "",
    stderr: result.stderr || "",
    diagnostics: result.diagnostics || [],
    timings: {
      parse_ms: parseMs,
      lower_ms: lowerMs,
      eval_ms: evalMs,
      total_ms: parseMs + lowerMs + evalMs,
      cache_hit: false,
    },
    bindings: result.bindings || {},
  });
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
