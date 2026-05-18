from prototype.parser.nomi.desugar.pipeline import (
    DESUGAR_PASSES,
    render_desugar_pass_table,
)


def test_active_desugar_passes_declare_outputs_and_normal_forms():
    for pass_cls in DESUGAR_PASSES:
        assert pass_cls.input_node_types, (
            f"{pass_cls.__name__} must declare input_node_types"
        )
        assert all(isinstance(node_type, type) for node_type in pass_cls.input_node_types)
        assert pass_cls.produced_node_types, (
            f"{pass_cls.__name__} must declare produced_node_types"
        )
        assert all(isinstance(node_type, type) for node_type in pass_cls.produced_node_types)
        assert pass_cls.normal_forms, f"{pass_cls.__name__} must declare normal_forms"
        assert all(isinstance(form, str) for form in pass_cls.normal_forms)


def test_render_desugar_pass_table_shows_phase_order_and_contracts():
    table = render_desugar_pass_table()

    assert table.startswith("| pass | phase | feature | profiles | inputs |")
    assert (
        "| PiecewiseFunction | syntax | piecewise-functions | default, reduced | "
        "FunctionDef | - | FunctionDef, Match, match_case | canonical-function, "
        "match-dispatch | - |"
    ) in table
    assert (
        "| WhereClause | semantic | where-clauses | default, reduced | "
        "Assign, Expr, FunctionDef | - | "
        "FunctionDef, Return, Call, Assign, Expr | local-binding-rewrite, "
        "function-call | PiecewiseFunction |"
    ) in table
    assert (
        "| AugAssign | syntax | aug-assign-desugar | reduced | AugAssign | "
        "AugAssign | Assign, BinOp | assignment, binary-operation | - |"
    ) in table
    assert "AugAssign" in table
    assert "WhereClause" in table
    assert table.index("AugAssign") < table.index("WhereClause")


def test_render_desugar_pass_table_can_show_default_profile():
    table = render_desugar_pass_table(profile="default")

    assert "PiecewiseFunction" in table
    assert "WhereClause" in table
    assert "AugAssign" not in table
