import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")
RUNTIME_JS = ROOT / "web" / "runtime.js"


@pytest.mark.contract
@pytest.mark.frontend
@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_web_runtime_displays_final_expression_value_when_stdout_is_empty():
    completed = subprocess.run(
        [
            NODE,
            "-e",
            (
                "global.window = {};"
                f"const runtime = require({str(RUNTIME_JS)!r});"
                "function assert(condition, message) { if (!condition) throw new Error(message); }"
                "assert(runtime.outputForResult({error: 'boom', output: 'ignored'}) === 'boom', 'error wins');"
                "assert(runtime.outputForResult({output: 'printed\\n', has_value: true, value: 3}) === 'printed\\n', 'stdout wins');"
                "assert(runtime.outputForResult({output: '', has_value: true, value: 3}) === '3', 'numeric value displays');"
                "assert(runtime.outputForResult({has_value: true, value: {a: 1}}) === '{\"a\":1}', 'object value displays');"
                "assert(runtime.outputForResult({}) === '(no output)', 'empty result fallback');"
                "const bindings = runtime.bindingEntries({bindings: {z: 1, a: 2}});"
                "assert(bindings[0][0] === 'a' && bindings[1][0] === 'z', 'bindings sort by name');"
                "const diagnostics = runtime.diagnosticsForResult({error: 'broken'});"
                "assert(diagnostics.length === 1 && diagnostics[0].phase === 'runtime', 'errors become diagnostics');"
                "const timings = runtime.timingEntries({timings: {parse_ms: 1.2, lower_ms: 2.6, eval_ms: 3.4}}, 9);"
                "assert(JSON.stringify(timings) === JSON.stringify([['Parse',1],['Lower',3],['Evaluate',3]]), 'timings normalize');"
            ),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
