import ast

from .base import NomiDesugarer


class Decorator(NomiDesugarer):
    """"@deco\\nfunc f(): body"  →  "func f(): body\\nf = deco(f)"

    Decorators on class definitions are desugared the same way.
    The NodeTransformer flattens returned lists into the parent body
    so multiple output statements replace a single decorated definition.
    """

    def _desugar_decorators(self, node, name):
        if not node.decorator_list:
            return node
        decorators = node.decorator_list
        node.decorator_list = []
        target = ast.Name(id=name, ctx=ast.Store())
        decorated_name = ast.Name(id=name, ctx=ast.Load())
        for deco in reversed(decorators):
            decorated_name = ast.Call(
                func=deco,
                args=[decorated_name],
                keywords=[],
            )
        assign = ast.Assign(targets=[target], value=decorated_name)
        ast.copy_location(assign, node)
        return [node, assign]

    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        if node.name is not None:
            return self._desugar_decorators(node, node.name)
        return node

    def visit_ClassDef(self, node):
        self.generic_visit(node)
        return self._desugar_decorators(node, node.name)
