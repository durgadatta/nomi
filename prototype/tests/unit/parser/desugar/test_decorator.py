import ast

from prototype.parser.nomi.desugar import desugar_module
from prototype.tests.unit.parser.desugar.conftest import find_node


class TestDecorator:
    def test_function_with_single_decorator(self):
        tree = ast.parse("@d\ndef f():\n    pass\n")
        tree = desugar_module(tree)
        func = find_node(tree, ast.FunctionDef)
        assert func is not None
        assert func.decorator_list == []

        assigns = [n for n in ast.iter_child_nodes(tree) if isinstance(n, ast.Assign)]
        assert len(assigns) == 1
        assert isinstance(assigns[0].targets[0], ast.Name)
        assert assigns[0].targets[0].id == "f"
        assert isinstance(assigns[0].value, ast.Call)
        assert isinstance(assigns[0].value.func, ast.Name)
        assert assigns[0].value.func.id == "d"

    def test_function_with_multiple_decorators(self):
        tree = ast.parse("@d2\n@d1(x)\ndef f():\n    pass\n")
        tree = desugar_module(tree)
        func = find_node(tree, ast.FunctionDef)
        assert func.decorator_list == []

        assigns = [n for n in ast.iter_child_nodes(tree) if isinstance(n, ast.Assign)]
        assert len(assigns) == 1
        call = assigns[0].value
        assert isinstance(call, ast.Call)
        assert isinstance(call.func, ast.Name)
        assert call.func.id == "d2"
        assert isinstance(call.args[0], ast.Call)
        assert isinstance(call.args[0].func, ast.Call)
        assert call.args[0].func.func.id == "d1"

    def test_function_without_decorators_unchanged(self):
        tree = ast.parse("def f():\n    pass\n")
        tree = desugar_module(tree)
        func = find_node(tree, ast.FunctionDef)
        assert func is not None
        assigns = [n for n in ast.iter_child_nodes(tree) if isinstance(n, ast.Assign)]
        assert len(assigns) == 0

    def test_class_decorator(self):
        tree = ast.parse("@register\nclass MyClass:\n    pass\n")
        tree = desugar_module(tree)
        cls = find_node(tree, ast.ClassDef)
        assert cls is not None
        assert cls.decorator_list == []
        assigns = [n for n in ast.iter_child_nodes(tree) if isinstance(n, ast.Assign)]
        assert len(assigns) == 1
        assert assigns[0].targets[0].id == "MyClass"
