"""Core Runtime pattern matching support."""

from prototype.runtime.backends.core_runtime import CoreRuntimeEvaluator
from prototype.syntax.core import (
    Bind,
    Literal,
    Load,
    MappingLiteral,
    Match,
    Module,
    PatternTest,
    Sequence,
    Spread,
)


def test_core_runtime_matches_literal_pattern():
    backend = CoreRuntimeEvaluator()
    core = Module(
        body=(
            Match(
                subject=Literal(value=2),
                cases=(
                    PatternTest(
                        pattern=Literal(value=1),
                        body=Module(body=(Bind(name="label", value=Literal(value="one")),)),
                    ),
                    PatternTest(
                        pattern=Literal(value=2),
                        body=Module(body=(Bind(name="label", value=Literal(value="two")),)),
                    ),
                ),
            ),
        )
    )

    result = backend.evaluate(core)

    assert result.bindings["label"] == "two"


def test_core_runtime_matches_sequence_capture_pattern():
    backend = CoreRuntimeEvaluator()
    core = Module(
        body=(
            Match(
                subject=Sequence(elements=(Literal(value=10), Literal(value=20))),
                cases=(
                    PatternTest(
                        pattern=Sequence(elements=(Load(name="head"), Load(name="tail"))),
                        body=Module(body=(Bind(name="result", value=Load(name="head")),)),
                    ),
                ),
            ),
        )
    )

    result = backend.evaluate(core)

    assert result.bindings["head"] == 10
    assert result.bindings["tail"] == 20
    assert result.bindings["result"] == 10


def test_core_runtime_matches_mapping_capture_pattern():
    backend = CoreRuntimeEvaluator()
    core = Module(
        body=(
            Match(
                subject=MappingLiteral(
                    entries=((Literal(value="theme"), Literal(value="dark")),)
                ),
                cases=(
                    PatternTest(
                        pattern=MappingLiteral(
                            entries=((Literal(value="theme"), Load(name="theme")),)
                        ),
                        body=Module(body=(Bind(name="result", value=Load(name="theme")),)),
                    ),
                ),
            ),
        )
    )

    result = backend.evaluate(core)

    assert result.bindings["theme"] == "dark"
    assert result.bindings["result"] == "dark"


def test_core_runtime_rolls_back_failed_pattern_captures():
    backend = CoreRuntimeEvaluator()
    core = Module(
        body=(
            Match(
                subject=Sequence(elements=(Literal(value=1),)),
                cases=(
                    PatternTest(
                        pattern=Sequence(elements=(Load(name="head"), Load(name="tail"))),
                        body=Module(body=(Bind(name="result", value=Load(name="head")),)),
                    ),
                    PatternTest(
                        pattern=Load(name="_"),
                        body=Module(body=(Bind(name="result", value=Literal(value=None)),)),
                    ),
                ),
            ),
        )
    )

    result = backend.evaluate(core)

    assert result.bindings["result"] is None
    assert "head" not in result.bindings


def test_core_runtime_matches_sequence_rest_pattern():
    backend = CoreRuntimeEvaluator()
    core = Module(
        body=(
            Match(
                subject=Sequence(
                    elements=(
                        Literal(value=10),
                        Literal(value=20),
                        Literal(value=30),
                    )
                ),
                cases=(
                    PatternTest(
                        pattern=Sequence(
                            elements=(
                                Load(name="head"),
                                Spread(value=Load(name="rest")),
                            )
                        ),
                        body=Module(body=(Bind(name="result", value=Load(name="rest")),)),
                    ),
                ),
            ),
        )
    )

    result = backend.evaluate(core)

    assert result.bindings["head"] == 10
    assert result.bindings["rest"] == [20, 30]
    assert result.bindings["result"] == [20, 30]
