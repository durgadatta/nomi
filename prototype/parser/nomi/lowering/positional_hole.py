"""Positional hole lowering: ``$1`` → ``Name('$1')``.

The actual lambda wrapping is done by the ``PositionalHole`` desugar pass.
"""

import ast


class PositionalHoleMixin:
    def dollar_hole(self, items):
        return ast.Name(id=items[0].value, ctx=ast.Load())
