#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"
CRATE_DIR="$ROOT/prototype/parser/backends/rust_fast_ast"
OUT_DIR="$ROOT/prototype/runtime/js/pkg"
METADATA_PATH="$OUT_DIR/nomi_parser_build.json"

MODE="${1:-build}"

source_hash() {
  python3 - "$CRATE_DIR" <<'PY'
import hashlib
import sys
from pathlib import Path

crate_dir = Path(sys.argv[1])
paths = [
    crate_dir / "Cargo.toml",
    crate_dir / "Cargo.lock",
    *sorted((crate_dir / "src").glob("*.rs")),
]
digest = hashlib.sha256()
for path in paths:
    digest.update(str(path.relative_to(crate_dir)).encode("utf-8"))
    digest.update(b"\0")
    digest.update(path.read_bytes())
    digest.update(b"\0")
print(digest.hexdigest())
PY
}

write_metadata() {
  local hash
  hash="$(source_hash)"
  python3 - "$METADATA_PATH" "$hash" <<'PY'
import json
import subprocess
import sys
from pathlib import Path

metadata_path = Path(sys.argv[1])
source_hash = sys.argv[2]

def version(command):
    try:
        return subprocess.check_output(command, text=True).strip()
    except Exception:
        return "unknown"

payload = {
    "schema": "nomi.wasm-parser-build",
    "version": 1,
    "source_hash": source_hash,
    "crate": "prototype/parser/backends/rust_fast_ast",
    "target": "wasm32-unknown-unknown",
    "wasm_bindgen": version(["wasm-bindgen", "--version"]),
    "outputs": [
        "nomi_parser.js",
        "nomi_parser_bg.wasm",
        "nomi_parser_bg.wasm.d.ts",
        "nomi_parser.d.ts",
        "nomi_parser_worker.js",
        "nomi_parser_worker_bg.wasm",
        "nomi_parser_worker_bg.wasm.d.ts",
        "nomi_parser_worker.d.ts",
    ],
}
metadata_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
PY
}

check_metadata() {
  python3 - "$OUT_DIR" "$METADATA_PATH" "$(source_hash)" <<'PY'
import json
import sys
from pathlib import Path

out_dir = Path(sys.argv[1])
metadata_path = Path(sys.argv[2])
current_hash = sys.argv[3]

required = [
    "nomi_parser.js",
    "nomi_parser_bg.wasm",
    "nomi_parser_worker.js",
    "nomi_parser_worker_bg.wasm",
]
missing = [name for name in required if not (out_dir / name).exists()]
if missing:
    raise SystemExit(f"missing WASM parser output(s): {', '.join(missing)}")
if not metadata_path.exists():
    raise SystemExit(
        "missing nomi_parser_build.json; run scripts/build_wasm.sh to generate it"
    )

payload = json.loads(metadata_path.read_text(encoding="utf-8"))
if payload.get("schema") != "nomi.wasm-parser-build":
    raise SystemExit("unexpected WASM parser metadata schema")
if payload.get("source_hash") != current_hash:
    raise SystemExit(
        "WASM parser output is stale for rust_fast_ast sources; "
        "run scripts/build_wasm.sh"
    )

for name in payload.get("outputs", ()):
    if not (out_dir / name).exists():
        raise SystemExit(f"metadata output is missing: {name}")

print(f"{metadata_path} is up to date ({len(payload.get('outputs', ()))} outputs)")
PY
}

mkdir -p "$OUT_DIR"

if [[ "$MODE" == "--check" ]]; then
  check_metadata
  exit 0
fi

if [[ "$MODE" != "build" ]]; then
  echo "usage: scripts/build_wasm.sh [--check]" >&2
  exit 2
fi

echo "Building WASM parser..."
cd "$CRATE_DIR"
cargo build --release --target wasm32-unknown-unknown

echo "Generating JS bindings (web target)..."
wasm-bindgen \
  --target web \
  --out-dir "$OUT_DIR" \
  --out-name nomi_parser \
  "$CRATE_DIR/target/wasm32-unknown-unknown/release/nomi_rust_fast_ast.wasm"

echo "Generating JS bindings (no-modules target for workers)..."
wasm-bindgen \
  --target no-modules \
  --out-dir "$OUT_DIR" \
  --out-name nomi_parser_worker \
  "$CRATE_DIR/target/wasm32-unknown-unknown/release/nomi_rust_fast_ast.wasm"

echo "WASM parser built:"
ls -lh "$OUT_DIR/nomi_parser_bg.wasm" "$OUT_DIR/nomi_parser.js" "$OUT_DIR/nomi_parser_worker.js"
write_metadata
echo "Wrote $METADATA_PATH"
