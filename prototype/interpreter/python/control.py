import ast

from prototype.interpreter.python.base import (
    Environment, ControlException, GeneratorState, 
    BreakException, ContinueException, YieldException
)

class ControlMixin:
    def eval_While(self, node: ast.While) -> None:
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
        exc = self.eval(node.exc) if node.exc else None
        cause = self.eval(node.cause) if node.cause else None
        if exc is None:
            raise SyntaxError(f"raise requires an exception at line {self.get_lineno(node)}")
        if cause:
            raise exc from cause
        raise exc

    def eval_Try(self, node: ast.Try) -> None:
        exc = None
        handler_executed = False
        
        try:
            for stmt in node.body:
                self.eval(stmt)
        except Exception as e:
            exc = e
            for handler in node.handlers:
                handler_type = self.eval(handler.type) if handler.type else None
                if handler_type is None or isinstance(e, handler_type):
                    if handler.name:
                        self.current_env.set(handler.name, e)
                    # Set flag and break out of try-except
                    handler_executed = True
                    break
            if not handler_executed:
                raise
        
        # Now execute handler body outside the try block
        if handler_executed:
            for handler in node.handlers:
                handler_type = self.eval(handler.type) if handler.type else None
                if handler_type is None or isinstance(exc, handler_type):
                    for stmt in handler.body:
                        self.eval(stmt)
                    break
        
        if not exc:  # No exception occurred
            for stmt in node.orelse:
                self.eval(stmt)
        
        for stmt in node.finalbody:
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
        

    def _execute_for_loop(self, node: ast.For, generator_state: 'GeneratorState', start_index: int):
        """
        Internal, resume-aware loop executor.
        """
        state = generator_state.compound_state
        iterator = state['iterator']
        
        assign_fn = getattr(self, "assign_target", None) or getattr(self, "_assign_target", None)
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
                
                # Reset start_index for next iteration (if we complete the body)
                start_index = 0
                
                while i < len(node.body):
                    stmt = node.body[i]
                    try:
                        self.eval(stmt)
                        i += 1
                    except YieldException as ye:
                        # Save the NEXT index to execute
                        generator_state.compound_state = {
                            'type': 'For', 
                            'node': node, 
                            'iterator': iterator,
                            'body_index': i + 1,  # Save NEXT index (we've completed this statement)
                            'broke': broke
                        }
                        raise ye
                    except BreakException:
                        broke = True
                        break
                    except ContinueException:
                        break  # Break out of inner while, continue to next iteration
                
                # Check if we broke out due to break
                if broke:
                    break

        except YieldException:
            raise
        except Exception:
            generator_state.compound_state = None
            raise
        
        # Loop completed
        generator_state.compound_state = None
        if not broke and hasattr(node, 'orelse'):
            for stmt in node.orelse:
                self.eval(stmt)

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
                
            assign_fn = getattr(self, "assign_target", None) or getattr(self, "_assign_target", None)
            if assign_fn is None:
                raise RuntimeError("No assignment helper found for blocking For loop.")
            
            broke = False
            
            try:
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
            except Exception:
                raise
            
            if not broke:
                for stmt in node.orelse:
                    self.eval(stmt)
            return

        # Generator case
        if generator_state.compound_state and generator_state.compound_state.get('type') == 'For':
            # Resuming existing for loop
            self._execute_for_loop(node, generator_state, generator_state.compound_state['body_index'])
        else:
            # Starting new for loop
            iter_obj = self.eval(node.iter)
            iterator = iter(iter_obj)

            generator_state.compound_state = {
                'type': 'For', 
                'node': node, 
                'iterator': iterator,
                'body_index': 0, 
                'broke': False
            }
            
            self._execute_for_loop(node, generator_state, 0)

    def resume_For(self, node: ast.For, generator_state: 'GeneratorState'):
        """Resume execution of a paused For loop."""
        state = generator_state.compound_state
        if not state:
            return
            
        start_index = state['body_index']
        self._execute_for_loop(node, generator_state, start_index)