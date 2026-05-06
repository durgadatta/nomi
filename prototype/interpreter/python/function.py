import ast
from typing import List, Any

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
        """Determine if a function is a generator by checking for yield statements, skipping nested functions."""
        
        def _check_for_yield(node: ast.AST) -> bool:
            """Recursively check for yield in this node and its children, skipping nested functions."""
            # Check current node
            if isinstance(node, (ast.Yield, ast.YieldFrom)):
                return True
            
            # Check children, but skip nested function/class definitions
            for child in ast.iter_child_nodes(node):
                # Skip function and class definitions - don't descend into them
                if isinstance(child, (ast.FunctionDef, ast.ClassDef)):
                    continue
                if _check_for_yield(child):
                    return True
            return False

        # Just use the recursive function on the entire function body
        # It will automatically skip nested functions due to the check in _check_for_yield
        is_generator = _check_for_yield(node)
        return is_generator
    

    def eval_generator_obj(self, body, local_env, block=None):
        ''' so that it can be overridden'''
        return self.gen_state(self, body, local_env)

    def _execute_function_body(self, body):
        try:
            self.eval(body)
            return None
        except ReturnException as re:
            return re.value

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
            is_generator = self._is_generator_function(node)
            
            #env is copied so that constraints work properly
            # Constraints from parent are relevant only on global/non-local scope (to-implement)
            local_env = func_env.copy()
            block = kwargs.pop('__block__', None)
            with self.this_env(local_env):
                self._bind_function_args(node, local_env, args, kwargs)
            if is_generator:
                return self.eval_generator_obj(node.body, local_env, block=block)
            else:                
                with self.this_env(local_env):
                    return self._execute_function_body(node.body)
   
        func.func_env = func_env 
        # this is used in eval_Call to determine user-defined function
        #TODO: there maybe a better way to handle this
        func.ast_node = node

        return func

    def eval_FunctionDef(self, node:ast.FunctionDef):

        func = self.eval_Function(node)
        name = node.name 
        if not name:
            # function expr; also no decorator processing
            # TODO: rethink this hook-up
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

    def _bind_function_args(self, func_node, env, posargs, kwargs, self_obj=None):
        '''
        NOTE: this is called by both definition and call
        for call, arguments are already evaluated
        for definition, we need to evaluate the defaults

        We may actually eval all of them here 
        '''


        # Note: constraints are already set up in parent env, so env.set() will check them automatically
        
        params = list(func_node.args.args)
        defaults = func_node.args.defaults or []
        
        if self_obj is not None:
            # Bind to first parameter, regardless of its name
            if params:
                env.set(params[0].arg, self_obj)
                params = params[1:]  # Remove the bound parameter
            else:
                # No parameters but self_obj provided - might be an error case
                # Or handle __init__ without parameters
                pass

        # Bind positional arguments (constraints checked by env.set())
        for i, param in enumerate(params):
            if i < len(posargs):
                env.set(param.arg, posargs[i])
            elif param.arg in kwargs:
                env.set(param.arg, kwargs[param.arg])

        # Bind keyword arguments
        for key, value in kwargs.items():
            # Only bind if not already bound by position
            if key not in [p.arg for p in params[:len(posargs)]]:
                env.set(key, value)

        # Apply defaults
        num_defaults = len(defaults)
        if num_defaults:
            default_start = len(params) - num_defaults
            for i, param in enumerate(params):
                if param.arg not in env.bindings and i >= default_start:
                    default_idx = i - default_start
                    if default_idx < len(defaults):
                        env.set(param.arg, self.eval(defaults[default_idx]))

        # Handle *args
        if func_node.args.vararg:
            vararg_name = func_node.args.vararg.arg
            consumed_pos = min(len(params), len(posargs))
            remaining_args = posargs[consumed_pos:]
            env.set(vararg_name, tuple(remaining_args))

        # Handle **kwargs
        if func_node.args.kwarg:
            kwarg_name = func_node.args.kwarg.arg
            consumed_kw = {p.arg for p in params if p.arg in env.bindings}
            extra_kwargs = {k: v for k, v in kwargs.items() if k not in consumed_kw}
            env.set(kwarg_name, extra_kwargs)
    
    def eval_Return(self, node: ast.Return) -> None:
        value = self.eval(node.value) if node.value else None
        raise ReturnException(value)
