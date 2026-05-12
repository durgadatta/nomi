import ast
from ...interpreter.constants import BLOCK_KWARG, Block

class FunctionsMixin:
    def func_equation(self, items):
        """func_equation: name '(' [func_eq_args] ')' '=' test

        Simple:  add(a, b) = a + b  →  func add(a, b): return a + b
        Literal: fact(1) = 1       →  func fact(__0): return 1
        (PiecewiseFunction pass merges adjacent same-name equations.)
        """
        name, eq_args, body = items
        if eq_args is None:
            eq_args = []
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