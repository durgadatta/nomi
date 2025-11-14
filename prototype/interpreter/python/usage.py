import ast 
from typing import Dict, Any
from pathlib import Path

from ..python import Interpreter
from ...parser.python.utils import generate_ast


def run_eval_loop(code = None, file_name=None, tree=None) -> Dict[str, Any]:
    assert code or file_name or tree
    if tree is None:
        if code is None:
            code = Path(file_name).read_text(encoding='utf-8')
        tree = generate_ast(code=code)
        

    tree = ast.fix_missing_locations(tree)
    interpreter = Interpreter()
    interpreter.eval(tree)
    return interpreter.global_env.bindings
