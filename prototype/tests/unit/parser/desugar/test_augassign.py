import ast

from prototype.parser.nomi.desugar import desugar_module
from prototype.tests.unit.parser.desugar.conftest import find_node, is_store, is_load


class TestAugAssign:
    def test_simple_name_target(self):
        tree = ast.parse("x += 1\n")
        tree = desugar_module(tree)
        assert find_node(tree, ast.AugAssign) is None
        assign = find_node(tree, ast.Assign)
        assert assign is not None
        binop = find_node(tree, ast.BinOp)
        assert binop is not None
        assert isinstance(assign.targets[0], ast.Name)
        assert assign.targets[0].id == "x"
        assert is_store(assign.targets[0])
        assert binop.left.id == "x"
        assert is_load(binop.left)

    def test_all_operators(self):
        operators = {
            "+=": ast.Add, "-=": ast.Sub, "*=": ast.Mult, "/=": ast.Div,
            "//=": ast.FloorDiv, "%=": ast.Mod, "**=": ast.Pow,
            "&=": ast.BitAnd, "|=": ast.BitOr, "^=": ast.BitXor,
            "<<=": ast.LShift, ">>=": ast.RShift,
        }
        for aug_str, bin_op_type in operators.items():
            tree = ast.parse(f"x {aug_str} 2\n")
            tree = desugar_module(tree)
            assert find_node(tree, ast.AugAssign) is None
            binop = find_node(tree, ast.BinOp)
            assert isinstance(binop.op, bin_op_type), f"Failed for {aug_str}"

    def test_attribute_target(self):
        tree = ast.parse("obj.attr += 1\n")
        tree = desugar_module(tree)
        assert find_node(tree, ast.AugAssign) is None
        binop = find_node(tree, ast.BinOp)
        assert isinstance(binop.left, ast.Attribute)
        assert binop.left.attr == "attr"
        assert is_load(binop.left)

    def test_subscript_target(self):
        tree = ast.parse("a[0] += 1\n")
        tree = desugar_module(tree)
        assert find_node(tree, ast.AugAssign) is None
        binop = find_node(tree, ast.BinOp)
        assert isinstance(binop.left, ast.Subscript)
        assert is_load(binop.left)
