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
    
    def _setup_function_parameters(self, func_node, env):
        """Set up parameter constraints in the given environment."""
        for param in func_node.args.args:
            if param.annotation:
                ann_assign = ast.AnnAssign(
                    target=ast.Name(id=param.arg, ctx=ast.Store()),
                    annotation=param.annotation,
                    value=None,
                    simple=1
                )
                old_env = self.current_env
                self.current_env = env
                try:
                    self.eval_AnnAssign(ann_assign)
                finally:
                    self.current_env = old_env

    def eval_FunctionDef(self, node: ast.FunctionDef) -> None:
        # Create function environment with closure as parent

        super().eval_FunctionDef(node)
        func = self.current_env.get(node.name)
        self._setup_function_parameters(node, func.func_env)

        return func