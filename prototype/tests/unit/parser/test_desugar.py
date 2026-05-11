import ast
import textwrap

from prototype.parser.nomi.desugar import desugar_module


def dedent(code):
    return textwrap.dedent(code).strip()


def find_node(tree, node_type):
    for node in ast.walk(tree):
        if isinstance(node, node_type):
            return node
    return None


def is_store(node):
    return isinstance(node.ctx, ast.Store)


def is_load(node):
    return isinstance(node.ctx, ast.Load)


class TestAugAssignDesugar:
    def test_simple_name_target(self):
        tree = ast.parse("x += 1\n")
        tree = desugar_module(tree)

        assert find_node(tree, ast.AugAssign) is None, "AugAssign should be removed"
        assign = find_node(tree, ast.Assign)
        assert assign is not None, "Should have Assign"
        binop = find_node(tree, ast.BinOp)
        assert binop is not None, "Should have BinOp"
        assert isinstance(assign.targets[0], ast.Name)
        assert assign.targets[0].id == "x"
        assert is_store(assign.targets[0])
        assert binop.left.id == "x"
        assert is_load(binop.left)

    def test_all_operators(self):
        operators = {
            "+=": ast.Add,
            "-=": ast.Sub,
            "*=": ast.Mult,
            "/=": ast.Div,
            "//=": ast.FloorDiv,
            "%=": ast.Mod,
            "**=": ast.Pow,
            "&=": ast.BitAnd,
            "|=": ast.BitOr,
            "^=": ast.BitXor,
            "<<=": ast.LShift,
            ">>=": ast.RShift,
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


class TestAssertDesugar:
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
