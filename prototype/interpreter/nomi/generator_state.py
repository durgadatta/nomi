from ..python.generator_state import GeneratorState as PythonGeneratorState


class GeneratorState(PythonGeneratorState):
    def __init__(self, *args, block=None, **kwargs):
        super().__init__(*args, **kwargs)
        #TODO: make it explicit block/env
        self.block = block 


    def _handle_yield_to_block(self):
        if self.block:
            block, env = self.block
            if block is None:
                return 
            with self.interpreter.this_env(env):
                #TODO: is block not wrapped in .body like other ones?
                # also abstract other "for stmt in" block execution with env as optional param
                self.interpreter.eval(block)

    def _handle_yield(self):
        try:
            self._handle_yield_to_block()
        except Exception as e:
            # transfer the exception from block to the generator state
            self.throw(e)
        super()._handle_yield()