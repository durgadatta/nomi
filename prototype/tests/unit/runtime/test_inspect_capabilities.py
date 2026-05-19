from prototype.runtime import InspectionResult, inspect


def test_inspect_returns_feature_capability_table():
    result = inspect(stage="capabilities")

    assert isinstance(result, InspectionResult)
    assert result.stage == "capabilities"
    assert "| feature | target-only | parse | lower |" in result.output
    assert "piecewise-functions" in result.output
    assert result.timings["total"] >= 0
