import ast
from lark import Transformer

from prototype.syntax.surface import _is_stmt_or_surface

from . import (
    BindingMixin, ExpressionMixin, StatementMixin, FunctionMixin, ControlMixin,
    ClassMixin, ExceptionMixin, ModuleMixin, PatternMixin, OthersMixin
)

class ModuleMixin(
    BindingMixin,
    ExpressionMixin,
    StatementMixin,
    ControlMixin,
    FunctionMixin,
    ExceptionMixin,
    PatternMixin,
    ClassMixin,
    ModuleMixin,
    OthersMixin
):
    def file_input(self, items):
        body = []
        for it in items:
            if isinstance(it, list):
                for s in it:
                    if _is_stmt_or_surface(s):
                        body.append(s)
            elif _is_stmt_or_surface(it):
                body.append(it)
        return ast.Module(body=body, type_ignores=[])

    def single_input(self, items): return self.file_input(items)
    def eval_input(self, items):
        if items: return items[0]
        return ast.Expression(body=ast.Constant(None))


class PythonASTTransformer(
    ModuleMixin,
    Transformer):
    pass
