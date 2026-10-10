"""Unsupported text prefixes must not silently change values in the browser."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="Node is not installed")
LOWER = """
const fs = require('node:fs');
const parser = require('./prototype/runtime/js/pkg/nomi_parser.js');
parser.initSync({module: fs.readFileSync('./prototype/runtime/js/pkg/nomi_parser_bg.wasm')});
const {lowerRustAstToCoreIr} = require('./prototype/runtime/js/lower_to_core_ir.js');
const source = JSON.parse(fs.readFileSync(0, 'utf8'));
process.stdout.write(JSON.stringify(lowerRustAstToCoreIr(JSON.parse(parser.parse_nomi(source)))));
"""


def lower(source):
    result = subprocess.run([NODE, "-e", LOWER], input=json.dumps(source), cwd=ROOT, capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


@pytest.mark.parametrize("prefix,capability", [
    ("b", "text.bytes-literal"), ("B", "text.bytes-literal"),
    ("br", "text.bytes-literal"), ("Rb", "text.bytes-literal"),
    ("f", "text.formatted-literal"), ("F", "text.formatted-literal"),
    ("rf", "text.formatted-literal"), ("Fr", "text.formatted-literal"),
])
@pytest.mark.parametrize("context", ["print({literal})", "func message():\n    return {literal}\nprint(message())"])
def test_prefix_refusal_keeps_source_and_capability(prefix, capability, context):
    literal = prefix + '"Hello {name}"'
    payload = lower("name = 'Ada'\n" + context.format(literal=literal) + "\n")
    assert payload["diagnosticCount"] == 1
    diagnostic = payload["diagnostics"][0]
    assert diagnostic["phase"] == "lower"
    assert diagnostic["node_type"] == "String"
    assert diagnostic["code"] == "NOMI-UNSUPPORTED-LITERAL"
    assert diagnostic["source_excerpt"] == literal
    assert diagnostic["capability"] == capability


@pytest.mark.parametrize("prefix", ["", "r", "R", "u", "U"])
def test_supported_text_prefixes_still_lower_without_diagnostics(prefix):
    assert lower('print(' + prefix + '"Hello"' + ')\n')["diagnosticCount"] == 0
