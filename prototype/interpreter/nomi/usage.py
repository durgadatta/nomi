from .interpreter import Interpreter
from ...parser.nomi.usage import generate_ast
from ..runner import make_runner


run_eval_loop = make_runner(
    generate_ast=generate_ast,
    interpreter_cls=Interpreter,
    wrap_errors=True,
)
