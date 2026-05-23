"""Core Runtime support for data-access nodes."""

from prototype.runtime import create_session
from prototype.runtime.backends.core_runtime import CoreRuntimeEvaluator
from prototype.syntax.core import (
    Bind,
    ConditionalExpr,
    GetItem,
    Literal,
    MappingLiteral,
    Module,
    Sequence,
    Spread,
)


def test_core_runtime_evaluates_mapping_and_subscript():
    backend = CoreRuntimeEvaluator()
    core = Module(
        body=(
            Bind(
                name="data",
                value=MappingLiteral(
                    entries=((Literal(value="name"), Literal(value="Nomi")),)
                ),
            ),
            Bind(
                name="name",
                value=GetItem(
                    object_=GetItem(
                        object_=MappingLiteral(
                            entries=(
                                (
                                    Literal(value="user"),
                                    MappingLiteral(
                                        entries=(
                                            (
                                                Literal(value="name"),
                                                Literal(value="Nomi"),
                                            ),
                                        )
                                    ),
                                ),
                            )
                        ),
                        key=Literal(value="user"),
                    ),
                    key=Literal(value="name"),
                ),
            ),
        )
    )

    result = backend.evaluate(core)

    assert result.bindings["data"] == {"name": "Nomi"}
    assert result.bindings["name"] == "Nomi"


def test_core_runtime_evaluates_conditional_expression_and_spread():
    backend = CoreRuntimeEvaluator()
    core = Module(
        body=(
            Bind(
                name="choice",
                value=ConditionalExpr(
                    test=Literal(value=True),
                    then_value=Literal(value="yes"),
                    else_value=Literal(value="no"),
                ),
            ),
            Bind(
                name="items",
                value=Sequence(
                    elements=(
                        Literal(value=1),
                        Spread(value=Sequence(elements=(Literal(value=2), Literal(value=3)))),
                        Literal(value=4),
                    )
                ),
            ),
        )
    )

    result = backend.evaluate(core)

    assert result.bindings["choice"] == "yes"
    assert result.bindings["items"] == [1, 2, 3, 4]


def test_core_runtime_session_runs_data_access_source():
    session = create_session(mode="nomi", eval_backend="core-runtime")

    result = session.run(
        source=(
            "data = {'name': 'Nomi', 'items': [1, 2]}\n"
            "name = data['name']\n"
            "items = [0, *data['items'], 3]\n"
            "display = name if data else 'missing'\n"
        )
    )

    assert result.ok
    assert result.bindings["name"] == "Nomi"
    assert result.bindings["items"] == [0, 1, 2, 3]
    assert result.bindings["display"] == "Nomi"
