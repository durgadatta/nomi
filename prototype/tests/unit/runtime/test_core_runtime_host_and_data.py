"""Direct Core Runtime host-call and data-constructor coverage."""

from prototype.runtime import create_session
from prototype.runtime.backends.core_runtime import CoreRuntimeEvaluator
from prototype.syntax.core import (
    Bind,
    Call,
    ConstructData,
    CompareOp,
    Function,
    Literal,
    Load,
    Module,
    Return,
    Sequence,
)


def test_core_runtime_has_default_host_builtins():
    backend = CoreRuntimeEvaluator()
    core = Module(
        body=(
            Bind(
                name="items",
                value=Call(
                    func=Load(name="list"),
                    args=(
                        Call(
                            func=Load(name="range"),
                            args=(Literal(value=1), Literal(value=4)),
                        ),
                    ),
                ),
            ),
            Bind(name="total", value=Call(func=Load(name="sum"), args=(Load(name="items"),))),
            Bind(name="label", value=Call(func=Load(name="str"), args=(Load(name="total"),))),
        )
    )

    result = backend.evaluate(core)

    assert result.bindings["items"] == [1, 2, 3]
    assert result.bindings["total"] == 6
    assert result.bindings["label"] == "6"


def test_core_runtime_default_map_and_filter_call_core_functions():
    backend = CoreRuntimeEvaluator()
    core = Module(
        body=(
            Bind(name="nums", value=Sequence(elements=(Literal(value=-1), Literal(value=2)))),
            Bind(
                name="positive",
                value=Function(
                    params=("x",),
                    body=Module(
                        body=(
                            Return(
                                value=CompareOp(
                                    left=Load(name="x"),
                                    ops=(">",),
                                    comparators=(Literal(value=0),),
                                )
                            ),
                        )
                    ),
                ),
            ),
            Bind(
                name="double",
                value=Function(
                    params=("x",),
                    body=Module(
                        body=(
                            Return(
                                value=Call(
                                    func=Load(name="sum"),
                                    args=(Sequence(elements=(Load(name="x"), Load(name="x"))),),
                                )
                            ),
                        )
                    ),
                ),
            ),
            Bind(
                name="kept",
                value=Call(func=Load(name="filter"), args=(Load(name="positive"), Load(name="nums"))),
            ),
            Bind(
                name="mapped",
                value=Call(func=Load(name="map"), args=(Load(name="double"), Load(name="nums"))),
            ),
        )
    )

    result = backend.evaluate(core)

    assert result.bindings["kept"] == [2]
    assert result.bindings["mapped"] == [-2, 4]


def test_core_runtime_constructs_data_values_from_data_declaration():
    backend = CoreRuntimeEvaluator()
    core = Module(
        body=(
            ConstructData(
                name="Point",
                fields=(("x", Literal(value=None)), ("y", Literal(value=None))),
            ),
            Bind(
                name="p",
                value=Call(
                    func=Load(name="Point"),
                    args=(Literal(value=3.0), Literal(value=5.0)),
                ),
            ),
            Bind(name="display", value=Call(func=Load(name="str"), args=(Load(name="p"),))),
        )
    )

    result = backend.evaluate(core)

    assert result.bindings["Point"] == "<data Point>"
    assert result.bindings["p"] == {"Point": {"x": 3.0, "y": 5.0}}
    assert result.bindings["display"] == "Point(x=3.0, y=5.0)"


def test_core_runtime_session_handles_host_builtins_and_data_declaration():
    session = create_session(mode="nomi", eval_backend="core-runtime")

    result = session.run(
        source=(
            "data Point:\n"
            "    x: float\n"
            "    y: float\n"
            "p = Point(3.0, 5.0)\n"
            "nums = list(1..3)\n"
            "total = sum(nums)\n"
            "display = str(p)\n"
        )
    )

    assert result.ok
    assert result.bindings["nums"] == [1, 2, 3]
    assert result.bindings["total"] == 6
    assert result.bindings["display"] == "Point(x=3.0, y=5.0)"
