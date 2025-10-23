import ast

from .base import (
    GeneratorState, 
    BreakException, ContinueException, YieldException
)

from .exceptions import ExceptionMixin

class ControlMixin(ExceptionMixin):
    def eval_If(self, node: ast. ast.If) -> None:
        if self.eval(node.test):
            for stmt in node.body:
                self.eval(stmt)
        else:
            for stmt in node.orelse:
                self.eval(stmt)

    def eval_AsyncFor(self, node: ast.AsyncFor) -> None:
        iterable = self.eval(node.iter)
        if hasattr(iterable, '__aiter__'):
            iterable = iterable.__aiter__().__anext__
            while True:
                try:
                    item = iterable().__next__()
                    self.assign_target(node.target, item)
                    try:
                        for stmt in node.body:
                            self.eval(stmt)
                    except BreakException:
                        break
                    except ContinueException:
                        continue
                except StopAsyncIteration:
                    break
        else:
            self.eval_For(node)
        for stmt in node.orelse:
            self.eval(stmt)

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

    def _setup_loop_state(self, generator_state, node_type, node, **extra_state):
        """Common setup for loop compound state."""
        base_state = {
            'type': node_type,
            'node': node, 
            'body_index': 0,
            'broke': False
        }
        base_state.update(extra_state)
        generator_state.compound_state = base_state

    def _should_resume_loop(self, generator_state, expected_type):
        """Check if we should resume a loop."""
        return (generator_state.compound_state and 
                generator_state.compound_state.get('type') == expected_type)

    def _handle_loop_completion(self, node, generator_state):
        """Handle loop completion (else clause and state cleanup)."""
        state = generator_state.compound_state
        if not state.get('broke', False) and hasattr(node, 'orelse') and node.orelse:
            for stmt in node.orelse:
                self.eval(stmt)
        generator_state.compound_state = None

    def eval_For(self, node: ast.For, generator_state: 'GeneratorState' = None) -> None:
        """Evaluate a For loop node - unified approach."""
        
        # Check if we're resuming first
        if generator_state is not None and generator_state.compound_state is not None:
            # Resuming - use existing state
            state = generator_state.compound_state
            # Iterator is already in state, no need to create
        else:
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
            self._execute_for_loop(node, state)      
        except YieldException:
            # Save state and re-raise for generator handling
            if generator_state:
                generator_state.compound_state = state
            raise

    def _execute_for_loop(self, node: ast.For, state: dict):
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
                    self.eval(stmt)
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
            for stmt in node.orelse:
                self.eval(stmt)

    def eval_While(self, node: ast.While, generator_state: 'GeneratorState' = None) -> None:
        """Evaluate a While loop node - unified approach."""
        
        # Initialize state
        if generator_state is not None and generator_state.compound_state is not None:
            # Resuming - use existing state
            state = generator_state.compound_state
        else:
            # New execution
            if generator_state:
                state = {
                    'node' : node,
                    'broke': False,
                    'body_index': 0
                }
        try:
            self._execute_while_loop(node, state)      
        except YieldException:
            # Save state and re-raise for generator handling
            if generator_state:
                generator_state.compound_state = state
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
            for stmt in node.orelse:
                self.eval(stmt)
