from ...parser.python.ast_ import PythonASTTransformer
from .functions import FunctionsMixin

class NomiToPythonAST(
    FunctionsMixin,
    PythonASTTransformer
):
    pass 