import pytest

from prototype.runtime import ExecutionResult, InspectionResult, execute, inspect


def test_execute_returns_structured_result_for_nomi_mode():
    result = execute(source="x = 1 + 2\n", mode="nomi")

    assert isinstance(result, ExecutionResult)
    assert result.ok
    assert result.mode == "nomi"
    assert result.profile == "default"
    assert result.pipeline.parser == "prototype.parser.nomi.usage.generate_ast"
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


def test_inspect_returns_python_ast_dump_for_mode():
    result = inspect(source="x = 1 + 2\n", mode="nomi")

    assert isinstance(result, InspectionResult)
    assert result.stage == "python_ast"
    assert result.pipeline.mode == "nomi"
    assert "Module(" in result.output
    assert "Assign(" in result.output
    assert result.timings["total"] >= 0


def test_inspect_rejects_unknown_stage_until_pipeline_stages_exist():
    with pytest.raises(ValueError, match="Unsupported inspection stage"):
        inspect(source="x = 1\n", stage="surface")
