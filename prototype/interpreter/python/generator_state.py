import ast
from typing import List, Optional, Any

from .signals import YieldException, ReturnException

class CoroutineState:
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

    __slots__ = (
        'interpreter', 'body', 'env', 'index', 'return_value',
        'injected_exception', 'paused_frames', '_processing_frame',
        'sent_value', 'is_first_iteration',
    )

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

        # TODO: move paused frame bookkeeping into a dedicated resumable-frame type.
        # This is only for compound statements (For/While/Try).
        self.paused_frames = []
        self._processing_frame = None  # Frame currently being evaluated 

        # for implementing send()
        self.sent_value = None
        self.is_first_iteration = True

    def _frame(self, node, state):
        return {
            'node': node,
            'state': state,
        }

    def _is_processing_node(self, node) -> bool:
        return self._processing_frame and self._processing_frame['node'] == node

    def _queue_paused_frame(self, node, state) -> None:
        self.paused_frames.append(self._frame(node, state))

    def _queue_current_frame(self, node, state) -> None:
        self.paused_frames.insert(0, self._frame(node, state))

    def pause(self, node, state):
        # Check if this yield comes from the frame we're currently processing
        if self._is_processing_node(node):
            # Current frame yielded again - put at front for immediate continuation
            self._queue_current_frame(node, state)
        else:
            # New frame yielding - add to end (normal nesting)
            self._queue_paused_frame(node, state)
        self._processing_frame = None  # Reset processing state

    def resume(self):
        # ALWAYS process compound statement stack first
        if self.pending_compound_state:
            while self.pending_compound_state:
                node, state = self.frame_to_resume()
                self.eval(node, state)
            # only advance if there was a pending state and is completed
            self.index += 1 

        while self.index < len(self.body):
            stmt = self.body[self.index]
            self.eval(stmt, state=None)
            self.index += 1

    def frame_to_resume(self):
        # TODO(NOMI-ARCH-014): Replace raw paused-frame dictionaries with a
        # named resumable-frame/policy model before adding richer block policies.
        # TODO: make the pause/resume policy explicit instead of relying on list order here.
        if self.paused_frames:
            frame = self.paused_frames.pop(0)
            self._processing_frame = frame  # Track what we're processing
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
            self.is_first_iteration = False
            self.resume()
        except YieldException as ye:
            return ye.value
        
        raise StopIteration(self.return_value)
    
    def send(self, value):
        if self.is_first_iteration and value is not None:
            raise TypeError("can't send non-None value to a just-started generator")
        
        self.sent_value = value
        self.is_first_iteration = False
        result =  self.__next__()
        return result
    
    def get_sent_value(self):
        ''' get sent value alongside critical reset'''
        value = self.sent_value
        self.sent_value = None 
        return value 
    
    def eval(self, node, state):
        with self.interpreter.this_env(self.env):
            try:
                self.interpreter.eval(node, state=state, generator_state=self)
            except ReturnException as re:
                self.return_value = re.value
                raise StopIteration(self.return_value)
            except YieldException as ye:
                # Compound statement yielded - return the value
                self._handle_yield(ye.value)
                raise ye # so that next() can return

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
        """Handle other exceptions by inserting a raise statement.

        Currently unused — the throw() path and contextlib integration
        handle exception propagation through a different mechanism.
        Kept as a hook point for future resumable-frame error handling.
        """
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
        # TODO: derive line info from the active paused frame stack, not just the current index.
        if self.index < len(self.body):
            return getattr(self.body[self.index], 'lineno', 1)
        
        return 
