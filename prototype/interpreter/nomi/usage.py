from .interpreter import Interpreter
from ...parser.nomi.usage import generate_ast
from ...parser.nomi.desugar import desugar_module_for_nomi_interpreter
from ..runner import make_runner


run_eval_loop = make_runner(
    generate_ast=generate_ast,
    interpreter_cls=Interpreter,
    desugar=desugar_module_for_nomi_interpreter,
    wrap_errors=True,
)
