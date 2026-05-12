"""Precedence restructuring pass.

The grammar now produces flat left-to-right BinOp chains for arithmetic
and bitwise operators.  This pass restructures them into the correct
precedence tree using the standard shunting-yard algorithm.
"""

import ast

from .base import NomiDesugarer


# (lbp, rbp, is_left_associative)
# lbp = left binding power (used when this operator is on the left of another)
# rbp = right binding power (used when parsing the right operand)
_BINARY_TABLE = {
    ast.BitOr:     (1, 2, True),    # |
    ast.BitXor:    (3, 4, True),    # ^
    ast.BitAnd:    (5, 6, True),    # &
    ast.LShift:    (7, 8, True),    # <<
    ast.RShift:    (7, 8, True),    # >>
    ast.Add:       (9, 10, True),   # +
    ast.Sub:       (9, 10, True),   # -
    ast.Mult:      (11, 12, True),  # *
    ast.Div:       (11, 12, True),  # /
    ast.FloorDiv:  (11, 12, True),  # //
    ast.Mod:       (11, 12, True),  # %
    ast.MatMult:   (11, 12, True),  # @
}


class Precedence(NomiDesugarer):
    """Restructure flat BinOp chains into correct precedence trees."""

    @staticmethod
    def _precedence(op):
        return _BINARY_TABLE.get(type(op), (0, 0, True))

    def _restructure_chain(self, operands, operators):
        """Shunting-yard restructure of a flat operand-operator chain.

        operands: [expr1, expr2, ..., exprn]
        operators: [op1, op2, ..., op(n-1)]

        Returns a single BinOp tree with correct precedence.
        """
        val_stack = [operands[0]]
        op_stack = []

        for i, op in enumerate(operators):
            rhs = operands[i + 1]
            lbp, rbp, left_assoc = self._precedence(op)

            while op_stack:
                prev_op = op_stack[-1]
                prev_lbp, prev_rbp, prev_left = self._precedence(prev_op)
                # Resolve previous operator if it has higher precedence,
                # or equal precedence and is left-associative
                if prev_lbp > lbp or (prev_lbp == lbp and prev_left):
                    op_stack.pop()
                    r = val_stack.pop()
                    l = val_stack.pop()
                    val_stack.append(self._binop(l, prev_op, r))
                else:
                    break

            op_stack.append(op)
            val_stack.append(rhs)

        while op_stack:
            op = op_stack.pop()
            r = val_stack.pop()
            l = val_stack.pop()
            val_stack.append(self._binop(l, op, r))

        return val_stack[0]

    @staticmethod
    def _binop(left, op, right):
        return ast.BinOp(left=left, op=op, right=right)

    def visit_BinOp(self, node):
        """Collect a flat BinOp chain and restructure it."""
        self.generic_visit(node)

        # Collect the flat chain: operands and operators
        operands = []
        operators = []

        current = node
        while isinstance(current, ast.BinOp) and isinstance(current.op, tuple(_BINARY_TABLE.keys())):
            operands.append(current.left)
            operators.append(current.op)
            current = current.right

        operands.append(current)  # last operand

        if len(operators) <= 1:
            return node  # nothing to restructure

        return ast.copy_location(self._restructure_chain(operands, operators), node)
