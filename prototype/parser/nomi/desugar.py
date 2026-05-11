"""
AST desugaring passes.

Each pass transforms a Python AST by replacing compound syntactic
forms with equivalent compositions of simpler primitives. The reduced
interpreter uses these passes so it only needs to implement the
primitive forms.
"""

import ast


class _BaseDesugarer(ast.NodeTransformer):
    """Common helpers for all desugar passes.

    Handles recursive visitation of AST nodes embedded in tuples
    (block bodies stored in ast.keyword.value).
    """

    def visit_keyword(self, node):
        self.generic_visit(node)
        if isinstance(node.value, tuple):
            node.value = tuple(self._visit_tuple_item(v) for v in node.value)
        return node

    def _visit_tuple_item(self, item):
        if isinstance(item, ast.AST):
            return self.visit(item)
        if isinstance(item, list):
            return [self._visit_tuple_item(v) for v in item]
        if isinstance(item, tuple):
            return tuple(self._visit_tuple_item(v) for v in item)
        return item


class _AugAssignDesugarer(_BaseDesugarer):
    """x += y  →  x = x + y"""

    def _to_load(self, node):
        if isinstance(node, ast.Name):
            return ast.Name(id=node.id, ctx=ast.Load())
        if isinstance(node, ast.Attribute):
            return ast.Attribute(
                value=self._to_load(node.value),
                attr=node.attr,
                ctx=ast.Load(),
            )
        if isinstance(node, ast.Subscript):
            return ast.Subscript(
                value=node.value,
                slice=node.slice,
                ctx=ast.Load(),
            )
        return node

    def visit_AugAssign(self, node):
        read_target = self._to_load(node.target)
        new_value = ast.BinOp(
            left=read_target,
            op=node.op,
            right=node.value,
        )
        new_node = ast.Assign(
            targets=[node.target],
            value=new_value,
        )
        return ast.copy_location(new_node, node)


class _AssertDesugarer(_BaseDesugarer):
    """assert cond [, msg]  →  if not cond: raise AssertionError([msg])"""

    def visit_Assert(self, node):
        exc_args = [node.msg] if node.msg else []
        raise_stmt = ast.Raise(
            exc=ast.Call(
                func=ast.Name(id='AssertionError', ctx=ast.Load()),
                args=exc_args,
                keywords=[],
            ),
            cause=None,
        )
        if_node = ast.If(
            test=ast.UnaryOp(
                op=ast.Not(),
                operand=node.test,
            ),
            body=[raise_stmt],
            orelse=[],
        )
        return ast.copy_location(if_node, node)


class _DecoratorDesugarer(_BaseDesugarer):
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


def desugar_module(tree: ast.Module) -> ast.Module:
    tree = _AugAssignDesugarer().visit(tree)
    tree = _AssertDesugarer().visit(tree)
    tree = _DecoratorDesugarer().visit(tree)
    ast.fix_missing_locations(tree)
    return tree
