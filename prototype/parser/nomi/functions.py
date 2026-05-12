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
    def func_equation(self, items):
        """func_equation: name '(' [func_eq_args] ')' '=' test

        Simple:  add(a, b) = a + b  →  func add(a, b): return a + b
        Literal: fact(1) = 1       →  func fact(__0): return 1
        (PiecewiseFunction pass merges adjacent same-name equations.)
        """
        name, eq_args, body = items
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
        Reduce it to funcdef
        
        name may or may not be there; 
        body is a single expression

        #TODO: when the value is FunctionDef
        update assignment to change the name of FunctionDef
        '''
        
        # this is an anonymous function 
        # TODO: later handle FunctionDef to handle function without name
        # or just abstract the function without name
        # when None is passed eval_FunctionDef is expected not to bind name
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