import ast

from .base import NomiDesugarer


class FString(NomiDesugarer):
    """Desugar f-strings into string concatenation and format calls.

    f"hello {name}"  →  "hello " + format(name, '')
    f"{x:.2f}"       →  format(x, ".2f")
    f"{x!r}"         →  format(repr(x), '')
    """

    removed_node_types = (ast.JoinedStr, ast.FormattedValue,)

    def _format_call(self, value, format_spec):
        if format_spec is not None:
            spec = self.visit(format_spec)
        else:
            spec = ast.Constant(value="")
        return ast.Call(
            func=ast.Name(id="format", ctx=ast.Load()),
            args=[value, spec],
            keywords=[],
        )

    def visit_FormattedValue(self, node):
        value = self.visit(node.value)
        if node.conversion != -1:
            conv_func = {115: "str", 114: "repr", 97: "ascii"}.get(node.conversion)
            if conv_func:
                value = ast.Call(
                    func=ast.Name(id=conv_func, ctx=ast.Load()),
                    args=[value],
                    keywords=[],
                )
        return self._format_call(value, node.format_spec)

    def visit_JoinedStr(self, node):
        values = [self.visit(v) for v in node.values]
        if not values:
            return ast.copy_location(ast.Constant(value=""), node)
        result = values[0]
        for v in values[1:]:
            result = ast.copy_location(
                ast.BinOp(left=result, op=ast.Add(), right=v), node
            )
        return result
