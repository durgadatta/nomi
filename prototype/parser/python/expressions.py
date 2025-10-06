'''
Synthesize expression and function call; 
expression usually deal with special notation like infix, postfix etc. 
but both are conceptually same

'''
import ast
from lark import Token

from prototype.parser.python import ensure_expr, tokval



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
    
    def star_expr(self, items):
        return ast.Starred(value=items[0])

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
        """
        Handle Python '**' operator, robust to different Lark parse shapes.
        items can be:
        - [base]
        - [base, exponent]
        - [base, '**', exponent]
        """
        if not items:
            return ast.Constant(value=None)

        base = ensure_expr(items[0])

        if len(items) == 1:
            return base

        # Two-item form: [base, exponent]
        if len(items) == 2:
            exponent = ensure_expr(items[1])
            return ast.BinOp(left=base, op=ast.Pow(), right=exponent)

        # Three-item form: [base, '**', exponent]
        if len(items) == 3:
            exponent = ensure_expr(items[2])
            return ast.BinOp(left=base, op=ast.Pow(), right=exponent)

        # Left-fold multiple '**': [a, '**', b, '**', c] → ((a**b)**c)
        left = base
        i = 1
        while i < len(items):
            # Skip token if present
            if isinstance(items[i], Token) and items[i].type == '**':
                i += 1
                if i >= len(items):
                    raise ValueError(f"Power '**' missing right operand in {items!r}")
            right = ensure_expr(items[i])
            left = ast.BinOp(left=left, op=ast.Pow(), right=right)
            i += 1

        return left


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
        
    def getitem(self, items):
        """
        Handle atom_expr "[" subscriptlist "]" -> getitem.
        items: [value_expr, subscriptlist_expr]
        """
        value = ensure_expr(items[0])
        subscr = items[1]
        # Check if subscr is a direct subscript (not a list) or a single-element list
        if not isinstance(subscr, list):
            # Single subscript: could be test or slice
            slice_node = ensure_expr(subscr)
        elif len(subscr) == 1:
            # Single subscript in a list (from subscript rule)
            slice_node = ensure_expr(subscr[0])
        else:
            # Multiple subscripts (from subscript_tuple): produce ast.Tuple
            slice_node = ast.Tuple(elts=[ensure_expr(s) for s in subscr], ctx=ast.Load())
        return ast.Subscript(value=value, slice=slice_node, ctx=ast.Load())

    def subscript(self, items):
        """
        Handle subscript: test | ([test] ":" [test] [sliceop]) -> slice.
        items: either [test] or [start, ":", stop, sliceop?] for slices
        """
        if len(items) == 1 and not isinstance(items[0], Token):
            # Single test, e.g., a[1]
            return ensure_expr(items[0])
        # Slice form: [start, ":", stop, sliceop?]
        start = ensure_expr(items[0]) if items and items[0] is not None else None
        stop = None
        step = None
        if len(items) > 2:
            # items[2] is stop if present
            stop = ensure_expr(items[2]) if items[2] is not None else None
            # items[3] is sliceop if present
            step = ensure_expr(items[3]) if len(items) > 3 and items[3] is not None else None
        elif len(items) > 1:
            # items[1] is ":"; items[2] is stop if present
            stop = ensure_expr(items[2]) if len(items) > 2 and items[2] is not None else None
        return ast.Slice(lower=start, upper=stop, step=step)

    def subscript_tuple(self, items):
        """
        Handle subscript_tuple: subscript ("," subscript)+ [","].
        Returns list of subscript elements.
        """
        return [ensure_expr(it) for it in items]
    
    def slice(self, items):
        """
        Handle slice: ([test] ":" [test] [sliceop]).
        Expects items as [lower, upper, step] (already transformed ast.expr nodes).
        """
        print(f"slice: items={items}, len={len(items)}")  # Debug
        lower = items[0] if items and items[0] is not None else None
        upper = None
        step = None
        if len(items) >= 2:
            upper = items[1] if items[1] is not None else None
        if len(items) >= 3:
            step = items[2] if items[2] is not None else None
        print(f"slice: lower={lower}, upper={upper}, step={step}")  # Debug
        return ast.Slice(lower=lower, upper=upper, step=step)

    def sliceop(self, items):
        """
        Handle sliceop: ":" [test].
        """
        if items and items[0] is not None:
            return ensure_expr(items[0])
        return None
    
    def list(self, items):
            """
            Handle list literals: "[" _exprlist? "]" -> list.
            items: list of test_or_star_expr from _exprlist, or empty
            """
            elts = [ensure_expr(it) for it in items if it is not None]
            return ast.List(elts=elts, ctx=ast.Load())
    
    def tuple(self, items):
            """
            Handle tuple expressions: "(" _tuple_inner? ")".
            """
            elts = [ensure_expr(it) for it in items if it is not None]
            return ast.Tuple(elts=elts, ctx=ast.Load())
 
    def dict(self, items):
        """
        Handle dict literals: {key: value, **expr, ...}
        items: list of key_value tuples, '**' unpack tuples, or possibly lone ast.expr
        """
        keys = []
        values = []

        for it in items:
            # Unpacking: '**expr' tuple
            if isinstance(it, tuple) and len(it) == 2 and it[0] == "**":
                keys.append(None)  # ast.Dict uses None for unpacked dicts
                values.append(ensure_expr(it[1]))

            # Normal key:value pair
            elif isinstance(it, tuple) and len(it) == 2:
                key_node = ensure_expr(it[0])
                value_node = ensure_expr(it[1])
                keys.append(key_node)
                values.append(value_node)

            # Bare expression (single expression not in key:value form)
            elif isinstance(it, (ast.expr, Token)):
                # Treat as **expr unpack automatically
                keys.append(None)
                values.append(ensure_expr(it))

            else:
                raise TypeError(f"Unexpected dict item: {it!r}")

        return ast.Dict(keys=keys, values=values)

    def _dict_exprlist(self, items):
        """Pass through the list of items to dict()"""
        return items

    def key_value(self, items):
        """Return a tuple (key, value) for dict items"""
        return (items[0], items[1])