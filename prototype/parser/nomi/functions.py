import ast

class FunctionsMixin:
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