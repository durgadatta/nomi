import ast

from prototype.interpreter.python.base import (
    Environment, ControlException, GeneratorState, 
    BreakException, ContinueException
)

class ControlMixin:
    def eval_While(self, node: ast.While) -> None:
        while self.eval(node.test):
            try:
                for stmt in node.body:
                    self.eval(stmt)
            except BreakException:
                break
            except ContinueException:
                continue
        else:
            for stmt in node.orelse:
                self.eval(stmt)

    def eval_If(self, node: ast. ast.If) -> None:
        if self.eval(node.test):
            for stmt in node.body:
                self.eval(stmt)
        else:
            for stmt in node.orelse:
                self.eval(stmt)

    def eval_For(self, node: ast.For) -> None:
        """
        for TARGET in ITER:
            BODY
        else:
            ORELSE
        """
        iter_obj = self.eval(node.iter)
        
        # Handle generator objects specially
        if isinstance(iter_obj, GeneratorState):
            iterator = iter_obj
        else:
            try:
                iterator = iter(iter_obj)
            except TypeError as e:
                raise TypeError(f"'{type(iter_obj).__name__}' object is not iterable at line {self.get_lineno(node)}") from e

        # Support either assign_target or _assign_target (compatibility)
        assign_fn = getattr(self, "assign_target", None) or getattr(self, "_assign_target", None)
        if assign_fn is None:
            raise RuntimeError("No assignment helper found (expected 'assign_target' or '_assign_target')")

        broke = False
        try:
            while True:
                try:
                    item = next(iterator)
                except StopIteration:
                    break

                # Bind the loop target (handles tuple unpacking etc.)
                assign_fn(node.target, item)

                try:
                    for stmt in node.body:
                        self.eval(stmt)
                except BreakException:
                    broke = True
                    break
                except ContinueException:
                    # continue to next iteration
                    continue

        except Exception:
            # Any exception (other than Break/Continue which are handled above)
            # prevents 'orelse' from running — re-raise.
            raise
        else:
            # Loop completed normally (no break and no exception): run orelse
            if not broke:
                for stmt in node.orelse:
                    self.eval(stmt)

        def eval_AsyncFor(self, node: ast.AsyncFor) -> None:
            iterable = self.eval(node.iter)
            if hasattr(iterable, '__aiter__'):
                iterable = iterable.__aiter__().__anext__
                while True:
                    try:
                        item = iterable().__next__()
                        self.assign_target(node.target, item)
                        try:
                            for stmt in node.body:
                                self.eval(stmt)
                        except BreakException:
                            break
                        except ContinueException:
                            continue
                    except StopAsyncIteration:
                        break
            else:
                self.eval_For(node)
            for stmt in node.orelse:
                self.eval(stmt)

    def eval_Raise(self, node: ast.Raise) -> None:
        exc = self.eval(node.exc) if node.exc else None
        cause = self.eval(node.cause) if node.cause else None
        if exc is None:
            raise SyntaxError(f"raise requires an exception at line {self.get_lineno(node)}")
        if cause:
            raise exc from cause
        raise exc

    def eval_Try(self, node: ast.Try) -> None:
        exc = None
        try:
            for stmt in node.body:
                self.eval(stmt)
        except Exception as e:
            exc = e
            handled = False
            for handler in node.handlers:
                handler_type = self.eval(handler.type) if handler.type else None
                if handler_type is None or isinstance(e, handler_type):
                    if handler.name:
                        self.current_env.set(handler.name, e)
                    for stmt in handler.body:
                        self.eval(stmt)
                    handled = True
                    break
            if not handled:
                raise
        if not exc:
            for stmt in node.orelse:
                self.eval(stmt)
        for stmt in node.finalbody:
            self.eval(stmt)

    def eval_Pass(self, node: ast.Pass) -> None:
        pass

    def eval_Break(self, node: ast.Break) -> None:
        raise BreakException

    def eval_Continue(self, node: ast.Continue) -> None:
        raise ContinueException
    
    def eval_Assert(self, node: ast.Assert) -> None:
        if not self.eval(node.test):
            msg = self.eval(node.msg) if node.msg else None
            raise AssertionError(msg)


