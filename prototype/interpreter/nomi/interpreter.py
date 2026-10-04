from ...interpreter.python import Interpreter as PythonInterpreter
from .env import Environment
from .generator_state import CoroutineState
from .binding import ConstraintBindingMixin
from .functions import BlockFunctionMixin
from ...runtime.collections import fold, scan


class Interpreter(ConstraintBindingMixin, BlockFunctionMixin, PythonInterpreter):
    env_class = Environment
    gen_state = CoroutineState

    def __init__(self):
        super().__init__()
        self.builtin_env.bindings.update(fold=fold, scan=scan)
