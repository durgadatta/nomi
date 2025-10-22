import ast
from .base import Environment, ReturnException


class ContextMangerMixin:
    def eval_With(self, node: ast.With) -> None:
        """Evaluate a 'with' statement with multiple context managers."""
        context_managers = self._setup_context_managers(node.items)
        entered_managers = self._enter_contexts(context_managers)
        self._execute_with_body(node.body, entered_managers)

    def _setup_context_managers(self, items):
        """Process and validate all with_item nodes."""
        context_managers = []
        for item in items:
            context_obj = self.eval(item.context_expr)
            self._validate_context_manager(context_obj, item)
            context_managers.append((context_obj, item.optional_vars))
        return context_managers

    def _validate_context_manager(self, context_obj, item):
        """Validate that an object is a proper context manager."""
        if not (hasattr(context_obj, "__enter__") and hasattr(context_obj, "__exit__")):
            raise TypeError(f"Object {context_obj} is not a context manager at line {self.get_lineno(item)}")

    def _enter_contexts(self, context_managers):
        """Enter all context managers and return their exit methods."""
        entered = []
        for context_obj, opt_var in context_managers:
            enter_result = self._call_enter(context_obj)
            if opt_var:
                self.current_env.set(opt_var.id, enter_result)
            entered.append((context_obj, context_obj.__exit__))
        return entered

    def _execute_with_body(self, body, entered_managers):
        """Execute the with statement body with proper exception handling."""
        try:
            for stmt in body:
                self.eval(stmt)
        except Exception as e:
            self._handle_exception(entered_managers, e)
        else:
            self._handle_normal_exit(entered_managers)

    def _handle_exception(self, entered_managers, exception):
        """Handle exception by calling __exit__ on all managers in reverse order."""
        suppressed = False
        exc_type, exc_val, exc_tb = type(exception), exception, exception.__traceback__
        
        for context_obj, exit_method in reversed(entered_managers):
            try:
                exit_result = self._call_exit(context_obj, exit_method, exc_type, exc_val, exc_tb)
                if exit_result:
                    suppressed = True
            except Exception as exit_e:
                raise RuntimeError(f"Error in __exit__ of {context_obj}: {exit_e}") from exit_e

        if not suppressed:
            raise

    def _handle_normal_exit(self, entered_managers):
        """Handle normal exit by calling __exit__(None, None, None) on all managers."""
        for context_obj, exit_method in reversed(entered_managers):
            try:
                self._call_exit(context_obj, exit_method, None, None, None)
            except Exception as e:
                raise RuntimeError(f"Error calling __exit__: {e}") from e

    def _call_enter(self, context_obj):
        """Call __enter__ on a context manager."""
        return self._call_context_method(context_obj, context_obj.__enter__, "__enter__")

    def _call_exit(self, context_obj, exit_method, exc_type, exc_val, exc_tb):
        """Call __exit__ on a context manager."""
        return self._call_context_method(context_obj, exit_method, "__exit__", exc_type, exc_val, exc_tb)

    def _call_context_method(self, context_obj, method, name, *args):
        """Call __enter__ or __exit__, handling user-defined function nodes."""
        method_node = getattr(method, "ast_node", None)
        closure_env = getattr(method, "closure_env", self.current_env)
        call_env = Environment(self, parent=closure_env)
        old_env = self.current_env
        self.current_env = call_env
        try:
            if method_node and isinstance(method_node, ast.FunctionDef):
                call_env.set(method_node.args.args[0].arg, context_obj)
                if name == "__exit__":
                    call_env.set("exc_type", args[0] if args else None)
                    call_env.set("exc_val", args[1] if len(args) > 1 else None)
                    call_env.set("exc_tb", args[2] if len(args) > 2 else None)
                for stmt in method_node.body:
                    self.eval(stmt)
            else:
                return method(*args)
        except ReturnException as re:
            return re.value
        finally:
            self.current_env = old_env