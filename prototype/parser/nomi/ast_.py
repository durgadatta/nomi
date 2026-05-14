from ...parser.python.ast_ import PythonASTTransformer
from .functions import FunctionsMixin

# TODO(NOMI-SUBSTRATE-005): Insert a Nomi-owned Surface AST layer before this
# Python AST transformer. New syntax such as data declarations, block calls,
# match expressions, constraints, and syntax islands should preserve source
# shape first, then lower to core normal forms and finally to Python AST.
# TODO(NOMI-SUBSTRATE-004): When the Surface AST lands, attach SourceSpan data
# here instead of relying only on Python AST line/column fields.
class NomiToPythonAST(
    FunctionsMixin,
    PythonASTTransformer
):
    pass
