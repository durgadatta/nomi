"""User names must be data, not inherited JavaScript object behavior."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from prototype.runtime import create_session

ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")
pytestmark = [
    pytest.mark.contract,
    pytest.mark.skipif(NODE is None, reason="node unavailable"),
]


def run_node(script, payload):
    completed = subprocess.run(
        [NODE, "-e", script, json.dumps(payload)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    return json.loads(completed.stdout)


@pytest.mark.parametrize(
    "name", ["__proto__", "constructor", "toString", "hasOwnProperty"]
)
def test_user_binding_names_survive_export(name):
    payload = json.loads(
        create_session().core_json(source=f"{name} = {{'value': 7}}\n")
    )
    result = run_node(
        "const {CoreRuntime}=require('./prototype/runtime/js/core_runtime.js'); process.stdout.write(JSON.stringify(new CoreRuntime().evaluate(JSON.parse(process.argv[1]))));",
        payload,
    )
    assert result["bindings"][name] == {"value": 7}


def test_mapping_transport_keeps_special_text_keys():
    source = "payload = {'__proto__': {'safe': 1}, 'constructor': 2, 'toString': 3}\n"
    payload = json.loads(create_session().core_json(source=source))
    result = run_node(
        "const {CoreRuntime}=require('./prototype/runtime/js/core_runtime.js'); process.stdout.write(JSON.stringify(new CoreRuntime().evaluate(JSON.parse(process.argv[1]))));",
        payload,
    )
    assert result["bindings"]["payload"] == {
        "__proto__": {"safe": 1},
        "constructor": 2,
        "toString": 3,
    }


@pytest.mark.parametrize("constructor", [False, True])
def test_nominal_fields_keep_special_names(constructor):
    fields = [["__proto__", {"type": "Literal", "value": None if constructor else 7}]]
    body = [
        {
            "type": "Bind",
            "name": "record",
            "value": {"type": "ConstructData", "name": "Record", "fields": fields},
        }
    ]
    if constructor:
        body.append(
            {
                "type": "Bind",
                "name": "record",
                "value": {
                    "type": "Call",
                    "func": {"type": "Load", "name": "Record"},
                    "args": [{"type": "Literal", "value": 7}],
                },
            }
        )
    result = run_node(
        "const {CoreRuntime}=require('./prototype/runtime/js/core_runtime.js'); process.stdout.write(JSON.stringify(new CoreRuntime().evaluate(JSON.parse(process.argv[1]))));",
        {"type": "Module", "body": body},
    )
    assert result["bindings"]["record"] == {"Record": {"__proto__": 7}}


def test_missing_nominal_field_cannot_read_an_inherited_host_method():
    script = """
const {CoreRuntime} = require('./prototype/runtime/js/core_runtime.js');
const runtime = new CoreRuntime();
runtime.globalFrame.bind('record', {kind: 'data', name: 'Record', fields: {own: {kind: 'int', value: 7}}});
try { runtime.eval({type: 'GetField', object_: {type: 'Load', name: 'record'}, field: 'toString'}); process.stdout.write('false'); }
catch (_) { process.stdout.write('true'); }
"""
    assert run_node(script, {}) is True


def test_legacy_map_conversion_preserves_special_keys():
    script = """
const fs = require('node:fs'), vm = require('node:vm');
const context = {self: {}, Map}; vm.createContext(context);
vm.runInContext(fs.readFileSync('./web/worker_pyodide.js', 'utf8'), context);
const result = context.convertPyValue(new Map([['__proto__', {safe: 1}], ['constructor', 2]]));
process.stdout.write(JSON.stringify(result));
"""
    assert run_node(script, {}) == {"__proto__": {"safe": 1}, "constructor": 2}
