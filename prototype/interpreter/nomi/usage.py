from .interpreter import Interpreter
from ...parser.nomi.usage import generate_ast
from ...parser.nomi.desugar import desugar_module
from ..runner import make_runner


run_eval_loop = make_runner(
    generate_ast=generate_ast,
    interpreter_cls=Interpreter,
    desugar=desugar_module,
    wrap_errors=True,
)
