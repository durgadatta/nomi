import ast
from prototype.interpreter.python.base import Environment, ReturnException, BreakException, ContinueException

class ClassMixin:
    def eval_ClassDef(self, node: ast.ClassDef) -> None:
        bases = [self.eval(b) for b in node.bases]
        class_env = Environment(self, parent=self.current_env)
        old_env = self.current_env
        self.current_env = class_env
        for stmt in node.body:
            self.eval(stmt)
            if isinstance(stmt, ast.FunctionDef):
                func = class_env.bindings.get(stmt.name)
                if func:
                    func.closure_env = class_env
                    func.ast_node = stmt
        self.current_env = old_env
        class_dict = class_env.bindings
        try:
            cls = type(node.name, tuple(bases), class_dict)
        except Exception as e:
            raise RuntimeError(f"Error creating class '{node.name}' at line {self.get_lineno(node)}: {str(e)}") from e
        cls = self.apply_decorators(cls, node.decorator_list)
        self.current_env.set(node.name, cls)
        
    def eval_With(self, node: ast.With) -> None:
        """
        Evaluate a 'with' statement:
        with EXPR as VAR:
            BODY
        """

        # Handle chained 'with': with a(), b() as y:
        contexts = []
        for item in node.items:
            context_obj = self.eval(item.context_expr)
            enter = getattr(context_obj, "__enter__", None)
            exit_ = getattr(context_obj, "__exit__", None)
            if not callable(enter) or not callable(exit_):
                raise TypeError(f"Object {context_obj} is not a context manager at line {self.get_lineno(node)}")

            contexts.append((context_obj, enter, exit_, item.optional_vars))

        # We enter contexts in order, and exit in reverse order.
        entered = []
        try:
            for context_obj, enter, exit_, opt_var in contexts:
                # Call __enter__
                enter_result = self._call_context_method(context_obj, enter, "__enter__")

                if opt_var:
                    self.current_env.set(opt_var.id, enter_result)

                entered.append((context_obj, exit_))

            # Execute body
            for stmt in node.body:
                self.eval(stmt)

        except BreakException:
            raise SyntaxError(f"'break' outside loop at line {self.get_lineno(node)}")
        except ContinueException:
            raise SyntaxError(f"'continue' outside loop at line {self.get_lineno(node)}")

        except Exception as e:
            # Exit all entered contexts (in reverse)
            suppressed = False
            for context_obj, exit_ in reversed(entered):
                try:
                    res = self._call_context_method(context_obj, exit_, "__exit__", type(e), e, e.__traceback__)
                    if res:
                        suppressed = True
                except Exception as exit_e:
                    raise RuntimeError(f"Error in __exit__ of {context_obj}: {exit_e}") from exit_e

            if not suppressed:
                raise

        else:
            # Normal exit: no exception
            for context_obj, exit_ in reversed(entered):
                try:
                    self._call_context_method(context_obj, exit_, "__exit__", None, None, None)
                except Exception as e:
                    raise RuntimeError(f"Error calling __exit__ at line {self.get_lineno(node)}: {e}") from e
                
    def eval_Attribute(self, node: ast.Attribute) -> Any:
        value = self.eval(node.value)
        try:
            return getattr(value, node.attr)
        except AttributeError:
            raise AttributeError(f"'{type(value).__name__}' object has no attribute '{node.attr}' at line {self.get_lineno(node)}")

    def eval_Subscript(self, node: ast.Subscript) -> Any:
        value = self.eval(node.value)
        slice_ = self.eval(node.slice)
        try:
            return value[slice_]
        except (IndexError, KeyError) as e:
            raise IndexError(f"Subscript error at line {self.get_lineno(node)}: {str(e)}") from e
        
    def _call_context_method(self, context_obj, method, name, *args):
        """Helper: call __enter__ or __exit__, handling user-defined function nodes."""
        method_node = getattr(method, "ast_node", None)
        closure_env = getattr(method, "closure_env", self.current_env)
        call_env = Environment(self, parent=closure_env)
        old_env = self.current_env
        self.current_env = call_env
        try:
            if method_node and isinstance(method_node, ast.FunctionDef):
                call_env.set(method_node.args.args[0].arg, context_obj)
                # Bind exit() args if applicable
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