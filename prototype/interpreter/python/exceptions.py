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
        Evaluate a try statement.
        
        Args:
            generator_state: Ignored in non-resumable version, kept for interface compatibility
        """
        result = None
        exception_occurred = False
        return_exception = None
        caught_exception = None
        
        # Execute the try block
        try:
            for stmt in node.body:
                result = self.eval(stmt)
        except ReturnException as re:
            # Store the return exception but don't raise it yet
            return_exception = re
        except Exception as e:
            exception_occurred = True
            caught_exception = e
            handler_found = False
            
            # Try each exception handler
            for handler in node.handlers:
                if handler.type is None:
                    # Bare except: always matches
                    handler_found = True
                else:
                    # Check if this handler matches the exception type
                    handler_type = self.eval(handler.type)
                    # Handle both class and instance comparisons
                    if (isinstance(handler_type, type) and isinstance(e, handler_type)) or handler_type == type(e):
                        handler_found = True
                
                if handler_found:
                    # Create environment for the handler with the SAME parent as current
                    # This ensures assignments in the handler are visible in the outer scope
                    handler_env = self.env_class(self, parent=self.current_env.parent)
                    
                    # Copy current bindings to maintain scope
                    for key, value in self.current_env.bindings.items():
                        handler_env.set(key, value)
                    
                    # Bind the exception if there's a name
                    if handler.name:
                        handler_env.set(handler.name, e)
                    
                    # Execute handler body in the new environment
                    old_env = self.current_env
                    self.current_env = handler_env
                    try:
                        for stmt in handler.body:
                            result = self.eval(stmt)
                        # Copy back any assignments made in the handler
                        for key, value in handler_env.bindings.items():
                            if key not in ['__exception__']:  # Skip internal vars
                                old_env.set(key, value)
                    except ReturnException as re:
                        return_exception = re
                    finally:
                        self.current_env = old_env
                    break
            
            # If no handler caught the exception, re-raise it
            if not handler_found:
                raise caught_exception
        
        # Execute else block if no exception occurred and no return
        if not exception_occurred and not return_exception and node.orelse:
            for stmt in node.orelse:
                result = self.eval(stmt)
        
        # Execute finally block (ALWAYS, even if there's a return)
        if node.finalbody:
            for stmt in node.finalbody:
                try:
                    self.eval(stmt)
                except ReturnException:
                    # Ignore returns in finally blocks for now
                    pass
        
        # If there was a return in try or except, raise it AFTER finally
        if return_exception:
            raise return_exception
        
        return result