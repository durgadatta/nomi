from ..python.generator_state import GeneratorState as PythonGeneratorState


class GeneratorState(PythonGeneratorState):
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
            # abstract that part in function call/def handling
            if params:
                if not isinstance(yield_values, tuple):
                    yield_values = (yield_values,)
                for arg, param_value in zip(params.args, yield_values):
                    param_name = arg.arg
                    env.set(param_name, param_value)
            with self.interpreter.this_env(env): 
                self.interpreter.eval(block)

    def _handle_yield(self, yield_values):
        super()._handle_yield()
        try:
            self._handle_yield_to_block(yield_values)
        except Exception as e:
            # transfer the exception from block to the generator state
            self.throw(e)
        