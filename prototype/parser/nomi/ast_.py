import os
import sys

from lark import Tree as LarkTree

from ...parser.python.ast_ import PythonASTTransformer
from .functions import FunctionsMixin

# Set NOMI_LOG_UNHANDLED_RULES=1 to print every grammar rule that falls
# through to Lark's default Tree constructor (diagnostic for Pyodide).
_SHOULD_LOG_UNHANDLED = os.environ.get(
    "NOMI_LOG_UNHANDLED_RULES", ""
).lower() in ("1", "true", "yes")

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
    def __default__(self, data, children, meta):
        if _SHOULD_LOG_UNHANDLED:
            print(
                f"[nomi] unhandled rule: {data!r} ({len(children)} children)",
                file=sys.stderr,
            )
        return LarkTree(data, children, meta)
