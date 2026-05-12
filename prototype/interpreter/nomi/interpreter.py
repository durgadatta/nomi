from ...interpreter.python import Interpreter as PythonInterpreter
from .env import Environment
from .generator_state import CoroutineState
from .binding import ConstraintBindingMixin
from .functions import BlockFunctionMixin


class Interpreter(
    ConstraintBindingMixin, BlockFunctionMixin,
    PythonInterpreter):
    env_class = Environment
    gen_state = CoroutineState


