"""Core Runtime exception fencing and handler matching."""

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
    Return,
)


def test_native_host_exception_becomes_error_value():
    backend = CoreRuntimeEvaluator()
    core = Module(
        body=(
            Bind(
                name="value",
                value=Call(func=Load(name="int"), args=(Literal(value="nan"),)),
            ),
        )
    )

    result = backend.eval(core.body[0])

    assert isinstance(result, ErrorValue)
    assert result.kind == "ValueError"


def test_core_runtime_handle_matches_native_error_kind():
    backend = CoreRuntimeEvaluator()
    core = Module(
        body=(
            Bind(
                name="parsed",
                value=Handle(
                    body=Module(
                        body=(
                            Call(
                                func=Load(name="int"),
                                args=(Literal(value="nan"),),
                            ),
                        )
                    ),
                    handlers=(
                        PatternTest(
                            pattern=Load(name="ValueError"),
                            body=Module(body=(Literal(value=0),)),
                        ),
                    ),
                ),
            ),
        )
    )

    result = backend.evaluate(core)

    assert result.bindings["parsed"] == 0


def test_unhandled_native_error_raises_at_module_boundary():
    backend = CoreRuntimeEvaluator()
    core = Module(
        body=(Call(func=Load(name="int"), args=(Literal(value="nan"),)),)
    )

    with pytest.raises(RuntimeError, match="invalid literal"):
        backend.evaluate(core)


def test_core_runtime_session_handles_try_expression_lowering():
    session = create_session(mode="nomi", eval_backend="core-runtime")

    result = session.run(
        source=(
            "parsed = try int('not-a-number') except ValueError: 0\n"
        )
    )

    assert result.ok
    assert result.bindings["parsed"] == 0
