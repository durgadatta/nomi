import ast

from prototype.parser.nomi.desugar import desugar_module
from prototype.tests.unit.parser.desugar.conftest import find_node


class TestFString:
    def test_simple_fstring(self):
        tree = ast.parse("f'hello {name}'\n")
        tree = desugar_module(tree)
        assert find_node(tree, ast.JoinedStr) is None
        assert find_node(tree, ast.FormattedValue) is None
        binop = find_node(tree, ast.BinOp)
        assert isinstance(binop.op, ast.Add)

    def test_format_spec(self):
        tree = ast.parse("f'{x:.2f}'\n")
        tree = desugar_module(tree)
        assert find_node(tree, ast.FormattedValue) is None

    def test_conversion(self):
        tree = ast.parse("f'{x!r}'\n")
        tree = desugar_module(tree)
        assert find_node(tree, ast.FormattedValue) is None
        assert find_node(tree, ast.JoinedStr) is None

    def test_empty_fstring(self):
        tree = ast.parse("f''\n")
        tree = desugar_module(tree)
        assert find_node(tree, ast.JoinedStr) is None
