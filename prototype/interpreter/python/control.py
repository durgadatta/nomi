import ast

from .base import (
    Environment, ReturnException, GeneratorState, 
    BreakException, ContinueException, YieldException
)

class ControlMixin:
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

    def eval_Raise(self, node: ast.Raise) -> None:
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

    def eval_Try(self, node: ast.Try) -> Any:
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
                    handler_env = Environment(self, parent=self.current_env.parent)
                    
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
