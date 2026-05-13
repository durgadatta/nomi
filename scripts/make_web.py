"""Generate web/manifest.json for the browser playground.

The browser runtime loads the prototype source tree into Pyodide from this
manifest. Run this after adding, removing, or renaming runtime `.py` or `.lark`
files under prototype/.
"""

import argparse
import difflib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROTOTYPE_DIR = ROOT / "prototype"
SAMPLES_DIR = ROOT / "samples"
MANIFEST_PATH = ROOT / "web" / "manifest.json"
RUNTIME_SUFFIXES = {".py", ".lark"}
SAMPLE_SUFFIXES = {".nomi", ".nomi.nb"}
IGNORED_PARTS = {"__pycache__", "tests"}


def should_include(path: Path) -> bool:
    if not path.is_file() or path.suffix not in RUNTIME_SUFFIXES:
        return False
    if any(part in IGNORED_PARTS for part in path.parts):
        return False
    return "backup" not in str(path)


def build_manifest() -> dict:
    files = [
        str(path.relative_to(ROOT))
        for path in sorted(PROTOTYPE_DIR.rglob("*"))
        if should_include(path)
    ]
    samples = [
        str(path.relative_to(ROOT))
        for path in sorted(SAMPLES_DIR.rglob("*"))
        if path.is_file() and (path.suffix in SAMPLE_SUFFIXES or str(path).endswith(".nomi.nb"))
    ]
    return {"files": files, "samples": samples}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if web/manifest.json is out of date without writing it",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = build_manifest()
    rendered = json.dumps(manifest, indent=2) + "\n"

    if args.check:
        current = MANIFEST_PATH.read_text() if MANIFEST_PATH.exists() else ""
        if current != rendered:
            diff = difflib.unified_diff(
                current.splitlines(),
                rendered.splitlines(),
                fromfile=str(MANIFEST_PATH),
                tofile=f"{MANIFEST_PATH} (generated)",
                lineterm="",
            )
            print("\n".join(diff))
            return 1
        print(
            f"{MANIFEST_PATH} is up to date "
            f"({len(manifest['files'])} runtime files, {len(manifest['samples'])} samples)"
        )
        return 0

    MANIFEST_PATH.write_text(rendered)
    print(
        f"Wrote {len(manifest['files'])} runtime files and "
        f"{len(manifest['samples'])} samples to {MANIFEST_PATH}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
