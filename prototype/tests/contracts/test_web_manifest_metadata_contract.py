import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "web" / "manifest.json"
METADATA = ROOT / "web" / "manifest_metadata.json"


def test_web_manifest_metadata_matches_manifest():
    manifest_text = MANIFEST.read_text(encoding="utf-8")
    manifest = json.loads(manifest_text)
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))

    assert metadata["schema"] == "nomi.web-manifest-metadata"
    assert metadata["version"] == 1
    assert metadata["generated_by"] == "scripts/make_web.py"
    assert metadata["file_count"] == len(manifest["files"])
    assert metadata["sample_count"] == len(manifest["samples"])
    assert metadata["manifest_digest"] == hashlib.sha256(
        manifest_text.encode("utf-8")
    ).hexdigest()


def test_web_manifest_and_metadata_are_fresh():
    completed = subprocess.run(
        ["python3", str(ROOT / "scripts" / "make_web.py"), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "manifest.json is up to date" in completed.stdout
