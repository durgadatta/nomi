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
   
        # this will received by throw() and executed at the resumable
        # node at the beginning, if present; maybe this needs to be
        # node specific (stack) - review later
        self.injected_exception: Optional[Exception] = None

        #TODO: move this to a separate class later
        # List(Dict(node, state)
        # This is only for compound statements (For/While/Try)
        self.execution_stack = [] 

    def push_frame(self, node, state):
        self.execution_stack.append({
            'node': node,
            'state': state,
        })
        
    def pop_frame(self):
        #TODO: this essentially make this queue, not a stack, change this later

        if self.execution_stack:
            return self.execution_stack.pop(0)
        return None
        
    def current_frame(self):
        if self.execution_stack:
            return self.execution_stack[0]
        return None
        
    def is_stack_empty(self):
        return len(self.execution_stack) == 0

    def __iter__(self):
        return self

    def __next__(self):
        if not self.active:
            raise StopIteration(self.return_value)
        
        # ALWAYS process compound statement stack first
        while not self.is_stack_empty():
            #TODO: do we need result?
            # move the YieldException handling here from _execute_compound_frame
            result = self._execute_compound_frame()
            if result is not None:  # Yield occurred
                return result
        
        # No compound statements pending - execute sequential statements
        return self._execute_sequential()
    
    def eval(self, node, state):
        with self.interpreter.this_env(self.env):
            self.interpreter.eval(node, state=state, generator_state=self)
        
    def _execute_compound_frame(self):
        """
        Execute a single compound statement frame from the stack.
        Returns yield value if execution yielded, None otherwise.
        """
        node, state = self.current_frame()
        
        try:
            # Execute the compound statement with its state
            # The compound statement manages its own yielding

            frame = self.pop_frame()
            #TODO: handle this in pop
            node, state = frame['node'], frame['state']
            self.eval(node, state)
            #TODO: think about what happens if exception is raised here
            # the common exception handle as in execute_sequential should be followed
            
        except YieldException as ye:
            # Compound statement yielded - return the value
            self._handle_yield()
            return ye.value
        
        #TODO: avoid duplication with _execute_sequential
        except ReturnException as re:
            self.active = False
            self.return_value = re.value
            raise StopIteration(self.return_value)

    def _execute_sequential(self):
        """
        Execute sequential statements until we hit a compound statement or yield.
        Returns yield value if execution yielded.
        """
        while self.index < len(self.body):
            stmt = self.body[self.index]
            
            try:
                # Execute statement - may push compound frames to stack
                self.eval(stmt, state=None)
                # If we get here, statement completed without yielding
                self.index += 1
            except YieldException as ye:
                # Simple statement yielded
                self._handle_yield()
                return ye.value
                
            except ReturnException as re:
                self.active = False
                self.return_value = re.value
                raise StopIteration(self.return_value)
                
            except Exception as e:
                # Other exceptions
                self._handle_other_exception(e)
                return e
        
        # All statements completed
        self.active = False
        raise StopIteration(self.return_value)

    def _handle_yield(self):
        """Handle a yield exception and update state accordingly.
        
        This is a hook; nomi overrides this method to handle ruby-like
        yielding to block
        """

        # compound statement are handled in stack
        # only advance to next for simple ones (non-resumable)
        if self.is_stack_empty:
            self.index += 1


    def _handle_return(self, re: ReturnException):
        """Handle a return exception by marking generator as complete."""
        self.active = False
        self.return_value = re.value

    def _handle_other_exception(self, e: Exception):
        """Handle other exceptions by inserting a raise statement."""
        raise_node = ast.Raise(exc=e, cause=None)
        self.body.insert(self.index, raise_node)

    def raise_injected_exception(self):
        '''
        exception raised within the passed block or with-block
        should be at the resumption point
        '''
        if self.injected_exception is not None:
            exc = self.injected_exception
            self.injected_exception = None
            raise exc

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
        #TODO: handle lines from compound state stack 
        if self.index < len(self.body):
            return getattr(self.body[self.index], 'lineno', 1)
        
        return 

