"""Acceptance tests for the non-Python JavaScript Core Runtime."""

from __future__ import annotations

import contextlib
import io
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from prototype.runtime.backends.core_runtime import CoreRuntimeEvaluator
from prototype.runtime import create_session
from prototype.runtime.backends import get_eval_backend
from prototype.runtime.backends.js_core import JS_CORE_BACKEND_SPEC
from prototype.syntax.core import (
    BinaryOp,
    Bind,
    Call,
    CORE_NODE_TYPES,
    ConstructData,
    GetField,
    GetItem,
    Handle,
    ForEach,
    Function,
    Literal,
    Load,
    MappingLiteral,
    Match,
    Module,
    PatternTest,
    Raise,
    Return,
    Sequence,
    Spread,
    Yield,
)
from prototype.syntax.core_json import core_to_json_payload


ROOT = Path(__file__).resolve().parents[4]
NODE = shutil.which("node")


def _fixture_core() -> Module:
    return Module(
        body=(
            Bind(name="total", value=Literal(value=0)),
            Bind(
                name="add",
                value=Function(
                    params=("a", "b"),
                    body=Module(
                        body=(
                            Return(
                                value=BinaryOp(
                                    left=Load(name="a"),
                                    op="+",
                                    right=Load(name="b"),
                                )
                            ),
                        )
                    ),
                ),
            ),
            Bind(
                name="result",
                value=Call(
                    func=Load(name="add"),
                    args=(Literal(value=3), Literal(value=4)),
                ),
            ),
            Bind(
                name="point",
                value=ConstructData(
                    name="Point",
                    fields=(
                        ("x", Literal(value=5)),
                        ("y", Literal(value=8)),
                    ),
                ),
            ),
            Bind(
                name="point_x",
                value=GetField(object_=Load(name="point"), field="x"),
            ),
            Bind(
                name="items",
                value=Sequence(
                    elements=(
                        Literal(value=1),
                        Literal(value=2),
                        Literal(value=3),
                    )
                ),
            ),
            ForEach(
                target="item",
                iterable=Load(name="items"),
                body=Module(
                    body=(
                        Bind(
                            name="total",
                            value=BinaryOp(
                                left=Load(name="total"),
                                op="+",
                                right=Load(name="item"),
                            ),
                        ),
                    )
                ),
            ),
            Call(
                func=Load(name="print"),
                args=(Literal(value="total"), Load(name="total")),
            ),
        )
    )


def _run_python_core_runtime(core: Module) -> tuple[dict[str, object], str]:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        result = CoreRuntimeEvaluator().evaluate(core)
    return result.bindings, stdout.getvalue()


def _run_js_core_runtime(core: Module) -> dict[str, object]:
    return _run_js_payload(json.dumps(core_to_json_payload(core)))


def _run_js_payload(payload: str) -> dict[str, object]:
    completed = subprocess.run(
        [NODE, str(ROOT / "web/core_runtime.js")],
        input=payload,
        text=True,
        capture_output=True,
        check=True,
        cwd=ROOT,
    )
    return json.loads(completed.stdout)


def _assert_js_matches_python(core: Module) -> dict[str, object]:
    js_result = _run_js_core_runtime(core)
    python_bindings, python_stdout = _run_python_core_runtime(core)

    assert js_result["bindings"] == python_bindings
    assert js_result["stdout"] == python_stdout
    return js_result


def test_js_core_runtime_dispatches_every_registered_core_node():
    source = (ROOT / "web/core_runtime.js").read_text(encoding="utf-8")

    missing = [
        node_type.__name__
        for node_type in CORE_NODE_TYPES
        if f"eval{node_type.__name__}(" not in source
    ]

    assert missing == []


def test_js_core_runtime_backend_is_registered():
    backend = get_eval_backend("js-core-runtime")

    assert backend.spec is JS_CORE_BACKEND_SPEC
    assert backend.spec.capabilities.evaluates_native_ir is True
    assert backend.spec.capabilities.supports_blocks is True


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_js_core_runtime_matches_python_reference_for_serialized_fixture():
    core = _fixture_core()
    js_result = _run_js_core_runtime(core)
    python_bindings, python_stdout = _run_python_core_runtime(core)

    assert js_result["backend"] == "js-core-runtime"
    assert js_result["bindings"]["result"] == python_bindings["result"] == 7
    assert (
        js_result["bindings"]["items"]
        == python_bindings["items"]
        == [1, 2, 3]
    )
    assert js_result["bindings"]["total"] == python_bindings["total"] == 6
    assert js_result["stdout"] == python_stdout == "total 6\n"


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_js_core_runtime_matches_python_for_data_mapping_and_spread():
    core = Module(
        body=(
            Bind(
                name="items",
                value=Sequence(
                    elements=(
                        Literal(value=1),
                        Spread(value=Sequence(elements=(Literal(value=2), Literal(value=3)))),
                    )
                ),
            ),
            Bind(
                name="mapping",
                value=MappingLiteral(
                    entries=(
                        (Literal(value="a"), Literal(value=10)),
                        (Literal(value="b"), Literal(value=20)),
                    )
                ),
            ),
            Bind(
                name="fallback",
                value=Call(
                    func=GetField(object_=Load(name="mapping"), field="get"),
                    args=(Literal(value="missing"), Literal(value=99)),
                ),
            ),
            Bind(
                name="value",
                value=GetItem(object_=Load(name="mapping"), key=Literal(value="a")),
            ),
        )
    )

    _assert_js_matches_python(core)


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_js_core_runtime_matches_python_for_match_and_errors():
    core = Module(
        body=(
            Bind(
                name="matched",
                value=Match(
                    subject=Sequence(
                        elements=(
                            Literal(value=1),
                            Literal(value=2),
                            Literal(value=3),
                        )
                    ),
                    cases=(
                        PatternTest(
                            pattern=Sequence(
                                elements=(
                                    Literal(value=0),
                                    Spread(value=Load(name="rest")),
                                )
                            ),
                            body=Module(body=(Literal(value="no"),)),
                        ),
                        PatternTest(
                            pattern=Sequence(
                                elements=(
                                    Literal(value=1),
                                    Spread(value=Load(name="rest")),
                                )
                            ),
                            body=Module(body=(Load(name="rest"),)),
                        ),
                    ),
                ),
            ),
            Handle(
                body=Module(body=(Raise(exception=Literal(value="boom")),)),
                handlers=(
                    PatternTest(
                        pattern=Load(name="Exception"),
                        body=Module(
                            body=(Bind(name="handled", value=Literal(value=True)),)
                        ),
                    ),
                ),
                finalbody=Module(
                    body=(Bind(name="finalized", value=Literal(value=True)),)
                ),
            ),
        )
    )

    _assert_js_matches_python(core)


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_js_core_runtime_matches_python_for_yield_to_block():
    core = Module(
        body=(
            Bind(name="collected", value=Sequence(elements=())),
            Bind(
                name="emit",
                value=Function(
                    params=("value",),
                    body=Module(body=(Yield(value=Load(name="value")),)),
                ),
            ),
            Call(
                func=Load(name="emit"),
                args=(Literal(value=4),),
                block=Function(
                    params=("item",),
                    body=Module(
                        body=(
                            Bind(
                                name="collected",
                                value=Sequence(
                                    elements=(
                                        Spread(value=Load(name="collected")),
                                        Load(name="item"),
                                    )
                                ),
                            ),
                        )
                    ),
                ),
            ),
        )
    )

    _assert_js_matches_python(core)


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_js_core_runtime_runs_core_json_from_session_source_pipeline():
    session = create_session(mode="nomi")
    payload = session.core_json(source="x = 1 + 2\nprint(x)\n")

    result = _run_js_payload(payload)

    assert result["backend"] == "js-core-runtime"
    assert result["bindings"]["x"] == 3
    assert result["stdout"] == "3\n"


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_runtime_session_can_select_js_core_runtime_backend():
    session = create_session(mode="nomi", eval_backend="js-core-runtime")

    result = session.run(
        source="x = 1 + 2\nprint(x)\nx\n",
        capture_output=True,
        display_last_expr=True,
    )

    assert result.ok
    assert result.bindings["x"] == 3
    assert result.stdout == "3\n"
    assert result.has_value is True
    assert result.value == 3


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_js_core_runtime_runs_demo_through_session_core_json():
    session = create_session(mode="nomi")
    payload = session.core_json(filename=ROOT / "samples/demo.nomi")

    result = _run_js_payload(payload)

    assert result["bindings"]["count"] == 2
    assert result["bindings"]["collected"] == [2, 4, 6]
    assert result["bindings"]["total"] == 6
    assert result["bindings"]["parsed"] == 0
    assert "add(3, 4)         = 7" in result["stdout"]
    assert "block: collected  = [2, 4, 6]" in result["stdout"]


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_all_backends_demo_stdout_parity():
    path = ROOT / "samples/demo.nomi"
    results = {}
    for backend in ("python-ast", "core-runtime", "js-core-runtime"):
        results[backend] = create_session(
            mode="nomi", eval_backend=backend
        ).run(filename=path, capture_output=True)

    assert results["js-core-runtime"].stdout == results["core-runtime"].stdout
    assert results["core-runtime"].stdout == results["python-ast"].stdout


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_runtime_session_runs_demo_on_js_core_runtime_backend():
    session = create_session(mode="nomi", eval_backend="js-core-runtime")

    result = session.run(
        filename=ROOT / "samples/demo.nomi",
        capture_output=True,
    )

    assert result.ok
    assert result.bindings["count"] == 2
    assert result.bindings["collected"] == [2, 4, 6]
    assert result.bindings["parsed"] == 0
    assert "block: collected  = [2, 4, 6]" in result.stdout
