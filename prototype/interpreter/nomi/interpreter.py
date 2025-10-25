from ...interpreter.python import Interpreter as PythonInterpreter
from .base import Environment
from .binding import BindingMixin
from .functions import FunctionMixin

class Interpreter(
    BindingMixin, FunctionMixin,
    PythonInterpreter):
    env_class = Environment


