'''
Synthesize expression and function call; 
expression usually deal with special notation like infix, postfix etc. 
but both are conceptually same

'''
import ast
from lark import Token

from . import ensure_expr



class IdentifierMixin:
    def NAME(self, token):
        return token.value 
    
    def name(self, items):
        ''' almost always str form is used; in certain context ast.Name is required
        such as class_pattern
        '''
        return items[0]
    
    def var(self, items):
        # name (as atom ) -> var
        # name is routed to var; so it will always be string 
        name_node = ast.Name(id=items[0], ctx=ast.Load())
        return name_node
    
    def dotted_name(self, items):
        """
        dotted_name: name ("." name)*
        Build an attribute access chain: a.b.c becomes ast.Attribute(ast.Attribute(ast.Name(a), b), c)

        TODO: name is now collapsed to string, so .value is not needed
        later, we may retain name as ast
        """
        if len(items) == 1:
            # Single name: just return a Name node
            return ast.Name(id=items[0], ctx=ast.Load())
        
        # Build attribute chain from left to right
        # items[0] is the first name, then alternating ['.', name, '.', name, ...]
        expr = ast.Name(id=items[0], ctx=ast.Load())
        
        # Skip the first item, then process pairs: we have [name, '.', name, '.', name, ...]
        # But actually items will be: [name, Token('.', '.'), name, Token('.', '.'), name, ...]
        for i in range(2, len(items), 2):
            attr_name = items[i]
            expr = ast.Attribute(
                value=expr,
                attr=attr_name,
                ctx=ast.Load(),
            )
        
        return expr
        

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

    def comp_op(self, items):
        def map_cmp_op(s):
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

        if len(items) == 1:
            op_token = items[0]
            op_str = op_token.value if isinstance(op_token, Token) else str(op_token)
            return map_cmp_op(op_str)
        elif len(items) == 2:
            first, second = items[0], items[1]
            first_str = first.value if isinstance(first, Token) else str(first)
            second_str = second.value if isinstance(second, Token) else str(second)
            if first_str == "not" and second_str == "in":
                return ast.NotIn()
            elif first_str == "is" and second_str == "not":
                return ast.IsNot()
        
        return ast.Eq()

    def range_expr(self, items):
        return items[0]

    def range_inclusive(self, items):
        left, _tok, right = items
        return ast.Call(
            func=ast.Name(id='range', ctx=ast.Load()),
            args=[left, ast.BinOp(left=right, op=ast.Add(), right=ast.Constant(value=1))],
            keywords=[],
        )

    def range_exclusive(self, items):
        left, _tok, right = items
        return ast.Call(
            func=ast.Name(id='range', ctx=ast.Load()),
            args=[left, right],
            keywords=[],
        )

    # -- pipe expression: x |> f  →  f(x),  x |> f |> g  →  g(f(x)) --

    def pipe_expr(self, items):
        if len(items) == 1:
            return items[0]
        result = items[0]
        for i in range(1, len(items), 2):
            right = items[i + 1]
            if isinstance(right, ast.Call):
                right.args.insert(0, result)
                result = right
            else:
                result = ast.Call(func=right, args=[result], keywords=[])
        return result

    def safe_call(self, items):
        """a?.m(args)  →  None if a is None else a.m(args)"""
        if len(items) == 3:
            obj, _tok, name = items
            args_tuple = ([], [])
        else:
            obj, _tok, name, args_tuple = items
            if args_tuple is None:
                args_tuple = ([], [])
        args, keywords = args_tuple
        attr_name = name if isinstance(name, str) else name.id
        call = ast.Call(
            func=ast.Attribute(value=self._safe_receiver_name(), attr=attr_name, ctx=ast.Load()),
            args=args,
            keywords=keywords,
        )
        return self._safe_access(obj, call)

    def safe_getattr(self, items):
        """a?.b  →  a.b if a is not None else None"""
        obj, _tok, name = items
        attr_name = name if isinstance(name, str) else name.id
        return self._safe_access(
            obj,
            ast.Attribute(value=self._safe_receiver_name(), attr=attr_name, ctx=ast.Load()),
        )

    def safe_getitem(self, items):
        """a?.[i]  →  a[i] if a is not None else None"""
        obj = items[0]
        subscr = items[-1]
        return self._safe_access(
            obj,
            ast.Subscript(
                value=self._safe_receiver_name(),
                slice=self._subscript_slice(subscr),
                ctx=ast.Load(),
            ),
        )

    @staticmethod
    def _safe_receiver_name():
        return ast.Name(id='__safe', ctx=ast.Load())

    @staticmethod
    def _safe_receiver_arg():
        return ast.arg(arg='__safe')

    def _safe_access(self, obj, body):
        """Evaluate the receiver once, then perform a guarded access."""
        receiver = self._safe_receiver_name()
        test = ast.Compare(
            left=receiver,
            ops=[ast.IsNot()],
            comparators=[ast.Constant(value=None)],
        )
        empty_args = ast.arguments(
            posonlyargs=[], args=[self._safe_receiver_arg()],
            kwonlyargs=[], kw_defaults=[], defaults=[],
            vararg=None, kwarg=None,
        )
        func = ast.FunctionDef(
            name=None,
            args=empty_args,
            body=[ast.Return(value=ast.IfExp(
                test=test,
                body=body,
                orelse=ast.Constant(value=None),
            ))],
            decorator_list=[],
            returns=None,
        )
        return ast.Call(func=func, args=[obj], keywords=[])

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
            op_node = items[i]
            if isinstance(op_node, Token):
                op_node = self.comp_op([op_node])
            elif not isinstance(op_node, ast.AST):
                op_node = self.comp_op([str(op_node)])
            
            ops.append(op_node)
            
            if i + 1 < len(items):
                comparators.append(ensure_expr(items[i + 1]))
            i += 2
            
        return ast.Compare(left=left, ops=ops, comparators=comparators)

    # -- flattened binary expression (precedence handled by Precedence pass) --

    _BINOP_MAP = {
        '*': ast.Mult, '/': ast.Div, '%': ast.Mod, '//': ast.FloorDiv, '@': ast.MatMult,
        '+': ast.Add, '-': ast.Sub,
        '<<': ast.LShift, '>>': ast.RShift,
        '&': ast.BitAnd, '|': ast.BitOr, '^': ast.BitXor,
    }

    def bin_expr(self, items):
        """Nomi-only: bin_expr builds flat left-to-right BinOp chain."""
        if len(items) == 1:
            return items[0]
        left = items[0]
        for i in range(1, len(items), 2):
            op_str = items[i] if isinstance(items[i], str) else str(items[i])
            right = items[i + 1]
            op_cls = self._BINOP_MAP.get(op_str)
            if op_cls is None:
                raise ValueError(f"Unknown binary operator: {op_str!r}")
            left = ast.BinOp(left=left, op=op_cls(), right=right)
        return left

    # -- legacy level-specific methods (used by Python parser's LALR grammar) --

    def _binop_chain(self, items, op_map):
        if len(items) == 1:
            return items[0]
        left = items[0]
        for i in range(1, len(items), 2):
            op_str = items[i] if isinstance(items[i], str) else str(items[i])
            right = items[i + 1]
            if op_str not in op_map:
                raise ValueError(f"Unknown operator in chain: {op_str!r}")
            left = ast.BinOp(left=left, op=op_map[op_str], right=right)
        return left

    def term(self, items):
        return self._binop_chain(items, {
            '*': ast.Mult(), '@': ast.MatMult(), '/': ast.Div(),
            '%': ast.Mod(), '//': ast.FloorDiv(),
        })

    def arith_expr(self, items):
        return self._binop_chain(items, {'+': ast.Add(), '-': ast.Sub()})

    def shift_expr(self, items):
        return self._binop_chain(items, {'<<': ast.LShift(), '>>': ast.RShift()})

    def factor(self, items):
        """
        factor: _unary_op factor | power
        """
        if len(items) == 1:
            return ensure_expr(items[0])
        
        op_str = items[0]  # Lark handles token conversion
        operand = ensure_expr(items[1])
        
        op_map = {
            '+': ast.UAdd(),
            '-': ast.USub(),
            '~': ast.Invert()
        }
        
        if op_str not in op_map:
            raise ValueError(f"Unknown unary operator: '{op_str}'")
        
        return ast.UnaryOp(op=op_map[op_str], operand=operand)

    def power(self, items):
        """
        power: await_expr ("**" factor)?
        """
        if len(items) == 1:
            return items[0]
        
        base = items[0]
        exponent = items[1] if len(items) > 1 else None
        
        return ast.BinOp(left=base, op=ast.Pow(), right=exponent)


    def not_test(self, items):
        """Handle 'not' unary operator."""
        operand = items[0]
        return ast.UnaryOp(op=ast.Not(), operand=operand)

    def nullish_expr(self, items):
        """nullish_expr: and_test (NULLISH and_test)*

        and_test is inline (?and_test), so its children leak into
        nullish_expr.  We find NULLISH tokens to split the stream.
        """
        if not any(isinstance(it, Token) and it.type == 'NULLISH' for it in items):
            return items[0] if len(items) == 1 else items  # passthrough

        # Find NULLISH positions, split into groups, and chain
        groups = []
        current = []
        for it in items:
            if isinstance(it, Token) and it.type == 'NULLISH':
                groups.append(current)
                current = []
            else:
                current.append(it)
        groups.append(current)

        # Convert each group back (first element or pass to and_test handler)
        def _to_expr(group):
            if len(group) == 1:
                return group[0]
            # Re-wrap for and_test transformer
            return self.and_test(group)

        result = _to_expr(groups[0])
        for g in groups[1:]:
            right = _to_expr(g)
            result = ast.IfExp(
                test=ast.Compare(left=result, ops=[ast.IsNot()],
                                  comparators=[ast.Constant(value=None)]),
                body=result,
                orelse=right,
            )
        return result

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
        return ast.Subscript(value=value, slice=self._subscript_slice(items[1]), ctx=ast.Load())

    def _subscript_slice(self, subscr):
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
        return slice_node

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
        lower = items[0] if items and items[0] is not None else None
        upper = None
        step = None
        if len(items) >= 2:
            upper = items[1] if items[1] is not None else None
        if len(items) >= 3:
            step = items[2] if items[2] is not None else None
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
        return ast.List(elts=items)
    
    def tuple(self, items):
        """
        Handle tuple expressions: "(" _tuple_inner? ")".
        """
        return ast.Tuple(elts=items)
    
    def set(self, items):
        return ast.Set(elts=items)
 
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
    
    def testlist_tuple(self, items):
        """
        testlist_tuple: test ("," test)+ [","] | test ","
        Returns: ast.Tuple for multiple items, single expression for one item
        """
        if len(items) == 1:
            return ensure_expr(items[0])
        else:
            # Filter out any comma tokens and ensure all are expressions
            exprs = [ensure_expr(item) for item in items if not isinstance(item, Token)]
            return ast.Tuple(elts=exprs, ctx=ast.Load())
