"""Block-call lowering: ``f(x) do: ... end`` → call with block body keyword."""

import ast

from ....interpreter.constants import BLOCK_KWARG, Block


class BlockCallMixin:
    def block_call_stmt(self, items):
        call, params, block = items
        block = ast.keyword(arg=BLOCK_KWARG, value=Block(body=block, params=params))
        call.keywords.append(block)
        return ast.Expr(value=call)
