"""Expression layer: precedence restructuring at the Lark parse-tree level.

Takes the flat bin_expr subtrees produced by the grammar and restructures
them into correct precedence/associativity trees before they reach the
Python AST transformer.
"""

from lark import Tree, Token

from ..layer import LayerTransform

# (lbp, rbp, is_left_associative)
_PRECEDENCE = {
    '|':  (2, 2, True),
    '^':  (4, 4, True),
    '&':  (6, 6, True),
    '<<': (8, 8, True),
    '>>': (8, 8, True),
    '+':  (10, 10, True),
    '-':  (10, 10, True),
    '*':  (12, 12, True),
    '/':  (12, 12, True),
    '%':  (12, 12, True),
    '//': (12, 12, True),
    '@':  (12, 12, True),
}


class ExpressionLayer(LayerTransform):
    """Restructure flat bin_expr Trees into correct precedence trees."""

    @staticmethod
    def _op_info(tok):
        if isinstance(tok, Token):
            return _PRECEDENCE.get(tok.value, (0, 0, True))
        return (0, 0, True)

    def bin_expr(self, children):
        """bin_expr: factor ((_binary_op) factor)*

        Lark calls this with children = [factor1, op1, factor2, op2, ...]
        Returns a restructured Tree with correct precedence.
        """
        if len(children) <= 1:
            return children[0] if children else Tree('bin_expr', [])

        operands = [children[i] for i in range(0, len(children), 2)]
        operators = [children[i] for i in range(1, len(children), 2)]

        if len(operators) <= 1:
            return Tree('bin_expr', list(children))

        return self._restructure(operands, operators)

    def _restructure(self, operands, operators):
        """Shunting-yard restructure into correct precedence tree."""
        val_stack = [operands[0]]
        op_stack = []

        for i, op in enumerate(operators):
            rhs = operands[i + 1]
            lbp, rbp, left_assoc = self._op_info(op)

            while op_stack:
                prev_op = op_stack[-1]
                prev_lbp, prev_rbp, prev_left = self._op_info(prev_op)
                if prev_lbp > lbp or (prev_lbp == lbp and prev_left):
                    op_stack.pop()
                    r = val_stack.pop()
                    l = val_stack.pop()
                    val_stack.append(self._combine(l, prev_op, r))
                else:
                    break

            op_stack.append(op)
            val_stack.append(rhs)

        while op_stack:
            op = op_stack.pop()
            r = val_stack.pop()
            l = val_stack.pop()
            val_stack.append(self._combine(l, op, r))

        return val_stack[0]

    @staticmethod
    def _combine(left, op, right):
        return Tree('bin_expr', [left, op, right])
