from prototype.runtime import InspectionResult, inspect


def test_inspect_returns_desugar_expansion_view_for_nomi_mode():
    result = inspect(source="scale = _ * 3\n", stage="expansions")

    assert isinstance(result, InspectionResult)
    assert result.stage == "expansions"
    assert "# Desugar expansion (default)" in result.output
    assert "## UnderscoreLambda" in result.output
    assert "- changed: yes" in result.output
    assert "canonical-function-literal" in result.output
