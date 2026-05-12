import ast

from .base import NomiDesugarer


class Pass(NomiDesugarer):
    """pass  →  Expr(Constant(0))"""

    removed_node_types = (ast.Pass,)

    def visit_Pass(self, node):
        return ast.copy_location(
            ast.Expr(value=ast.Constant(value=0)),
            node,
        )
