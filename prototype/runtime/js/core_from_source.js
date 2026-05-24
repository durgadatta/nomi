#!/usr/bin/env node
// Parse Nomi source with the Rust/WASM parser and print JS-lowered Core IR JSON.

"use strict";

const fs = require("fs");
const path = require("path");

const JS_DIR = __dirname;

const wasmBytes = fs.readFileSync(path.join(JS_DIR, "pkg", "nomi_parser_bg.wasm"));
const { initSync, parse_nomi } = require(path.join(JS_DIR, "pkg", "nomi_parser.js"));
const { lowerRustAstToCoreIr } = require(path.join(JS_DIR, "lower_to_core_ir.js"));

initSync({ module: wasmBytes });

const source = fs.readFileSync(0, "utf8");
const rustAst = JSON.parse(parse_nomi(source));
const coreIr = lowerRustAstToCoreIr(rustAst);
process.stdout.write(`${JSON.stringify(coreIr, null, 2)}\n`);
