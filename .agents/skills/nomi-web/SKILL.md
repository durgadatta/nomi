---
name: nomi-web
description: Work with the Nomi web playground — Rust/WASM parser worker, JS runtime, legacy Pyodide bridge, Monaco editor, manifest, deployment.
compatibility: deepseek
---

For the interactive experience target, see `docs/design/industrial.md` and the
diagnostic/explanation convergence in `docs/research/convergences.md`.

For a registered feature, run `python3 -m tools.design_passes show <id>` and
read its focused target and bridge. Do not expose target-only syntax in the
playground until parser payload, JavaScript/Pyodide behavior, diagnostics, and
manifest checks meet the packet gate.

## Feature Work Contract

When exposing syntax or runtime behavior in the playground, connect it to the
feature owner, layer/status, normal form or backend target, docs/spec surface,
focused tests, and inspection surface. Future feature toggles should come from
feature profiles or capability metadata, not one-off browser-only switches.

## Files
- `web/index.html` — Monaco Editor shell and notebook controls
- `web/app.js` — starts the browser worker and wires runtime request/response
- `prototype/runtime/js/worker.js` — Rust/WASM parser + JS Core Runtime worker
- `prototype/runtime/js/lower_to_core_ir.js` — Rust AST JSON to Core IR JSON lowerer
- `prototype/runtime/js/core_runtime.js` — JavaScript Core Runtime over serialized Core IR JSON
- `web/nomi_web.py` — legacy Pyodide bridge: loads prototype from manifest, provides run_nomi()
- `web/manifest.json` — Auto-generated file list (run `scripts/make_web.py`)
- `scripts/make_web.py` — Walks prototype/, writes manifest.json
- `scripts/launch_web.py` — Build manifest + start server + open browser

## Local testing
```bash
python3 scripts/launch_web.py
# or
python3 -m http.server 8080 → http://localhost:8080/web/
# JS/WASM execution is the current browser default.
```

## Deployment
- GitHub Pages: Settings → Pages → main branch → / (root)
- URL: https://<user>.github.io/nomi/web/
- No build step needed — static files + Pyodide CDN + Monaco CDN
- `.nojekyll` prevents Jekyll processing

## Adding files
When adding new `.py` files to `prototype/` or new runtime modules imported by
Pyodide:
```bash
python3 scripts/make_web.py    # regenerates manifest.json
python3 scripts/make_web.py --check
git add web/manifest.json       # commit the updated manifest
```

## Monaco language config
The Monarch tokenizer in `index.html` mirrors `tools/vscode/nomi/syntaxes/nomi.tmLanguage.json`.
To add syntax highlighting to the web IDE, update both:
1. `tools/vscode/nomi/syntaxes/nomi.tmLanguage.json` (VS Code, TextMate format)
2. `web/index.html` → `setMonarchTokensProvider("nomi", ...)` (web, Monarch format)
