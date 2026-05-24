import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def test_wasm_parser_build_metadata_is_fresh():
    completed = subprocess.run(
        [str(ROOT / "scripts" / "build_wasm.sh"), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "nomi_parser_build.json is up to date" in completed.stdout
