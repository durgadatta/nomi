import ast

from prototype.parser.nomi.desugar import desugar_module
from prototype.tests.unit.parser.desugar.conftest import find_node


class TestWith:
    def test_simple_with(self):
        tree = ast.parse("with open('f') as f:\n    pass\n")
        tree = desugar_module(tree)
        assert find_node(tree, ast.With) is None
        assert find_node(tree, ast.Try) is not None
        assert find_node(tree, ast.Pass) is None

    def test_with_multiple_items(self):
        tree = ast.parse("with a as x, b as y:\n    pass\n")
        tree = desugar_module(tree)
        assert find_node(tree, ast.With) is None
        tries = [n for n in ast.walk(tree) if isinstance(n, ast.Try)]
        assert len(tries) == 2

    def test_with_no_as(self):
        tree = ast.parse("with lock:\n    pass\n")
        tree = desugar_module(tree)
        assert find_node(tree, ast.With) is None
