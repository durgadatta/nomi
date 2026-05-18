import ast

from .base import NomiDesugarer, Phase


class Assert(NomiDesugarer):
    """assert cond [, msg]  →  if not cond: raise AssertionError([msg])"""
    phase = Phase.semantic

    input_node_types = (ast.Assert,)
    removed_node_types = (ast.Assert,)
    produced_node_types = (ast.If, ast.Raise, ast.Call, ast.UnaryOp)
    normal_forms = ("branch", "raise")

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
