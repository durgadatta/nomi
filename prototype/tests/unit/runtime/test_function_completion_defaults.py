"""Ordinary calls preserve lexical defaults and explicit function completion."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from prototype.runtime import create_session
from prototype.runtime.backends.core_runtime import CoreRuntimeEvaluator
from prototype.syntax.core import (
    Bind,
    Call,
    Function,
    Literal,
    Load,
    Module,
)
from prototype.syntax.core_json import core_to_json


ROOT = Path(__file__).resolve().parents[4]
NODE = shutil.which("node")
BACKENDS = ("python-ast", "core-runtime", "js-core-runtime")

CASES = (
    (
        "binding-fallthrough",
        "func calculate():\n    value = 7\nresult = calculate()\n",
        None,
        "",
    ),
    (
        "expression-fallthrough",
        "func calculate():\n    7\nresult = calculate()\n",
        None,
        "",
    ),
    (
        "branch-fallthrough",
        "func calculate():\n    if True:\n        value = 7\nresult = calculate()\n",
        None,
        "",
    ),
    (
        "explicit-return",
        "func calculate():\n    return 7\nresult = calculate()\n",
        7,
        "",
    ),
    (
        "arrow-result",
        "calculate = (value) => value + 1\nresult = calculate(7)\n",
        8,
        "",
    ),
    (
        "lexical-default",
        "value = 1\nfunc calculate(result=value):\n    return result\n"
        "func caller():\n    value = 2\n    return calculate()\nresult = caller()\n",
        1,
        "",
    ),
    (
        "earlier-parameter-defaults",
        "func calculate(first, second=first, third=second + 1):\n"
        "    return third\nresult = calculate(7)\n",
        8,
        "",
    ),
    (
        "call-time-default",
        "value = 1\nfunc calculate(result=value):\n    return result\n"
        "value = 2\nresult = calculate()\n",
        2,
        "",
    ),
    (
        "supplied-default-not-evaluated",
        "func calculate(value=missing):\n    return value\nresult = calculate(7)\n",
        7,
        "",
    ),
    (
        "normal-completion-runs-defer",
        "func calculate():\n    defer print('cleanup')\n    value = 7\n"
        "result = calculate()\n",
        None,
        "cleanup\n",
    ),
)


@pytest.mark.parametrize("backend", BACKENDS)
@pytest.mark.parametrize(
    "_name, source, expected, stdout", CASES, ids=[c[0] for c in CASES]
)
def test_function_completion_and_defaults_across_backends(
    backend, _name, source, expected, stdout
):
    if backend == "js-core-runtime" and NODE is None:
        pytest.skip("node is not installed")
    result = create_session(mode="nomi", eval_backend=backend).run(
        source=source,
        capture_output=True,
    )

    assert result.ok
    assert result.bindings["result"] == expected
    assert result.stdout == stdout


@pytest.mark.skipif(NODE is None, reason="node is not installed")
@pytest.mark.browser_pipeline
@pytest.mark.parametrize(
    "_name, source, expected, stdout", CASES, ids=[c[0] for c in CASES]
)
def test_function_contract_through_actual_browser_lowering(
    _name, source, expected, stdout
):
    lowered = subprocess.run(
        [NODE, "prototype/runtime/js/core_from_source.js"],
        input=source + "print(result)\n",
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=20,
    )
    payload = json.loads(lowered.stdout)
    assert payload["diagnosticCount"] == 0
    evaluated = subprocess.run(
        [NODE, "prototype/runtime/js/core_runtime.js"],
        input=lowered.stdout,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=20,
    )
    result = json.loads(evaluated.stdout)

    assert result["bindings"]["result"] == expected
    assert result["stdout"] == stdout + str(expected) + "\n"


@pytest.mark.parametrize("backend", BACKENDS)
def test_failed_default_stops_later_defaults_and_body(backend):
    if backend == "js-core-runtime" and NODE is None:
        pytest.skip("node is not installed")
    result = create_session(mode="nomi", eval_backend=backend).run(
        source=(
            "func observe():\n    print('later default')\n    return 2\n"
            "func calculate(first=missing, second=observe()):\n"
            "    print('body')\n    return second\ncalculate()\n"
        ),
        capture_output=True,
        raise_on_error=False,
    )

    assert not result.ok
    assert result.stdout == ""


def test_failed_default_restores_python_core_caller_frame():
    events = []
    evaluator = CoreRuntimeEvaluator(
        host_calls={"observe": lambda: events.append("executed")}
    )
    evaluator.evaluate(
        Module(
            body=(
                Bind(name="value", value=Literal(value="caller")),
                Bind(
                    name="calculate",
                    value=Function(
                        params=("value", "missing_default", "later_default"),
                        defaults=(
                            Load(name="missing"),
                            Call(func=Load(name="observe")),
                        ),
                        body=Module(body=(Call(func=Load(name="observe")),)),
                    ),
                ),
            )
        )
    )

    with pytest.raises(NameError, match="missing"):
        evaluator.eval(
            Call(func=Load(name="calculate"), args=(Literal(value="callee"),))
        )

    result = evaluator.evaluate(
        Module(body=(Bind(name="after", value=Load(name="value")),))
    )
    assert result.bindings["after"] == "caller"
    assert events == []


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_failed_default_restores_javascript_core_caller_frame():
    result = subprocess.run(
        [
            NODE,
            "-e",
            """
const { CoreRuntime } = require('./prototype/runtime/js/core_runtime.js');
const events = [];
const runtime = new CoreRuntime({observe: () => events.push('executed')});
runtime.eval({type: 'Bind', name: 'value', value: {type: 'Literal', value: 'caller'}});
runtime.eval({type: 'Bind', name: 'calculate', value: {
  type: 'Function', params: ['value', 'missing_default', 'later_default'],
  defaults: [{type: 'Load', name: 'missing'},
    {type: 'Call', func: {type: 'Load', name: 'observe'}, args: []}],
  body: {type: 'Module', body: [{type: 'Call', func: {type: 'Load', name: 'observe'}, args: []}]}
}});
let failed = false;
try {
  runtime.eval({type: 'Call', func: {type: 'Load', name: 'calculate'},
    args: [{type: 'Literal', value: 'callee'}]});
} catch (error) {
  failed = error instanceof ReferenceError;
}
const after = runtime.eval({type: 'Load', name: 'value'});
process.stdout.write(JSON.stringify({failed, after: after.value, events}));
""",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=20,
    )
    assert json.loads(result.stdout) == {
        "failed": True,
        "after": "caller",
        "events": [],
    }


def _arity_module(argument_count):
    return Module(
        body=(
            Bind(
                name="calculate",
                value=Function(
                    params=("first", "second"),
                    defaults=(Call(func=Load(name="observe")),),
                    body=Module(body=(Call(func=Load(name="observe")),)),
                ),
            ),
            Call(
                func=Load(name="calculate"),
                args=tuple(Literal(value=index) for index in range(argument_count)),
            ),
        )
    )


@pytest.mark.parametrize("argument_count", (0, 3), ids=("too-few", "too-many"))
def test_python_core_arity_rejection_precedes_default_and_body(argument_count):
    events = []
    evaluator = CoreRuntimeEvaluator(
        host_calls={"observe": lambda: events.append("executed")}
    )

    with pytest.raises(TypeError, match="Expected"):
        evaluator.evaluate(_arity_module(argument_count))

    assert events == []


@pytest.mark.skipif(NODE is None, reason="node is not installed")
@pytest.mark.parametrize("argument_count", (0, 3), ids=("too-few", "too-many"))
def test_javascript_core_arity_rejection_precedes_default_and_body(argument_count):
    result = subprocess.run(
        [
            NODE,
            "-e",
            """
const { CoreRuntime } = require('./prototype/runtime/js/core_runtime.js');
const payload = JSON.parse(require('node:fs').readFileSync(0, 'utf8'));
const events = [];
const runtime = new CoreRuntime({observe: () => events.push('executed')});
let failed = false;
try {
  runtime.evaluate(payload);
} catch (error) {
  failed = error instanceof TypeError && error.message.startsWith('Expected');
}
process.stdout.write(JSON.stringify({failed, events}));
""",
        ],
        input=core_to_json(_arity_module(argument_count)),
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=20,
    )
    assert json.loads(result.stdout) == {"failed": True, "events": []}
