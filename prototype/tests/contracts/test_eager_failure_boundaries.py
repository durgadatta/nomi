"""Abnormal prototype errors are not ordinary Result-like container elements."""

import contextlib
import io
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from prototype.runtime import create_session
from prototype.runtime.backends.core_runtime import CoreRuntimeEvaluator
from prototype.runtime.backends.values import ErrorValue
from prototype.syntax.core import (
    Bind,
    Call,
    Handle,
    Literal,
    Load,
    Module,
    PatternTest,
    Sequence,
)

ROOT = Path(__file__).resolve().parents[3]
NODE = shutil.which("node")

PRELUDE = """func observe(value):
    print('later')
    return value
func ignore(value):
    print('body')
    return 42
func fail(value):
    print(value)
    return int('invalid')
"""

CASES = [
    "ignore(int('invalid'))",
    "print(int('invalid'), observe(1))",
    "items = [int('invalid'), observe(1)]",
    "items = {'x': int('invalid'), 'y': observe(1)}",
    "items = {int('invalid'): observe(1)}",
    "int('invalid') + observe(1)",
    "items = list(map(fail, [1, 2, 3]))",
    "items = list(filter(fail, [1, 2, 3]))",
    "for item in [1, 2]:\n    int('invalid')\n    print('body')",
    "count = 0\nwhile count < 2:\n    count = count + 1\n    int('invalid')\n    print('body')",
    "func with_default(value=int('invalid')):\n    print('body')\n    return 1\nwith_default()",
]


@pytest.mark.parametrize("backend", ["core", "js"])
@pytest.mark.parametrize("body", CASES)
def test_eager_failure_stops_later_work(body, backend):
    source = PRELUDE + "print('before')\n" + body + "\nprint('after')\n"
    expected = (
        "before\n1\n" if "map(fail" in body or "filter(fail" in body else "before\n"
    )
    if backend == "core":
        evaluator = CoreRuntimeEvaluator()
        output = io.StringIO()
        with (
            contextlib.redirect_stdout(output),
            pytest.raises(RuntimeError, match="invalid"),
        ):
            evaluator.evaluate(create_session().lower_to_core_ir(source=source))
        assert output.getvalue() == expected
    else:
        if NODE is None:
            pytest.skip("node unavailable")
        payload = create_session().core_json(source=source)
        script = """
const fs = require('node:fs');
const {CoreRuntime} = require('./prototype/runtime/js/core_runtime.js');
const runtime = new CoreRuntime();
try { runtime.evaluate(JSON.parse(fs.readFileSync(0, 'utf8'))); process.exit(2); }
catch (error) { process.stdout.write(JSON.stringify({error: error.message, stdout: runtime.stdout.join('')})); }
"""
        result = subprocess.run(
            [NODE, "-e", script],
            input=payload,
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        record = json.loads(result.stdout)
        assert "invalid" in record["error"]
        assert record["stdout"] == expected


def test_failed_binding_never_publishes_an_error_value():
    evaluator = CoreRuntimeEvaluator()
    evaluator._global_frame.bind("fail", evaluator._host_calls["int"])
    result = evaluator.eval(
        Bind(
            name="result",
            value=Call(func=Load(name="fail"), args=(Literal(value="invalid"),)),
        )
    )
    assert isinstance(result, ErrorValue)
    assert "result" not in evaluator._global_frame.bindings


def test_handler_sees_the_original_error_before_an_argument_body_runs():
    core = create_session().lower_to_core_ir(
        source=PRELUDE + "ignore(int('invalid'))\n"
    )
    body = Module(body=core.body)
    wrapped = Module(
        body=(
            Handle(
                body=body,
                handlers=(
                    PatternTest(
                        pattern=Load(name="ValueError"),
                        body=Module(
                            body=(Bind(name="handled", value=Literal(value=True)),)
                        ),
                    ),
                ),
            ),
        )
    )
    result = CoreRuntimeEvaluator().evaluate(wrapped)
    assert result.bindings["handled"] is True


def test_finally_failure_is_not_discarded_as_a_normal_value():
    core = Module(
        body=(
            Handle(
                body=Module(body=(Literal(value=1),)),
                finalbody=Module(
                    body=(
                        Call(func=Load(name="int"), args=(Literal(value="invalid"),)),
                    )
                ),
            ),
        )
    )
    with pytest.raises(RuntimeError, match="invalid"):
        CoreRuntimeEvaluator().evaluate(core)


def test_normal_sequence_payloads_remain_values():
    core = Module(
        body=(
            Bind(
                name="result",
                value=Sequence(elements=(Literal(value=None), Literal(value=False))),
            ),
        )
    )
    assert CoreRuntimeEvaluator().evaluate(core).bindings["result"] == [None, False]
