"""Pure document framing/storage/position contracts plus worker diagnostics."""

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


def node(script, *args):
    result = subprocess.run(
        [NODE, "-e", script, *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
        check=True,
    )
    return json.loads(result.stdout)


@pytest.mark.parametrize(
    "source",
    [
        "# header\n\n# %% Named first\n\nprint(1)\n\n# %% Named second\nprint(2)\n",
        "# header\r\n# %% First\r\nprint(1)\r\n\r\n# %% Last\r\n",
        "x = 3\n# %% Uses preamble\nprint(x)\n",
        "# %% Blank",
        "print('plain')\n",
    ],
)
def test_notebook_framing_roundtrips_exact_source(source):
    result = node(
        "const d=require('./web/documents.js'); const p=d.splitNotebookDocument(process.argv[1]);process.stdout.write(JSON.stringify({source:d.joinNotebookDocument(p.preamble,p.cells),cells:p.cells}));",
        source,
    )
    assert result["source"] == source
    if source.startswith("x ="):
        assert result["cells"][0]["title"] == "Preamble"


def test_editing_after_eof_marker_inserts_a_required_line_boundary():
    assert (
        node(
            "const d=require('./web/documents.js'); const p=d.splitNotebookDocument('# %% Blank');p.cells[0].code='print(1)'; process.stdout.write(JSON.stringify(d.joinNotebookDocument(p.preamble,p.cells)));"
        )
        == "# %% Blank\nprint(1)"
    )


def test_storage_shape_is_validated_without_replacing_valid_drafts():
    result = node(
        "const d=require('./web/documents.js');const p=d.normalizeWorkbenchState({drafts:{terse:'print(1)',bad:42},scratchDocs:{'scratch-1':{title:'local.nomi'},'__proto__':{title:'bad'}},sidebarWidth:NaN,resultPane:999});process.stdout.write(JSON.stringify(p));"
    )
    assert result["drafts"] == {"terse": "print(1)"}
    assert result["scratchDocs"] == {"scratch-1": {"title": "local.nomi"}}
    assert result["sidebarWidth"] == 272
    assert result["resultPane"] == 68


def test_diagnostic_codepoint_columns_convert_to_editor_utf16():
    result = node(
        r"const d=require('./web/documents.js'); process.stdout.write(JSON.stringify([d.diagnosticPosition({span:{line:1,column:3,coordinate_unit:'unicode-code-point'}},'x\ud83d\ude00!'),d.diagnosticPosition({span:{line:9,column:1}},'x'),d.diagnosticPosition({span:{line:1,column:9,coordinate_unit:'unicode-code-point'}},'x')]));"
    )
    assert result == [{"lineNumber": 1, "column": 4}, None, None]


def test_worker_converts_rust_utf8_offsets_without_inventing_locations():
    result = node(
        r"const fs=require('fs'),vm=require('vm'); const c={self:{},TextEncoder,TextDecoder};vm.createContext(c);vm.runInContext(fs.readFileSync('./prototype/runtime/js/worker.js','utf8'),c);process.stdout.write(JSON.stringify([c.parseErrorLocation('unexpected at byte 5','x\ud83d\ude00!'),c.parseErrorLocation('unknown','x')]));"
    )
    assert result[0]["span"] == {
        "line": 1,
        "column": 4,
        "byte_offset": 5,
        "coordinate_unit": "utf16-code-unit",
    }
    assert result[1] == {}
