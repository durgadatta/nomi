#!/usr/bin/env node
// End-to-end test for the JS/WASM pipeline (parser → lowerer → runtime).
//
// Verifies:
//   1. WASM parser can parse all .nomi sample files
//   2. JS lowerer produces 0 diagnostics for demo_terse.nomi
//   3. Full pipeline produces correct output for demo_terse.nomi
//   4. comprehensive.nomi parses and lowers (may have diagnostics)

"use strict";

const fs = require("fs");
const path = require("path");

const WEB_DIR = path.dirname(__filename);
const ROOT = path.dirname(WEB_DIR);
const SAMPLES_DIR = path.join(ROOT, "samples");

let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    console.log(`  PASS  ${name}`);
    passed++;
  } catch (e) {
    console.log(`  FAIL  ${name}: ${e.message}`);
    failed++;
  }
}

function assert(condition, message) {
  if (!condition) throw new Error(message || "assertion failed");
}

// ── Load WASM parser ─────────────────────────────────────────────────────

const wasmBytes = fs.readFileSync(path.join(WEB_DIR, "pkg", "nomi_parser_bg.wasm"));
const { initSync, parse_nomi } = require(path.join(WEB_DIR, "pkg", "nomi_parser.js"));
initSync({ module: wasmBytes });

// ── Load lowerer and runtime ──────────────────────────────────────────────

const { lowerRustAstToCoreIr } = require(path.join(WEB_DIR, "lower_to_core_ir.js"));
const { evaluateCorePayload } = require(path.join(WEB_DIR, "core_runtime.js"));

// ── Helper ────────────────────────────────────────────────────────────────

function parseAndLower(source) {
  const json = parse_nomi(source);
  const rustAst = JSON.parse(json);
  return lowerRustAstToCoreIr(rustAst);
}

// ── Test 1: WASM parser can parse all sample files ────────────────────────

console.log("\nParse acceptance:");
for (const entry of fs.readdirSync(SAMPLES_DIR, { withFileTypes: true })) {
  if (!entry.name.endsWith(".nomi") || entry.name.endsWith(".nomi.nb")) continue;
  test(`parse ${entry.name}`, () => {
    const source = fs.readFileSync(path.join(SAMPLES_DIR, entry.name), "utf8");
    const json = parse_nomi(source);
    const ast = JSON.parse(json);
    assert(ast.type === "Module", "expected Module root");
    assert(Array.isArray(ast.body), "expected body array");
  });
}

// ── Test 2: demo_terse.nomi → 0 diagnostics ──────────────────────────────

console.log("\nLowering diagnostics:");
const demoSource = fs.readFileSync(path.join(SAMPLES_DIR, "demo_terse.nomi"), "utf8");
const demoCoreIr = parseAndLower(demoSource);
test("demo_terse.nomi → 0 diagnostics", () => {
  assert(demoCoreIr.diagnosticCount === 0, `expected 0 diagnostics, got ${demoCoreIr.diagnosticCount}`);
  assert(demoCoreIr.schema === "nomi.core-ir", "expected nomi.core-ir schema");
  assert(demoCoreIr.version === 1, "expected version 1");
  assert(demoCoreIr.root.type === "Module", "expected Module root");
});

// ── Test 3: Full pipeline outputs correct values ──────────────────────────

console.log("\nEval correctness:");
test("demo_terse.nomi eval", () => {
  const result = evaluateCorePayload(demoCoreIr, { displayLastExpr: true });
  const lines = result.stdout.trim().split("\n");
  assert(lines[0] === "Hello, Nomi", `line 0: ${lines[0]}`);
  assert(lines[1] === "120", `line 1: ${lines[1]}`);
  assert(lines[2] === "two", `line 2: ${lines[2]}`);
  assert(lines[3] === "anonymous", `line 3: ${lines[3]}`);
  assert(lines[4] === "55", `line 4: ${lines[4]}`);
});

// ── Test 4: comprehensive.nomi parses and lowers ──────────────────────────

test("comprehensive.nomi parse + lower", () => {
  const source = fs.readFileSync(path.join(SAMPLES_DIR, "comprehensive.nomi"), "utf8");
  const json = parse_nomi(source);
  const ast = JSON.parse(json);
  assert(ast.type === "Module", "expected Module root");
  assert(ast.body.length > 50, `expected many body entries, got ${ast.body.length}`);
  const coreIr = lowerRustAstToCoreIr(ast);
  assert(coreIr.schema === "nomi.core-ir", "expected nomi.core-ir schema");
  assert(coreIr.diagnosticCount === 0, `expected 0 diagnostics, got ${coreIr.diagnosticCount}`);
});

test("comprehensive.nomi eval", () => {
  const source = fs.readFileSync(path.join(SAMPLES_DIR, "comprehensive.nomi"), "utf8");
  const coreIr = parseAndLower(source);
  const result = evaluateCorePayload(coreIr, { displayLastExpr: true });
  assert(!result.error, `eval error: ${result.error}`);
  const lines = result.stdout.trim().split("\n");
  assert(lines.length > 190, `expected >190 output lines, got ${lines.length}`);
});

// ── Test 5: Error handling ────────────────────────────────────────────────

console.log("\nEdge cases:");
test("parse empty string", () => {
  const json = parse_nomi("");
  const ast = JSON.parse(json);
  assert(ast.type === "Module", "expected Module root");
  assert(ast.body.length === 0, "expected empty body");
});

test("lower empty module", () => {
  const coreIr = parseAndLower("");
  assert(coreIr.diagnosticCount === 0, "expected 0 diagnostics");
  const result = evaluateCorePayload(coreIr, { displayLastExpr: true });
  assert(result.stdout === "", "expected no output");
});

test("parse syntax error throws", () => {
  let threw = false;
  try {
    parse_nomi("func @@@ invalid");
  } catch (_) {
    threw = true;
  }
  assert(threw, "expected parse error to throw");
});

// ── Summary ───────────────────────────────────────────────────────────────

console.log(`\n${passed} passed, ${failed} failed`);
if (failed > 0) process.exit(1);
