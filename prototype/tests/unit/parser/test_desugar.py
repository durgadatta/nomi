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


class TestDecoratorDesugar:
    def test_function_with_single_decorator(self):
        tree = ast.parse(
            "@d\n"
            "def f():\n"
            "    pass\n"
        )
        tree = desugar_module(tree)

        func = find_node(tree, ast.FunctionDef)
        assert func is not None
        assert func.decorator_list == [], "decorator_list should be cleared"

        assigns = [n for n in ast.iter_child_nodes(tree) if isinstance(n, ast.Assign)]
        assert len(assigns) == 1
        assert isinstance(assigns[0].targets[0], ast.Name)
        assert assigns[0].targets[0].id == "f"
        assert isinstance(assigns[0].value, ast.Call)
        assert isinstance(assigns[0].value.func, ast.Name)
        assert assigns[0].value.func.id == "d"

    def test_function_with_multiple_decorators(self):
        tree = ast.parse(
            "@d2\n"
            "@d1(x)\n"
            "def f():\n"
            "    pass\n"
        )
        tree = desugar_module(tree)

        func = find_node(tree, ast.FunctionDef)
        assert func.decorator_list == []

        assigns = [n for n in ast.iter_child_nodes(tree) if isinstance(n, ast.Assign)]
        assert len(assigns) == 1
        call = assigns[0].value
        assert isinstance(call, ast.Call)
        assert isinstance(call.func, ast.Name)
        assert call.func.id == "d2"  # outermost decorator first
        assert isinstance(call.args[0], ast.Call)
        assert isinstance(call.args[0].func, ast.Call)
        assert call.args[0].func.func.id == "d1"

    def test_function_without_decorators_unchanged(self):
        tree = ast.parse("def f():\n    pass\n")
        tree = desugar_module(tree)
        func = find_node(tree, ast.FunctionDef)
        assert func is not None
        # No extra assigns
        assigns = [n for n in ast.iter_child_nodes(tree) if isinstance(n, ast.Assign)]
        assert len(assigns) == 0

    def test_class_decorator(self):
        tree = ast.parse(
            "@register\n"
            "class MyClass:\n"
            "    pass\n"
        )
        tree = desugar_module(tree)

        cls = find_node(tree, ast.ClassDef)
        assert cls is not None
        assert cls.decorator_list == []

        assigns = [n for n in ast.iter_child_nodes(tree) if isinstance(n, ast.Assign)]
        assert len(assigns) == 1
        assert assigns[0].targets[0].id == "MyClass"


class TestPassDesugar:
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


class TestWithDesugar:
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


class TestFStringDesugar:
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
