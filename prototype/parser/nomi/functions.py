import ast
from ...interpreter.constants import BLOCK_KWARG, Block

class FunctionsMixin:
    def func_equation(self, items):
        """func_equation: name '(' [parameters] ')' '=' test

        Syntactic sugar for ``func f(a, b): return expr``.
        """
        name, parameters, body = items
        return_node = ast.Return(value=body)
        return ast.FunctionDef(
            name=name,
            args=parameters or self.parameters([]),
            body=[return_node],
            decorator_list=[],
            returns=None,
        )

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