import ast
from lark import Token

from prototype.syntax.surface import _is_stmt_or_surface

from . import ensure_store

class StatementMixin():
    def nonlocal_stmt(self, items):
        return ast.Nonlocal(names=items)

    def global_stmt(self, items):
        return ast.Global(names=items)

    def suite(self, items):
        out = []
        for it in items:
            if isinstance(it, list):
                out.extend(it)
            elif _is_stmt_or_surface(it):
                out.append(it)
        return out

    def simple_stmt(self, items):
        out = []
        for it in items:
            if isinstance(it, list):
                out.extend(it)
            elif _is_stmt_or_surface(it):
                out.append(it)
        return out

    def expr_stmt(self, items):
        # detect simple assignment left '=' right
        for i, it in enumerate(items):
            if isinstance(it, Token) and it.value == '=':
                left = items[0]; right = items[i+1] if i+1 < len(items) else None
                target = ensure_store(left) if isinstance(left, (ast.Name, ast.Tuple, ast.List)) else left
                return ast.Assign(targets=[target], value=right)
        return ast.Expr(value=items[0])

    def pass_stmt(self, items): return ast.Pass()
    def break_stmt(self, items): return ast.Break()
    def continue_stmt(self, items): return ast.Continue()

    def del_stmt(self, items):
        """
        items: list of expressions / targets to delete
        Returns ast.Delete node.
        """
        targets = []
        for it in items:
            # Convert Name / Attribute / Subscript appropriately
            if isinstance(it, ast.Name):
                targets.append(ast.Name(id=it.id, ctx=ast.Del()))
            elif isinstance(it, ast.Attribute):
                # Attribute can be del target; the value stays the same
                targets.append(ast.Attribute(
                    value=it.value,
                    attr=it.attr,
                    ctx=ast.Del()
                ))
            elif isinstance(it, ast.Subscript):
                targets.append(ast.Subscript(
                    value=it.value,
                    slice=it.slice,
                    ctx=ast.Del()
                ))
            else:
                # Possibly other complex targets (Tuple, List)
                if isinstance(it, (ast.Tuple, ast.List)):
                    # recursively set ctx=Del for all elements
                    targets.append(self._del_target(it))
                else:
                    raise TypeError(f"Unsupported del target: {it!r}")
        return ast.Delete(targets=targets)

    def _del_target(self, node):
        """
        Recursively set ctx=Del for Tuple/List elements.
        """
        if isinstance(node, ast.Tuple):
            return ast.Tuple(
                elts=[self._del_target(e) for e in node.elts],
                ctx=ast.Del()
            )
        elif isinstance(node, ast.List):
            return ast.List(
                elts=[self._del_target(e) for e in node.elts],
                ctx=ast.Del()
            )
        elif isinstance(node, ast.Name):
            return ast.Name(id=node.id, ctx=ast.Del())
        elif isinstance(node, ast.Attribute):
            return ast.Attribute(value=node.value, attr=node.attr, ctx=ast.Del())
        elif isinstance(node, ast.Subscript):
            return ast.Subscript(value=node.value, slice=node.slice, ctx=ast.Del())
        else:
            raise TypeError(f"Unsupported del target in _del_target: {node!r}")



