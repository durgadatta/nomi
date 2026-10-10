"""Task-oriented sample discovery keeps experimental syntax out of first use."""

import json
from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")
pytestmark = [
    pytest.mark.contract,
    pytest.mark.frontend,
    pytest.mark.skipif(NODE is None, reason="node is not installed"),
]


def presentation(expression):
    script = """
const fs = require('fs'), vm = require('vm');
const context = { window: {}, console, setTimeout, clearTimeout };
vm.createContext(context);
vm.runInContext(fs.readFileSync('web/demos.js', 'utf8'), context);
process.stdout.write(JSON.stringify(vm.runInContext(process.argv[1], context)));
"""
    result = subprocess.run(
        [NODE, "-e", script, expression], cwd=ROOT, capture_output=True,
        text=True, check=True, timeout=10,
    )
    return json.loads(result.stdout)


def test_new_workbench_starts_with_calculation_but_restores_saved_document():
    result = subprocess.run(
        [NODE, "-e", "const d=require('./web/documents.js');"
         "process.stdout.write(JSON.stringify([d.normalizeWorkbenchState(null).active,"
         "d.normalizeWorkbenchState({active:'terse'}).active]));"],
        cwd=ROOT, capture_output=True, text=True, check=True, timeout=10,
    )
    assert json.loads(result.stdout) == ["calculate", "terse"]


def test_learning_groups_order_tasks_before_historical_experiments():
    result = presentation("sampleGroups(["
        "['old',{source:'samples/demo.nomi'}],"
        "['report',{source:'samples/report.nomi'}],"
        "['text',{source:'samples/text_pipeline.nomi.nb'}],"
        "['calculate',{source:'samples/calculate.nomi'}],"
        "['scratch',{local:true}]])"
        ".map(([label, entries]) => [label, entries.map(([key]) => key)])")
    assert result == [
        ["Local", ["scratch"]],
        ["Start here", ["calculate", "report"]],
        ["Data and text", ["text"]],
        ["Experiments", ["old"]],
    ]


def test_all_checkout_samples_have_explicit_learning_status():
    manifest = json.loads((ROOT / "web/manifest.json").read_text())
    result = presentation(
        f"{json.dumps(manifest['samples'])}.map(path => [path, sampleInfo(path)])"
    )
    assert len(result) == 13
    for path, info in result:
        assert info["description"]
        assert info["status"] in {"Prototype", "Experiment"}, path
        assert info["group"] in {"Start here", "Data and text", "Experiments"}
    assert dict(result)["samples/demo.nomi"]["status"] == "Experiment"
    assert dict(result)["samples/calculate.nomi"]["group"] == "Start here"


def test_unknown_sample_is_an_experiment_not_an_implied_supported_lesson():
    info = presentation("sampleInfo('samples/new-form.nomi')")
    assert info["status"] == "Experiment"
    assert info["group"] == "Experiments"


def test_catalog_is_presentation_metadata_and_does_not_duplicate_source():
    assert presentation("Object.values(SAMPLE_CATALOG).every(entry => !('code' in entry))")
