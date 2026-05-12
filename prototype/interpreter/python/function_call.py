'''
essentially all expression are function call or var ref, so most changes will concentrate here
thus, separating this into a new file
'''
import ast
from ..constants import BLOCK_KWARG, Block
from typing import Any

from .signals import YieldException


class FunctionCallResumable:
    def _extend_positional_arg(self, args, arg: ast.expr, *, generator_state=None):
        if isinstance(arg, ast.Starred):
            starred_val = self.eval(arg.value, generator_state=generator_state)
            args.extend(starred_val)
        else:
            args.append(self.eval(arg, generator_state=generator_state))

    def _merge_keyword_arg(self, kwargs, kw: ast.keyword, *, call_node=None, generator_state=None):
        if kw.arg is None:
            kw_val = self.eval(kw.value, generator_state=generator_state)
            if not isinstance(kw_val, dict):
                lineno = self.get_lineno(call_node or kw)
                raise TypeError(f"argument after ** must be a mapping at line {lineno}")
            kwargs.update(kw_val)
            return

        kwargs[kw.arg] = self._keyword_value(kw, generator_state=generator_state)

    def _keyword_value(self, kw: ast.keyword, *, generator_state=None):
        if kw.arg == BLOCK_KWARG:
            block = kw.value
            block.env = self.current_env
            return block
        return self.eval(kw.value, generator_state=generator_state)

    def eval_Call(self, node: ast.Call, *, state=None, generator_state=None) -> Any:
        """
        Evaluate a function call, supporting yields in arguments.
        """
        
        if state is not None:
            # Resuming from a yield in arguments
            func, evaluated_args, next_arg_index = state
            sent_value = generator_state.get_sent_value() if generator_state else None
            
            # Replace the yield with sent value and continue
            return self._continue_call_evaluation(node, func, evaluated_args, next_arg_index, sent_value, generator_state)
        
        else:
            # First time - start fresh
            func = self.eval(node.func, generator_state=generator_state)
            return self._continue_call_evaluation(node, func, [], 0, None, generator_state)

    def _continue_call_evaluation(self, node, func, evaluated_args, start_index, sent_value, generator_state):
        """
        Continue evaluating call arguments from start_index.
        """
        kwargs = {}
        
        # Track current evaluation index across both loops
        current_index = start_index
        
        try:
            # Process positional arguments
            for i in range(start_index, len(node.args)):
                arg = node.args[i]
                current_index = i
                
                # If we have a sent_value for this position (resuming from yield)
                if i == start_index and sent_value is not None:
                    evaluated_args.append(sent_value)
                    continue

                self._extend_positional_arg(evaluated_args, arg, generator_state=generator_state)
            
            # Process keyword arguments
            kw_start = 0
            if start_index > len(node.args):
                kw_start = start_index - len(node.args)
                
            for kw_index, kw in enumerate(node.keywords[kw_start:], kw_start):
                current_index = len(node.args) + kw_index
                
                # If we have a sent_value for this keyword (resuming from yield)
                if len(node.args) + kw_index == start_index and sent_value is not None:
                    if kw.arg == BLOCK_KWARG:
                        value = sent_value
                        if isinstance(value, Block):
                            value.env = self.current_env
                    else:
                        value = sent_value
                    kwargs[kw.arg] = value
                    continue

                self._merge_keyword_arg(kwargs, kw, call_node=node, generator_state=generator_state)
                    
        except YieldException as ye:
            # Pause at current index (works for both positional and keyword args)
            state = (func, evaluated_args, current_index)
            if generator_state:
                generator_state.pause(node, state)
            raise YieldException(ye.value)
        
        result = func(*evaluated_args, **kwargs)
        
        # NOTE: this is an abuse of mechanism used in for send() to 
        # communicate with assignment
        # review better way to deal with this
        if generator_state:
            generator_state.sent_value = result 
        return result
    

class FunctionCall:
    '''
    Keep this as well, as the resumable implementation significantly distorts the 
    readability/simplicity
    '''
    def eval_Call(self, node: ast.Call) -> Any:
        func = self.eval(node.func)
        # Evaluate arguments
        posargs = []
        for arg in node.args:
            self._extend_positional_arg(posargs, arg)

        kwargs = {}
        for kw in node.keywords:
            self._merge_keyword_arg(kwargs, kw, call_node=node)

        return func(*posargs, **kwargs)
    

class FunctionCallMixin(FunctionCallResumable, FunctionCall):
    pass
