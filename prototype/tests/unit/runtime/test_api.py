import ast

import pytest

from prototype.parser.nomi import frontend as parser_frontends
from prototype.parser.nomi.frontend import ParserFrontendCapabilities, ParserFrontendSpec
from prototype.runtime import ExecutionResult, InspectionResult, execute, inspect


def test_execute_returns_structured_result_for_nomi_mode():
    result = execute(source="x = 1 + 2\n", mode="nomi")

    assert isinstance(result, ExecutionResult)
    assert result.ok
    assert result.mode == "nomi"
    assert result.profile == "default"
    assert result.pipeline.parser == "prototype.parser.nomi.usage.generate_ast"
    assert result.pipeline.parser_frontend == "lark-lalr"
    assert result.bindings["x"] == 3
    assert result.timings["total"] >= 0


def test_execute_can_return_exception_without_raising():
    result = execute(
        source="x = 1 / 0\n",
        mode="python",
        raise_on_error=False,
    )

    assert not result.ok
    assert result.exception is not None
    assert result.bindings == {}
    assert result.timings["total"] >= 0


def test_execute_rejects_unknown_profile_until_feature_profiles_exist():
    with pytest.raises(ValueError, match="Unsupported runtime profile"):
        execute(source="x = 1\n", profile="lab")


def test_execute_can_preflight_with_named_parser_frontend(monkeypatch):
    calls = []

    class FakeFrontend:
        def parse_accepts(self, *, code=None, filename=None):
            calls.append((code, filename))

    monkeypatch.setitem(parser_frontends._FRONTENDS, "test-gate", FakeFrontend())

    result = execute(source="x = 1\n", mode="nomi", parser_frontend="test-gate")

    assert result.ok
    assert result.pipeline.parser_frontend == "test-gate"
    assert result.bindings["x"] == 1
    assert calls == [("x = 1\n", None)]


def test_execute_uses_python_ast_capable_parser_frontend(monkeypatch):
    calls = []

    class FakeFrontend:
        spec = ParserFrontendSpec(
            name="test-ast",
            status="test",
            grammar_format="test",
            implementation="test",
            cst_artifact="test",
            output_contract="test",
            capabilities=ParserFrontendCapabilities(lower_to_python_ast=True),
        )

        def generate_python_ast(self, *, code=None, filename=None):
            calls.append((code, filename))
            return ast.Module(
                body=[
                    ast.Assign(
                        targets=[ast.Name(id="x", ctx=ast.Store())],
                        value=ast.Constant(value=42),
                    )
                ],
                type_ignores=[],
            )

    monkeypatch.setitem(parser_frontends._FRONTENDS, "test-ast", FakeFrontend())

    result = execute(source="x = 1\n", mode="nomi", parser_frontend="test-ast")

    assert result.ok
    assert result.bindings["x"] == 42
    assert calls == [("x = 1\n", None)]


def test_execute_parser_frontend_gate_is_nomi_only(monkeypatch):
    class FakeFrontend:
        def parse_accepts(self, *, code=None, filename=None):
            raise AssertionError("python mode should fail before parsing")

    monkeypatch.setitem(parser_frontends._FRONTENDS, "test-gate", FakeFrontend())

    with pytest.raises(ValueError, match="Nomi parser modes"):
        execute(source="x = 1\n", mode="python", parser_frontend="test-gate")


def test_inspect_returns_python_ast_dump_for_mode():
    result = inspect(source="x = 1 + 2\n", mode="nomi")

    assert isinstance(result, InspectionResult)
    assert result.stage == "python_ast"
    assert result.pipeline.mode == "nomi"
    assert result.pipeline.parser_frontend == "lark-lalr"
    assert "Module(" in result.output
    assert "Assign(" in result.output
    assert result.timings["total"] >= 0


def test_inspect_returns_feature_layer_table():
    result = inspect(stage="features")

    assert isinstance(result, InspectionResult)
    assert result.stage == "features"
    assert "| feature | layer | semantic forms |" in result.output
    assert "piecewise-functions" in result.output
    assert result.timings["total"] >= 0


def test_inspect_can_preflight_with_named_parser_frontend(monkeypatch):
    calls = []

    class FakeFrontend:
        def parse_accepts(self, *, code=None, filename=None):
            calls.append((code, filename))

    monkeypatch.setitem(parser_frontends._FRONTENDS, "test-gate", FakeFrontend())

    result = inspect(source="x = 1\n", parser_frontend="test-gate")

    assert result.pipeline.parser_frontend == "test-gate"
    assert "Module(" in result.output
    assert calls == [("x = 1\n", None)]


def test_inspect_uses_python_ast_capable_parser_frontend(monkeypatch):
    class FakeFrontend:
        spec = ParserFrontendSpec(
            name="test-ast",
            status="test",
            grammar_format="test",
            implementation="test",
            cst_artifact="test",
            output_contract="test",
            capabilities=ParserFrontendCapabilities(lower_to_python_ast=True),
        )

        def generate_python_ast(self, *, code=None, filename=None):
            return ast.Module(
                body=[
                    ast.Assign(
                        targets=[ast.Name(id="from_frontend", ctx=ast.Store())],
                        value=ast.Constant(value=True),
                    )
                ],
                type_ignores=[],
            )

    monkeypatch.setitem(parser_frontends._FRONTENDS, "test-ast", FakeFrontend())

    result = inspect(source="x = 1\n", parser_frontend="test-ast")

    assert result.pipeline.parser_frontend == "test-ast"
    assert "from_frontend" in result.output


def test_inspect_returns_core_dump_for_tiny_subset():
    result = inspect(source="x = 1\n", stage="core")

    assert result.stage == "core"
    assert result.output == "\n".join(
        [
            "Module",
            "  Bind('x')",
            "    Literal(1)",
        ]
    )


def test_inspect_rejects_unknown_stage_until_more_pipeline_stages_exist():
    with pytest.raises(ValueError, match="Unsupported inspection stage"):
        inspect(source="x = 1\n", stage="surface")
