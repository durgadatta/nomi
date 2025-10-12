import ast

from prototype.interpreter.python.base import (
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

    # For Loop Implementation (minimal changes)
    def eval_For(self, node: ast.For, generator_state: 'GeneratorState'=None) -> None:
        """Evaluate a For loop node."""
        
        # Non-generator case (blocking execution)
        if generator_state is None:
            iter_obj = self.eval(node.iter)
            try:
                iterator = iter(iter_obj)
            except TypeError as e:
                lineno = getattr(node, 'lineno', 1) 
                raise TypeError(f"'{type(iter_obj).__name__}' object is not iterable at line {lineno}") from e
                
            assign_fn = getattr(self, "assign_target", None)
            if assign_fn is None:
                raise RuntimeError("No assignment helper found for blocking For loop.")
            
            broke = False
            for item in iterator:
                assign_fn(node.target, item)
                try:
                    for stmt in node.body:
                        self.eval(stmt)
                except BreakException:
                    broke = True
                    break
                except ContinueException:
                    continue
            
            if not broke:
                for stmt in node.orelse:
                    self.eval(stmt)
            return

        # Generator case
        if self._should_resume_loop(generator_state, 'For'):
            # Resuming existing for loop
            self._execute_for_loop(node, generator_state, generator_state.compound_state['body_index'])
        else:
            # Starting new for loop
            iter_obj = self.eval(node.iter)
            iterator = iter(iter_obj)
            self._setup_loop_state(generator_state, 'For', node, iterator=iterator)
            self._execute_for_loop(node, generator_state, 0)

    def _execute_for_loop(self, node: ast.For, generator_state: 'GeneratorState', start_index: int):
        """
        Internal, resume-aware for loop executor.
        """
        state = generator_state.compound_state
        iterator = state['iterator']
        
        assign_fn = getattr(self, "assign_target", None)
        if assign_fn is None:
            raise RuntimeError("No assignment helper found")

        broke = state.get('broke', False)

        try:
            while True:
                # Only get next item if we're starting a completely new iteration
                if start_index == 0:
                    try:
                        item = next(iterator)
                        assign_fn(node.target, item)
                    except StopIteration:
                        break

                # Execute the body from current start_index
                i = start_index
                
                while i < len(node.body):
                    stmt = node.body[i]
                    try:
                        self.eval(stmt)
                        i += 1
                    except YieldException as ye:
                        # Save the NEXT index to execute
                        i += 1 # yield statement is now processed
                        state.update({
                            'body_index': i, 
                            'broke': broke
                        })
                        raise ye
                    except BreakException:
                        broke = True
                        break
                    except ContinueException:
                        break  # Break out of inner while, continue to next iteration
                
                if i >= len(node.body):
                    start_index = 0  # Move to next iteration
                else:
                    # We broke out mid-body (due to break/continue), preserve the break
                    break
                
                # Check if we broke out due to break
                if broke:
                    break

        except YieldException:
            raise
        except Exception:
            generator_state.compound_state = None
            raise
        
        # Loop completed
        self._handle_loop_completion(node, generator_state)

    def resume_For(self, node: ast.For, generator_state: 'GeneratorState'):
        """Resume execution of a paused For loop."""
        state = generator_state.compound_state
        if not state:
            return
            
        start_index = state['body_index']
        self._execute_for_loop(node, generator_state, start_index)

    # While Loop Implementation (minimal changes)  
    def eval_While(self, node: ast.While, generator_state: 'GeneratorState'=None) -> None:
        """Evaluate a While loop node."""
        
        # Non-generator case (blocking execution)
        if generator_state is None:
            while self.eval(node.test):
                try:
                    for stmt in node.body:
                        self.eval(stmt)
                except BreakException:
                    break
                except ContinueException:
                    continue
            else:
                for stmt in node.orelse:
                    self.eval(stmt)
            return

        # Generator case
        if self._should_resume_loop(generator_state, 'While'):
            # Resuming existing while loop
            self._execute_while_loop(node, generator_state, generator_state.compound_state['body_index'])
        else:
            # Starting new while loop
            self._setup_loop_state(generator_state, 'While', node, iteration=0)
            self._execute_while_loop(node, generator_state, 0)

    def _execute_while_loop(self, node: ast.While, generator_state: 'GeneratorState', start_index: int):
        """Execute a while loop, handling yields and resumption."""
        state = generator_state.compound_state
        
        # Check condition first (only at start of loop iteration)
        if start_index == 0:
            condition = self.eval(node.test)
            if not condition:
                # Loop finished, execute else clause
                state['broke'] = False
                self._handle_loop_completion(node, generator_state)
                return
            state['iteration'] = state.get('iteration', 0) + 1
        
        # Execute loop body
        for i in range(start_index, len(node.body)):
            stmt = node.body[i]
            
            try:
                self.eval(stmt)
            except YieldException as ye:
                # Yield encountered - pause execution
                state['body_index'] = i
                # Re-raise the YieldException to be caught by the main generator loop
                raise
            except BreakException:
                state['broke'] = True
                generator_state.compound_state = None
                return
            except ContinueException:
                state['body_index'] = 0
                self._execute_while_loop(node, generator_state, 0)
                return
        
        # If we completed the body without break/continue/yield, start next iteration
        if not state.get('broke', False):
            state['body_index'] = 0
            self._execute_while_loop(node, generator_state, 0)
        else:
            generator_state.compound_state = None

    def resume_While(self, node: ast.While, generator_state: 'GeneratorState'):
        """Resume execution of a paused While loop."""
        state = generator_state.compound_state
        if not state:
            return
            
        start_index = state['body_index']
        # Resume from the NEXT statement after the yield
        self._execute_while_loop(node, generator_state, start_index + 1)