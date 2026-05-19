from prototype.runtime import inspect


def test_pass_inspection_uses_default_nomi_profile():
    result = inspect(stage="passes", mode="nomi")

    assert "PiecewiseFunction" in result.output
    assert "WhereClause" in result.output
    assert "AugAssign" not in result.output
    assert "Decorator" not in result.output


def test_pass_inspection_uses_full_pipeline_for_reduced_mode():
    result = inspect(stage="passes", mode="reduced")

    assert "PiecewiseFunction" in result.output
    assert "AugAssign" in result.output
    assert "Decorator" in result.output
