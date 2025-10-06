import ast 
from lark import Transformer

from prototype.parser.python import (
    ensure_expr, 
    BindingMixin, ExpressionMixin, StatementMixin, FunctionMixin, ControlMixin,
    ClassMixin, ExceptionMixin, ModuleMixin
)

class ModuleMixin(
    BindingMixin,
    ExpressionMixin, 
    StatementMixin,
    ControlMixin,
    FunctionMixin,
    ExceptionMixin, 
    ClassMixin,
    ModuleMixin  
):
    def file_input(self, items):
        body = []
        for it in items:
            if isinstance(it, list):
                for s in it:
                    if isinstance(s, ast.stmt): body.append(s)
            elif isinstance(it, ast.stmt): body.append(it)
        return ast.Module(body=body, type_ignores=[])

    def single_input(self, items): return self.file_input(items)
    def eval_input(self, items):
        if items: return ensure_expr(items[0])
        return ast.Expression(body=ast.Constant(None))


class PythonASTTransformer(
    ModuleMixin,
    Transformer):
    pass
    def __default__(self, data, children, meta):
        # collapse single-child wrappers
        if len(children) == 1:
            return children[0]
        return children
