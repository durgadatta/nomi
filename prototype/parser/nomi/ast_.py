from ...parser.python.ast_ import PythonASTTransformer
from .functions import FunctionsMixin

# TODO(NOMI-SUBSTRATE-005): Extend the Surface AST layer to cover data
# declarations, match expressions, constraints, and syntax islands.
# BlockCall already preserves source shape via surface node; the same
# pattern should apply to the remaining constructs.
# TODO(NOMI-SUBSTRATE-004): SourceSpan now flows through BlockCall lowering
# via captures_span (visit_wrapper). Apply @captures_span to remaining
# lowering methods that produce SurfaceNodes, and wire SourceSpan through
# the parser/lowering layer for AST nodes that don't use SurfaceNode
# (bindings, functions, calls, match cases).
class NomiToPythonAST(
    FunctionsMixin,
    PythonASTTransformer
):
    pass
