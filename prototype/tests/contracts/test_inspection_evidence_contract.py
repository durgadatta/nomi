"""A missing observation must not be displayed as a known empty/zero result."""

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
    pytest.mark.skipif(NODE is None, reason="node unavailable"),
]


def inspect_result(result):
    completed = subprocess.run(
        [
            NODE,
            "-e",
            """
global.window = {};
const r = require('./web/runtime.js');
const result = JSON.parse(process.argv[1]);
process.stdout.write(JSON.stringify({
  bindingsAvailable: r.bindingsAvailable(result),
  bindings: r.bindingEntries(result),
  pipeline: r.pipelineEntries(result),
  timings: r.timingEntries(result),
  label: r.runtimeLabel(result),
  timingLabel: r.formatTiming(result.timings, 12)
}));
""",
            json.dumps(result),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    return json.loads(completed.stdout)


def test_absent_observations_do_not_invent_pipeline_or_zero_timings():
    result = inspect_result({"backend": "future-engine"})
    assert result["bindingsAvailable"] is False
    assert result["bindings"] == []
    assert result["pipeline"] == [
        [label, "Unavailable"] for label in ["Frontend", "Lowerer", "Backend", "Host"]
    ]
    assert result["timings"] == [
        [label, None] for label in ["Parse", "Lower", "Evaluate"]
    ]
    assert result["label"] == "future-engine"
    assert result["timingLabel"] == "12 ms elapsed"


@pytest.mark.parametrize("bindings", [None, [], "not a capture"])
def test_invalid_binding_payload_is_not_reported_as_empty_capture(bindings):
    assert inspect_result({"bindings": bindings})["bindingsAvailable"] is False


def test_empty_captured_bindings_and_observed_zero_timings_are_known():
    result = inspect_result(
        {
            "bindings": {},
            "timings": {"parse_ms": 0, "lower_ms": 0, "eval_ms": 0, "total_ms": 0},
            "pipeline": {
                "parser_frontend": "custom",
                "lowerer": "lower",
                "eval_backend": "eval",
                "host": "host",
            },
        }
    )
    assert result["bindingsAvailable"] is True
    assert result["pipeline"] == [
        ["Frontend", "custom"],
        ["Lowerer", "lower"],
        ["Backend", "eval"],
        ["Host", "host"],
    ]
    assert result["timings"] == [["Parse", 0], ["Lower", 0], ["Evaluate", 0]]


@pytest.mark.parametrize("duration", [-1, "0", None, True])
def test_invalid_duration_is_unavailable_not_coerced(duration):
    assert inspect_result({"timings": {"parse_ms": duration}})["timings"][0] == [
        "Parse",
        None,
    ]


def test_known_legacy_backend_does_not_fill_missing_stage_evidence():
    result = inspect_result(
        {"backend": "python-ast", "pipeline": {"eval_backend": "python-ast"}}
    )
    assert result["label"] == "Pyodide"
    assert result["pipeline"] == [
        ["Frontend", "Unavailable"],
        ["Lowerer", "Unavailable"],
        ["Backend", "python-ast"],
        ["Host", "Unavailable"],
    ]


def test_cache_timing_does_not_require_repeated_parse_and_lower_observations():
    result = inspect_result(
        {"timings": {"cache_hit": True, "cache_ms": 0, "eval_ms": 2, "total_ms": 3}}
    )
    assert result["timingLabel"] == "3 ms total, 0 ms cached, 2 ms eval"
    assert result["timings"] == [["Parse", None], ["Lower", None], ["Evaluate", 2]]
