import ast
from typing import Any

from .base import ReturnException, YieldException

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
                'phase': 'try_body',  # 'try_body', 'handler_body', 'else_body'
                'index': 0,
                'current_handler': None,
                'caught_exception': None,
                'pending_return': None  # Store ReturnException for finally handling
            }

        def execute_block(statements):
            index_key = 'index'
            if not statements:
                return True
            i = state[index_key]
            if generator_state and generator_state.injected_exception is not None:
                i = 0
            while i < len(statements):
                stmt = statements[i]
                try:
                    if generator_state is not None:
                        generator_state.raise_injected_exception()
                    self.eval(stmt, generator_state=generator_state)
                    i += 1
                    state[index_key] = i
                except YieldException:
                    i += 1
                    state[index_key] = i
                    raise
                except ReturnException as re:
                    state['pending_return'] = re
                    return False
            return True

        def handle_try_body():
            try:
                completed = execute_block(node.body)
                if completed:
                    state['phase'] = 'else_body' if node.orelse else 'completed'
                    state['index'] = 0
            except Exception as e:
                state['caught_exception'] = e
                state['index'] = 0


        def match_handlers():
            for handler in node.handlers:
                matched = False
                if handler.type is None:
                    matched = True 
                else:
                    handler_type  = self.eval(handler.type)
                    if (isinstance(handler_type, type) and isinstance(state['caught_exception'], handler_type)):
                        matched = True

                if matched:
                    state['phase'] = 'handler_body'
                    state['current_handler'] = handler
                    break

        def handle_handler_body():
            handler = state['current_handler']
            
            if handler.name:
                self.current_env.set(handler.name, state['caught_exception'])

            execute_block(handler.body)
            state['caught_exception'] = None            

        def handle_completed():
            if state['caught_exception'] and not state['current_handler']:
                raise state['caught_exception']
        
        try:
            eval_finally = True
            if state['phase'] == 'try_body':
                handle_try_body()

            if state['caught_exception']:
                match_handlers()

            if state['phase'] == 'handler_body' and state['current_handler']:
                handle_handler_body()

            if state['phase'] == 'else_body' and node.orelse and not state['caught_exception']:
                execute_block(node.orelse)

            if state['phase'] == 'completed':
                handle_completed()

            # Propagate pending return to trigger finally
            if state['pending_return'] is not None:
                raise state['pending_return']
            
        except YieldException as ye:
            #NOTE: this is a signal for generator-state to process yield; it should not trigger "finally"
            eval_finally = False
            generator_state.pause(node, state)
            raise ye

        finally:
            if eval_finally:
            # Finally block (always executes, even on return)
                if node.finalbody:
                    self.eval(node.finalbody, generator_state=generator_state)
                
                e = state.get('caught_exception')
                if e is not None:
                    raise e
                # Re-raise pending return after finally completes
                if state.get('pending_return') is not None:
                    raise state['pending_return']
                