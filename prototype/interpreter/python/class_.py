import ast
from typing import Any

class ClassMixin:
    def eval_ClassDef(self, node: ast.ClassDef) -> None:
        bases = [self.eval(b) for b in node.bases]
        class_env = self.env_class(self, parent=self.current_env)
        with self.this_env(class_env):
            for stmt in node.body:
                self.eval(stmt)
                if isinstance(stmt, ast.FunctionDef):
                    func = class_env.bindings.get(stmt.name)
                    if func:
                        func.closure_env = class_env
                        func.ast_node = stmt
        class_dict = class_env.bindings
        try:
            cls = type(node.name, tuple(bases), class_dict)
        except Exception as e:
            raise RuntimeError(f"Error creating class '{node.name}' at line {self.get_lineno(node)}: {str(e)}") from e
        cls = self.apply_decorators(cls, node.decorator_list)
        self.current_env.set(node.name, cls)
        

    def eval_Attribute(self, node: ast.Attribute) -> Any:
        value = self.eval(node.value)
        try:
            return getattr(value, node.attr)
        except AttributeError:
            raise AttributeError(f"'{type(value).__name__}' object has no attribute '{node.attr}' at line {self.get_lineno(node)}")

    def eval_Subscript(self, node: ast.Subscript) -> Any:
        value = self.eval(node.value)
        slice_ = self.eval(node.slice)
        try:
            return value[slice_]
        except (IndexError, KeyError) as e:
            raise IndexError(f"Subscript error at line {self.get_lineno(node)}: {str(e)}") from e
        
