import ast

from .base import BaseDesugarer


class Pass(BaseDesugarer):
    """pass  →  Expr(Constant(0))"""

    def visit_Pass(self, node):
        return ast.copy_location(
            ast.Expr(value=ast.Constant(value=0)),
            node,
        )
