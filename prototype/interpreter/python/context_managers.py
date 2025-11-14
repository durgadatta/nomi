import ast
from .base import ReturnException, YieldException


class ContextManagerMixin:
    def eval_With(self, node: ast.With, *, state=None, generator_state=None) -> None:
        if state is None:
            managers_with_vars = []
            for item in node.items:
                context_obj = self.eval(item.context_expr)
                self._validate_context_manager(context_obj, item)
                enter_result = self._call_context_enter(context_obj)
                if item.optional_vars:
                    self.current_env.set(item.optional_vars.id, enter_result)
                managers_with_vars.append((context_obj, enter_result))
            state = {'managers': managers_with_vars, 'body_index': 0, 'node': node}

        self._execute_with_body(node.body, state['managers'], state=state, generator_state=generator_state)

    def _validate_context_manager(self, context_obj, item):
        """Validate that an object is a proper context manager."""
        if not (hasattr(context_obj, "__enter__") and hasattr(context_obj, "__exit__")):
            raise TypeError(f"Object {context_obj} is not a context manager at line {self.get_lineno(item)}")

    def _call_context_enter(self, context_obj):
        """Call __enter__ method on a context manager."""
        method = context_obj.__enter__
        method_node = getattr(method, "ast_node", None)
        closure_env = getattr(method, "closure_env", self.current_env)
        
        # For interpreted functions
        if method_node and isinstance(method_node, ast.FunctionDef):
            call_env = self.env_class(self, parent=closure_env)
            call_env.set(method_node.args.args[0].arg, context_obj)  # Set 'self'
            
            with self.this_env(call_env):
                try:
                    self.eval(method_node.body)
                    return None  # No explicit return in __enter__
                except ReturnException as re:
                    return re.value  # Return value if explicitly returned

        else:
            # For Python/native functions
            return method()

    def _call_context_exit(self, context_obj, exc_type, exc_val, exc_tb):
        """Call __exit__ method on a context manager."""
        method = context_obj.__exit__
        method_node = getattr(method, "ast_node", None)
        closure_env = getattr(method, "closure_env", self.current_env)
        
        # For interpreted functions
        if method_node and isinstance(method_node, ast.FunctionDef):
            call_env = self.env_class(self, parent=closure_env)
            call_env.set(method_node.args.args[0].arg, context_obj)  # Set 'self'
            
            # Set exception parameters based on actual parameter names
            param_names = [arg.arg for arg in method_node.args.args[1:]]  # Skip 'self'
            if len(param_names) >= 1:
                call_env.set(param_names[0], exc_type)
            if len(param_names) >= 2:
                call_env.set(param_names[1], exc_val)
            if len(param_names) >= 3:
                call_env.set(param_names[2], exc_tb)
            
            with self.this_env(call_env):
                try:
                    self.eval(method_node.body)
                    return False  # Default: don't suppress exception
                except ReturnException as re:
                    return re.value  # Return suppression flag
        else:
            # For Python/native functions
            return method(exc_type, exc_val, exc_tb)

    def _execute_with_body(self, body, managers_with_vars, *, state, generator_state=None):
        if generator_state and generator_state.injected_exception is not None:
            generator_state.raise_injected_exception()

        try:
            i = state.get('body_index', 0)
            while i < len(body):
                try:
                    self.eval(body[i], generator_state=generator_state)
                    i += 1
                except YieldException:
                    state['body_index'] = i + 1
                    if generator_state:
                        generator_state.pause(state['node'], state)
                    raise
            self._exit_contexts_normal(managers_with_vars)
        except Exception as e:
            suppressed = self._exit_contexts_with_exception(managers_with_vars, e)
            if not suppressed:
                raise

    def _exit_contexts_normal(self, managers_with_vars):
        """Exit all context managers with no exception."""
        for context_obj, _ in reversed(managers_with_vars):
            try:
                self._call_context_exit(context_obj, None, None, None)
            except Exception as e:
                raise RuntimeError(f"Error in __exit__ during normal exit: {e}") from e

    def _exit_contexts_with_exception(self, managers_with_vars, exception):
        """Exit all context managers with an exception, returning whether it was suppressed."""
        suppressed = False
        exc_type, exc_val, exc_tb = type(exception), exception, exception.__traceback__
        
        for context_obj, _ in reversed(managers_with_vars):
            try:
                exit_result = self._call_context_exit(context_obj, exc_type, exc_val, exc_tb)
                if exit_result:
                    suppressed = True
            except Exception as exit_e:
                raise RuntimeError(f"Error in __exit__ of {context_obj}: {exit_e}") from exit_e
        
        return suppressed