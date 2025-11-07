import ast
from typing import List, Any

from .base import (
    Environment, ReturnException, BreakException, ContinueException
)
from .generator_state import GeneratorState

class FunctionMixin:
    def apply_decorators(self, obj: Any, decorators: List[ast.expr]) -> Any:
        for dec in reversed(decorators):
            # Create new environment for decorator evaluation
            dec_env = self.env_class(self, parent=self.current_env)
            
            with self.this_env(dec_env):
                dec_func = self.eval(dec)
                
                # Store all original attributes
                original_attrs = {}
                for attr_name in ['__name__', 'ast_node', 'func_env']:
                    if hasattr(obj, attr_name):
                        original_attrs[attr_name] = getattr(obj, attr_name)
                
                # Apply the decorator
                obj = dec_func(obj)
                
                # Always restore critical attributes
                for attr_name, attr_value in original_attrs.items():
                    setattr(obj, attr_name, attr_value)
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

    def eval_Function(self, node: ast.FunctionDef) -> callable:
        '''
        isolate evaluating function from the binding
        note that, at the moment, there is no "Function" node
        there maybe one later; this allows function to be
        created without bindings
        '''
        # Create function environment with closure as parent
        func_env = self.env_class(self, parent=self.current_env)
        
        def func(*args, **kwargs):
            is_generator = self._is_generator_function(node)
            
            #env is copied so that constraints work properly
            # Constraints from parent are relevant only on global/non-local scope (to-implement)
            local_env = func_env.copy()
            self._bind_function_args(node, local_env, args, kwargs)
            if is_generator:
                gen = self.gen_state(self, node.body, local_env)
                # NOTE: TODO: this needs to be abstracted out to nomi layer
                # if needed handle gen separetley at call layer
                # but local_env needs to be correctly handled as well
                block = getattr(func, '_nomi_block', None)
                if block is not None:
                    gen._nomi_block = block
                return gen
            else:                
                with self.this_env(local_env):
                    try:
                        for stmt in node.body:
                            self.eval(stmt)
                        return None
                    except ReturnException as re:
                        return re.value
   
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
        func_env = self.env_class(self, parent=self.current_env) 
        
        def lambda_func(*args, **kwargs):
            local_env = func_env.copy()
            self._bind_function_args(node, local_env, args, kwargs)
            with self.this_env(local_env):
                return self.eval(node.body)
        
        lambda_func.func_env = func_env  
        lambda_func.ast_node = node
        return lambda_func

    def _bind_function_args(self, func_node, env, posargs, kwargs, self_obj=None):
        # Note: constraints are already set up in parent env, so env.set() will check them automatically
        
        params = list(func_node.args.args)
        defaults = func_node.args.defaults or []
        
        # Handle self binding
        if self_obj is not None:
            if params and params[0].arg == 'self':
                env.set('self', self_obj)
                params = params[1:]
            # If it's __init__, we should have self_obj but might not have 'self' param
            elif self_obj is not None and (not params or params[0].arg != 'self'):
                # Still set 'self' in environment for __init__
                env.set('self', self_obj)

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

    def eval_Call(self, node: ast.Call) -> Any:
        """
        Evaluate a function or class call:
        - built-in / native Python function
        - user-defined function (normal or generator)
        - class instantiation
        - decorators (native or interpreted)
        """
        func = self.eval(node.func)
        # Evaluate arguments
        posargs = []
        for arg in node.args:
            if isinstance(arg, ast.Starred):
                posargs.extend(self.eval(arg.value))
            else:
                posargs.append(self.eval(arg))

        kwargs = {}
        for kw in node.keywords:
            if kw.arg is None:
                kw_val = self.eval(kw.value)
                if not isinstance(kw_val, dict):
                    raise TypeError(f"argument after ** must be a mapping at line {self.get_lineno(node)}")
                kwargs.update(kw_val)
            else:
                kwargs[kw.arg] = self.eval(kw.value)

        # --- Built-in / native callable ---
        if callable(func) and not hasattr(func, "ast_node"):
            try:
                return func(*posargs, **kwargs)
            except StopIteration:
                # This is a control-signal from GeneratorState; don't wrap it
                raise 
            except Exception as e:
                raise RuntimeError(
                    f"Error calling built-in {getattr(func, '__name__', repr(func))} "
                    f"at line {self.get_lineno(node)}: {str(e)}"
                ) from e

        # --- User-defined function or generator ---
        func_node = getattr(func, "ast_node", None)
        
        if func_node and isinstance(func_node, ast.FunctionDef):
            # Just call the function - it will handle generator detection internally
            # pass the 

            #TODO: later move to nomi layer - create one helper to eval user-def function
            # Check if this call has a block

            block = getattr(node, '_nomi_block', None)
            # pass the block to be yield to actual function
            # so that it be relayed to generator state
            #TODO: organize this hooking 
            func._nomi_block = (block, self.current_env)
            result = func(*posargs, **kwargs)
            
            #TODO: FIX: this seems to have been removed during decorator application?
            # or other func_expr processing, revieww it later; we should not have to
            # check it here
            if getattr(node, '_nomi_block', None):
                del func._nomi_block
            return result

            

        # --- Class instantiation ---
        if isinstance(func, type):
            return self._instantiate_class(func, posargs, kwargs, node)

        # --- Fallback for callable objects (decorators, etc.) ---
        if callable(func):
            try:
                return func(*posargs, **kwargs)
            except Exception as e:
                raise RuntimeError(
                    f"Error calling callable {repr(func)} at line {self.get_lineno(node)}: {str(e)}"
                ) from e

        raise TypeError(f"Object {func} is not callable at line {self.get_lineno(node)}")
    
    def _instantiate_class(self, cls, posargs, kwargs, call_node=None):
        """Enhanced class instantiation"""
        # Create instance
        instance = cls.__new__(cls)
        if not isinstance(instance, cls):
            raise TypeError(f"__new__ returned non-instance of {cls.__name__}")

        # Get __init__ method
        init_method = getattr(instance, "__init__", None)
        
        if init_method is None:
            # No __init__, just return instance
            return instance

        # Check if it's an interpreted method
        func_node = getattr(init_method, "ast_node", None)
        func_env = getattr(init_method, "func_env", None)
        
        # If no explicit func_env, use current environment
        if func_env is None:
            func_env = self.current_env

        if func_node and isinstance(func_node, ast.FunctionDef):
            # Interpreted __init__
            call_env = self.env_class(self, parent=func_env)            
            # Bind self first
            call_env.set('self', instance)
            
            # Then bind other arguments
            self._bind_function_args(func_node, call_env, posargs, kwargs, self_obj=instance)

            # Execute __init__ body
            with self.this_env(call_env):
                try:
                    for stmt in func_node.body:
                        self.eval(stmt)
                except ReturnException as re:
                    if re.value is not None:
                        raise TypeError(f"__init__ should return None, got {re.value}")

        else:
            # Native __init__
            try:
                init_method(*posargs, **kwargs)
            except Exception as e:
                lineno = self.get_lineno(call_node) if call_node else "unknown"
                raise RuntimeError(f"Error in __init__ at line {lineno}: {str(e)}") from e

        return instance

    def eval_Return(self, node: ast.Return) -> None:
        value = self.eval(node.value) if node.value else None
        raise ReturnException(value)