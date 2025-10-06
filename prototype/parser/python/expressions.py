'''
Synthesize expression and function call; 
expression usually deal with special notation like infix, postfix etc. 
but both are conceptually same

'''
import ast
from lark import Token

from prototype.parser.python import ensure_expr

def tokval(t):
    return t.value if isinstance(t, Token) else str(t)

class IdentifierMixin:
    # def NAME(self, token):
    #         # Convert NAME token to ast.Name with context based on usage
    #         if not isinstance(token, Token) or token.type != 'NAME':
    #             raise ValueError(f"Expected NAME token, got {type(token)}: {token}")
    #         # Default to Store for comprehension targets; override in expr contexts if needed
    #         name_node = ast.Name(id=token.value, ctx=ast.Store())
    #         return name_node

    def name(self, items):
        return tokval(items[0])

    def var(self, items):
        # items[0] might be Token or str
        child = items[0]
        name_node = ast.Name(id=tokval(child), ctx=ast.Load())
        return name_node
        

class LiteralMixin:
    def number(self, items):
        return ensure_expr(items[0])

    def string(self, items):
        return ensure_expr(items[0])

    def const_none(self, items):
        return ast.Constant(value=None)

    def const_true(self, items):
        return ast.Constant(value=True)

    def const_false(self, items):
        return ast.Constant(value=False)

    def ellipsis(self, items):
        return ast.Constant(value=Ellipsis)

class ExpressionMixin(IdentifierMixin, LiteralMixin):
    # Simple expression nodes and folding for common binary/unary ops.

    def atom(self, items):
        return items[0] if items else ast.Constant(value=None)

    def atom_expr(self, items):
        # Lark routes to funccall/getitem/getattr first; otherwise child
        return items[0] if items else ast.Constant(value=None)

    def comparison(self, items):
        if not items:
            return ast.Constant(value=False)
        if len(items) == 1:
            return ensure_expr(items[0])
        left = ensure_expr(items[0])
        ops = []
        comparators = []
        i = 1
        while i < len(items):
            op = items[i]
            right = items[i+1] if i+1 < len(items) else None
            op_s = op.value if isinstance(op, Token) else str(op)
            ops.append(self._map_cmp_op(op_s))
            comparators.append(ensure_expr(right))
            i += 2
        return ast.Compare(left=left, ops=ops, comparators=comparators)

    def _map_cmp_op(self, s):
        return {
            '==': ast.Eq(),
            '!=': ast.NotEq(),
            '<>': ast.NotEq(),
            '<': ast.Lt(),
            '<=': ast.LtE(),
            '>': ast.Gt(),
            '>=': ast.GtE(),
            'in': ast.In(),
            'not in': ast.NotIn(),
            'is': ast.Is(),
            'is not': ast.IsNot(),
        }.get(s, ast.Eq())

    def _left_fold_binop(self, items):
        # items: operand (op operand)*
        if not items:
            return ast.Constant(value=0)
        left = ensure_expr(items[0])
        i = 1
        while i < len(items):
            op = items[i]
            right = ensure_expr(items[i+1]) if i+1 < len(items) else ast.Constant(value=None)
            op_s = op.value if isinstance(op, Token) else str(op)
            operator = {
                '+': ast.Add(),
                '-': ast.Sub(),
                '*': ast.Mult(),
                '/': ast.Div(),
                '//': ast.FloorDiv(),
                '%': ast.Mod(),
                '@': ast.MatMult(),
                '**': ast.Pow(),
            }.get(op_s, ast.Add())
            left = ast.BinOp(left=left, op=operator, right=right)
            i += 2
        return left

    def arith_expr(self, items):
        return self._left_fold_binop(items)

    def term(self, items):
        return self._left_fold_binop(items)

    def power(self, items):
        if len(items) == 1:
            return ensure_expr(items[0])
        return ast.BinOp(left=ensure_expr(items[0]), op=ast.Pow(), right=ensure_expr(items[2]))

    def factor(self, items):
        if len(items) == 1:
            return ensure_expr(items[0])
        op = items[0]
        operand = ensure_expr(items[1])
        op_s = op.value if isinstance(op, Token) else str(op)
        if op_s == '+':
            return operand
        if op_s == '-':
            return ast.UnaryOp(op=ast.USub(), operand=operand)
        if op_s == '~':
            return ast.UnaryOp(op=ast.Invert(), operand=operand)
        return operand
    
    UNARY_OPERATORS = {
        '+': ast.UAdd,
        '-': ast.USub,
        '~': ast.Invert,
        'not': ast.Not,
    }

    def _unary_op(self, items):
        """Return the operator instance."""
        op_token = str(items[0])
        if op_token not in self.UNARY_OPERATORS:
            raise ValueError(f"Unknown unary operator: {op_token}")
        return self.UNARY_OPERATORS[op_token]()

    def not_test(self, items):
        """Handle 'not' unary operator."""
        operand = items[0]
        return ast.UnaryOp(op=ast.Not(), operand=operand)

    def or_test(self, items):
        if not items:
            return ast.Constant(False)
        if len(items) == 1:
            return ensure_expr(items[0])
        return ast.BoolOp(op=ast.Or(), values=[ensure_expr(it) for it in items])

    def and_test(self, items):
        if not items:
            return ast.Constant(True)
        if len(items) == 1:
            return ensure_expr(items[0])
        return ast.BoolOp(op=ast.And(), values=[ensure_expr(it) for it in items])

    def test(self, items):
        """
        Handles ternary expressions as ast.IfExp if present, else passes through single item.
        """
        if len(items) == 1:
            return ensure_expr(items[0])
        elif len(items) == 3:
            # ternary: [body, test, orelse]
            body, test, orelse = items
            return ast.IfExp(
                test=ensure_expr(test),
                body=ensure_expr(body),
                orelse=ensure_expr(orelse)
            )
        else:
            raise ValueError(f"Unexpected number of items in test: {items!r}")