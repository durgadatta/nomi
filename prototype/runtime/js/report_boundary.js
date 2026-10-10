"use strict";

const fail = (kind, code, expected, message, path = []) => ({
  ok: false, kind, errors: [{ code, path, path_text: path.reduce((s, p) => s + (typeof p === "number" ? `[${p}]` : /^[A-Za-z_][A-Za-z_0-9]*$/.test(p) ? `.${p}` : `[${JSON.stringify(p)}]`), "$"), expected, message }], complete: false,
});

class BoundaryBudget {
  constructor(limits = {}) {
    this.inputBytes = 0; this.work = 0; this.outputBytes = 0;
    this.inputLimit = limits.input_bytes_per_call ?? 256 * 1024;
    this.aggregateInputLimit = limits.aggregate_input_bytes ?? 256 * 1024;
    this.workLimit = limits.work ?? 1_000_000;
    this.outputLimit = limits.encoded_bytes_per_run ?? 64 * 1024;
  }
  charge(field, amount, limit) { this[field] += amount; return this[field] <= limit; }
}

function parseJson(text, budget = new BoundaryBudget()) {
  if (typeof text !== "string") return fail("input-format", "NOMI-DECODE-TYPE", "Text", "Provide JSON as Text.");
  const bytes = new TextEncoder().encode(text).length;
  if (bytes > 256 * 1024 || bytes > budget.inputLimit || !budget.charge("inputBytes", bytes, budget.aggregateInputLimit)) return fail("input-format", "NOMI-BOUNDARY-LIMIT", "bounded input bytes", "Input exceeds the configured byte budget.");
  if (!budget.charge("work", Array.from(text).length, budget.workLimit)) return fail("input-format", "NOMI-BOUNDARY-LIMIT", "bounded boundary work", "Boundary processing exceeds the configured work budget.");
  let i = 0, nodes = 0;
  const ws = () => { while ([" ", "\t", "\r", "\n"].includes(text[i])) i++; };
  const str = () => {
    const start = i++;
    while (i < text.length) {
      if (text[i] === "\\") { i += 2; continue; }
      if (text[i++] === '"') {
        const value = JSON.parse(text.slice(start, i));
        if (Array.from(value).some(c => { const n = c.codePointAt(0); return n >= 0xd800 && n <= 0xdfff; })) throw { invalidText: true };
        return value;
      }
    }
    throw { syntax: true };
  };
  const value = (depth = 0) => {
    ws(); if (++nodes > 8192 || depth > 32 || !budget.charge("work", 1, budget.workLimit)) throw { limit: true };
    const c = text[i];
    if (c === '"') return { kind: "text", value: str() };
    if (c === "[") { i++; ws(); const items = []; if (text[i] === "]") { i++; return { kind: "list", items }; } while (true) { items.push(value(depth + 1)); ws(); if (text[i] === "]") { i++; break; } if (text[i++] !== ",") throw { syntax: true }; } return { kind: "list", items }; }
    if (c === "{") { i++; ws(); const entries = [], seen = new Set(); if (text[i] === "}") { i++; return { kind: "map", entries }; } while (true) { ws(); if (text[i] !== '"') throw { syntax: true }; const key = str(); if (seen.has(key)) throw { duplicate: key }; seen.add(key); ws(); if (text[i++] !== ":") throw { syntax: true }; entries.push([key, value(depth + 1)]); ws(); if (text[i] === "}") { i++; break; } if (text[i++] !== ",") throw { syntax: true }; } return { kind: "map", entries }; }
    for (const [token, node] of [["true", { kind: "bool", value: true }], ["false", { kind: "bool", value: false }], ["null", { kind: "null" }]]) if (text.startsWith(token, i)) { i += token.length; return node; }
    const m = text.slice(i).match(/^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/);
    if (m) { i += m[0].length; return { kind: "number", token: m[0] }; }
    throw { syntax: true };
  };
  try {
    ws(); const root = value(); ws(); if (i !== text.length) return fail("input-format", "NOMI-JSON-SYNTAX", "one JSON value", "Remove trailing content after the JSON value.");
    return { ok: true, value: { schema: "nomi.json-value", version: 1, root } };
  } catch (error) {
    if (error.duplicate !== undefined) return fail("input-format", "NOMI-JSON-DUPLICATE-KEY", "unique object key", "Remove the duplicate object key.", [error.duplicate]);
    if (error.invalidText) return fail("input-format", "NOMI-TEXT-INVALID", "Unicode scalar Text", "Replace the lone surrogate with valid Unicode text.");
    if (error.limit) return fail("input-format", "NOMI-BOUNDARY-LIMIT", "bounded value tree", "Input exceeds a structural boundary limit.");
    return fail("input-format", "NOMI-JSON-SYNTAX", "one JSON value", "Correct the JSON syntax.");
  }
}

function decodeData(tree, schemaName, budget = new BoundaryBudget()) {
  if (!tree || Object.keys(tree).sort().join(",") !== "root,schema,version" || tree.schema !== "nomi.json-value" || tree.version !== 1 || !("root" in tree)) return fail("decode", "NOMI-VALUE-TREE", "nomi.json-value version 1", "Provide a supported structural Value tree.");
  const decodeNode = (n, depth = 0) => {
    if (!n || typeof n !== "object" || depth > 32 || !budget.charge("work", 1, budget.workLimit)) throw new Error("tree");
    if (n.kind === "null" && Object.keys(n).sort().join(",") === "kind") return null;
    if (n.kind === "bool" && Object.keys(n).sort().join(",") === "kind,value" && typeof n.value === "boolean") return n.value;
    if (n.kind === "text" && Object.keys(n).sort().join(",") === "kind,value" && typeof n.value === "string" && ![...n.value].some(c => c.codePointAt(0) >= 0xd800 && c.codePointAt(0) <= 0xdfff)) return n.value;
    if (n.kind === "number" && Object.keys(n).sort().join(",") === "kind,token" && typeof n.token === "string" && /^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?$/.test(n.token)) return { $number: n.token };
    if (n.kind === "list" && Object.keys(n).sort().join(",") === "items,kind" && Array.isArray(n.items)) return n.items.map(x => decodeNode(x, depth + 1));
    if (n.kind === "map" && Object.keys(n).sort().join(",") === "entries,kind" && Array.isArray(n.entries)) { const o = Object.create(null); for (const [k, v] of n.entries) { if (typeof k !== "string" || k in o || [...k].some(c => c.codePointAt(0) >= 0xd800 && c.codePointAt(0) <= 0xdfff)) throw new Error("tree"); o[k] = decodeNode(v, depth + 1); } return o; }
    throw new Error("tree");
  };
  let root;
  try { root = decodeNode(tree.root); } catch (_) { return fail("decode", "NOMI-VALUE-TREE", "nomi.json-value version 1", "Provide a supported structural Value tree."); }
  const sourceNode = n => n.kind === "null" ? "null" : n.kind === "bool" ? (n.value ? "true" : "false") : n.kind === "text" ? JSON.stringify(n.value) : n.kind === "number" ? n.token : n.kind === "list" ? `[${n.items.map(sourceNode).join(",")}]` : `{${n.entries.map(([k,v]) => `${JSON.stringify(k)}:${sourceNode(v)}`).join(",")}}`;
  const treeBytes = new TextEncoder().encode(sourceNode(tree.root)).length;
  if (treeBytes > 256 * 1024 || treeBytes > budget.inputLimit || !budget.charge("inputBytes", treeBytes, budget.aggregateInputLimit)) return fail("decode", "NOMI-BOUNDARY-LIMIT", "bounded input bytes", "Input exceeds the configured byte budget.");
  if (!["report-options", "report-batch"].includes(schemaName)) return fail("decode", "NOMI-DECODE-TYPE", "known schema name", "Choose a supported report schema.");
  const errors = []; let truncated = false;
  const add = (code, path, expected, message) => { if (errors.length < 64) errors.push({ ...fail("decode", code, expected, message, path).errors[0] }); else truncated = true; };
  const num = (v, path) => { if (!v || !v.$number || !/^-?(?:0|[1-9][0-9]*)$/.test(v.$number)) { add("NOMI-DECODE-TYPE", path, "integer-form JSON number", "Use an integer-form JSON number for this field."); return null; } const n = BigInt(v.$number); if (n > BigInt(Number.MAX_SAFE_INTEGER)) { add("NOMI-NUMERIC-CAPACITY", path, "Int within backend capacity", "Use a backend that supports this exact integer."); return null; } if (n < 0n) { add("NOMI-DECODE-CONSTRAINT", path, "non-negative Int", "Use an integer greater than or equal to zero."); return null; } return Number(n); };
  const defaults = [];
  if (!root || typeof root !== "object" || Array.isArray(root)) add("NOMI-DECODE-TYPE", [], "object", "Use an object at this boundary.");
  let output;
  if (root && typeof root === "object" && !Array.isArray(root)) {
    const allowed = schemaName === "report-options" ? ["minimum_age"] : ["customers"];
    for (const k of Object.keys(root)) if (!allowed.includes(k)) add("NOMI-DECODE-EXTRA", [k], "declared field", "Remove the unexpected field.");
    if (schemaName === "report-options") {
      if (!("minimum_age" in root)) { defaults.push(["minimum_age"]); root.minimum_age = { $number: "13" }; }
      const age = num(root.minimum_age, ["minimum_age"]); output = age === null ? null : { minimum_age: age };
    } else {
      const rows = root.customers; const customers = [];
      if (!("customers" in root)) add("NOMI-DECODE-MISSING", ["customers"], "required field", "Provide the required field.");
      else if (!Array.isArray(rows)) add("NOMI-DECODE-TYPE", ["customers"], "list", "Use a list for customers.");
      else if (rows.length > 128) add("NOMI-BOUNDARY-LIMIT", ["customers"], "at most 128 customers", "Reduce the number of customers.");
      else rows.forEach((row, i) => {
        const p = ["customers", i]; if (!row || typeof row !== "object" || Array.isArray(row)) { add("NOMI-DECODE-TYPE", p, "object", "Use an object for each customer."); return; }
        for (const k of Object.keys(row)) if (!["id", "name", "age"].includes(k)) add("NOMI-DECODE-EXTRA", [...p, k], "declared field", "Remove the unexpected field.");
        const record = {};
        for (const k of ["id", "name"]) { if (!(k in row)) add("NOMI-DECODE-MISSING", [...p, k], "required field", "Provide the required field."); else if (typeof row[k] !== "string") add("NOMI-DECODE-TYPE", [...p, k], "Text", "Use Text for this field."); else if (!row[k].replace(/^[ \t\r\n\v\f]+|[ \t\r\n\v\f]+$/g, "")) add("NOMI-DECODE-CONSTRAINT", [...p, k], "nonblank Text", "Provide text that is nonblank after the declared trim."); else record[k] = row[k]; }
        if (!("age" in row)) add("NOMI-DECODE-MISSING", [...p, "age"], "required field", "Provide the required field."); else { const age = num(row.age, [...p, "age"]); if (age !== null) record.age = age; }
        if (Object.keys(record).length === 3) customers.push(record);
      });
      output = { customers };
    }
  }
  return errors.length ? { ok: false, kind: "decode", errors, complete: !truncated && !errors.some(e => ["NOMI-BOUNDARY-LIMIT", "NOMI-NUMERIC-CAPACITY"].includes(e.code)) } : { ok: true, value: output, defaults_applied: defaults };
}

function trimText(text) { if (typeof text !== "string") throw new TypeError("trim_text expects Text"); return text.replace(/^[ \t\r\n\v\f]+|[ \t\r\n\v\f]+$/g, ""); }

function encodeJson(value, budget = new BoundaryBudget()) {
  const active = new Set();
  const emit = (v) => {
    if (!budget.charge("work", 1, budget.workLimit)) throw { limit: true };
    if (v === null) return "null";
    if (v === true) return "true"; if (v === false) return "false";
    if (typeof v === "string") { if ([...v].some(c => c.codePointAt(0) >= 0xd800 && c.codePointAt(0) <= 0xdfff)) throw { invalid: true }; return JSON.stringify(v).replace(/\u2028|\u2029/g, m => m); }
    if (typeof v === "number" && Number.isSafeInteger(v)) return String(v);
    if (Array.isArray(v) || (v && Object.getPrototypeOf(v) === Object.prototype)) {
      if (active.has(v)) throw { cycle: true }; active.add(v);
      try { if (Array.isArray(v)) return `[${v.map(emit).join(",")}]`; const keys = Object.keys(v).sort((a,b) => { const aa = Array.from(a, c => c.codePointAt(0)), bb = Array.from(b, c => c.codePointAt(0)); for (let i=0; i<Math.min(aa.length,bb.length); i++) if (aa[i] !== bb[i]) return aa[i]-bb[i]; return aa.length-bb.length; }); return `{${keys.map(k => `${JSON.stringify(k)}:${emit(v[k])}`).join(",")}}`; } finally { active.delete(v); }
    }
    throw { invalidType: true };
  };
  let text;
  try { text = emit(value); } catch (e) {
    if (e.cycle) return fail("encode", "NOMI-ENCODE-CYCLE", "acyclic structural value", "Remove the cycle from this value.");
    if (e.limit) return fail("encode", "NOMI-BOUNDARY-LIMIT", "bounded boundary work", "Boundary processing exceeds the configured work budget.");
    if (e.invalid) return fail("encode", "NOMI-TEXT-INVALID", "Unicode scalar Text", "Replace the lone surrogate with valid Unicode text.");
    return fail("encode", "NOMI-ENCODE-TYPE", "JSON structural value", "Provide only null, Bool, Int, Text, List, and text-keyed Map values.");
  }
  const bytes = new TextEncoder().encode(text).length;
  if (bytes > 65536 || !budget.charge("outputBytes", bytes, budget.outputLimit)) return fail("encode", "NOMI-BOUNDARY-LIMIT", "bounded encoded output", "Encoded output exceeds the configured byte budget.");
  return { ok: true, text };
}

const NomiReportBoundary = { BoundaryBudget, parseJson, decodeData, encodeJson, trimText };
if (typeof module !== "undefined" && module.exports) module.exports = NomiReportBoundary;
if (typeof globalThis !== "undefined") globalThis.NomiReportBoundary = NomiReportBoundary;
