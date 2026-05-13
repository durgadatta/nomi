import ast
from ...interpreter.constants import BLOCK_KWARG, Block

class FunctionsMixin:

    # ── implicit multiplication ─────────────────────────────────────

    def implicit_mul_name(self, items):
        """implicit_mul_name: number power → number * power  (2x → 2*x)"""
        num, rhs = items
        return ast.BinOp(left=num, op=ast.Mult(), right=rhs)

    def implicit_mul_parens(self, items):
        """implicit_mul_parens: number '(' test ')' → number * test  (2(x+y) → 2*(x+y))"""
        num, test_expr = items
        return ast.BinOp(left=num, op=ast.Mult(), right=test_expr)

    # ── type alias ──────────────────────────────────────────────────

    def type_alias(self, items):
        """type_alias: 'type' NAME '=' test

        type UserId = str  →  UserId = str  (simple assignment)
        """
        name, value = items
        return ast.Assign(
            targets=[ast.Name(id=name, ctx=ast.Store())],
            value=value,
        )

    # ── if-let ───────────────────────────────────────────────────────

    def if_let_stmt(self, items):
        """if_let_stmt: 'if' pattern '=' test ':' suite ['else' ':' suite]

        if Some(v) = opt: body  →  match opt: case Some(v): body; case _: pass
        """
        if len(items) == 4:
            pattern, expr, body, else_body = items
        else:
            pattern, expr, body = items
            else_body = []

        match_case = ast.match_case(pattern=pattern, body=body)
        wildcard = ast.match_case(
            pattern=ast.MatchAs(pattern=None),
            body=else_body if else_body else [],
        )
        return ast.Match(
            subject=expr,
            cases=[match_case, wildcard],
        )

    def while_let_stmt(self, items):
        """while_let_stmt: 'while' pattern '=' test ':' suite

        while [head, *tail] = items:
            ...

        Desugars to a ``while True`` loop whose first statement matches the
        expression.  Non-match breaks out of the loop.
        """
        pattern, expr, body = items
        match_case = ast.match_case(pattern=pattern, guard=None, body=body)
        wildcard = ast.match_case(
            pattern=ast.MatchAs(pattern=None),
            guard=None,
            body=[ast.Break()],
        )
        return ast.While(
            test=ast.Constant(value=True),
            body=[ast.Match(subject=expr, cases=[match_case, wildcard])],
            orelse=[],
        )

    # ── try expression ───────────────────────────────────────────────

    def try_except_clause(self, items):
        """Normalize optional 'as' to always output (exc_type, exc_name, handler)."""
        exc_type, handler_expr = items[0], items[-1]
        exc_name = items[1] if len(items) == 3 else None
        return (exc_type, exc_name, handler_expr)

    def try_expr(self, items):
        """try_expr: 'try' test try_except_clause+

        try body except ValueError as e: handler
        Wraps in IIFE so it can be used in expression position.
        """
        body_expr, *clauses = items
        handlers = []
        for exc_type, exc_name, handler_expr in clauses:
            exc_node = ast.Name(id=exc_type, ctx=ast.Load())
            handlers.append(
                ast.ExceptHandler(
                    type=exc_node,
                    name=exc_name,
                    body=[ast.Return(value=handler_expr)],
                )
            )

        try_node = ast.Try(
            body=[ast.Return(value=body_expr)],
            handlers=handlers,
            orelse=[],
            finalbody=[],
        )

        empty_args = ast.arguments(
            posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[],
            defaults=[], vararg=None, kwarg=None,
        )
        func = ast.FunctionDef(
            name=None, args=empty_args, body=[try_node],
            decorator_list=[], returns=None,
        )
        return ast.Call(func=func, args=[], keywords=[])

    # ── inline match expression ──────────────────────────────────────

    def case_expr(self, items):
        """case_expr: 'case' pattern ['if' test] '=>' test"""
        if len(items) == 3:
            pattern, guard, value = items
        else:
            pattern, value = items
            guard = None
        return ast.match_case(
            pattern=pattern,
            guard=guard,
            body=[ast.Return(value=value)],
        )

    def case_block_expr(self, items):
        """case_block_expr: 'case' pattern ['if' test] ':' test _NEWLINE"""
        return self.case_expr(items)

    def match_inline(self, items):
        """match_inline: 'match' test ':' case_expr (';' case_expr)* [';']

        match value: case 1 => "one"; case _ => "many"
        Wraps in an IIFE so it can be used in expression position.
        """
        return self._match_expr_iife(items)

    def match_block_expr(self, items):
        """match_block_expr: 'match' test ':' _NEWLINE _INDENT case_block_expr+ _DEDENT

        match value:
            case 1: "one"
            case _: "many"
        """
        return self._match_expr_iife(items)

    def _match_expr_iife(self, items):
        subject, *cases = items
        match_node = ast.Match(subject=subject, cases=cases)
        empty_args = ast.arguments(
            posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[],
            defaults=[], vararg=None, kwarg=None,
        )
        func = ast.FunctionDef(
            name=None, args=empty_args, body=[match_node],
            decorator_list=[], returns=None,
        )
        return ast.Call(func=func, args=[], keywords=[])

    def assign_match_block(self, items):
        """assign_match_block: testlist_star_expr '=' match_block_expr"""
        return self.assign(items)

    def return_match_block(self, items):
        """return_match_block: 'return' match_block_expr"""
        return ast.Return(value=items[0])

    # ── where clause ────────────────────────────────────────────────

    def assign_where(self, items):
        """assign_where: small_stmt 'where' ':' suite

        Converted to the small_stmt with where_body stored as a custom
        attribute.  ``WhereClause`` desugar pass does the actual rewriting.
        """
        stmt, where_body = items
        if hasattr(stmt, '_nomi_where_body'):
            stmt._nomi_where_body.extend(where_body)
        else:
            stmt._nomi_where_body = where_body
        return stmt

    def assign_where_inline(self, items):
        """assign_where_inline: small_stmt 'where' small_stmt _NEWLINE

        Single-statement inline where: result = x + y where x = 10"""
        stmt, where_stmt = items
        stmt._nomi_where_body = [where_stmt]
        return stmt
    def dollar_hole(self, items):
        """Positional hole references: $1, $2, $3 ... (Swift-style)

        Lowered to ast.Name nodes with a '$' prefix id.
        The PositionalHole desugar pass wraps them in lambda functions.
        """
        return ast.Name(id=items[0].value, ctx=ast.Load())

    # ── function composition ─────────────────────────────────────────

    def compose_expr(self, items):
        """compose_expr: or_test ((COMP_BWD | COMP_FWD) or_test)*

        f >>> g  →  (__x) => g(f(__x))   — forward: apply f, then g
        f <<< g  →  (__x) => f(g(__x))   — backward: apply g, then f
        Chaining: f >>> g >>> h  →  (__x) => h(g(f(__x)))
        """
        if len(items) == 1:
            return items[0]

        x = ast.Name(id='__x', ctx=ast.Load())

        if str(items[1]) == '>>>':
            body = self._compose_call(items[0], x)
            i = 2
            while i < len(items):
                body = self._compose_call(items[i], body)
                i += 2
        else:
            body = self._compose_call(items[-1], x)
            i = len(items) - 3
            while i >= 0:
                body = self._compose_call(items[i], body)
                i -= 2

        param = ast.arg(arg='__x')
        params = ast.arguments(
            posonlyargs=[], args=[param], kwonlyargs=[], kw_defaults=[],
            defaults=[], vararg=None, kwarg=None,
        )
        return ast.FunctionDef(
            name=None, args=params, body=[ast.Return(value=body)],
            decorator_list=[], returns=None,
        )

    @staticmethod
    def _compose_call(func, arg):
        return ast.Call(func=func, args=[arg], keywords=[])

    # ── defer ────────────────────────────────────────────────────────

    def defer_stmt(self, items):
        """defer_stmt: 'defer' expr_stmt

        defer file.close()  →  stores the stmt on _nomi_defer for runtime
        """
        stmt = items[0]
        stmt._nomi_defer = True
        return stmt

    def func_equation_no_parens(self, items):
        """func_equation_no_parens: name NAME ['when' test] '=' test

        double x = x * 2       →  func double(x): return x * 2
        sign n when n > 0 = 1  →  func sign(n): return 1  (with guard)
        """
        if len(items) == 3:
            name, param_name, body = items
            guard = None
        else:
            name, param_name, guard, body = items
        args_list = [ast.arg(arg=param_name)]
        params = ast.arguments(
            posonlyargs=[], args=args_list, kwonlyargs=[], kw_defaults=[],
            defaults=[], vararg=None, kwarg=None,
        )
        fn = ast.FunctionDef(
            name=name, args=params, body=[ast.Return(value=body)],
            decorator_list=[], returns=None,
        )
        fn._nomi_eq_args = [param_name]
        if guard:
            fn._nomi_eq_guard = guard
        return fn

    def func_equation(self, items):
        """func_equation: name '(' [func_eq_args] ')' ['when' test] '=' test

        Simple:  add(a, b) = a + b  →  func add(a, b): return a + b
        Literal: fact(1) = 1       →  func fact(__0): return 1
        Guarded: sign(n) when n > 0 = 1
        (PiecewiseFunction pass merges adjacent same-name equations.)
        """
        if len(items) == 3:
            name, eq_args, body = items
            guard = None
        else:
            name, eq_args, guard, body = items
        if eq_args is None:
            eq_args = []
        elif isinstance(eq_args, list):
            pass  # already a list
        else:
            eq_args = [eq_args]  # single item
        args_list = []
        defaults = []
        for i, arg in enumerate(eq_args):
            if isinstance(arg, tuple):
                arg_name, arg_default = arg
                args_list.append(ast.arg(arg=arg_name))
                if arg_default is not None:
                    defaults.append(arg_default)
            elif isinstance(arg, str):
                args_list.append(ast.arg(arg=arg))
            else:
                args_list.append(ast.arg(arg=f'__{i}'))
        params = ast.arguments(
            posonlyargs=[], args=args_list, kwonlyargs=[], kw_defaults=[],
            defaults=defaults, vararg=None, kwarg=None,
        )
        fn = ast.FunctionDef(
            name=name, args=params, body=[ast.Return(value=body)],
            decorator_list=[], returns=None,
        )
        fn._nomi_eq_args = eq_args  # preserved for PiecewiseFunction pass
        if guard:
            fn._nomi_eq_guard = guard
        return fn

    _BINOP_CLS = {
        '*': ast.Mult, '/': ast.Div, '%': ast.Mod, '//': ast.FloorDiv, '@': ast.MatMult,
        '+': ast.Add, '-': ast.Sub,
        '<<': ast.LShift, '>>': ast.RShift,
        '&': ast.BitAnd, '|': ast.BitOr, '^': ast.BitXor,
    }

    def section(self, items):
        return items[0]

    def left_section(self, items):
        op_token, rhs = items
        return self._section_lambda(lambda p: ast.BinOp(
            left=ast.Name(id=p, ctx=ast.Load()),
            op=self._section_op(op_token)(), right=rhs,
        ))

    def right_section(self, items):
        lhs, op_token = items
        return self._section_lambda(lambda p: ast.BinOp(
            left=lhs, op=self._section_op(op_token)(),
            right=ast.Name(id=p, ctx=ast.Load()),
        ))

    def operator_value(self, items):
        op_token = items[0]
        op_cls = self._section_op(op_token)
        return self._section_lambda(
            lambda a, b: ast.BinOp(
                left=ast.Name(id=a, ctx=ast.Load()),
                op=op_cls(),
                right=ast.Name(id=b, ctx=ast.Load()),
            ),
            param_names=('__a', '__b'),
        )

    def _section_op(self, op_token):
        name = op_token.value if hasattr(op_token, 'value') else str(op_token)
        return self._BINOP_CLS.get(name, ast.Add)

    @staticmethod
    def _section_lambda(body_fn, param_names=('__s',)):
        params = [ast.arg(arg=n) for n in param_names]
        if len(param_names) == 1:
            ret_val = body_fn(param_names[0])
        else:
            ret_val = body_fn(*param_names)
        args = ast.arguments(
            posonlyargs=[], args=params, kwonlyargs=[], kw_defaults=[],
            defaults=[], vararg=None, kwarg=None,
        )
        return ast.FunctionDef(
            name=None, args=args, body=[ast.Return(value=ret_val)],
            decorator_list=[], returns=None,
        )
        return items

    def func_eq_args(self, items):
        return items

    def name_arg(self, items):
        if len(items) == 1:
            return (items[0], None)
        return (items[0], items[1])

    def value_arg(self, items):
        return items[0]

    def func_expr(self, items):
        '''
        Reduce it to funcdef.
        Supports: (x,y) => expr, (x) => expr, x => expr
        '''
        # Single-param: NAME "=>" test  → 2 items: [name, body]
        if len(items) == 2 and isinstance(items[0], str):
            name, body = items
            param = ast.arg(arg=name)
            params = ast.arguments(
                posonlyargs=[], args=[param], kwonlyargs=[], kw_defaults=[],
                defaults=[], vararg=None, kwarg=None,
            )
            return_node = ast.Return(value=body)
            return ast.FunctionDef(
                name=None, args=params, body=[return_node],
                decorator_list=[], returns=None,
            )

        # Multi-param: "(" [parameters] ")" "=>" test
        name = None
        items.insert(0, name)

        expr = items[-1]
        return_node = ast.Return(value=expr)
        func_body = [return_node]
        # adapt the "return annotation" TODO:
        items.insert(-1, None)
        items[-1] = func_body
            
        fn = self.funcdef(items)
        return fn
    
    def block_call_stmt(self, items):
        '''
            NOTE:
            adhoc/temp implementation of function call
            that accepts block, later to be fully harmonized with 
            regular call
        '''
        call, params, block = items 
        block = ast.keyword(arg=BLOCK_KWARG, value=Block(body=block, params=params))
        call.keywords.append(block)

         # Make it a statement, note that ast.Expr < ast.stmt
         # else it will be ignored by file_start parsing
        return ast.Expr(value=call)
