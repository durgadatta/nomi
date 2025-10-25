import ast 

class FunctionMixin:
    def eval_arg(self, node:ast.arg):
        #TODO: this is currently not reached
        # we can later use this when the function parameters are bound at definition site
        name, annotation = node.name, node.annotation
        
        # eval AnnAssign so that the constraints are set properly
        self.eval(
            ast.AnnAssign(
                target=ast.Name(id=name, ctx=ast.Store()),
                annotation=annotation
            )
        )

        # this is handled generically in Python's interpreter
        return self.eval(node)