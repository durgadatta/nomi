"""Independent boundary counterexamples from the selected report laws."""

import json
from pathlib import Path
import shutil
import subprocess

import pytest

from prototype.runtime import report_boundary as boundary


ROOT = Path(__file__).resolve().parents[4]
NODE = shutil.which("node")
RUNTIMES = [
    "python",
    pytest.param(
        "javascript",
        marks=pytest.mark.skipif(NODE is None, reason="node is not installed"),
    ),
]


def outcome(runtime, operation, value, limits=None):
    limits = limits or {}
    if runtime == "python":
        budget = boundary.BoundaryBudget(**limits)
        if operation == "decode":
            parsed = boundary.parse_json(value, budget)
            if not parsed["ok"]:
                return parsed
            return boundary.decode_data(parsed["value"], "report-batch", budget)
        if operation == "parse":
            return boundary.parse_json(value, budget)
        if operation == "encode":
            return boundary.encode_json(value, budget)
        if operation == "tree":
            return boundary.decode_data(value, "report-options", budget)
        raise AssertionError(operation)
    script = """
const b = require('./prototype/runtime/js/report_boundary.js');
const request = JSON.parse(require('node:fs').readFileSync(0, 'utf8'));
const budget = new b.BoundaryBudget(request.limits);
let result;
if (request.operation === 'parse') result = b.parseJson(request.value, budget);
if (request.operation === 'encode') result = b.encodeJson(request.value, budget);
if (request.operation === 'tree') result = b.decodeData(request.value, 'report-options', budget);
if (request.operation === 'decode') {
 const parsed = b.parseJson(request.value, budget);
 result = parsed.ok ? b.decodeData(parsed.value, 'report-batch', budget) : parsed;
}
process.stdout.write(JSON.stringify(result));
"""
    completed = subprocess.run(
        [NODE, "-e", script],
        cwd=ROOT,
        input=json.dumps({"operation": operation, "value": value, "limits": limits}),
        text=True,
        capture_output=True,
        check=True,
        timeout=15,
    )
    return json.loads(completed.stdout)


@pytest.mark.parametrize("runtime", RUNTIMES)
def test_nested_duplicate_is_reported_before_its_malformed_value(runtime):
    result = outcome(
        runtime, "parse", '{"customers":[{"name":"Ada","\\u006eame":notJSON}]}'
    )
    assert not result["ok"] and result["complete"] is False
    assert result["errors"][0]["code"] == "NOMI-JSON-DUPLICATE-KEY"
    assert result["errors"][0]["path"] == ["customers", 0, "name"]
    assert result["errors"][0]["path_text"] == "$.customers[0].name"


@pytest.mark.parametrize("runtime", RUNTIMES)
def test_null_customers_is_a_type_error_not_an_empty_batch(runtime):
    result = outcome(runtime, "decode", '{"customers":null}')
    assert result["ok"] is False and result["complete"] is True
    assert [(e["code"], e["path"]) for e in result["errors"]] == [
        ("NOMI-DECODE-TYPE", ["customers"])
    ]


@pytest.mark.parametrize("runtime", RUNTIMES)
def test_known_fields_precede_sorted_extras_and_root_extras(runtime):
    text = '{"z":0,"customers":[{"z":0,"age":-1,"name":"","a":0,"id":""}],"a":0}'
    result = outcome(runtime, "decode", text)
    assert result["complete"] is True
    assert [e["path"] for e in result["errors"]] == [
        ["customers", 0, "id"],
        ["customers", 0, "name"],
        ["customers", 0, "age"],
        ["customers", 0, "a"],
        ["customers", 0, "z"],
        ["a"],
        ["z"],
    ]


@pytest.mark.parametrize("runtime", RUNTIMES)
def test_cardinality_constraint_suppresses_dependent_row_checks(runtime):
    result = outcome(runtime, "decode", json.dumps({"customers": [{}] * 129}))
    assert result["complete"] is True
    assert [(e["code"], e["path"]) for e in result["errors"]] == [
        ("NOMI-DECODE-CONSTRAINT", ["customers"])
    ]


@pytest.mark.parametrize("runtime", RUNTIMES)
@pytest.mark.parametrize("depth, accepted", [(32, True), (33, False)])
def test_depth_counts_containers_but_not_primitive_leaves(runtime, depth, accepted):
    result = outcome(runtime, "parse", "[" * depth + "0" + "]" * depth)
    assert result["ok"] is accepted
    if not accepted:
        assert result["errors"][0]["code"] == "NOMI-BOUNDARY-LIMIT"


@pytest.mark.parametrize("runtime", RUNTIMES)
@pytest.mark.parametrize("rows, complete", [(16, True), (17, False)])
def test_sixty_four_retained_errors_are_complete_only_without_omission(
    runtime, rows, complete
):
    result = outcome(
        runtime,
        "decode",
        json.dumps({"customers": [{"id": "", "name": "", "age": -1, "x": 0}] * rows}),
    )
    assert len(result["errors"]) == 64
    assert result["complete"] is complete
    assert result["errors"][0]["path"] == ["customers", 0, "id"]
    assert result["errors"][-1]["path"] == ["customers", 15, "x"]


@pytest.mark.parametrize("runtime", RUNTIMES)
def test_oversized_diagnostic_replaces_lossless_paths_with_explicit_refusal(runtime):
    result = outcome(runtime, "decode", json.dumps({"customers": [], "x" * 10000: 1}))
    assert result["complete"] is False
    assert result["errors"] == [
        {
            "code": "NOMI-BOUNDARY-LIMIT",
            "path": [],
            "path_text": "$",
            "expected": "bounded diagnostic output",
            "message": "Validation stopped at the diagnostic budget.",
        }
    ]


@pytest.mark.parametrize("runtime", RUNTIMES)
@pytest.mark.parametrize(
    "token", ["-" + "9" * 5000, "9" * 5000], ids=["negative-wide", "positive-wide"]
)
def test_native_conversion_capacity_refuses_before_host_conversion_or_constraint(
    runtime, token
):
    result = outcome(
        runtime, "decode", '{"customers":[{"id":"a","name":"","age":' + token + "}]}"
    )
    assert result["complete"] is False
    assert len(result["errors"]) == 1
    assert result["errors"][0]["code"] == "NOMI-NUMERIC-CAPACITY"
    assert result["errors"][0]["path"] == ["customers", 0, "age"]


@pytest.mark.parametrize("runtime", RUNTIMES)
@pytest.mark.parametrize(
    "node",
    [
        {"kind": "number", "token": "01"},
        {"kind": "null", "value": None},
        {"kind": "map", "entries": [["a", {"kind": "null"}, 3]]},
        {"kind": "map", "entries": [["a", {"kind": "null"}], ["a", {"kind": "null"}]]},
    ],
)
def test_malformed_supplied_tree_never_enters_schema_validation(runtime, node):
    result = outcome(
        runtime, "tree", {"schema": "nomi.json-value", "version": 1, "root": node}
    )
    assert result["complete"] is False
    assert result["errors"][0]["code"] == "NOMI-VALUE-TREE"


@pytest.mark.parametrize("runtime", RUNTIMES)
@pytest.mark.parametrize("operation", ["parse", "encode"])
def test_node_limit_counts_each_primitive_occurrence(runtime, operation):
    result = outcome(
        runtime,
        operation,
        "[0,0]" if operation == "parse" else [0, 0],
        {"node_limit": 2},
    )
    assert not result["ok"]
    assert result["errors"][0]["code"] == "NOMI-BOUNDARY-LIMIT"


@pytest.mark.parametrize("runtime", RUNTIMES)
def test_work_budget_charges_scanning_before_processing(runtime):
    result = outcome(runtime, "parse", "[0]", {"work_limit": 1})
    assert not result["ok"] and result["complete"] is False
    assert result["errors"][0]["code"] == "NOMI-BOUNDARY-LIMIT"


@pytest.mark.parametrize("runtime", RUNTIMES)
def test_nonascii_control_policy_and_scalar_key_order_are_exact(runtime):
    value = {"😀": '\b\t\n\f\r\x00\x1f/"\\\u2028\u2029', "\ue000": 0}
    result = outcome(runtime, "encode", value)
    assert result == {
        "ok": True,
        "text": '{"\ue000":0,"😀":"\\b\\t\\n\\f\\r\\u0000\\u001f/\\"\\\\\u2028\u2029"}',
    }
