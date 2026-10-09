import ast
from copy import copy
from inspect import Parameter, Signature
from typing import List, Any

from ..constants import BLOCK_KWARG
from .signals import ReturnException
from .function_call import FunctionCallMixin
from .continuation import contains_scope_yield

class FunctionMixin(FunctionCallMixin):
    FUNCTION_METADATA_ATTRS = ('__name__', 'ast_node', 'func_env')

    def _new_closure_env(self):
        # TODO(NOMI-ARCH-016): Introduce explicit call-frame/environment
        # ownership before constraints, capabilities, and block policies make
        # shallow environment copies semantically or performance-sensitive.
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
        """Check for yield/yield-from in the function body, skipping nested definitions.

        Result is cached on the node so repeated calls (one per invocation) are free.
        """
        cached = getattr(node, '_nomi_is_generator', None)
        if cached is not None:
            return cached

        found = any(contains_scope_yield(statement) for statement in node.body)
        node._nomi_is_generator = found
        return found
    

    def eval_generator_obj(self, body, local_env, block=None):
        ''' so that it can be overridden'''
        return self.gen_state(self, body, local_env)

    def _execute_function_body(self, body):
        saved_defer = getattr(self, '_defer_stack', [])
        self._defer_stack = []
        try:
            self.eval(body)
            return None
        except ReturnException as re:
            return re.value
        finally:
            try:
                for stmt in reversed(self._defer_stack):
                    # Do not mutate cached source when cleanup calls recurse.
                    deferred = copy(stmt)
                    if hasattr(deferred, '_nomi_defer'):
                        delattr(deferred, '_nomi_defer')
                    self.eval(deferred)
            finally:
                self._defer_stack = saved_defer

    def eval_Function(self, node: ast.FunctionDef) -> callable:
        '''
        isolate evaluating function from the binding
        note that, at the moment, there is no "Function" node
        NOMI-ARCH-016 tracks the eventual call-frame/function value boundary;
        this keeps function creation separate from binding for now.
        '''
        # Create function environment with closure as parent
        func_env = self._new_closure_env()
        
        def func(*args, **kwargs):
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
            with self.this_env(local_env):
                self._bind_function_args(node, local_env, args, kwargs)
                return self.eval(node.body)
        
        lambda_func.func_env = func_env  
        lambda_func.ast_node = node
        return lambda_func

    def _function_signature(self, func_node):
        """Adapt hosted AST parameters without evaluating their defaults."""
        arguments = func_node.args
        positional = list(arguments.posonlyargs) + list(arguments.args)
        defaults = dict(zip(
            (param.arg for param in positional[len(positional) - len(arguments.defaults):]),
            arguments.defaults,
        ))
        parameters = []
        for index, param in enumerate(positional):
            kind = (Parameter.POSITIONAL_ONLY if index < len(arguments.posonlyargs)
                    else Parameter.POSITIONAL_OR_KEYWORD)
            parameters.append(Parameter(
                param.arg, kind, default=defaults.get(param.arg, Parameter.empty),
            ))
        if arguments.vararg:
            parameters.append(Parameter(arguments.vararg.arg, Parameter.VAR_POSITIONAL))
        for param, default in zip(arguments.kwonlyargs, arguments.kw_defaults):
            parameters.append(Parameter(
                param.arg, Parameter.KEYWORD_ONLY,
                default=default if default is not None else Parameter.empty,
            ))
        if arguments.kwarg:
            parameters.append(Parameter(arguments.kwarg.arg, Parameter.VAR_KEYWORD))
        return Signature(parameters)

    def _bind_function_args(self, func_node, env, posargs, kwargs, self_obj=None):
        # TODO(NOMI-SUBSTRATE-011): Replace this hosted shape adapter with the
        # shared Nomi binding contract; it does not check types/captures/effects.
        signature = self._function_signature(func_node)
        if self_obj is not None:
            posargs = (self_obj, *posargs)
        positional_only = {param.arg for param in func_node.args.posonlyargs}
        collisions = positional_only.intersection(kwargs)
        if collisions and func_node.args.kwarg is None:
            names = ', '.join(sorted(collisions))
            raise TypeError(f"positional-only arguments passed by keyword: {names}")
        # Host inspect versions disagree on omitted positional-only defaults.
        # Keep these keys in the collector, never in ordinary name matching.
        named = {name: value for name, value in kwargs.items() if name not in positional_only}
        supplied = signature.bind(*posargs, **named).arguments
        if func_node.args.kwarg:
            consumed = {
                name for name, param in signature.parameters.items()
                if param.kind in (Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY)
            }
            supplied[func_node.args.kwarg.arg] = {
                name: value for name, value in kwargs.items() if name not in consumed
            }

        # Validate the whole call before any frame write or default/constraint
        # evaluation. AST defaults remain lexical and call-time, not host values.
        for name, param in signature.parameters.items():
            if name in supplied:
                value = supplied[name]
            elif param.kind == Parameter.VAR_POSITIONAL:
                value = ()
            elif param.kind == Parameter.VAR_KEYWORD:
                value = {}
            else:
                value = self.eval(param.default)
            env.set(name, value)
    
    def eval_Return(self, node: ast.Return) -> None:
        value = self.eval(node.value) if node.value else None
        raise ReturnException(value)
