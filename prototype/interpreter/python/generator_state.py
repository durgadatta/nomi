import ast
from typing import List, Optional, Any

from .base import YieldException, ReturnException

class GeneratorState:
    """
    Manages state for generator functions.
    
    Handles resumable execution of compound statements (For, While, Try)
    and supports exception injection via throw() for context managers.

    NOTE:
    This is the most fragile piece

    Tricky part in handling exception withing with-blocks.
    Also check the python's implementation of contextmanager.contextlib -
    there are several subtle comments and potential issues.
    specially review the "throw" method.
    https://stackoverflow.com/questions/11485591/what-is-generator-throw-good-for

    """
    
    def __init__(self, interpreter: 'Interpreter', body: List[ast.stmt], env: 'Environment'):
        self.interpreter = interpreter
        self.body = body
        self.env = env
        self.index = 0
        self.active = True
        self.return_value: Optional[Any] = None
        self.compound_state: Optional[dict] = None
        self.injected_exception: Optional[Exception] = None

    def __iter__(self):
        return self

    def __next__(self):
        if not self.active:
            raise StopIteration(self.return_value)
        
        with self.interpreter.this_env(self.env):
            return self._execute_statements()


    def _execute_statements(self):
        """Execute generator statements until yield, return, or completion."""
        while self.index < len(self.body):
            stmt = self.body[self.index]
            
            try:
                self._execute_statement(stmt)
                # Statement completed without yielding - move to next
                self.index += 1
                
            except YieldException as ye:
                self._handle_yield()
                return ye.value

            except ReturnException as re:
                self._handle_return(re)
                raise StopIteration(self.return_value)
                
            except Exception as e:
                self._handle_other_exception(e)
                return  # Return to allow exception propagation
        
        # All statements completed
        self.active = False
        raise StopIteration(self.return_value)

    def _execute_statement(self, stmt: ast.stmt):
        """Execute a single statement with compound statement support."""
        if isinstance(stmt, ast.For):
            self.interpreter.eval_For(stmt, self)
        elif isinstance(stmt, ast.While): 
            self.interpreter.eval_While(stmt, self)
        elif isinstance(stmt, ast.Try): 
            self.interpreter.eval_Try(stmt, self)
        else:
            self.interpreter.eval(stmt)

    def _handle_yield(self):
        """Handle a yield exception and update state accordingly."""
        
        # Only increment index for simple yields (non-compound statements)
        if not self.compound_state:
            self.index += 1
        # For compound statements, index is managed by the compound statement itself

    def _handle_return(self, re: ReturnException):
        """Handle a return exception by marking generator as complete."""
        self.active = False
        self.return_value = re.value

    def _handle_other_exception(self, e: Exception):
        """Handle other exceptions by inserting a raise statement."""
        raise_node = ast.Raise(exc=e, cause=None)
        self.body.insert(self.index, raise_node)

    def throw(self, exc_value: Exception):
        """Inject exception into generator for context manager exception handling."""
        if not self.active:
            raise exc_value
        
        self.injected_exception = exc_value
        
        try:
            self.__next__()
            # If we reach here, generator didn't handle the exception properly
            raise RuntimeError("generator didn't stop after throw()")
        except StopIteration:
            # Re-raise so contextlib can catch it
            raise
        except Exception as e:
            # Return False if generator re-raised the same exception
            return e is not exc_value

    def close(self):
        """Implement generator.close() to allow proper cleanup."""
        # Could be extended to handle generator cleanup
        pass

    def get_lineno(self) -> int:
        """Get current line number for error reporting."""
        # Try compound state first
        if self.compound_state:
            return self._get_compound_state_lineno()
        
        # Fall back to current statement
        if self.index < len(self.body):
            return getattr(self.body[self.index], 'lineno', 1)
        
        return 1

    def _get_compound_state_lineno(self) -> int:
        """Get line number from compound state."""
        node = self.compound_state['node']
        state_type = self.compound_state['type']
        
        if state_type in ['For', 'While']:
            idx = self.compound_state['body_index']
            if idx < len(node.body):
                return getattr(node.body[idx], 'lineno', 1)
                
        elif state_type == 'Try' and self.compound_state['phase'] == 'body':
            idx = self.compound_state['index']
            if idx < len(node.body):
                return getattr(node.body[idx], 'lineno', 1)
        
        return getattr(node, 'lineno', 1)