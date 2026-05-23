#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"
CRATE_DIR="$ROOT/prototype/parser/backends/rust_fast_ast"
OUT_DIR="$ROOT/web/pkg"

mkdir -p "$OUT_DIR"

echo "Building WASM parser..."
cd "$CRATE_DIR"
cargo build --release --target wasm32-unknown-unknown

echo "Generating JS bindings..."
wasm-bindgen \
  --target web \
  --out-dir "$OUT_DIR" \
  --out-name nomi_parser \
  "$CRATE_DIR/target/wasm32-unknown-unknown/release/nomi_rust_fast_ast.wasm"

echo "WASM parser built:"
ls -lh "$OUT_DIR/nomi_parser_bg.wasm" "$OUT_DIR/nomi_parser.js"
