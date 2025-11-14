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
        self.return_value: Optional[Any] = None
   
        # this will received by throw() and executed at the resumable
        # node at the beginning, if present; maybe this needs to be
        # node specific (stack) - review later
        self.injected_exception: Optional[Exception] = None

        #TODO: move this to a separate class later
        # List(Dict(node, state)
        # This is only for compound statements (For/While/Try)
        self.paused_frames = [] 

    def pause(self, node, state):
        self.paused_frames.append({
            'node': node,
            'state': state,
        })
        
    def frame_to_resume(self):
        #TODO: this essentially make this queue, not a stack, change this later
        if self.paused_frames:
            frame = self.paused_frames.pop(0)
            return (frame['node'], frame['state'])
        return None
        
    def current_frame(self):
        if self.paused_frames:
            return self.paused_frames[0]
        return None
        
    @property
    def pending_compound_state(self):
        return len(self.paused_frames) > 0

    def __iter__(self):
        return self

    def __next__(self):        
        try:
            # ALWAYS process compound statement stack first
            if self.pending_compound_state:
                while self.pending_compound_state:
                    node, state = self.frame_to_resume()
                    self.eval(node, state)
                # only advance if there was a pending state and is completed
                self.index += 1 

            self._execute_sequential()
        except YieldException as ye:
            # Compound statement yielded - return the value
            self._handle_yield(ye.value)
            return ye.value
        except ReturnException as re:
            self.return_value = re.value
            raise StopIteration(self.return_value)
        
        raise StopIteration(self.return_value)
    
    def eval(self, node, state):
        with self.interpreter.this_env(self.env):
            self.interpreter.eval(node, state=state, generator_state=self)

    def _execute_sequential(self):
        while self.index < len(self.body):
            stmt = self.body[self.index]
            self.eval(stmt, state=None)
            self.index += 1

    def _handle_yield(self, yield_value=None):
        """Handle a yield exception and update state accordingly.
        
        This is a hook; nomi overrides this method to handle ruby-like
        yielding to block
        """

        # compound statement are handled in stack
        # only advance to next for simple ones (non-resumable)
        if not self.pending_compound_state:
            self.index += 1

    def _handle_other_exception(self, e: Exception):
        """Handle other exceptions by inserting a raise statement."""
        #TODO: this is not currently in effect; 
        # see the interaction between this and throw()
        # contextlib relies on throw() to pass exception generated inside
        # context block; it's also used by yield-to-block
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
        self.injected_exception = exc_value
        
        try:
            self.__next__()
        finally:
            self.injected_exception = None

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

