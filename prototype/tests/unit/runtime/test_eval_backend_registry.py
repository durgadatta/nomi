"""Tests for the eval backend registry."""

import pytest

from prototype.runtime.backends import (
    EvalBackendCapabilities,
    EvalBackendResult,
    EvalBackendSpec,
    get_eval_backend,
    get_selectable_eval_backends,
    register_backend,
    render_eval_backend_table,
)


def test_default_capabilities_all_false():
    caps = EvalBackendCapabilities()
    for field_name in (
        "evaluates_native_ir",
        "lowers_to_python_ast",
        "supports_full_language",
        "supports_blocks",
        "supports_exceptions",
        "supports_resume",
        "supports_python_interop",
        "supports_source_maps",
        "selectable_for_session_execution",
        "selectable_for_browser_execution",
        "default_for_cli",
        "default_for_web",
        "selectable_for_execution",
    ):
        assert getattr(caps, field_name) is False
    assert caps.requires_host_capabilities == ()


def test_capabilities_can_be_selectively_enabled():
    caps = EvalBackendCapabilities(
        lowers_to_python_ast=True,
        selectable_for_session_execution=True,
        selectable_for_execution=True,
    )
    assert caps.lowers_to_python_ast is True
    assert caps.selectable_for_session_execution is True
    assert caps.selectable_for_execution is True
    assert caps.evaluates_native_ir is False


def test_spec_requires_capabilities():
    spec = EvalBackendSpec(
        name="test",
        status="experimental",
        ir_contract="Core IR",
        implementation="test",
        output_contract="bindings",
    )
    assert spec.name == "test"
    assert spec.capabilities.selectable_for_session_execution is False


def test_backend_result_stores_bindings_and_value():
    result = EvalBackendResult(bindings={"x": 1}, value=1, has_value=True)
    assert result.bindings == {"x": 1}
    assert result.value == 1
    assert result.has_value is True


def test_backend_result_default_no_value():
    result = EvalBackendResult(bindings={})
    assert result.has_value is False
    assert result.value is None
    assert result.diagnostics == ()
    assert result.stdout == ""
    assert result.stderr == ""


def test_register_and_get_backend():
    class FakeBackend:
        spec = EvalBackendSpec(
            name="fake",
            status="test",
            ir_contract="none",
            implementation="none",
            output_contract="none",
            capabilities=EvalBackendCapabilities(selectable_for_execution=True),
        )

    register_backend("fake", FakeBackend())
    backend = get_eval_backend("fake")
    assert backend.spec.name == "fake"


def test_get_unknown_backend_raises():
    with pytest.raises(ValueError, match="Unknown eval backend"):
        get_eval_backend("nonexistent")


def test_get_selectable_backends():
    class Selectable:
        spec = EvalBackendSpec(
            name="selectable",
            status="ok",
            ir_contract="nope",
            implementation="nope",
            output_contract="nope",
            capabilities=EvalBackendCapabilities(selectable_for_execution=True),
        )

    class NotSelectable:
        spec = EvalBackendSpec(
            name="not-selectable",
            status="ok",
            ir_contract="nope",
            implementation="nope",
            output_contract="nope",
            capabilities=EvalBackendCapabilities(selectable_for_execution=False),
        )

    register_backend("selectable", Selectable())
    register_backend("not-selectable", NotSelectable())

    names = get_selectable_eval_backends()
    assert "selectable" in names
    assert "not-selectable" not in names


def test_render_eval_backend_table_includes_registered():
    class B:
        spec = EvalBackendSpec(
            name="test-b",
            status="demo",
            ir_contract="Core IR",
            implementation="test",
            output_contract="bindings",
            capabilities=EvalBackendCapabilities(selectable_for_execution=False),
        )

    register_backend("test-b", B())
    table = render_eval_backend_table()
    assert "test-b" in table
    assert "demo" in table
    assert "no" in table


def test_python_ast_is_registered():
    """python-ast should expose capabilities even though it is mode-constructed."""
    table = render_eval_backend_table()
    backend = get_eval_backend("python-ast")

    assert backend.spec.name == "python-ast"
    assert backend.spec.capabilities.selectable_for_session_execution is True
    assert backend.spec.capabilities.selectable_for_execution is True
    assert "python-ast" in table
    assert "implemented" in table


def test_js_core_runtime_is_registered():
    table = render_eval_backend_table()
    backend = get_eval_backend("js-core-runtime")

    assert backend.spec.capabilities.selectable_for_browser_execution is True
    assert backend.spec.capabilities.default_for_web is True
    assert "js-core-runtime" in table
    assert "Core IR JSON" in table
