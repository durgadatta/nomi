from .interpreter import Interpreter
from ...parser.nomi.usage import generate_ast
from ...parser.nomi.desugar.underscore_lambda import UnderscoreLambda
from ...parser.nomi.desugar.piecewise import PiecewiseFunction
from ...parser.nomi.desugar.where_clause import WhereClause
from ..runner import make_runner


def _nomi_desugar(tree):
    """Nomi-only desugar passes (run before interpreter eval)."""
    tree = UnderscoreLambda().visit(tree)
    tree = PiecewiseFunction().visit(tree)
    tree = WhereClause().visit(tree)
    import ast
    ast.fix_missing_locations(tree)
    return tree


run_eval_loop = make_runner(
    generate_ast=generate_ast,
    interpreter_cls=Interpreter,
    desugar=_nomi_desugar,
    wrap_errors=True,
)
