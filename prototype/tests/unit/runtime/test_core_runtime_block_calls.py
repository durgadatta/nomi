"""Direct Core Runtime support for yield-to-block calls."""

from prototype.runtime import create_session
from prototype.runtime.backends.core_runtime import CoreRuntimeEvaluator
from prototype.syntax.core import (
    BinaryOp,
    Bind,
    Call,
    Function,
    Literal,
    Load,
    Module,
    Return,
    Yield,
)


def test_core_runtime_yield_runs_attached_block():
    backend = CoreRuntimeEvaluator()
    core = Module(
        body=(
            Bind(
                name="twice",
                value=Function(
                    params=(),
                    body=Module(body=(Yield(), Yield())),
                ),
            ),
            Bind(name="count", value=Literal(value=0)),
            Call(
                func=Load(name="twice"),
                block=Function(
                    params=(),
                    body=Module(
                        body=(
                            Bind(
                                name="count",
                                value=BinaryOp(
                                    left=Load(name="count"),
                                    op="+",
                                    right=Literal(value=1),
                                ),
                            ),
                        )
                    ),
                ),
            ),
        )
    )

    result = backend.evaluate(core)

    assert result.bindings["count"] == 2


def test_core_runtime_yield_passes_value_to_block_parameter():
    backend = CoreRuntimeEvaluator()
    core = Module(
        body=(
            Bind(
                name="once",
                value=Function(
                    params=(),
                    body=Module(
                        body=(
                            Yield(value=Literal(value=7)),
                            Return(value=Literal(value=None)),
                        )
                    ),
                ),
            ),
            Bind(name="seen", value=Literal(value=0)),
            Call(
                func=Load(name="once"),
                block=Function(
                    params=("n",),
                    body=Module(body=(Bind(name="seen", value=Load(name="n")),)),
                ),
            ),
        )
    )

    result = backend.evaluate(core)

    assert result.bindings["seen"] == 7


def test_core_runtime_session_runs_simple_block_call_source():
    session = create_session(mode="nomi", eval_backend="core-runtime")

    result = session.run(
        source=(
            "func twice():\n"
            "    yield\n"
            "    yield\n"
            "count = 0\n"
            "twice():\n"
            "    count = count + 1\n"
        )
    )

    assert result.ok
    assert result.bindings["count"] == 2
