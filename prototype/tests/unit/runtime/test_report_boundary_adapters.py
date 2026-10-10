"""The tagged seam rejects malformed/foreign values before structural encoding."""

import json
from pathlib import Path
import shutil
import subprocess

import pytest

from prototype.runtime.backends.core_runtime import CoreRuntimeEvaluator
from prototype.runtime.backends.values import (
    BoolValue,
    IntValue,
    MappingValue,
    SequenceValue,
    StrValue,
)
from prototype.runtime import report_boundary as boundary
from prototype.runtime.report_boundary import BoundaryBudget
from prototype.runtime.report_boundary_adapter import invoke
from prototype.syntax.core import Bind, Call, Literal, Load, Module


ROOT = Path(__file__).resolve().parents[4]
NODE = shutil.which("node")


@pytest.mark.parametrize("digits", [3, 4300])
def test_decimal_capacity_refuses_before_native_integer_formatting(monkeypatch, digits):
    def forbidden_format(value):
        pytest.fail("native formatter ran outside the declared capacity")

    monkeypatch.setattr(boundary, "str", forbidden_format, raising=False)
    budget = BoundaryBudget(numeric_digit_limit=digits)
    with pytest.raises(boundary.BoundaryRefusal) as caught:
        boundary._write(10**digits, boundary._Sink(budget, "output", 65536))
    assert caught.value.code == "NOMI-NUMERIC-CAPACITY"


@pytest.mark.parametrize(
    "value",
    [
        IntValue(True),
        BoolValue(1),
        StrValue(0),
        SequenceValue([]),
        MappingValue({0: IntValue(1)}),
    ],
)
def test_python_tagged_storage_does_not_borrow_a_structural_family(value):
    result = invoke("encode_json", [value], BoundaryBudget())
    assert result["ok"] is False
    assert result["errors"][0]["code"] == "NOMI-ENCODE-TYPE"


def test_python_tagged_graph_preserves_cycle_and_shared_occurrences():
    cycle = MappingValue({})
    cycle.entries["child"] = cycle
    failure = invoke("encode_json", [cycle], BoundaryBudget())
    assert failure["errors"][0]["code"] == "NOMI-ENCODE-CYCLE"
    assert failure["errors"][0]["path"] == ["child"]
    shared = MappingValue({"x": IntValue(1)})
    assert invoke(
        "encode_json", [SequenceValue((shared, shared))], BoundaryBudget()
    ) == {"ok": True, "text": '[{"x":1},{"x":1}]'}


def test_fork_has_independent_default_provider_allowance_and_keeps_custom_calls():
    parent = CoreRuntimeEvaluator(host_calls={"constant": lambda: 42})
    parent._report_boundary_budget.output_limit = 0
    child = parent.fork()
    result = child.evaluate(
        Module(
            body=(
                Bind(
                    name="encoded",
                    value=Call(func=Load(name="encode_json"), args=(Literal(value=0),)),
                ),
                Bind(name="custom", value=Call(func=Load(name="constant"), args=())),
            )
        )
    )
    assert result.bindings["encoded"] == {"ok": True, "text": "0"}
    assert result.bindings["custom"] == 42
    assert parent._report_boundary_budget.output_bytes == 0


JS_PROBES = {
    "foreign-tag": "new (class Foreign { constructor() { this.kind='str'; this.value='a'; } })()",
    "getter-tag": "Object.defineProperty({kind:'str'}, 'value', {get() { throw new Error('getter ran'); }, enumerable:true})",
    "symbol-tag": "Object.assign({kind:'str',value:'a'}, {[Symbol('hidden')]:0})",
    "sparse-sequence": "{kind:'sequence',elements:new Array(1)}",
    "foreign-elements": "{kind:'sequence',elements:new (class Foreign extends Array {})({kind:'int',value:1})}",
    "foreign-entries": "{kind:'mapping',entries:new (class Foreign extends Map {})([['a',{kind:'int',value:1}]])}",
    "bool-as-int": "{kind:'int',value:true}",
    "bad-nil": "{kind:'nil',value:null}",
}


@pytest.mark.skipif(NODE is None, reason="node is not installed")
@pytest.mark.parametrize("probe", JS_PROBES)
def test_js_tagged_seam_refuses_foreign_and_malformed_storage(probe):
    program = """const {CoreRuntime} = require('./prototype/runtime/js/core_runtime.js');
const runtime = new CoreRuntime();
const value = VALUE;
const result = runtime.defaultHostCalls().encode_json.call(value);
process.stdout.write(JSON.stringify({ok:result.entries.get('ok').value,
  code:result.entries.get('errors').elements[0].entries.get('code').value}));
""".replace("VALUE", JS_PROBES[probe])
    output = subprocess.run(
        [NODE, "-e", program], cwd=ROOT, capture_output=True, text=True, check=True
    )
    assert json.loads(output.stdout) == {"ok": False, "code": "NOMI-ENCODE-TYPE"}
