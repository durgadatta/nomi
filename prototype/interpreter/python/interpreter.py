import ast
from typing import Any, List, Optional
import builtins
from contextlib import contextmanager


from .env import (
    Environment
)
from .generator_state import CoroutineState
from .function import FunctionMixin
from .expressions import ExpressionMixin
from .ds import DataStructMixin
from .control import ControlMixin
from .patterns import PatternMixin
from .class_ import ClassMixin
from .binding import BindingMixin
from .others import OthersMixin

from .context_managers import ContextManagerMixin

class Interpreter(
    BindingMixin, FunctionMixin, ExpressionMixin, DataStructMixin,
    PatternMixin, ControlMixin, ClassMixin, ContextManagerMixin, OthersMixin
):
    """Evaluates AST nodes."""

    env_class = Environment
    gen_state = CoroutineState

    resumable_node_types: tuple = (
        ast.If,
        ast.For,
        ast.While,
        ast.Try,
        ast.With,
        ast.Assign,
        ast.Call,
    )

    pass_through_exceptions: tuple = (
        StopIteration, ZeroDivisionError, StopAsyncIteration,
        RuntimeError, TypeError, ValueError, NameError,
        AttributeError, SyntaxError, IndexError, KeyError,
        AssertionError,
    )

    __eval_dispatch = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.__eval_dispatch = cls._build_eval_dispatch()

    @classmethod
    def _build_eval_dispatch(cls):
        """Auto-build {ast_type: unbound_method} from eval_* methods in the MRO."""
        # TODO(NOMI-SUBSTRATE-024): Keep this convenient method-name dispatch,
        # but layer semantic metadata on top: feature owner, operation name,
        # accepted node kinds, resumable policy, and trace/diagnostic hooks.
        dispatch = {}
        for attr_name in dir(cls):
            if not attr_name.startswith('eval_') or attr_name == 'eval_list':
                continue
            node_name = attr_name[5:]
            node_type = getattr(ast, node_name, None)
            if node_type is not None:
                dispatch[node_type] = getattr(cls, attr_name)
        return dispatch

    def __init__(self):
        self.builtin_env = self.env_class(self)
        self.builtin_env.bindings = builtins.__dict__.copy()
        self.global_env = self.env_class(self, parent=self.builtin_env)
        self.current_env = self.global_env
        if type(self).__eval_dispatch is None:
            type(self).__eval_dispatch = self._build_eval_dispatch()

    @staticmethod
    def get_lineno(node):
        """Get line number from node, defaulting to 1 if missing."""
        return getattr(node, 'lineno', 1)

    @classmethod
    def is_resumable(cls, node):
        return isinstance(node, cls.resumable_node_types)

    def eval(self, node: Optional[ast.AST|List], *, state=None, generator_state=None) -> Any:
        '''
        :param state: State to resume from 
        :param generator_state: one per generator, 
            uses stack to keep track of yields within nested resume-ables
        '''
        # Handle list of statements (common case)
        if isinstance(node, list):
            for stmt in node:
                self.eval(stmt, state=state, generator_state=generator_state)
            return None

        # Handle None node
        if node is None:
            return None

        func = self.__eval_dispatch.get(type(node))
        if func is None:
            lineno = self.get_lineno(node)
            raise NotImplementedError(
                f"Node type {node.__class__.__name__} not supported at line {lineno}"
            )
        try:
            if self.is_resumable(node):
                return func(self, node, state=state, generator_state=generator_state)
            return func(self, node)
        except self.pass_through_exceptions:
            raise
        except Exception as e:
            lineno = self.get_lineno(node)
            raise RuntimeError(
                f"Error evaluating {node.__class__.__name__} at line {lineno}: {str(e)}"
            ) from e


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

            TODO: for resumable eval, we need to know at what point we resumed
                maybe return, the number of statements evaluated
        '''
        for stmt in stmts:
            self.eval(stmt)
        
    def eval_Module(self, node: ast.Module) -> Any:
        self.eval(node.body)
