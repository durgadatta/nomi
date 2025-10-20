from prototype.interpreter.python import Interpreter as PythonInterpreter
from .base import Environment
from .binding import BindingMixin

class Interpreter(BindingMixin, PythonInterpreter):
    env_class = Environment


