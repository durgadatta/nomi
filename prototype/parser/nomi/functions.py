import ast
from ...interpreter.constants import BLOCK_KWARG, Block

class FunctionsMixin:
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
        for i, arg in enumerate(eq_args):
            if isinstance(arg, str):
                args_list.append(ast.arg(arg=arg))
            else:
                args_list.append(ast.arg(arg=f'__{i}'))
        params = ast.arguments(
            posonlyargs=[], args=args_list, kwonlyargs=[], kw_defaults=[],
            defaults=[], vararg=None, kwarg=None,
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
        return items[0]

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