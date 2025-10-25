import ast
from .base import Environment, ReturnException


class ContextManagerMixin:
    def eval_With(self, node: ast.With) -> None:
        """Evaluate a 'with' statement with multiple context managers."""
        managers_with_vars = []
        
        # Setup all context managers
        for item in node.items:
            context_obj = self.eval(item.context_expr)
            self._validate_context_manager(context_obj, item)
            
            # Call __enter__ and store the result
            enter_result = self._call_context_enter(context_obj)
            if item.optional_vars:
                self.current_env.set(item.optional_vars.id, enter_result)
            
            managers_with_vars.append((context_obj, enter_result))
        
        # Execute the body with proper exception handling
        self._execute_with_body(node.body, managers_with_vars)

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
            
            old_env = self.current_env
            self.current_env = call_env
            try:
                for stmt in method_node.body:
                    self.eval(stmt)
                return None  # No explicit return in __enter__
            except ReturnException as re:
                return re.value  # Return value if explicitly returned
            finally:
                self.current_env = old_env
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
            
            old_env = self.current_env
            self.current_env = call_env
            try:
                for stmt in method_node.body:
                    self.eval(stmt)
                return False  # Default: don't suppress exception
            except ReturnException as re:
                return re.value  # Return suppression flag
            finally:
                self.current_env = old_env
        else:
            # For Python/native functions
            return method(exc_type, exc_val, exc_tb)

    def _execute_with_body(self, body, managers_with_vars):
        """Execute the with statement body with proper exception handling."""
        try:
            for stmt in body:
                self.eval(stmt)
            # Normal exit - no exception occurred
            self._exit_contexts_normal(managers_with_vars)
        except Exception as e:
            # Exception occurred - handle it through context managers
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