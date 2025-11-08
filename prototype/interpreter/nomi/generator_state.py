from ..python.generator_state import GeneratorState as PythonGeneratorState


class GeneratorState(PythonGeneratorState):
    def __init__(self, *args, block=None, **kwargs):
        super().__init__(*args, **kwargs)
        #TODO: make it explicit block/env
        self.block = block 


    def _handle_yield_to_block(self):
        if self.block:
            block, env = self.block 
            with self.interpreter.this_env(env):
                #TODO: is block not wrapped in .body like other ones?
                # also abstract other "for stmt in" block execution with env as optional param
                for stmt in block or []:
                    self.interpreter.eval(stmt)

    def _handle_yield(self):
        super()._handle_yield()
        self._handle_yield_to_block()
