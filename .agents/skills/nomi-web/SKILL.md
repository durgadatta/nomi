---
name: nomi-web
description: Work with the Nomi web playground — Pyodide bridge, Monaco editor, manifest, deployment.
compatibility: deepseek
---

For the interactive experience design rationale, see
`docs/research/interactive_explanation_deep_dive.md` and
`docs/research/ai_readable_semantics_deep_dive.md`.

## Files
- `web/index.html` — Monaco Editor with Nomi language definition, Pyodide init, run button
- `web/nomi_web.py` — Pyodide bridge: loads prototype from manifest, provides run_nomi()
- `web/manifest.json` — Auto-generated file list (run `scripts/make_web.py`)
- `scripts/make_web.py` — Walks prototype/, writes manifest.json
- `scripts/launch_web.py` — Build manifest + start server + open browser

## Local testing
```bash
python3 scripts/launch_web.py
# or
python3 -m http.server 8080 → http://localhost:8080/web/
```

## Deployment
- GitHub Pages: Settings → Pages → main branch → / (root)
- URL: https://<user>.github.io/nomi/web/
- No build step needed — static files + Pyodide CDN + Monaco CDN
- `.nojekyll` prevents Jekyll processing

## Adding files
When adding new .py files to prototype/:
```bash
python3 scripts/make_web.py    # regenerates manifest.json
git add web/manifest.json       # commit the updated manifest
```

## Monaco language config
The Monarch tokenizer in `index.html` mirrors `tools/vscode/nomi/syntaxes/nomi.tmLanguage.json`.
To add syntax highlighting to the web IDE, update both:
1. `tools/vscode/nomi/syntaxes/nomi.tmLanguage.json` (VS Code, TextMate format)
2. `web/index.html` → `setMonarchTokensProvider("nomi", ...)` (web, Monarch format)
