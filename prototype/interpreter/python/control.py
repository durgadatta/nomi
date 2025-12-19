import ast

from .base import (
    BreakException, ContinueException, YieldException
)

from .exceptions import ExceptionMixin

class ControlMixin(ExceptionMixin):

    def eval_If(self, node: ast.If, *, state=None, generator_state: 'CoroutineState' = None) -> None:
        '''
        Note that elif's are already parses as nested if/orelse
        '''
        if state is None:
            # First time: evaluate condition, choose branch, save it
            test_val = self.eval(node.test)
            if test_val:
                chosen_body = node.body
            else:
                chosen_body = node.orelse

            state = {
                'chosen_body': chosen_body,
                'body_index': 0,
            }

        if generator_state:
            generator_state.raise_injected_exception()

        # Execute the chosen body, resumably
        body = state['chosen_body']
        i = state['body_index']

        while i < len(body):
            stmt = body[i]
            try:
                self.eval(stmt, generator_state=generator_state)
                i += 1
            except YieldException:
                state['body_index'] = i + 1
                generator_state.pause(node, state)
                raise

    def eval_AsyncFor(self, node: ast.AsyncFor) -> None:
        iterable = self.eval(node.iter)
        if hasattr(iterable, '__aiter__'):
            iterable = iterable.__aiter__().__anext__
            while True:
                try:
                    item = iterable().__next__()
                    self.assign_target(node.target, item)
                    try:
                        self.eval(node.body )
                    except BreakException:
                        break
                    except ContinueException:
                        continue
                except StopAsyncIteration:
                    break
        else:
            self.eval_For(node)
        self.eval(node.orelse)

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

    def eval_For(self, node: ast.For, *, state=None, generator_state: 'CoroutineState' = None) -> None:
        """Evaluate a For loop node - unified approach."""
        
        #TODO: when gen-state is None, fallback to regular without out even creating
        # a state; now a state is created regardless
        if state is None:
            # New execution - create iterator
            iter_obj = self.eval(node.iter)
            try:
                iterator = iter(iter_obj)
            except TypeError as e:
                lineno = getattr(node, 'lineno', 1) 
                raise TypeError(f"'{type(iter_obj).__name__}' object is not iterable at line {lineno}") from e

            # Initialize state
            state = {
                'node': node, # generator needs to know this to resume 
                'iterator': iterator,
                'broke': False,
                'body_index': 0
            }
        try:
            if generator_state:
                generator_state.raise_injected_exception()
            self._execute_for_loop(node, state, generator_state=generator_state)      
        except YieldException:
            # Save state and re-raise for generator handling
            generator_state.pause(node, state)
            raise

    def _execute_for_loop(self, node: ast.For, state: dict, generator_state):
        """
        Unified for loop executor that handles both yielding and non-yielding cases.
        """

        iterator = state['iterator']
        start_index = state.get('body_index', 0)
        
        while True:
            # Get next item if starting new iteration
            if start_index == 0:
                try:
                    item = next(iterator)
                    self.assign_target(node.target, item)
                except StopIteration:
                    state['broke'] = False
                    break

            # Execute body statements
            i = start_index
            while i < len(node.body):
                stmt = node.body[i]
                try:
                    self.eval(stmt, generator_state=generator_state)
                    i += 1
                except YieldException:
                    # Save where to resume and re-raise
                    state['body_index'] = i + 1
                    raise
                except BreakException:
                    state['broke'] = True
                    return
                except ContinueException:
                    break  # Break to next iteration
            
            # Check if we completed the body or broke mid-way
            if i >= len(node.body):
                start_index = 0  # Ready for next iteration
                state['body_index'] = 0
            else:
                # ContinueException broke us out mid-body
                start_index = 0
                state['body_index'] = 0
                continue

        # Loop completed normally - handle orelse if not broken
        if not state['broke']:
            self.eval(node.orelse)

    def eval_While(self, node: ast.While, *, state=None, generator_state: 'CoroutineState' = None) -> None:
        """Evaluate a While loop node - unified approach."""
        
        # Initialize state
        if state is None:
            # New execution
            state = {
                'node' : node,
                'broke': False,
                'body_index': 0
            }
        try:
            if generator_state:
                generator_state.raise_injected_exception()
            self._execute_while_loop(node, state)      
        except YieldException:
            # Save state and re-raise for generator handling
            generator_state.pause(node, state)
            raise


    def _execute_while_loop(self, node: ast.While, state:dict):
        """Unified while loop executor."""
        start_index = state.get('body_index', 0)
        while True:
            # Check condition at start of each iteration
            if start_index == 0:
                if not self.eval(node.test):
                    state['broke'] = False
                    break

            # Execute body statements
            i = start_index
            while i < len(node.body):
                stmt = node.body[i]
                try:
                    self.eval(stmt)
                    i += 1
                except YieldException:
                    # Save where to resume
                    state['body_index'] = i + 1
                    raise
                except BreakException:
                    state['broke'] = True
                    return
                except ContinueException:
                    break  # Continue to next iteration
            
            # Reset for next iteration unless we broke out
            if not state['broke']:
                start_index = 0
                state['body_index'] = 0
            else:
                break

        # Handle orelse if loop completed normally
        if not state['broke']:
            self.eval(node.orelse)
