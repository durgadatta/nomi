from ...interpreter.python import Interpreter as PythonInterpreter
from .base import Environment
from .generator_state import CoroutineState
from .binding import BindingMixin
from .functions import FunctionMixin

class Interpreter(
    BindingMixin, FunctionMixin,
    PythonInterpreter):
    env_class = Environment
    gen_state = CoroutineState


