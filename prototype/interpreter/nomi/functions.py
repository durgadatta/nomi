import ast
from ..constants import Block

class BlockFunctionMixin:
    def eval_arg(self, node:ast.arg):
        # This handler exists so parameter binding can route through the
        # Nomi constraint path when constraints are attached to function
        # parameters at definition time.  Currently the base interpreter
        # handles arg nodes before this is reached.
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
        params = list(func_node.args.posonlyargs)
        params.extend(func_node.args.args)
        params.extend(func_node.args.kwonlyargs)
        if func_node.args.vararg:
            params.append(func_node.args.vararg)
        if func_node.args.kwarg:
            params.append(func_node.args.kwarg)

        for param in params:
            if param.annotation:
                ann_assign = ast.AnnAssign(
                    target=ast.Name(id=param.arg, ctx=ast.Store()),
                    annotation=param.annotation,
                    value=None,
                    simple=1
                )
                with self.this_env(env):
                    self.eval_AnnAssign(ann_assign)

    def eval_FunctionDef(self, node: ast.FunctionDef) -> None:
        # Create function environment with closure as parent

        func = super().eval_FunctionDef(node)
        self._setup_function_parameters(node, func.func_env)

        return func
    

    def eval_generator_obj(self, body, local_env, block=None):
        # The block parameter piggybacks on generator creation — the
        # generator is consumed to exhaustion when a block is attached.
        # A cleaner split would create the generator, then attach the
        # block policy as a separate step.
        gen = self.gen_state(self, body, local_env, block=block)
        if block is not None:
            if block:
                list(gen)
        return gen
