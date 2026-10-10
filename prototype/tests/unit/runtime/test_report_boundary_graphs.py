"""Graph, caller-contract and capacity probes independent of parser output."""

import json
from pathlib import Path
import shutil
import subprocess

import pytest

from prototype.runtime import report_boundary as b


ROOT = Path(__file__).resolve().parents[4]
NODE = shutil.which("node")
RUNTIMES = [
    "python",
    pytest.param(
        "javascript",
        marks=pytest.mark.skipif(NODE is None, reason="node is not installed"),
    ),
]


def graph_probe(runtime, probe):
    if runtime == "python":
        if probe == "encode-cycle":
            value = []
            value.append(value)
            return b.encode_json(value)
        if probe == "encode-shared":
            value = {"x": 1}
            return b.encode_json([value, value])
        if probe == "tree-cycle":
            root = {"kind": "list", "items": []}
            root["items"].append(root)
            return b.decode_data(
                {"schema": "nomi.json-value", "version": 1, "root": root},
                "report-options",
            )
        if probe.startswith("tree-shared"):
            leaf = {"kind": "number", "token": "0"}
            tree = {
                "schema": "nomi.json-value",
                "version": 1,
                "root": {"kind": "list", "items": [leaf, leaf]},
            }
            budget = b.BoundaryBudget(node_limit=2 if probe.endswith("limit") else 3)
            return {
                "result": b.decode_data(tree, "report-options", budget),
                "input_bytes": budget.input_bytes,
            }
        if probe == "detached-rows":
            row = b.parse_json('{"id":"a","name":"Ada","age":20}')["value"]["root"]
            tree = {
                "schema": "nomi.json-value",
                "version": 1,
                "root": {
                    "kind": "map",
                    "entries": [["customers", {"kind": "list", "items": [row, row]}]],
                },
            }
            result = b.decode_data(tree, "report-batch")
            result["value"]["customers"][0]["name"] = "changed"
            return {
                "second": result["value"]["customers"][1]["name"],
                "original": row["entries"][1][1]["value"],
            }
        if probe == "output-aggregate":
            budget = b.BoundaryBudget(output_limit=3)
            return [b.encode_json(0, budget) for _ in range(4)]
        if probe == "caller-contract":
            budget = b.BoundaryBudget()
            refused = []
            for function, args in [
                (b.parse_json, [0]),
                (b.decode_data, [{}, "unknown"]),
                (b.trim_text, [None]),
            ]:
                try:
                    function(*args, budget=budget)
                except (TypeError, ValueError):
                    refused.append(True)
            return {
                "refused": refused,
                "work": budget.work,
                "input_bytes": budget.input_bytes,
            }
        raise AssertionError(probe)
    script = """
const b=require('./prototype/runtime/js/report_boundary.js');
const probe=process.argv[1]; let result;
if(probe==='encode-cycle') { const value=[]; value.push(value); result=b.encodeJson(value); }
if(probe==='encode-shared') { const value={x:1}; result=b.encodeJson([value,value]); }
if(probe==='tree-cycle') { const root={kind:'list',items:[]};root.items.push(root); result=b.decodeData({schema:'nomi.json-value',version:1,root},'report-options'); }
if(probe.startsWith('tree-shared')) { const leaf={kind:'number',token:'0'}; const budget=new b.BoundaryBudget({node_limit:probe.endsWith('limit')?2:3}); const tree={schema:'nomi.json-value',version:1,root:{kind:'list',items:[leaf,leaf]}}; result={result:b.decodeData(tree,'report-options',budget),input_bytes:budget.inputBytes}; }
if(probe==='detached-rows') { const row=b.parseJson('{"id":"a","name":"Ada","age":20}').value.root; const tree={schema:'nomi.json-value',version:1,root:{kind:'map',entries:[['customers',{kind:'list',items:[row,row]}]]}}; const decoded=b.decodeData(tree,'report-batch'); decoded.value.customers[0].name='changed'; result={second:decoded.value.customers[1].name,original:row.entries[1][1].value}; }
if(probe==='output-aggregate') {const budget=new b.BoundaryBudget({output_limit:3});result=Array.from({length:4},()=>b.encodeJson(0,budget));}
if(probe==='caller-contract') {const budget=new b.BoundaryBudget();const refused=[];for(const [f,args] of [[b.parseJson,[0]],[b.decodeData,[{},'unknown']],[b.trimText,[null]]])try{f(...args,budget)}catch(e){refused.push(true)}result={refused,work:budget.work,input_bytes:budget.inputBytes};}
process.stdout.write(JSON.stringify(result));
"""
    completed = subprocess.run(
        [NODE, "-e", script, probe],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
        timeout=15,
    )
    return json.loads(completed.stdout)


@pytest.mark.parametrize("runtime", RUNTIMES)
@pytest.mark.parametrize(
    "probe, code, path",
    [
        ("encode-cycle", "NOMI-ENCODE-CYCLE", [0]),
        ("tree-cycle", "NOMI-VALUE-TREE", [0]),
    ],
)
def test_active_ancestor_reference_is_a_cycle(runtime, probe, code, path):
    result = graph_probe(runtime, probe)
    assert result["complete"] is False
    assert result["errors"][0]["code"] == code
    assert result["errors"][0]["path"] == path


@pytest.mark.parametrize("runtime", RUNTIMES)
def test_shared_acyclic_values_encode_each_occurrence(runtime):
    assert graph_probe(runtime, "encode-shared") == {
        "ok": True,
        "text": '[{"x":1},{"x":1}]',
    }


@pytest.mark.parametrize("runtime", RUNTIMES)
def test_shared_tree_occurrences_count_as_nodes_and_minimal_json_bytes(runtime):
    admitted = graph_probe(runtime, "tree-shared")
    assert admitted["input_bytes"] == 5
    assert admitted["result"]["errors"][0]["code"] == "NOMI-DECODE-TYPE"
    refused = graph_probe(runtime, "tree-shared-limit")
    assert refused["result"]["complete"] is False
    assert refused["result"]["errors"][0]["code"] == "NOMI-BOUNDARY-LIMIT"


@pytest.mark.parametrize("runtime", RUNTIMES)
def test_shared_input_rows_decode_into_independent_fresh_records(runtime):
    assert graph_probe(runtime, "detached-rows") == {"second": "Ada", "original": "Ada"}


@pytest.mark.parametrize("runtime", RUNTIMES)
def test_encoded_output_allowance_is_shared_without_refunds(runtime):
    outcomes = graph_probe(runtime, "output-aggregate")
    assert outcomes[:3] == [{"ok": True, "text": "0"}] * 3
    assert outcomes[3]["errors"][0]["code"] == "NOMI-BOUNDARY-LIMIT"


@pytest.mark.parametrize("runtime", RUNTIMES)
def test_bad_call_types_and_unknown_schemas_do_not_consume_boundary_allowance(runtime):
    assert graph_probe(runtime, "caller-contract") == {
        "refused": [True] * 3,
        "work": 0,
        "input_bytes": 0,
    }


def test_python_foreign_objects_and_structural_subclasses_cannot_borrow_json_status():
    class Foreign(dict):
        pass

    for value in (Foreign(x=1), (1,), lambda: 1, 1.0):
        result = b.encode_json(value)
        assert result["errors"][0]["code"] == "NOMI-ENCODE-TYPE"
