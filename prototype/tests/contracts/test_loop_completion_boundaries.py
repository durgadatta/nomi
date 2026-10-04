"""Portable loop completion distinguishes exhaustion from an early break."""

import ast
import contextlib
import io
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from prototype.runtime.backends.core_runtime import CoreRuntimeEvaluator
from prototype.syntax.core import lower_python_ast_to_core
from prototype.syntax.core_json import core_to_json

ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")


@pytest.mark.parametrize("backend", ["core", "js", "wasm-js"])
@pytest.mark.parametrize(
    "items,body,expected",
    [
        ("[]", "pass", "done\nafter\n"),
        ("[1, 2]", "pass", "done\nafter\n"),
        ("[1, 2]", "continue", "done\nafter\n"),
        ("[1, 2]", "break", "after\n"),
    ],
)
def test_for_else_runs_on_normal_exhaustion_not_only_empty_input(
    backend, items, body, expected
):
    source = (
        f"for item in {items}:\n    {body}\nelse:\n    print('done')\nprint('after')\n"
    )
    assert_stdout(backend, source, expected)


@pytest.mark.parametrize("backend", ["core", "js", "wasm-js"])
def test_while_else_survives_source_lowering(backend):
    assert_stdout(
        backend, "while False:\n    pass\nelse:\n    print('done')\n", "done\n"
    )


def assert_stdout(backend, source, expected):
    tree = ast.parse(source)
    core = lower_python_ast_to_core(tree)
    if backend == "core":
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            CoreRuntimeEvaluator().evaluate(core)
        assert output.getvalue() == expected
    else:
        if NODE is None:
            pytest.skip("node unavailable")
        script = """
const fs = require('node:fs');
const {CoreRuntime} = require('./prototype/runtime/js/core_runtime.js');
const input = fs.readFileSync(0, 'utf8');
let payload;
if (process.argv[1] === 'wasm-js') {
  const parser = require('./prototype/runtime/js/pkg/nomi_parser.js');
  parser.initSync({module: fs.readFileSync('./prototype/runtime/js/pkg/nomi_parser_bg.wasm')});
  const {lowerRustAstToCoreIr} = require('./prototype/runtime/js/lower_to_core_ir.js');
  payload = lowerRustAstToCoreIr(JSON.parse(parser.parse_nomi(input)));
} else {
  payload = JSON.parse(input);
}
process.stdout.write(JSON.stringify(new CoreRuntime().evaluate(payload)));
"""
        result = subprocess.run(
            [NODE, "-e", script, backend],
            input=source if backend == "wasm-js" else core_to_json(core),
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        assert json.loads(result.stdout)["stdout"] == expected
