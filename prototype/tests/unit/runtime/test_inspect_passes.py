from prototype.runtime import InspectionResult, inspect


def test_inspect_returns_desugar_pass_table():
    result = inspect(stage="passes")

    assert isinstance(result, InspectionResult)
    assert result.stage == "passes"
    assert "| pass | phase | feature | profiles |" in result.output
    assert "PiecewiseFunction" in result.output
    assert "WhereClause" in result.output
    assert result.timings["total"] >= 0
