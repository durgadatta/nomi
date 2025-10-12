from prototype.interpreter.python.base import Environment, GeneratorState
import ast
from typing import List, Any, Callable

from prototype.interpreter.python.base import (
    ReturnException, BreakException, ContinueException, YieldException
)

class FunctionMixin:
    def apply_decorators(self, obj: Any, decorators: List[ast.expr]) -> Any:
        for dec in reversed(decorators):
            try:
                old_env = self.current_env
                self.current_env = Environment(self, parent=old_env)
                dec_func = self.eval(dec)
                obj = dec_func(obj)
                self.current_env = old_env
            except Exception as e:
                self.current_env = old_env
                raise RuntimeError(f"Error applying decorator at line {self.get_lineno(dec)}: {str(e)}") from e
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

    def eval_FunctionDef(self, node: ast.FunctionDef) -> None:
        closure_env = self.current_env
        
        def func(*args, **kwargs):            
            is_generator = self._is_generator_function(node)
            
            if is_generator:
                local_env = Environment(self, parent=closure_env)
                self._bind_function_args(node, local_env, args, kwargs)
                gen = GeneratorState(self, node.body, local_env)
                return gen
            else:
                # Regular function: execute the body normally
                local_env = Environment(self, parent=closure_env)
                self._bind_function_args(node, local_env, args, kwargs)
                
                old_env = self.current_env
                self.current_env = local_env
                try:
                    for stmt in node.body:
                        self.eval(stmt)
                    return None
                except ReturnException as re:
                    return re.value
                except BreakException:
                    raise SyntaxError(f"'break' outside loop at line {self.get_lineno(node)}")
                except ContinueException:
                    raise SyntaxError(f"'continue' outside loop at line {self.get_lineno(node)}")
                finally:
                    self.current_env = old_env

        func.closure_env = closure_env
        func.ast_node = node
        
        # Apply decorators and store the function
        old_env = self.current_env
        self.current_env = closure_env
        func = self.apply_decorators(func, node.decorator_list)
        self.current_env = old_env
        
        self.current_env.set(node.name, func)

    def eval_Lambda(self, node: ast.Lambda) -> Any:
        closure_env = self.current_env  # ⭐ Capture the current environment
        
        def lambda_func(*args, **kwargs):
            local_env = Environment(self, parent=closure_env)  # ⭐ Use the captured closure
            self._bind_function_args(node, local_env, args, kwargs)
            
            old_env = self.current_env
            self.current_env = local_env
            try:
                return self.eval(node.body)
            finally:
                self.current_env = old_env
        
        lambda_func.closure_env = closure_env
        lambda_func.ast_node = node
        return lambda_func

    def _bind_function_args(self, func_node, env, posargs, kwargs, self_obj=None):
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

        # Bind positional arguments
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
        closure_env = getattr(func, "closure_env", None)
        
        if func_node and isinstance(func_node, ast.FunctionDef):
            # Just call the function - it will handle generator detection internally
            return func(*posargs, **kwargs)

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
        closure_env = getattr(init_method, "closure_env", None)
        
        # If no explicit closure_env, use current environment
        if closure_env is None:
            closure_env = self.current_env

        if func_node and isinstance(func_node, ast.FunctionDef):
            # Interpreted __init__
            call_env = Environment(self, parent=closure_env)
            
            # Bind self first
            call_env.set('self', instance)
            
            # Then bind other arguments
            self._bind_function_args(func_node, call_env, posargs, kwargs, self_obj=instance)

            # Execute __init__ body
            old_env = self.current_env
            self.current_env = call_env
            try:
                for stmt in func_node.body:
                    self.eval(stmt)
            except ReturnException as re:
                if re.value is not None:
                    raise TypeError(f"__init__ should return None, got {re.value}")
            finally:
                self.current_env = old_env
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