import ast
from typing import Any, Dict, List, Optional, Tuple, Callable, Iterator, Set
import builtins


from .base import (
    Environment, ReturnException, BreakException, ContinueException, YieldException
)
from .function import FunctionMixin
from .expressions import ExpresssionMixin
from .ds import DataStructMixin
from .control import ControlMixin
from .patterns import PatternMixin
from .class_ import ClassMixin
from .binding import BindingMixin
from .others import OthersMixin

from .context_managers import ContextMangerMixin

class Interpreter(
    BindingMixin, FunctionMixin, ExpresssionMixin, DataStructMixin,
    PatternMixin, ControlMixin, ClassMixin, ContextMangerMixin, OthersMixin
):
    """Evaluates AST nodes."""
    env_class = Environment
    def __init__(self):
        self.builtin_env = self.env_class(self)
        self.builtin_env.bindings = builtins.__dict__.copy()
        self.global_env = self.env_class(self, parent=self.builtin_env)
        self.current_env = self.global_env

    def eval(self, node: Optional[ast.AST]) -> Any:
        if node is None:
            return None
        method = getattr(self, f'eval_{node.__class__.__name__}', None)
        if method is None:
            raise NotImplementedError(f"Node type {node.__class__.__name__} not supported at line {self.get_lineno(node)}")

        try:
            method = getattr(self, f"eval_{node.__class__.__name__}", None)
            return method(node)
        except (StopIteration, ZeroDivisionError):
            # Re-raise semantic exceptions unchanged
            raise
        except Exception as e:
            # Only wrap "unexpected" exceptions, not user-raised ones
            if isinstance(e, (RuntimeError, TypeError, ValueError, NameError, AttributeError, SyntaxError)):
                # These are likely user-raised or Python built-in exceptions
                # Let them propagate for try-except blocks to catch
                raise
            else:
                # Wrap other exceptions as interpreter errors
                raise RuntimeError(f"Error evaluating {node.__class__.__name__} at line {self.get_lineno(node)}: {str(e)}") from e
        
    def eval_Module(self, node: ast.Module) -> Any:
        for stmt in node.body:
            self.eval(stmt)
        return None
        


