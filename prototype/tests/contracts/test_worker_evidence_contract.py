"""Skipped phases and uncaptured bindings are not zero/empty observations."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")
pytestmark = [
    pytest.mark.contract,
    pytest.mark.skipif(NODE is None, reason="node unavailable"),
]


@pytest.mark.parametrize("phase", ["parse", "lower", "eval", "success"])
def test_worker_only_reports_captured_phase_facts(phase):
    script = """
const fs = require('node:fs'), vm = require('node:vm');
const phase = process.argv[1]; let tick = 0;
const context = {self: {}, performance: {now: () => ++tick},
  wasm_bindgen: {parse_nomi: () => {if (phase === 'parse') throw new Error('parse failed'); return '{}';}}
};
context.self.NomiCoreLowerer = {lowerRustAstToCoreIr: () => ({
  diagnosticCount: phase === 'lower' ? 1 : 0,
  diagnostics: phase === 'lower' ? [{phase: 'lower', message: 'lower failed'}] : []
})};
vm.createContext(context);
vm.runInContext(fs.readFileSync('./prototype/runtime/js/worker.js', 'utf8'), context);
vm.runInContext(String.raw`runtime = {stdout: ['before\\n'], evaluate: () => {
  if (${JSON.stringify(phase)} === 'eval') throw new Error('eval failed');
  return {bindings: {}, stdout: ''};
}}`, context);
process.stdout.write(JSON.stringify(context.runWithWasmJs('source')));
"""
    completed = subprocess.run(
        [NODE, "-e", script, phase],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    result = json.loads(completed.stdout)
    phases = {
        key for key in result["timings"] if key in {"parse_ms", "lower_ms", "eval_ms"}
    }
    assert (
        phases
        == {
            "parse": {"parse_ms"},
            "lower": {"parse_ms", "lower_ms"},
            "eval": {"parse_ms", "lower_ms", "eval_ms"},
            "success": {"parse_ms", "lower_ms", "eval_ms"},
        }[phase]
    )
    assert result["bindings"] == ({} if phase == "success" else None)
    if phase == "eval":
        assert result["stdout"] == "before\n"
