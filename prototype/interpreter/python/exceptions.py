import ast
from typing import Any, Optional, Dict

from .base import (
    Environment, ReturnException, YieldException
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

    def eval_Try(self, node: ast.Try, generator_state: 'GeneratorState' = None) -> Any:
        # Check if we're resuming a paused try block
        if generator_state and generator_state.compound_state is not None:
            state = generator_state.compound_state
            if state['type'] == 'try' and state['node'] == node:
                return self._resume_try_execution(node, state, generator_state)
        
        # Check if we have an injected exception from throw()
        if generator_state and hasattr(generator_state, 'injected_exception') and generator_state.injected_exception:
            # Handle the injected exception immediately
            exception_occurred = True
            caught_exception = generator_state.injected_exception
            generator_state.injected_exception = None
            
            # Execute exception handlers
            handler_found = False
            for handler in node.handlers:
                if self._handler_matches_exception(handler, caught_exception):
                    handler_found = True
                    return_exception = self._execute_exception_handler(handler, caught_exception, None)
                    break
            
            if not handler_found:
                raise caught_exception
            
            # Execute finally block
            if node.finalbody:
                for stmt in node.finalbody:
                    try:
                        self.eval(stmt)
                    except ReturnException:
                        pass
            
            return None
        
        # Fresh execution (no injected exception)
        return self._execute_try_fresh(node, generator_state)

    def _execute_try_fresh(self, node: ast.Try, generator_state: Any = None) -> Any:
        """
        Execute a try block from the beginning with yield support.
        """
        result = None
        exception_occurred = False
        return_exception = None
        caught_exception = None
        
        # Execute the try block with yield support
        try:
            for i, stmt in enumerate(node.body):
                try:
                    result = self.eval(stmt)
                except YieldException as ye:
                    # Save state for resumption if we're in a generator context
                    if generator_state:
                        generator_state.compound_state = {
                            'type': 'try',
                            'node': node,
                            'phase': 'body',
                            'index': i + 1,  # Move to next statement
                            'exception_occurred': False,
                            'return_exception': None,
                            'caught_exception': None
                        }
                    raise ye
                except ReturnException as re:
                    return_exception = re
                    break
        except Exception as e:
            exception_occurred = True
            caught_exception = e
        
        # If we yielded during body execution, return now
        if generator_state and generator_state.compound_state is not None:
            return result
        
        # Otherwise, complete the execution
        return self._complete_try_execution(
            node, exception_occurred, caught_exception, return_exception, result
        )

    def _resume_try_execution(self, node: ast.Try, state: Dict, generator_state: Any) -> Any:
        """
        Resume try execution from saved state.
        """       
        # Check if we have an injected exception from throw()
        if hasattr(generator_state, 'injected_exception') and generator_state.injected_exception:
            # Handle the injected exception immediately
            exception_occurred = True
            caught_exception = generator_state.injected_exception
            generator_state.injected_exception = None
            
            # Clear compound state since we're handling the exception
            generator_state.compound_state = None
            
            # Execute exception handlers
            handler_found = False
            for handler in node.handlers:
                if self._handler_matches_exception(handler, caught_exception):
                    handler_found = True
                    return_exception = self._execute_exception_handler(handler, caught_exception, None)
                    break
            
            if not handler_found:
                raise caught_exception
            
            # Execute finally block
            if node.finalbody:
                for stmt in node.finalbody:
                    try:
                        self.eval(stmt)
                    except ReturnException:
                        pass
            
            return None
        
        # Normal resumption without injected exception
        result = None
        exception_occurred = state['exception_occurred']
        return_exception = state['return_exception']
        caught_exception = state['caught_exception']
        
        try:
            # Resume from where we left off in try body
            if state['phase'] == 'body' and not exception_occurred:
                i = state['index']
                while i < len(node.body):
                    stmt = node.body[i]
                    try:
                        result = self.eval(stmt)
                        i += 1
                    except YieldException as ye:
                        # Still yielding from body
                        state['index'] = i
                        generator_state.compound_state = state
                        raise ye
                    except ReturnException as re:
                        return_exception = re
                        break
                    except Exception as e:
                        exception_occurred = True
                        caught_exception = e
                        break
                
                # If we completed the body without yielding
                if i >= len(node.body):
                    result = self._complete_try_execution(
                        node, exception_occurred, caught_exception, return_exception, result
                    )
                    generator_state.compound_state = None
                    return result
                else:
                    # We broke out due to return or exception, but didn't yield
                    state['index'] = i
                    generator_state.compound_state = state
                    return result
                    
        except YieldException:
            # Re-raise YieldException - state is already updated
            raise
        
        return result

    def _complete_try_execution(self, node: ast.Try, exception_occurred: bool,
                              caught_exception: Optional[Exception],
                              return_exception: Optional[ReturnException],
                              result: Any) -> Any:
        """
        Complete try execution after body is done (exception handling, else, finally).
        """
        # Handle exceptions if any occurred
        if exception_occurred:
            handler_found = False
            for handler in node.handlers:
                if self._handler_matches_exception(handler, caught_exception):
                    handler_found = True
                    return_exception = self._execute_exception_handler(handler, caught_exception, return_exception)
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

    def _handler_matches_exception(self, handler: ast.ExceptHandler, 
                                 exception: Exception) -> bool:
        """Check if a handler matches the given exception."""
        if handler.type is None:
            # Bare except: always matches
            return True
        
        # Check if this handler matches the exception type
        handler_type = self.eval(handler.type)
        # Handle both class and instance comparisons
        return ((isinstance(handler_type, type) and isinstance(exception, handler_type)) 
                or handler_type == type(exception))

    def _execute_exception_handler(self, handler: ast.ExceptHandler, exception: Exception,
                                 return_exception: ReturnException) -> ReturnException:
        """
        Execute an exception handler with proper scope management.
        """
        # Create environment for the handler with the SAME parent as current
        handler_env = Environment(self, parent=self.current_env.parent)
        
        # Copy current bindings to maintain scope continuity
        for key, value in self.current_env.bindings.items():
            handler_env.set(key, value)
        
        # Bind the exception if there's a name
        if handler.name:
            handler_env.set(handler.name, exception)
        
        # Execute handler body in the new environment
        old_env = self.current_env
        self.current_env = handler_env
        try:
            for stmt in handler.body:
                self.eval(stmt)
            # Copy back any assignments made in the handler
            for key, value in handler_env.bindings.items():
                if key not in ['__exception__']:  # Skip internal vars
                    old_env.set(key, value)
        except ReturnException as re:
            return_exception = re
        finally:
            self.current_env = old_env
        
        return return_exception