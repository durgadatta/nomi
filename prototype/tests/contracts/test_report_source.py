"""Closed ordinary source report across independent Python and WASM producers."""

import json
from pathlib import Path
import shutil
import subprocess

import pytest

from prototype.runtime import create_session


ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "prototype/tests/data/report_boundary/v1.json"
REPORT = ROOT / "samples/report.nomi"
NODE = shutil.which("node")
ROUTES = ["python-ast", "core-runtime", "js-python", "js-wasm"]
CASES = [
    case
    for case in json.loads(FIXTURE.read_text())["cases"]
    if case["operations"] == ["build_report"]
]
pytestmark = pytest.mark.contract


def run_source(source, route):
    if route in ("python-ast", "core-runtime"):
        result = create_session(eval_backend=route).run(
            source=source, raise_on_error=False, capture_output=True
        )
        assert result.ok, result.exception
        return {"bindings": result.bindings, "stdout": result.stdout}
    if NODE is None:
        pytest.skip("node is not installed")
    if route == "js-python":
        core = create_session().core_json(source=source)
    else:
        core = subprocess.run(
            [NODE, "prototype/runtime/js/core_from_source.js"],
            input=source,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
            timeout=20,
        ).stdout
    result = subprocess.run(
        [NODE, "prototype/runtime/js/core_runtime.js"],
        input=core,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
        timeout=20,
    )
    payload = json.loads(result.stdout)
    assert payload["ok"], payload["diagnostics"]
    return payload


def library_source():
    source, marker, _ = REPORT.read_text(encoding="utf-8").partition("# Demonstration:")
    assert marker
    return source


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize("case", CASES, ids=[case["id"] for case in CASES])
def test_prepared_report_outcome_is_computed_by_ordinary_source(route, case):
    args = case["input"]
    source = (
        library_source()
        + f"\nactual = build_report({args['text']!r}, {args['options_text']!r})\n"
    )
    result = run_source(source, route)
    assert result["bindings"]["actual"] == case["expected"]
    assert result["stdout"] == ""


@pytest.mark.parametrize("route", ROUTES)
def test_default_options_and_explicit_encoding_preserve_report_wire(route):
    source = (
        library_source()
        + """
result = build_report('{"customers":[{"id":" c-1 ","name":" Ada ","age":20},{"id":"c-2","name":"Bo","age":12}]}')
wire = report_json(result["report"])
"""
    )
    result = run_source(source, route)["bindings"]
    expected = next(
        case["expected"]
        for case in json.loads(FIXTURE.read_text())["cases"]
        if case["id"] == "report-wire"
    )
    assert result["wire"] == expected
    assert result["result"]["defaults_applied"] == [["minimum_age"]]


@pytest.mark.parametrize("route", ROUTES)
def test_integral_float_and_nominal_values_require_explicit_encoder_projection(route):
    source = """data CustomerId:
    value: str

float_result = encode_json(20.0)
nominal_result = encode_json(CustomerId("a"))
data_result = encode_json({"kind": "str", "value": "Ada"})
"""
    bindings = run_source(source, route)["bindings"]
    for name in ("float_result", "nominal_result"):
        assert bindings[name]["ok"] is False
        assert bindings[name]["errors"][0]["code"] == "NOMI-ENCODE-TYPE"
    assert bindings["data_result"] == {
        "ok": True,
        "text": '{"kind":"str","value":"Ada"}',
    }


@pytest.mark.parametrize("route", ROUTES)
def test_source_library_failure_records_keep_kind_as_user_data(route):
    source = """parsed = parse_json("broken")
decoded = decode_data(parse_json("null")["value"], "report-batch")
encoded = encode_json([1.0])
"""
    bindings = run_source(source, route)["bindings"]
    assert bindings["parsed"]["kind"] == "input-format"
    assert bindings["decoded"]["kind"] == "decode"
    assert bindings["encoded"]["kind"] == "encode"
