import re
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")
PIPELINE_SCRIPT = ROOT / "prototype" / "runtime" / "js" / "test_pipeline.js"
WASM_PARSER = ROOT / "prototype" / "runtime" / "js" / "pkg" / "nomi_parser_bg.wasm"


@pytest.mark.skipif(NODE is None, reason="node is not installed")
@pytest.mark.skipif(not WASM_PARSER.exists(), reason="WASM parser artifact is missing")
def test_wasm_js_pipeline_smoke_contract():
    completed = subprocess.run(
        [NODE, str(PIPELINE_SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert re.search(r"\b\d+ passed, 0 failed\b", completed.stdout)
