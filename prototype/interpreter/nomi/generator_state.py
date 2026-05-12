from ..python.generator_state import CoroutineState as PythonCoroutineState
from ..constants import Block
import ast


class CoroutineState(PythonCoroutineState):
    def __init__(self, *args, block=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.block: Block = block

    def _handle_yield_to_block(self, yield_values):
        block = self.block
        if block and block.body:
            with self.interpreter.this_env(block.env):
                if block.params:
                    self.interpreter.assign_target(block.params, yield_values)
                self.interpreter.eval(block.body)

    def _handle_yield(self, yield_value=None):
        super()._handle_yield()
        try:
            self._handle_yield_to_block(yield_value)
        except Exception as e:
            self.throw(e)