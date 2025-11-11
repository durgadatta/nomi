import ast
from typing import Any

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

    def eval_Try(self, node: ast.Try, state: dict = None, generator_state: Any = None) -> Any:
        """
        Evaluate a try statement with resumable execution
        """
        # Initialize state if new execution
        if state is None:
            state = {
                'phase': 'try_body',  # 'try_body', 'handlers', 'handler_body', 'else_body'
                'index': 0,
                'current_handler': None,
                'handler_body_index': 0, # index will refer to which handler
                'exception_occurred': False,
                'caught_exception': None,
                'handler_found': False,
                'pending_return': None  # Store ReturnException for finally handling
            }

        result = None
        
        try:
            try:
                if state['phase'] == 'try_body':
                    # Execute try body statements directly
                    i = state['index']
                    # HACK TODO: Keep the hack for now
                    if generator_state and generator_state.injected_exception is not None:
                        i = 0
                    while i < len(node.body):
                        stmt = node.body[i]
                        try:
                            if generator_state is not None:
                                generator_state.raise_injected_exception()
                            self.eval(stmt, generator_state=generator_state)
                            i += 1
                            state['index'] = i
                        except YieldException:
                            i += 1
                            state['index'] = i
                            raise  # Re-raise to pause execution
                        except ReturnException as re:
                            state['pending_return'] = re
                            break  # Interrupted by return
                        except Exception as e:
                            # Handle exception in try body
                            state['exception_occurred'] = True
                            state['caught_exception'] = e
                            state['phase'] = 'handlers'
                            state['index'] = 0
                            break
                    
                    # Move to next phase if try body completed
                    if state['pending_return'] is None and not state['exception_occurred'] and i >= len(node.body):
                        state['phase'] = 'else_body' if node.orelse else 'completed'
                        state['index'] = 0

                if state['phase'] == 'handlers' and state['exception_occurred']:
                    i = state['index']
                    while i < len(node.handlers):
                        handler = node.handlers[i]
                        
                        # Check if handler matches exception
                        if handler.type is None:
                            state['handler_found'] = True
                            state['current_handler'] = handler
                            state['phase'] = 'handler_body'
                            state['handler_body_index'] = 0
                            break
                        else:
                            handler_type = self.eval(handler.type)
                            if (isinstance(handler_type, type) and isinstance(state['caught_exception'], handler_type)) or handler_type == type(state['caught_exception']):
                                state['handler_found'] = True
                                state['current_handler'] = handler
                                state['phase'] = 'handler_body'
                                state['handler_body_index'] = 0
                                break
                        
                        i += 1
                        state['index'] = i
                    
                    if not state['handler_found'] and state['index'] >= len(node.handlers):
                        state['phase'] = 'completed'

                if state['phase'] == 'handler_body' and state['current_handler']:
                    handler = state['current_handler']
                    
                    if handler.name:
                        self.current_env.set(handler.name, state['caught_exception'])
                    
                    # Execute handler body directly
                    i = state['handler_body_index']
                    # HACK TODO: Keep the hack for now
                    if generator_state and generator_state.injected_exception is not None:
                        i = 0
                    while i < len(handler.body):
                        stmt = handler.body[i]
                        try:
                            if generator_state is not None:
                                generator_state.raise_injected_exception()
                            self.eval(stmt, generator_state=generator_state)
                            i += 1
                            state['handler_body_index'] = i
                        except YieldException:
                            i += 1
                            state['handler_body_index'] = i
                            raise  # Re-raise to pause execution
                        except ReturnException as re:
                            state['pending_return'] = re
                            break  # Interrupted by return
                        except Exception as e:
                            # Exception in handler body - let it propagate to outer try
                            raise e
                    
                    # Handler completed
                    if state['pending_return'] is None and i >= len(handler.body):
                        state['phase'] = 'completed'
                        state['current_handler'] = None
                        state['handler_body_index'] = 0

                if state['phase'] == 'else_body' and node.orelse and not state['exception_occurred']:
                    # Execute else block directly
                    i = state['index']
                    # HACK TODO: Keep the hack for now
                    if generator_state and generator_state.injected_exception is not None:
                        i = 0
                    while i < len(node.orelse):
                        stmt = node.orelse[i]
                        try:
                            if generator_state is not None:
                                generator_state.raise_injected_exception()
                            self.eval(stmt, generator_state=generator_state)
                            i += 1
                            state['index'] = i
                        except YieldException:
                            i += 1
                            state['index'] = i
                            raise  # Re-raise to pause execution
                        except ReturnException as re:
                            state['pending_return'] = re
                            break  # Interrupted by return
                        except Exception as e:
                            # Exception in else body - let it propagate to outer try
                            raise e
                    
                    if state['pending_return'] is None and i >= len(node.orelse):
                        state['phase'] = 'completed'

                # Final phase completion check
                if state['phase'] == 'completed':
                    if state['exception_occurred'] and not state['handler_found']:
                        raise state['caught_exception']
                
            except YieldException as ye:
                if generator_state:
                    generator_state.pause(node, state)
                raise ye

            # Propagate pending return to trigger finally
            if state['pending_return'] is not None:
                raise state['pending_return']

        finally:
            # Finally block (always executes, even on return)
            if node.finalbody:
                self.eval(node.finalbody, generator_state=generator_state)
            
            # Re-raise pending return after finally completes
            if state.get('pending_return') is not None:
                raise state['pending_return']

        return result