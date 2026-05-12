import ast

from prototype.parser.nomi.desugar import desugar_module
from prototype.tests.unit.parser.desugar.conftest import find_node


class TestPass:
    def test_pass_removed(self):
        tree = ast.parse("pass\n")
        tree = desugar_module(tree)
        assert find_node(tree, ast.Pass) is None

    def test_pass_replaced_with_expr(self):
        tree = ast.parse("if True:\n    pass\n")
        tree = desugar_module(tree)
        assert find_node(tree, ast.Pass) is None
        if_node = find_node(tree, ast.If)
        assert isinstance(if_node.body[0], ast.Expr)
        assert isinstance(if_node.body[0].value, ast.Constant)
        assert if_node.body[0].value.value == 0
