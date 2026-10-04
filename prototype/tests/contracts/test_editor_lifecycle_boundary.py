"""Bound the pinned Monaco WordHighlighter disposal workaround at its owner."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")
pytestmark = [
    pytest.mark.contract,
    pytest.mark.frontend,
    pytest.mark.skipif(NODE is None, reason="node is not installed"),
]


@pytest.mark.parametrize("plain", [True, False])
def test_every_editor_creation_disables_only_automatic_occurrence_highlighting(plain):
    script = r"""
const fs = require('fs'), vm = require('vm');
const plain = process.argv[1] === 'true';
let options;
const host = { style: {} };
const editor = {
  layout() {}, focus() {}, addAction() {},
  onDidContentSizeChange() {}, onDidChangeModelContent() {},
  onDidFocusEditorText() {}, onDidChangeCursorPosition() {},
};
const context = {
  window: {}, _cellEditors: [], _cellResults: [],
  document: { querySelector: () => host },
  byId: () => ({ clientHeight: 600, classList: { contains: name => plain && name === 'plain-mode' } }),
  requestAnimationFrame() {},
  monaco: {
    KeyMod: { CtrlCmd: 1, Shift: 2 }, KeyCode: { Enter: 4 },
    editor: { create: (element, configuration) => { options = configuration; return editor; } },
  },
};
vm.createContext(context);
vm.runInContext(fs.readFileSync('./web/cells.js', 'utf8'), context);
context.createEditor(0, 'token = token\n', plain);
process.stdout.write(JSON.stringify({
  automatic: options.occurrencesHighlight,
  selectionEnabled: options.selectionHighlight !== false,
  language: options.language,
  editorCount: context._cellEditors.length,
}));
"""
    result = subprocess.run(
        [NODE, "-e", script, json.dumps(plain)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    assert json.loads(result.stdout) == {
        "automatic": "off",
        "selectionEnabled": True,
        "language": "nomi",
        "editorCount": 1,
    }
