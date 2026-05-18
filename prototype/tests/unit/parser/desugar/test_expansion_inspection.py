import ast

from prototype.parser.nomi.desugar.pipeline import render_desugar_expansion


def test_render_desugar_expansion_shows_changed_pass_before_and_after():
    tree = ast.parse("x += 1\n")

    output = render_desugar_expansion(tree)

    assert output.startswith("# Desugar expansion (reduced)")
    assert "## AugAssign" in output
    assert "- normal forms: assignment, binary-operation" in output
    assert "- changed: yes" in output
    assert "before:" in output
    assert "AugAssign(" in output
    assert "after:" in output
    assert "Assign(" in output
    assert "BinOp(" in output


def test_render_desugar_expansion_respects_default_profile():
    tree = ast.parse("x += 1\n")

    output = render_desugar_expansion(tree, profile="default")

    assert output.startswith("# Desugar expansion (default)")
    assert "## PiecewiseFunction" in output
    assert "## AugAssign" not in output
