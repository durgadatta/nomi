"""Direct Core Runtime support for ForEach nodes."""

from prototype.runtime import create_session
from prototype.runtime.backends.core_runtime import CoreRuntimeEvaluator
from prototype.syntax.core import (
    BinaryOp,
    Bind,
    ForEach,
    Literal,
    Load,
    Module,
    Sequence,
)


def test_core_runtime_for_each_binds_iteration_target():
    backend = CoreRuntimeEvaluator()
    core = Module(
        body=(
            Bind(name="total", value=Literal(value=0)),
            ForEach(
                target="item",
                iterable=Sequence(elements=(Literal(value=1), Literal(value=2))),
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
        )
    )

    result = backend.evaluate(core)

    assert result.bindings["item"] == 2
    assert result.bindings["total"] == 3


def test_core_runtime_session_runs_for_yield_block_source():
    session = create_session(mode="nomi", eval_backend="core-runtime")

    result = session.run(
        source=(
            "func each(sequence):\n"
            "    for item in sequence:\n"
            "        yield item\n"
            "collected = []\n"
            "each([1, 2, 3]) -> n:\n"
            "    collected = collected + [n * 2]\n"
        )
    )

    assert result.ok
    assert result.bindings["collected"] == [2, 4, 6]
