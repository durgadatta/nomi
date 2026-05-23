from prototype.runtime import InspectionResult, inspect


def test_inspect_returns_feature_capability_table():
    result = inspect(stage="capabilities")

    assert isinstance(result, InspectionResult)
    assert result.stage == "capabilities"
    assert "| feature | target-only | parse | lower |" in result.output
    assert "piecewise-functions" in result.output
    assert result.timings["total"] >= 0


def test_inspect_returns_parser_frontend_table():
    result = inspect(stage="parser_frontends")

    assert isinstance(result, InspectionResult)
    assert result.stage == "parser_frontends"
    assert "| frontend | status | full grammar | python AST | selectable | roles |" in result.output
    assert "lark-lalr" in result.output
    assert "tree-sitter-cst" in result.output


def test_inspect_returns_core_json_payload():
    result = inspect(source="x = 1\n", stage="core_json")

    assert isinstance(result, InspectionResult)
    assert result.stage == "core_json"
    assert '"schema": "nomi.core-ir"' in result.output
    assert '"type": "Module"' in result.output
