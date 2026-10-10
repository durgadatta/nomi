import json
import shutil
import subprocess
from pathlib import Path

import pytest

from prototype.runtime.report_boundary import (
    BoundaryBudget,
    decode_data,
    encode_json,
    parse_json,
    trim_text,
)


ROOT = Path(__file__).resolve().parents[4]
FIXTURE = ROOT / "prototype/tests/data/report_boundary/v1.json"
JS_BOUNDARY = ROOT / "prototype/runtime/js/report_boundary.js"
NODE = shutil.which("node")
CASE_OPERATIONS = {"parse_json", "decode_data", "encode_json", "trim_text"}


def _python_outcome(case):
    if case.get("profile") == "js-safe-int":
        return None
    budget = BoundaryBudget(**{
        "input_limit": case.get("limits", {}).get("input_bytes_per_call", 256 * 1024),
        "output_limit": case.get("limits", {}).get("encoded_bytes_per_run", 64 * 1024),
    })
    result = None
    parsed = None
    for operation in case["operations"]:
        if operation not in CASE_OPERATIONS:
            return None
        if operation == "parse_json":
            parsed = parse_json(case["input"]["text"], budget)
            result = parsed
        elif operation == "decode_data":
            tree = case["input"].get("tree", parsed["value"] if parsed and parsed.get("ok") else None)
            result = decode_data(tree, case["input"].get("schema_name"), budget)
        elif operation == "encode_json":
            value = case["input"]["value"]
            if isinstance(value, str) and value == "\n":
                value = "\n"
            result = encode_json(value, budget)
        elif operation == "trim_text":
            result = trim_text(case["input"]["text"])
    return result


@pytest.fixture(scope="module")
def boundary_cases():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))["cases"]


def test_prepared_standalone_boundary_cases_match_python(boundary_cases):
    exercised = 0
    for case in boundary_cases:
        result = _python_outcome(case)
        if result is None:
            continue
        assert result == case["expected"], case["id"]
        exercised += 1
    assert exercised == 20


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_prepared_standalone_boundary_cases_match_javascript(boundary_cases):
    cases = [case for case in boundary_cases if set(case["operations"]) <= CASE_OPERATIONS]
    script = f"""
const fs=require('node:fs');
const b=require({str(JS_BOUNDARY)!r});
const cases=JSON.parse(fs.readFileSync(0,'utf8'));
const out=cases.map(c=>{{
 const budget=new b.BoundaryBudget({{input_bytes_per_call:c.limits?.input_bytes_per_call,encoded_bytes_per_run:c.limits?.encoded_bytes_per_run}});
 let parsed=null, result=null;
 for(const op of c.operations) {{
  if(op==='parse_json') {{ parsed=b.parseJson(c.input.text,budget); result=parsed; }}
  if(op==='decode_data') result=b.decodeData(c.input.tree || parsed?.value,c.input.schema_name,budget);
  if(op==='encode_json') result=b.encodeJson(c.input.value,budget);
  if(op==='trim_text') result=b.trimText(c.input.text);
 }}
 return result;
}});
process.stdout.write(JSON.stringify(out));
"""
    completed = subprocess.run(
        [NODE, "-e", script], input=json.dumps(cases, ensure_ascii=False),
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    assert completed.returncode == 0, completed.stderr
    outcomes = json.loads(completed.stdout)
    assert len(outcomes) == len(cases)
    for case, outcome in zip(cases, outcomes):
        assert outcome == case["expected"], case["id"]


def test_python_core_runtime_exposes_boundary_as_ordinary_calls():
    from prototype.runtime.backends.core_runtime import CoreRuntimeEvaluator

    names = CoreRuntimeEvaluator()._default_host_calls()
    assert {"parse_json", "decode_data", "encode_json", "trim_text"} <= names.keys()


@pytest.mark.parametrize("runtime", [
    "python",
    pytest.param("javascript", marks=pytest.mark.skipif(NODE is None, reason="node is not installed")),
])
def test_parse_and_decode_share_the_run_input_allowance(runtime):
    if runtime == "python":
        budget = BoundaryBudget(aggregate_input_limit=3)
        parsed = parse_json("{}", budget)
        result = decode_data(parsed["value"], "report-options", budget)
    else:
        script = f"""
const b=require({str(JS_BOUNDARY)!r});
const budget=new b.BoundaryBudget({{aggregate_input_bytes:3}});
const parsed=b.parseJson("{{}}",budget);
process.stdout.write(JSON.stringify(b.decodeData(parsed.value,"report-options",budget)));
"""
        completed = subprocess.run(
            [NODE, "-e", script], cwd=ROOT, text=True, capture_output=True,
            check=False,
        )
        assert completed.returncode == 0, completed.stderr
        result = json.loads(completed.stdout)
    assert result == {
        "ok": False,
        "kind": "decode",
        "errors": [{
            "code": "NOMI-BOUNDARY-LIMIT",
            "path": [],
            "path_text": "$",
            "expected": "bounded input bytes",
            "message": "Input exceeds the configured byte budget.",
        }],
        "complete": False,
    }
