import pytest

from prototype.runtime import ExecutionResult, execute


def test_execute_returns_structured_result_for_nomi_mode():
    result = execute(source="x = 1 + 2\n", mode="nomi")

    assert isinstance(result, ExecutionResult)
    assert result.ok
    assert result.mode == "nomi"
    assert result.profile == "default"
    assert result.bindings["x"] == 3


def test_execute_can_return_exception_without_raising():
    result = execute(
        source="x = 1 / 0\n",
        mode="python",
        raise_on_error=False,
    )

    assert not result.ok
    assert result.exception is not None
    assert result.bindings == {}


def test_execute_rejects_unknown_profile_until_feature_profiles_exist():
    with pytest.raises(ValueError, match="Unsupported runtime profile"):
        execute(source="x = 1\n", profile="lab")
