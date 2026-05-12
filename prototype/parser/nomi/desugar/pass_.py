import ast

from .base import NomiDesugarer


class Pass(NomiDesugarer):
    """pass  →  Expr(Constant(0))"""

    def visit_Pass(self, node):
        return ast.copy_location(
            ast.Expr(value=ast.Constant(value=0)),
            node,
        )
