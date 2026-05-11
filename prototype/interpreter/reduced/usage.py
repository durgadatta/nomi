import ast
from typing import Dict, Any
from pathlib import Path

from .interpreter import Interpreter
from ...parser.nomi.usage import generate_ast
from ...parser.nomi.desugar import desugar_module


def run_eval_loop(code=None, file_name=None, tree=None) -> Dict[str, Any]:
    assert code or file_name or tree
    if tree is None:
        if code is None:
            code = Path(file_name).read_text(encoding='utf-8')
        tree = generate_ast(code=code, dump=False)

    tree = desugar_module(tree)
    tree = ast.fix_missing_locations(tree)
    interpreter = Interpreter()
    try:
        interpreter.eval(tree)
        return interpreter.global_env.bindings
    except Exception as e:
        raise RuntimeError(f"Execution failed: {str(e)}") from e
