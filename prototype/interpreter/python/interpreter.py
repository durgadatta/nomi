import ast
from typing import Any, Dict, List, Optional, Tuple, Callable, Iterator, Set
import builtins
from contextlib import contextmanager


from .base import (
    Environment, ReturnException, BreakException, ContinueException, YieldException
)
from .generator_state import GeneratorState
from .function import FunctionMixin
from .expressions import ExpresssionMixin
from .ds import DataStructMixin
from .control import ControlMixin
from .patterns import PatternMixin
from .class_ import ClassMixin
from .binding import BindingMixin
from .others import OthersMixin

from .context_managers import ContextManagerMixin

class Interpreter(
    BindingMixin, FunctionMixin, ExpresssionMixin, DataStructMixin,
    PatternMixin, ControlMixin, ClassMixin, ContextManagerMixin, OthersMixin
):
    """Evaluates AST nodes."""
    env_class = Environment
    gen_state = GeneratorState
    def __init__(self):
        self.builtin_env = self.env_class(self)
        self.builtin_env.bindings = builtins.__dict__.copy()
        self.global_env = self.env_class(self, parent=self.builtin_env)
        self.current_env = self.global_env


    @staticmethod
    def is_resumable(node):
        can_resume = (
            ast.For,
            ast.While
        )
        return isinstance(node, can_resume)

    def eval(self, node: Optional[ast.AST|List], *, state=None, generator_state=None) -> Any:
        '''
        :param state: State to resume from 
        :param generator_state: one per generator, 
            uses stack to keep track of yields withing nested resume-ables
        '''

        #TODO: why do we get this?
        if node is None:
            return None
        
        node_name = node.__class__.__name__
        method = getattr(self, f'eval_{node_name}', None)
        if method is None:
            raise NotImplementedError(f"Node type {node_name} not supported at line {self.get_lineno(node)}")
        try:
            if self.is_resumable(node):
                return method(node, state=state, generator_state=generator_state)
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

    @contextmanager
    def this_env(self, env):
        """
        Context manager for temporarily switching environments.
        """
        old_env = self.current_env
        self.current_env = env
        try:
            yield
        finally:
            self.current_env = old_env

    def eval_list(self, stmts):
        '''
            Note: this is not actually an ast.node
            but a Python list; convenience for most block
            structure. This is not evaluating list in target language
            but is used as a helper in host language, elements of
            list are ASTs for target language.

            This maybe only one non-ast node.
            Think if adding other structure might help
        '''
        for stmt in stmts:
            self.eval(stmt)
        
    def eval_Module(self, node: ast.Module) -> Any:
        self.eval(node.body)
