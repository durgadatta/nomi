#!/usr/bin/env bash
# Run the JS/WASM pipeline end-to-end tests.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"

exec node "$ROOT/prototype/runtime/js/test_pipeline.js"
