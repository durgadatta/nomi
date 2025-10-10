import ast
from typing import Any, Dict, List, Optional, Tuple, Callable, Iterator, Set
import builtins


from prototype.interpreter.python.base import Environment, ControlException
from prototype.interpreter.python.function import FunctionMixin
from prototype.interpreter.python.expressions import ExpresssionMixin
from prototype.interpreter.python.ds import DataStructMixin
from prototype.interpreter.python.control import ControlMixin
from prototype.interpreter.python.patterns import PatternMixin
from prototype.interpreter.python.klass import ClassMixin
from prototype.interpreter.python.binding import BindingMixin
from prototype.interpreter.python.others import OthersMixin

class Interpreter(
    BindingMixin, FunctionMixin, ExpresssionMixin, DataStructMixin,
    PatternMixin, ControlMixin, ClassMixin, OthersMixin
):
    """Evaluates AST nodes."""
    def __init__(self):
        self.builtin_env = Environment(self)
        self.builtin_env.bindings = builtins.__dict__.copy()
        self.global_env = Environment(self, parent=self.builtin_env)
        self.current_env = self.global_env

    def eval(self, node: Optional[ast.AST]) -> Any:
        if node is None:
            return None
        method = getattr(self, f'eval_{node.__class__.__name__}', None)
        if method is None:
            raise NotImplementedError(f"Node type {node.__class__.__name__} not supported at line {self.get_lineno(node)}")
        try:
            return method(node)
        except ControlException as ce:
            raise
        except Exception as e:
            raise RuntimeError(f"Error evaluating {node.__class__.__name__} at line {self.get_lineno(node)}: {str(e)}") from e


    def eval_Module(self, node: ast.Module) -> Any:
        for stmt in node.body:
            self.eval(stmt)
        return None
        


