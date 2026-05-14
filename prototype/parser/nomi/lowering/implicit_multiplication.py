"""Implicit multiplication: ``2x`` → ``2 * x``, ``2(x+y)`` → ``2 * (x+y)``."""

import ast


class ImplicitMulMixin:
    def implicit_mul_name(self, items):
        num, rhs = items
        return ast.BinOp(left=num, op=ast.Mult(), right=rhs)

    def implicit_mul_parens(self, items):
        num, test_expr = items
        return ast.BinOp(left=num, op=ast.Mult(), right=test_expr)
