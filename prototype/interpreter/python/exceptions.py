import ast
from typing import Any

from .base import (
    Environment, ReturnException
)

class ExceptionMixin:
    def eval_Raise(self, node: ast.Raise) -> None:
        """Evaluate a raise statement."""
        if node.exc:
            exc = self.eval(node.exc)
            if isinstance(exc, type) and issubclass(exc, Exception):
                # It's an exception class, instantiate it
                if node.cause:
                    cause = self.eval(node.cause)
                    raise exc() from cause
                else:
                    raise exc()
            else:
                # It's already an exception instance
                if node.cause:
                    cause = self.eval(node.cause)
                    raise exc from cause
                else:
                    raise exc
        else:
            # Re-raise the current exception
            raise

    def eval_Try(self, node: ast.Try, generator_state: Any = None) -> Any:
        """
        Evaluate a try statement
        """
        result = None
        exception_occurred = False
        
        try:
            # Execute try block
            try:
                #TODO: this should be made available in any resumable nodes like For, While as well
                if generator_state and generator_state.injected_exception is not None:
                    exc = generator_state.injected_exception
                    generator_state.injected_exception = None
                    raise exc  # This will be caught by the except handlers below

                for stmt in node.body:
                    result = self.eval(stmt)
            except Exception as e:
                exception_occurred = True
                caught_exception = e
                handler_found = False
                
                # Try each exception handler
                for handler in node.handlers:
                    if handler.type is None:
                        handler_found = True
                    else:
                        handler_type = self.eval(handler.type)
                        if (isinstance(handler_type, type) and isinstance(e, handler_type)) or handler_type == type(e):
                            handler_found = True
                    
                    if handler_found:
                        # Use current scope for handler (standard Python behavior)
                        if handler.name:
                            self.current_env.set(handler.name, e)
                        
                        for stmt in handler.body:
                            result = self.eval(stmt)
                        break
                
                if not handler_found:
                    raise caught_exception
            
            # Execute else block if no exception occurred
            if not exception_occurred and node.orelse:
                for stmt in node.orelse:
                    result = self.eval(stmt)
        
        finally:
            # Execute finally block (always runs, can override returns/exceptions)
            if node.finalbody:
                for stmt in node.finalbody:
                    result = self.eval(stmt)
        
        return result