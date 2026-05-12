import ast

from prototype.parser.nomi.desugar import desugar_module
from prototype.tests.unit.parser.desugar.conftest import find_node


class TestAssert:
    def test_bare_assert(self):
        tree = ast.parse("assert x\n")
        tree = desugar_module(tree)
        assert find_node(tree, ast.Assert) is None
        if_node = find_node(tree, ast.If)
        assert if_node is not None
        assert isinstance(if_node.test, ast.UnaryOp)
        assert isinstance(if_node.test.op, ast.Not)
        assert isinstance(if_node.body[0], ast.Raise)

    def test_assert_with_message(self):
        tree = ast.parse("assert False, 'oh no'\n")
        tree = desugar_module(tree)
        assert find_node(tree, ast.Assert) is None
        raise_stmt = find_node(tree, ast.Raise)
        assert isinstance(raise_stmt.exc, ast.Call)
        assert isinstance(raise_stmt.exc.func, ast.Name)
        assert raise_stmt.exc.func.id == "AssertionError"
        assert raise_stmt.exc.args[0].value == "oh no"
