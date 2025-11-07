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
    
    def block_call_stmt(self, items):
        '''
            NOTE:
            adhoc/temp implemenation of function call
            that accepts block, later to be fully harmonized with 
            regular call
        '''
        caller, block = items 

        #TODO: the first exp may not be a call
        # it may be a function that can only take block 
        # so just f or expr without f()
        # now it will be a generator state
        # also it will not handle sending parameter to block fow now
            # immediate next task
        # in this case, we may need to wrap it into a call explicitly
        ## later think of more systematic way to handle internal
        #metadata
        # can also create a separate node for this
        # though this is part of regular call

        #NOTE: __block will interfere with ast slots and private names
        caller._nomi_block = block

        # force it to run until it is exhausted
        call_expr = ast.Call(
            func=ast.Name('list'), 
            args=[caller]
        )

         # This makes it a statement
         # else it would get filtered out in file_input parsing
         # note that ast.Expr is subclass of ast.stmt
        return ast.Expr(value=call_expr) 