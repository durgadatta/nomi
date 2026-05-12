from ..python.generator_state import CoroutineState as PythonCoroutineState
import ast


class CoroutineState(PythonCoroutineState):
    def __init__(self, *args, block=None, **kwargs):
        super().__init__(*args, **kwargs)
        #TODO: make it explicit block/params/env
        self.block = block 


    def _handle_yield_to_block(self, yield_values):
        if self.block:
            block, params, env = self.block
            if block is None:
                return 
            
            #TODO: use the same mechanism as function params binding here
            with self.interpreter.this_env(env): 
                if params:
                    self.interpreter.assign_target(params, yield_values)

                self.interpreter.eval(block)

    def _handle_yield(self, yield_value=None):
        super()._handle_yield()
        try:
            self._handle_yield_to_block(yield_value)
        except Exception as e:
            self.throw(e)
        