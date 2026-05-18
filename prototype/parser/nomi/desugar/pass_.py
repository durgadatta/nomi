import ast

from .base import NomiDesugarer, Phase


class Pass(NomiDesugarer):
    """pass  →  Expr(Constant(0))"""
    phase = Phase.syntax

    input_node_types = (ast.Pass,)
    removed_node_types = (ast.Pass,)
    produced_node_types = (ast.Expr, ast.Constant)
    normal_forms = ("no-op-expression",)

    def visit_Pass(self, node):
        return ast.copy_location(
            ast.Expr(value=ast.Constant(value=0)),
            node,
        )
