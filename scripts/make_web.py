"""Generate web/manifest.json listing all prototype source files.

Run after adding/removing files in prototype/:
    python3 scripts/make_web.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROTOTYPE_DIR = ROOT / "prototype"

files = []
for p in sorted(PROTOTYPE_DIR.rglob("*")):
    if p.is_file() and p.suffix in (".py", ".lark") and "backup" not in str(p):
        rel = str(p.relative_to(ROOT))
        files.append(rel)

manifest = {"files": files}
out = ROOT / "web" / "manifest.json"
out.write_text(json.dumps(manifest, indent=2))
print(f"Wrote {len(files)} files to {out}")
