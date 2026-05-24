"""Generate web/manifest.json for the browser playground.

Run this after adding, removing, or renaming runtime `.py` or `.lark` files
under prototype/.
"""

import argparse
import difflib
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROTOTYPE_DIR = ROOT / "prototype"
SAMPLES_DIR = ROOT / "samples"
WEB_DIR = ROOT / "web"
MANIFEST_PATH = WEB_DIR / "manifest.json"
METADATA_PATH = WEB_DIR / "manifest_metadata.json"
RUNTIME_SUFFIXES = {".py", ".lark"}
SAMPLE_SUFFIXES = {".nomi", ".nomi.nb"}
IGNORED_PARTS = {"__pycache__", "tests", "archive"}


def should_include(path: Path) -> bool:
    if not path.is_file() or path.suffix not in RUNTIME_SUFFIXES:
        return False
    if any(part in IGNORED_PARTS for part in path.parts):
        return False
    return "backup" not in str(path)


def _runtime_files():
    return sorted(
        path for path in PROTOTYPE_DIR.rglob("*") if should_include(path)
    )


def build_manifest() -> dict:
    files = [str(path.relative_to(ROOT)) for path in _runtime_files()]
    samples = [
        str(path.relative_to(ROOT))
        for path in sorted(SAMPLES_DIR.rglob("*"))
        if path.is_file() and (path.suffix in SAMPLE_SUFFIXES or str(path).endswith(".nomi.nb"))
    ]
    return {"files": files, "samples": samples}


def build_metadata(manifest: dict) -> dict:
    rendered_manifest = json.dumps(manifest, indent=2) + "\n"
    return {
        "schema": "nomi.web-manifest-metadata",
        "version": 1,
        "generated_by": "scripts/make_web.py",
        "runtime_profile": "browser-wasm-js",
        "file_count": len(manifest["files"]),
        "sample_count": len(manifest["samples"]),
        "manifest_digest": hashlib.sha256(
            rendered_manifest.encode("utf-8")
        ).hexdigest(),
    }


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
    metadata = build_metadata(manifest)
    rendered = json.dumps(manifest, indent=2) + "\n"
    rendered_metadata = json.dumps(metadata, indent=2, sort_keys=True) + "\n"

    if args.check:
        current = MANIFEST_PATH.read_text() if MANIFEST_PATH.exists() else ""
        current_metadata = (
            METADATA_PATH.read_text() if METADATA_PATH.exists() else ""
        )
        failed = False
        if current != rendered:
            diff = difflib.unified_diff(
                current.splitlines(),
                rendered.splitlines(),
                fromfile=str(MANIFEST_PATH),
                tofile=f"{MANIFEST_PATH} (generated)",
                lineterm="",
            )
            print("\n".join(diff))
            failed = True
        if current_metadata != rendered_metadata:
            diff = difflib.unified_diff(
                current_metadata.splitlines(),
                rendered_metadata.splitlines(),
                fromfile=str(METADATA_PATH),
                tofile=f"{METADATA_PATH} (generated)",
                lineterm="",
            )
            print("\n".join(diff))
            failed = True
        if failed:
            return 1
        print(
            f"{MANIFEST_PATH} is up to date "
            f"({len(manifest['files'])} runtime files, {len(manifest['samples'])} samples)"
        )
        return 0

    MANIFEST_PATH.write_text(rendered)
    METADATA_PATH.write_text(rendered_metadata)
    print(
        f"Wrote {len(manifest['files'])} runtime files and "
        f"{len(manifest['samples'])} samples to {MANIFEST_PATH} "
        f"and {METADATA_PATH}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
