from prototype.parser.nomi.desugar.pipeline import render_desugar_pass_table


def test_render_desugar_pass_table_shows_phase_order_and_contracts():
    table = render_desugar_pass_table()

    assert table.startswith("| pass | phase | feature | profiles |")
    assert "| PiecewiseFunction | syntax | piecewise-functions |" in table
    assert "| WhereClause | semantic | where-clauses |" in table
    assert "| AugAssign | syntax | aug-assign-desugar |" in table
    assert "AugAssign" in table
    assert "WhereClause" in table
    assert table.index("AugAssign") < table.index("WhereClause")


def test_render_desugar_pass_table_can_show_default_profile():
    table = render_desugar_pass_table(profile="default")

    assert "PiecewiseFunction" in table
    assert "WhereClause" in table
    assert "AugAssign" not in table
