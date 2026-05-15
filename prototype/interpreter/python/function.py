import ast
from typing import List, Any

from ..constants import BLOCK_KWARG, Block
from .signals import ReturnException
from .function_call import FunctionCallMixin

class FunctionMixin(FunctionCallMixin):
    FUNCTION_METADATA_ATTRS = ('__name__', 'ast_node', 'func_env')

    def _new_closure_env(self):
        return self.env_class(self, parent=self.current_env)

    def _preserve_function_metadata(self, obj: Any) -> dict:
        return {
            attr_name: getattr(obj, attr_name)
            for attr_name in self.FUNCTION_METADATA_ATTRS
            if hasattr(obj, attr_name)
        }

    def _restore_function_metadata(self, obj: Any, metadata: dict) -> None:
        for attr_name, attr_value in metadata.items():
            setattr(obj, attr_name, attr_value)

    def apply_decorators(self, obj: Any, decorators: List[ast.expr]) -> Any:
        for dec in reversed(decorators):
            # Create new environment for decorator evaluation
            dec_env = self._new_closure_env()
            
            with self.this_env(dec_env):
                dec_func = self.eval(dec)
                original_attrs = self._preserve_function_metadata(obj)
                obj = dec_func(obj)
                self._restore_function_metadata(obj, original_attrs)
        return obj
    
    def _is_generator_function(self, node: ast.FunctionDef) -> bool:
        """Check for yield/yield-from in the function body, skipping nested definitions."""

        class _YieldFinder(ast.NodeVisitor):
            def __init__(self):
                self.found = False

            def visit_Yield(self, node):
                self.found = True

            def visit_YieldFrom(self, node):
                self.found = True

            def visit_FunctionDef(self, node):
                pass  # do not descend into nested functions

            def visit_ClassDef(self, node):
                pass  # do not descend into nested classes

        finder = _YieldFinder()
        for stmt in node.body:
            finder.visit(stmt)
        return finder.found
    

    def eval_generator_obj(self, body, local_env, block=None):
        ''' so that it can be overridden'''
        return self.gen_state(self, body, local_env)

    def _execute_function_body(self, body):
        self._defer_stack = []
        try:
            self.eval(body)
            return None
        except ReturnException as re:
            return re.value
        finally:
            for stmt in reversed(self._defer_stack):
                if hasattr(stmt, '_nomi_defer'):
                    delattr(stmt, '_nomi_defer')
                self.eval(stmt)
            self._defer_stack = []

    def eval_Function(self, node: ast.FunctionDef) -> callable:
        '''
        isolate evaluating function from the binding
        note that, at the moment, there is no "Function" node
        there maybe one later; this allows function to be
        created without bindings
        '''
        # Create function environment with closure as parent
        func_env = self._new_closure_env()
        
        def func(*args, **kwargs):
            # TODO: cache generator detection on the node; this is recomputed on every call.
            is_generator = self._is_generator_function(node)
            
            #env is copied so that constraints work properly
            # Constraints from parent are relevant only on global/non-local scope (to-implement)
            local_env = func_env.copy()
            block = kwargs.pop(BLOCK_KWARG, None)
            with self.this_env(local_env):
                self._bind_function_args(node, local_env, args, kwargs)
            if is_generator:
                return self.eval_generator_obj(node.body, local_env, block=block)
            else:                
                with self.this_env(local_env):
                    return self._execute_function_body(node.body)
   
        func.func_env = func_env
        # ast_node is attached so eval_Call can distinguish user-defined
        # functions from builtins.  If call resolution moves to a registry,
        # this tag can be dropped.
        func.ast_node = node

        return func

    def eval_FunctionDef(self, node:ast.FunctionDef):

        func = self.eval_Function(node)
        name = node.name 
        if not name:
            # function expression — no name to bind, return as-is.
            # Decorator processing is skipped because expression functions
            # have no declaration-site name to wrap.
            return func
        
        func.__name__ = name
        decorated_func = self.apply_decorators(func, node.decorator_list)        

        self.current_env.set(node.name, decorated_func)
        return decorated_func

    def eval_Lambda(self, node: ast.Lambda) -> Any:
        # Create function environment with closure as parent  
        func_env = self._new_closure_env()
        
        def lambda_func(*args, **kwargs):
            local_env = func_env.copy()
            self._bind_function_args(node, local_env, args, kwargs)
            with self.this_env(local_env):
                return self.eval(node.body)
        
        lambda_func.func_env = func_env  
        lambda_func.ast_node = node
        return lambda_func

    def _bind_self_obj(self, env, params, self_obj):
        if self_obj is None:
            return params
        if params:
            env.set(params[0].arg, self_obj)
            return params[1:]
        return params

    def _bind_declared_params(self, env, params, posargs, kwargs, keywordable_params=None):
        if keywordable_params is None:
            keywordable_params = params
        keywordable = {param.arg for param in keywordable_params}
        for i, param in enumerate(params):
            if i < len(posargs):
                env.set(param.arg, posargs[i])
            elif param.arg in keywordable and param.arg in kwargs:
                env.set(param.arg, kwargs[param.arg])

    def _bind_keyword_values(self, env, params, kwonlyargs, posargs, kwargs):
        bound_by_position = {param.arg for param in params[:len(posargs)]}
        declared_names = {param.arg for param in params}
        declared_names.update(param.arg for param in kwonlyargs)
        for key, value in kwargs.items():
            if key in declared_names and key not in bound_by_position:
                env.set(key, value)

    def _apply_param_defaults(self, env, params, defaults):
        num_defaults = len(defaults)
        if not num_defaults:
            return

        default_start = len(params) - num_defaults
        for i, param in enumerate(params):
            if param.arg not in env.bindings and i >= default_start:
                default_idx = i - default_start
                if default_idx < len(defaults):
                    env.set(param.arg, self.eval(defaults[default_idx]))

    def _apply_kwonly_defaults(self, env, params, defaults):
        for param, default in zip(params, defaults or []):
            if param.arg not in env.bindings and default is not None:
                env.set(param.arg, self.eval(default))

    def _bind_varargs(self, func_node, env, params, posargs):
        if not func_node.args.vararg:
            return

        vararg_name = func_node.args.vararg.arg
        consumed_pos = min(len(params), len(posargs))
        remaining_args = posargs[consumed_pos:]
        env.set(vararg_name, tuple(remaining_args))

    def _bind_kwargs(self, func_node, env, params, kwargs):
        if not func_node.args.kwarg:
            return

        kwarg_name = func_node.args.kwarg.arg
        consumed_kw = {p.arg for p in params if p.arg in env.bindings}
        extra_kwargs = {k: v for k, v in kwargs.items() if k not in consumed_kw}
        env.set(kwarg_name, extra_kwargs)

    def _bind_function_args(self, func_node, env, posargs, kwargs, self_obj=None):
        '''
        NOTE: this is called by both definition and call
        for call, arguments are already evaluated
        for definition, we need to evaluate the defaults

        We may actually eval all of them here 
        '''


        # Note: constraints are already set up in parent env, so env.set() will check them automatically
        # TODO: route this through the shared binding/constraint engine once the parser and runtime agree on one path.
        
        posonlyargs = list(func_node.args.posonlyargs)
        positional_or_keyword_args = list(func_node.args.args)
        params = posonlyargs + positional_or_keyword_args
        kwonlyargs = list(func_node.args.kwonlyargs)
        defaults = func_node.args.defaults or []
        
        params = self._bind_self_obj(env, params, self_obj)
        self._bind_declared_params(env, params, posargs, kwargs, positional_or_keyword_args)
        self._bind_keyword_values(env, positional_or_keyword_args, kwonlyargs, posargs, kwargs)
        self._apply_param_defaults(env, params, defaults)
        self._apply_kwonly_defaults(env, kwonlyargs, func_node.args.kw_defaults)
        self._bind_varargs(func_node, env, params, posargs)
        self._bind_kwargs(func_node, env, params + kwonlyargs, kwargs)
    
    def eval_Return(self, node: ast.Return) -> None:
        value = self.eval(node.value) if node.value else None
        raise ReturnException(value)
